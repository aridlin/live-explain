"""Small authoring vocabulary. Content stays executable Python, not a YAML DSL."""

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Callable


@dataclass(frozen=True)
class Script:
    objective: str
    cue: str
    wording: str
    next_sentence: str
    boundary: str
    recap: str = ""
    resume_sentence: str = "Wróćmy dokładnie do miejsca, w którym przerwaliśmy."
    entry_sentence: str = "Teraz spójrzmy na ten sam mechanizm z nowej perspektywy."


@dataclass(frozen=True)
class Event:
    at: float
    kind: str
    payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Beat:
    id: str
    checkpoint: str
    title: str
    subtitle: str
    composition: str
    script: Script
    holds: tuple[float, ...] = (0.0, 2.0, 4.0, 6.0)
    events: tuple[Event, ...] = ()
    covers: frozenset[str] = frozenset()
    requires: frozenset[str] = frozenset()
    detours: tuple[str, ...] = ("cache-location",)
    code: tuple[str, ...] = ()
    spans: dict[str, tuple[int, str]] = field(default_factory=dict)
    seed: int = 17
    planned_seconds: int = 60
    stage_cues: tuple[str, ...] = ()
    diagram: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Landing:
    canonical: str
    beat: str
    requires: frozenset[str] = frozenset()
    bridge: str | None = None


@dataclass
class Presentation:
    id: str
    beats: dict[str, Beat]
    routes: dict[str, tuple[str, ...]]
    detours: dict[str, str]
    landings: dict[str, Landing]
    initial: Callable[[Beat], dict]
    reduce: Callable[[dict, Event], None]
    model_version: str = "1"
    checkpoint_landings: dict[str, dict[str, Landing]] = field(default_factory=dict)

    def validate(self):
        if set(self.routes) != {"simple", "normal", "deep"}:
            raise ValueError("Exactly three canonical routes required")
        for key, beat in self.beats.items():
            if key != beat.id or not beat.holds or beat.holds[0] != 0:
                raise ValueError(f"Invalid beat: {key}")
            if beat.planned_seconds <= 0 or (beat.stage_cues and len(beat.stage_cues) != len(beat.holds)):
                raise ValueError(f"Invalid presenter pacing: {key}")
            if tuple(sorted(set(beat.holds))) != beat.holds:
                raise ValueError(f"Unordered holds: {key}")
            if any(e.at < 0 or e.at > beat.holds[-1] for e in beat.events):
                raise ValueError(f"Event outside sequence: {key}")
            if list(beat.events) != sorted(beat.events, key=lambda e: e.at):
                raise ValueError(f"Unordered events: {key}")
            for line, text in beat.spans.values():
                if line >= len(beat.code) or line < 0 or beat.code[line].count(text) != 1:
                    raise ValueError(f"Ambiguous code span: {key}/{text}")
            if not all(
                (
                    beat.script.objective,
                    beat.script.cue,
                    beat.script.wording,
                    beat.script.next_sentence,
                    beat.script.boundary,
                )
            ):
                raise ValueError(f"Incomplete script: {key}")
            if any(d not in self.detours for d in beat.detours):
                raise ValueError(f"Missing detour: {key}")
        reached = set(self.detours.values())
        for route in self.routes.values():
            if not route or len(route) != len(set(route)):
                raise ValueError("Empty or duplicate route")
            covered = set()
            for key in route:
                if key not in self.beats:
                    raise ValueError(f"Missing destination: {key}")
                beat = self.beats[key]
                if not beat.requires <= covered:
                    raise ValueError(f"Unestablished route prerequisite: {key}")
                covered.update(beat.covers)
            reached.update(route)
        for checkpoint, landings in self.checkpoint_landings.items():
            if set(landings) != set(self.routes):
                raise ValueError(f"Incomplete checkpoint correspondence: {checkpoint}")
        all_landings = list(self.landings.values()) + [
            landing for group in self.checkpoint_landings.values() for landing in group.values()
        ]
        for landing in all_landings:
            if landing.canonical not in self.routes or landing.beat not in self.routes[landing.canonical]:
                raise ValueError("Landing must belong to canonical")
            if landing.bridge:
                if landing.bridge not in self.beats:
                    raise ValueError("Missing bridge")
                if not landing.requires <= self.beats[landing.bridge].covers:
                    raise ValueError("Bridge cannot establish landing requirements")
                reached.add(landing.bridge)
        if reached != set(self.beats):
            raise ValueError(f"Missing or unreachable beats: {reached ^ set(self.beats)}")

    @property
    def fingerprint(self):
        from dataclasses import asdict

        value = dict(
            id=self.id,
            model_version=self.model_version,
            beats={k: asdict(v) for k, v in self.beats.items()},
            routes=self.routes,
            detours=self.detours,
            landings={k: asdict(v) for k, v in self.landings.items()},
            checkpoint_landings={
                key: {k: asdict(v) for k, v in group.items()}
                for key, group in self.checkpoint_landings.items()
            },
        )
        return sha256(json.dumps(value, sort_keys=True, default=lambda x: sorted(x)).encode()).hexdigest()
