"""Single authoritative session. Rendering is a read-only projection."""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
import uuid

from .authoring import Presentation


@dataclass
class Playback:
    position: float = 0.0
    playing: bool = False
    target: float = 0.0


@dataclass
class Narrative:
    canonical: str
    beat: str
    bridge_target: str | None = None


@dataclass
class Suspended:
    narrative: Narrative
    playback: Playback
    cue_index: int
    return_sentence: str


@dataclass
class SessionState:
    narrative: Narrative
    playback: Playback = field(default_factory=Playback)
    detours: list[Suspended] = field(default_factory=list)
    cue_index: int = 0
    return_sentence: str = ""


class Session:
    def __init__(self, presentation: Presentation, canonical="normal"):
        presentation.validate()
        self.presentation = presentation
        self.state = SessionState(Narrative(canonical, presentation.routes[canonical][0]))
        self.epoch = uuid.uuid4().hex
        self.revision = 0
        self.generation = 0
        self.elapsed = 0.0
        self.delivered: set[str] = set()
        self.assessments: dict[str, str] = {}
        self.history: list[SessionState] = []
        self.recording: list[dict] = []
        self.initial_canonical = canonical
        self.status = "Gotowe. Strzałka w prawo rozpoczyna kolejny krok."

    @property
    def beat(self):
        return self.presentation.beats[self.state.narrative.beat]

    @property
    def model(self):
        model = self.presentation.initial(self.beat)
        for event in self.beat.events:
            if event.at <= self.state.playback.position:
                self.presentation.reduce(model, event)
        return model

    def snapshot(self):
        return deepcopy(self.state)

    def _remember(self):
        self.history.append(self.snapshot())
        self.history = self.history[-32:]

    def _changed(self):
        self.revision += 1
        self.generation += 1

    def _entry(self, key):
        self.state.narrative.beat = key
        self.state.playback = Playback()
        self.state.cue_index = 0
        self.state.return_sentence = ""
        self._changed()

    def _coverage(self):
        if self.state.playback.position >= self.beat.holds[-1]:
            self.delivered.update(self.beat.covers)

    def tick(self, delta, generation=None):
        if not math.isfinite(delta) or delta < 0:
            raise ValueError("Invalid time delta")
        if generation is not None and generation != self.generation:
            return
        self.elapsed += delta
        p = self.state.playback
        if not p.playing:
            return
        if delta > 0.5:
            p.playing = False
            self._changed()
            self.status = "Wstrzymano po przerwie zegara."
            return
        p.position = min(p.position + delta, p.target)
        if p.position >= p.target:
            p.playing = False
            self._coverage()
            self._changed()

    def seek(self, position):
        if not isinstance(position, (float, int)) or not math.isfinite(position):
            raise ValueError("Invalid seek")
        if not 0 <= position <= self.beat.holds[-1]:
            raise ValueError("Seek outside beat")
        self.state.playback = Playback(float(position), False, float(position))
        self._changed()
        # Seeking is not evidence that the explanation was delivered.

    def landing_gaps(self, canonical):
        landing = self.presentation.landings[canonical]
        return landing.requires - self.delivered

    def command(self, kind, value=None, expected_revision=None, record=True):
        if expected_revision is not None and expected_revision != self.revision:
            return False, "Nieaktualny stan sterowania."
        before = (self.beat.id, asdict(self.state.playback), sorted(self.delivered))
        accepted, message = self._command(kind, value)
        self.status = message
        if accepted and record:
            self.recording.append(
                dict(kind=kind, value=value, beat=before[0], playback=before[1], delivered=before[2])
            )
        return accepted, message

    def _command(self, kind, value):
        p = self.state.playback
        if kind in {"pause", "freeze"}:
            p.playing = False
            self._changed()
            return True, "Wstrzymano."
        if kind == "seek":
            self.seek(value)
            return True, "Wybrano pozycję; odtwarzanie wstrzymane."
        if kind == "replay":
            self.seek(max((t for t in self.beat.holds if t < p.position - 1e-8), default=0))
            return True, "Początek kroku. Naciśnij Dalej, aby odtworzyć."
        if kind in {"advance", "play", "step", "finish"}:
            if p.playing and kind != "finish":
                return False, "Trwa krok; użyj Pauza albo Dokończ."
            next_hold = next((t for t in self.beat.holds if t > p.position + 1e-8), None)
            if next_hold is not None:
                if kind in {"step", "finish"}:
                    self.seek(next_hold)
                    self._coverage()
                else:
                    p.target = next_hold
                    p.playing = True
                    self._changed()
                self.state.return_sentence = ""
                return True, "Kolejny krok."
            if kind != "advance":
                return False, "Koniec sekwencji. Dalej wybiera następny punkt."
            if self.state.narrative.bridge_target:
                target = self.state.narrative.bridge_target
                self._remember()
                self._land(target)
                return True, "Most zakończony. Wybrano nową kontynuację."
            if self.state.detours:
                return False, "Koniec odpowiedzi. Wybierz Powrót lub inną kontynuację."
            route = self.presentation.routes[self.state.narrative.canonical]
            index = route.index(self.beat.id)
            if index + 1 >= len(route):
                return False, "Koniec tej trasy. Możesz odtworzyć fragment lub zmienić trasę."
            self._remember()
            self._entry(route[index + 1])
            return True, "Następny punkt."
        if kind == "detour":
            if value not in self.beat.detours or value not in self.presentation.detours:
                return False, "Ta odpowiedź nie jest dostępna w tym miejscu."
            if len(self.state.detours) >= 2:
                return False, "Najpierw wróć o jeden poziom."
            self._remember()
            self.state.detours.append(
                Suspended(
                    deepcopy(self.state.narrative),
                    deepcopy(p),
                    self.state.cue_index,
                    self.state.return_sentence,
                )
            )
            self.state.narrative.bridge_target = None
            self._entry(self.presentation.detours[value])
            return True, "Wyjaśnienie dodatkowe; poprzedni stan zachowany."
        if kind == "return":
            if not self.state.detours:
                return False, "Brak przerwanego wyjaśnienia."
            self._remember()
            frame = self.state.detours.pop()
            self.state.narrative = frame.narrative
            self.state.playback = frame.playback
            self.state.playback.playing = False
            self.state.cue_index = frame.cue_index
            self.state.return_sentence = "Wróćmy dokładnie do miejsca, w którym przerwaliśmy."
            self._changed()
            return True, "Przywrócono dokładną pozycję; wstrzymane."
        if kind == "depth":
            if value not in self.presentation.landings:
                return False, "Nieznana trasa."
            landing = self.presentation.landings[value]
            missing = self.landing_gaps(value)
            if missing and not landing.bridge:
                return False, "Brak przygotowanego mostu: " + ", ".join(sorted(missing))
            self._remember()
            if missing:
                self._entry(landing.bridge)
                self.state.narrative.bridge_target = value
                return True, "Najpierw most: " + ", ".join(sorted(missing))
            self._land(value)
            return True, "Nowa trasa; autorski stan wejściowy."
        if kind == "undo":
            if not self.history:
                return False, "Brak wcześniejszej nawigacji."
            self.state = self.history.pop()
            self.state.playback.playing = False
            self._changed()
            return True, "Cofnięto nawigację; odtwarzanie wstrzymane."
        return False, "Nieznane polecenie."

    def _land(self, canonical):
        self.state.narrative = Narrative(canonical, self.presentation.landings[canonical].beat)
        self.state.detours.clear()
        self._entry(self.state.narrative.beat)
        self.state.return_sentence = "Teraz spójrzmy na ten sam mechanizm z nowej perspektywy."

    def controller_state(self):
        return dict(
            epoch=self.epoch,
            revision=self.revision,
            canonical=self.state.narrative.canonical,
            beat=self.beat.id,
            position=self.state.playback.position,
            playing=self.state.playback.playing,
            cue=self.beat.script.cue,
            detours=self.beat.detours,
            return_to=self.state.detours[-1].narrative.beat if self.state.detours else None,
        )

    def save(self, path):
        """JSON recovery; never deserialize Python objects. Save a safe canonical entry."""
        canonical = self.state.narrative.canonical
        route = self.presentation.routes[canonical]
        key = self.beat.id if self.beat.id in route else route[0]
        value = dict(version=1, content=self.presentation.fingerprint, canonical=canonical, beat=key)
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(json.dumps(value), encoding="utf-8")
        temporary.replace(destination)

    def recover(self, path):
        value = json.loads(Path(path).read_text())
        if value.get("content") != self.presentation.fingerprint or value.get("version") != 1:
            raise ValueError("Incompatible recovery content")
        canonical, key = value.get("canonical"), value.get("beat")
        if canonical not in self.presentation.routes or key not in self.presentation.routes[canonical]:
            raise ValueError("Invalid recovery destination")
        self.state = SessionState(Narrative(canonical, key))
        self.epoch = uuid.uuid4().hex
        self.history.clear()
        self._changed()

    def export_recording(self):
        return dict(
            content=self.presentation.fingerprint,
            canonical=self.initial_canonical,
            commands=deepcopy(self.recording),
        )

    def replay_recording(self, recording):
        if recording["content"] != self.presentation.fingerprint:
            raise ValueError("Recording content mismatch")
        if recording.get("canonical") != self.state.narrative.canonical:
            raise ValueError("Recording canonical mismatch")
        for command in recording["commands"]:
            if command["beat"] != self.beat.id:
                raise ValueError("Recording route mismatch")
            self.seek(command["playback"]["position"])
            self.state.playback = Playback(**command["playback"])
            self.delivered = set(command["delivered"])
            accepted, message = self.command(command["kind"], command["value"], record=False)
            if not accepted:
                raise ValueError(message)

    def digest(self):
        return json.dumps(dict(state=asdict(self.state), model=self.model), sort_keys=True)
