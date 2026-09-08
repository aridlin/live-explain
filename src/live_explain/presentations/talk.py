"""Full Polish talk: three authored routes, 16 corresponding conceptual chapters."""

from dataclasses import replace
from ..authoring import Beat, Event, Landing, Presentation, Script
from . import spectre
from .talk_text import CHAPTERS

PUBLIC_CODE = ("index = 4;", "value = memory[index];", "again = memory[index];")
BRANCH_CODE = (
    "// x pochodzi z zewnątrz",
    "if (x < length) {",
    "    value = data[x];",
    "    touch(probe[value * stride]);",
    "}",
)


def initial(beat):
    model = spectre.initial(beat)
    model.update(
        memory=[(i * 13 + 7) % 256 for i in range(32)],
        public_value=1,
        fault=False,
        allowed=None,
        history=[],
        measurements=None,
        noise=beat.diagram.get("noise", False),
    )
    model["memory"][4], model["memory"][12] = 7, 2
    if beat.checkpoint in {"bytes", "cache", "timing"} or beat.id.startswith("bridge.foundations"):
        model["index"] = 4
    if beat.checkpoint == "decode":
        model.update(probe=2, cached=True, discarded=True)
    return model


def reduce(model, event):
    if event.kind == "allow":
        model["allowed"] = True
    elif event.kind == "deny":
        model["allowed"] = False
    elif event.kind == "train":
        model["history"].append(event.payload["index"])
    elif event.kind == "fault":
        model["fault"] = True
    elif event.kind == "encode-public":
        model.update(probe=model["public_value"], cached=True)
    elif event.kind == "measure":
        model["measurements"] = (
            [[2, 9, 8, 9], [9, 8, 3, 10], [8, 9, 2, 9]]
            if model["noise"]
            else [2 if index == model["probe"] else 9 for index in range(4)]
        )
    else:
        spectre.reduce(model, event)


COVERS = {
    "opening": set(),
    "isolation": {"isolation"},
    "bytes": {"addresses"},
    "cache": {"cache"},
    "timing": {"timing"},
    "channel": {"encoding"},
    "speculation": {"prediction"},
    "rollback": {"transient"},
    "bounds": {"bounds"},
    "training": {"training"},
    "spectre": {"spectre"},
    "decode": {"decode"},
    "meltdown": {"meltdown", "permissions"},
    "compare": {"distinction"},
    "defenses": {"mitigation"},
    "recap": set(),
}
REQUIRES = {
    "bytes": {"isolation"},
    "cache": {"addresses"},
    "timing": {"addresses", "cache"},
    "channel": {"addresses", "timing"},
    "speculation": {"timing"},
    "rollback": {"prediction"},
    "bounds": {"addresses", "isolation"},
    "training": {"bounds", "prediction"},
    "spectre": {"bounds", "prediction", "encoding"},
    "decode": {"encoding", "timing"},
    "meltdown": {"addresses", "isolation", "transient", "encoding"},
    "compare": {"spectre", "meltdown"},
    "defenses": {"distinction"},
    "recap": {"distinction"},
}
STAGES = {
    "opening": ("Postaw pytanie o wynik i ślad.", "Pokaż oficjalną odpowiedź.", "Pokaż osobną obserwację."),
    "isolation": (
        "Nazwij dwa rodzaje granic.",
        "Pokaż dozwolony wybór.",
        "Pokaż odmowę: reguła nadal obowiązuje.",
    ),
    "bytes": (
        "Wskaż adres 4 i wartość 7. Odczytaj kod.",
        "Zatrzymaj ruch i zapytaj, co podróżuje.",
        "Odczyt zakończony; oddziel wartość od adresu.",
    ),
    "cache": ("Umiejsców cache.", "Odsłoń kopie / linię.", "Nazwij skutek dla kolejnego odczytu."),
    "timing": (
        "Ten sam adres 4; kopii jeszcze nie ma.",
        "Adres w drodze; nie zmieniamy danych.",
        "Pierwszy odczyt: 9 umownych jednostek.",
        "Drugi odczyt: 2. Zapytaj o przyczynę.",
    ),
    "channel": (
        "Publiczny przykład: wartość 1.",
        "Wartość wybrała probe[1].",
        "Adres pozostawił możliwy do rozpoznania ślad.",
    ),
    "speculation": (
        "Warunek czeka na dane.",
        "Przewidywanie wybiera ścieżkę.",
        "Rozstrzygnięcie nie zgadza się z przewidywaniem.",
    ),
    "rollback": ("Rozdziel wynik i cache.", "Praca zmieniła cache.", "Odrzuć wynik, pozostaw ślad."),
    "bounds": (
        "Zakres funkcji: 0–7.",
        "Poprawne wejście mieści się w zakresie.",
        "12 < 8 jest fałszywe; pokaż granicę.",
    ),
    "training": (
        "Historia jest schematem, nie emulatorem predyktora.",
        "Poprawne wejścia.",
        "Kolejne poprawne wejścia.",
        "Nowe wejście: 12. Warunek nadal fałszywy.",
    ),
    "spectre": (
        "Nowe dane ofiary: sekret pod adresem 12 jest ukryty.",
        "Przewidziana ścieżka rozpoczęła odczyt.",
        "Wartość zasila adres probe.",
        "Wynik odrzucony, ślad pozostaje.",
        "Zostaw sekret zasłonięty; przejdź do pomiaru.",
    ),
    "decode": (
        "Obserwator nie otrzymał oficjalnie wartości.",
        "Porównaj cztery pokazane czasy.",
        "Odsłoń 2 i sprawdź regułę kodowania.",
    ),
    "meltdown": (
        "Nie ma ifa: odczyt narusza uprawnienia.",
        "Na podatnym układzie dane mogą przejściowo zasilić pracę.",
        "Zależny dostęp zostawił ślad.",
        "Brak zatwierdzonego wyniku; błąd nie usuwa śladu.",
        "Pomiar rozpoznaje wartość; nie jest to pomiar laptopa.",
    ),
    "compare": (
        "Najpierw nazwij dwie różne przyczyny.",
        "Porównaj granice dostępu.",
        "Dopiero teraz wskaż wspólny kanał.",
    ),
    "defenses": (
        "Pytaj, który etap chronimy.",
        "Kod / platforma ograniczają przejściowy dostęp.",
        "PTI ogranicza mapowania; sprzęt musi chronić przepływ danych.",
    ),
    "recap": (
        "Nie dodawaj nowych terminów.",
        "Odtwórz łańcuch wartości, adresu i czasu.",
        "Pozostały czas przeznacz na pytania i powroty.",
    ),
}


RETURN_POINTS = {
    "opening": "odrzucony wynik i obserwowalny ślad to dwie różne rzeczy",
    "isolation": "reguła funkcji i sprzętowe uprawnienia tworzą różne granice",
    "bytes": "adres 4 wskazuje miejsce, a 7 jest jego zawartością",
    "cache": "cache przechowuje kopie danych używane przez procesor",
    "timing": "odczytujemy ten sam adres, lecz stan cache może być inny",
    "channel": "publiczna wartość 1 wybiera miejsce w probe",
    "speculation": "przewidywanie dotyczy drogi wykonania, a nie zgadywania sekretu",
    "rollback": "odrzucenie wyniku nie musi usunąć śladu w cache",
    "bounds": "indeks 12 nie mieści się w zakresie od 0 do 7",
    "training": "historia poprawnych wejść może wpłynąć na przewidywany kierunek",
    "spectre": "ofiara przejściowo używa danych za granicą udostępnianego zakresu",
    "decode": "czas odczytu kandydatów pozwala próbować rozpoznać wcześniejszy wybór",
    "meltdown": "niedozwolony odczyt może na podatnym układzie zasilić zależną pracę",
    "compare": "podobny kanał nie oznacza tej samej przyczyny",
    "defenses": "ochrona musi przerwać konkretny etap tego mechanizmu",
    "recap": "wartość może wpłynąć na adres, cache i obserwowany czas",
}


def build():
    specimen = spectre.build()
    beats, routes, checkpoints = {}, {}, {}
    for canonical in ("simple", "normal", "deep"):
        route = []
        for chapter in CHAPTERS:
            phase = chapter.id
            key = f"{canonical}.{phase}"
            wording = getattr(chapter, canonical)
            script = Script(
                objective=chapter.cue,
                cue=chapter.cue,
                wording=wording + "\n\n[Opcjonalne pytanie do grupy]\n" + chapter.question,
                next_sentence=chapter.next_sentence,
                boundary=chapter.boundary,
                recap=RETURN_POINTS[phase].capitalize() + ".",
                resume_sentence="Wróćmy do zachowanego momentu: " + RETURN_POINTS[phase] + ".",
                entry_sentence=(
                    "Rozłóżmy to dokładniej: "
                    if canonical == "deep"
                    else "Zachowajmy podstawową zależność: "
                    if canonical == "simple"
                    else "Połączmy teraz kroki: "
                )
                + RETURN_POINTS[phase]
                + ".",
            )
            composition = "story:" + phase
            code, spans = (), {}
            holds = tuple(float(2 * i) for i in range(len(STAGES[phase])))
            events = ()
            covers = set(COVERS[phase])
            requires = set(REQUIRES.get(phase, set()))
            diagram = {"phase": phase, "canonical": canonical}
            if phase in {"bytes", "timing"}:
                composition = (
                    "simple" if canonical == "simple" else "lines" if canonical == "deep" else "timing"
                )
                code = PUBLIC_CODE[:2] if phase == "bytes" else PUBLIC_CODE
                spans = {"index": (1, "index")}
                events = (Event(0.1, "issue"), Event(4, "read"))
                if phase == "timing":
                    events += (Event(6, "repeat"),)
            elif phase == "cache":
                composition = "story:cache-line" if canonical == "deep" else "location"
                if canonical == "deep":
                    covers.add("lines")
            elif phase == "channel":
                events = (Event(2, "encode-public"),)
            elif phase in {"isolation", "bounds"}:
                events = (Event(2, "allow"), Event(4, "deny"))
            elif phase == "speculation":
                events = (Event(2, "predict"), Event(4, "discard"))
            elif phase == "rollback":
                events = (Event(2, "encode"), Event(4, "discard"))
            elif phase == "training":
                events = tuple(
                    Event(t, "train", {"index": index}) for t, index in ((0.5, 1), (2, 3), (3, 0), (4, 2))
                )
            elif phase == "spectre":
                composition = "probe" if canonical == "deep" else "branch"
                code, spans = BRANCH_CODE, {"index": (2, "x")}
                events = (Event(0.1, "predict"), Event(2, "issue"), Event(4, "encode"), Event(6, "discard"))
                diagram["secret"] = True
            elif phase == "decode":
                events = (Event(0.1, "measure"), Event(4, "reveal"))
                diagram["secret"] = True
            elif phase == "meltdown":
                code = (
                    "value = read(protected_address);",
                    "touch(probe[value * stride]);",
                    "// brak dozwolonego wyniku odczytu",
                )
                spans = {"address": (0, "protected_address")}
                events = (
                    Event(0.1, "fault"),
                    Event(2, "issue"),
                    Event(4, "encode"),
                    Event(6, "discard"),
                    Event(8, "reveal"),
                )
                diagram["secret"] = True
            if canonical == "deep" and phase in {"timing", "channel", "spectre", "decode"}:
                requires.add("lines")
            detours = (
                ("cache-location", "cache-lines", "timing-noise")
                if phase in {"cache", "timing", "channel", "decode"}
                else ("rollback-detail", "cache-location")
                if phase in {"speculation", "rollback", "spectre"}
                else ("vulnerable-device", "attack-difference")
                if phase in {"meltdown", "compare", "defenses", "recap"}
                else ("bytes-detail",)
            )
            beats[key] = Beat(
                key,
                phase,
                chapter.title,
                chapter.subtitle,
                composition,
                script,
                holds,
                events,
                frozenset(covers),
                frozenset(requires),
                detours,
                code,
                spans,
                planned_seconds=chapter.seconds,
                stage_cues=STAGES[phase],
                diagram=diagram,
            )
            route.append(key)
        routes[canonical] = tuple(route)

    detours = {}
    for name, source in (("cache-location", "shared.location"), ("cache-lines", "shared.lines")):
        beat = specimen.beats[source]
        beats[source] = replace(beat, planned_seconds=45, diagram={"phase": "cache", "canonical": "deep"})
        detours[name] = source
    extra = (
        (
            "bytes-detail",
            "bytes",
            "Odczytajmy zapis jeszcze raz.",
            "Adres wybiera miejsce. Odczyt daje wartość.",
        ),
        (
            "rollback-detail",
            "rollback",
            "Co dokładnie jest odrzucane?",
            "Wynik programu i stan cache mają różne role.",
        ),
        (
            "attack-difference",
            "compare",
            "Wróćmy do różnicy mechanizmów.",
            "Podobny ślad nie oznacza takiej samej granicy.",
        ),
        (
            "timing-noise",
            "decode",
            "Pojedynczy pomiar może mylić.",
            "Powtórzenia i szum: ilustracja, nie pomiar laptopa.",
        ),
        (
            "vulnerable-device",
            "defenses",
            "Czy ten komputer jest podatny?",
            "Z diagramu nie da się odczytać stanu konkretnego urządzenia.",
        ),
    )
    for name, phase, title, subtitle in extra:
        base = beats[f"normal.{phase}"]
        key = "detour." + name
        wording = base.script.wording
        if name == "timing-noise":
            wording = (
                "Pojedynczy szybki wynik nie jest automatycznie dowodem. Inna praca może zmienić cache, "
                "a opóźnienia różnych przypadków mogą się nakładać. W tej przygotowanej serii jeden "
                "z pierwszych wyników jest mylący. Dopiero powtórzenia pokazują bardziej stabilną "
                "różnicę. To nadal umowne liczby, nie pomiar sprzętu. Nie ustalamy tutaj "
                "uniwersalnego progu ani liczby prób gwarantującej sukces.\n\n"
                + "[Powrót] Zachowajmy zasadę kanału, ale nie przypisujmy pojedynczej obserwacji pewności."
            )
        if name == "vulnerable-device":
            wording = (
                "Nie można tego ustalić na podstawie naszej animacji ani samej nazwy producenta. "
                "Znaczenie mają dokładny model procesora, wariant problemu, system, firmware "
                "i aktywne zabezpieczenia. Raport systemu może pomóc sprawdzić wybrane znane "
                "klasy problemów, ale nie jest uniwersalnym dowodem braku wszystkich kanałów. "
                "Nie wyłączamy tutaj ochron ani nie uruchamiamy exploita. Praktyczne działanie "
                "to używanie wspieranego systemu i aktualizacji właściwych dla urządzenia. "
                "Jeżeli chcemy ocenić konkretny komputer, zróbmy to osobno, na podstawie "
                "jego rzeczywistej konfiguracji i dokumentacji producenta."
            )
        beats[key] = replace(
            base,
            id=key,
            title=title,
            subtitle=subtitle,
            requires=frozenset(),
            planned_seconds=45,
            detours=("cache-location",),
            script=replace(
                base.script,
                wording=wording,
                next_sentence="Wróćmy do zachowanego miejsca albo wybierzmy odpowiednią wersję tej samej kontynuacji.",
            ),
            diagram={**base.diagram, "noise": name == "timing-noise"},
        )
        detours[name] = key

    bridge_groups = {
        "foundations": (
            {"isolation", "addresses", "cache", "timing", "lines"},
            "Adres wybiera bajt. Cache przechowuje linie.",
            "Zanim zmienimy sposób wyjaśnienia, ustalmy potrzebne założenia. Granica funkcji nie jest "
            "tym samym co uprawnienia pamięci. Adres wybiera miejsce, a odczyt zwraca jego wartość. "
            "Cache przechowuje kopie grup bajtów, zwanych liniami. Dostęp do wybranego bajtu może "
            "sprowadzić całą linię. Kolejny odczyt może być szybszy; czas pozwala próbować wnioskować "
            "o wcześniejszym dostępie. To jeszcze nie jest dowód zrozumienia ani rzeczywisty pomiar.",
            ("ADRES I WARTOŚĆ", "Adres 4 → wartość 7", "CACHE I CZAS", "Kopie linii → możliwa różnica czasu"),
        ),
        "transient": (
            {
                "bounds",
                "prediction",
                "encoding",
                "transient",
                "timing",
                "lines",
                "training",
                "isolation",
                "addresses",
            },
            "Przypomnijmy drogę od danych do śladu.",
            "Warunek może jeszcze czekać na dane, kiedy procesor przewiduje kierunek. Oficjalny wynik "
            "błędnej drogi zostanie odrzucony. Nie musi to usunąć zmian cache. Wartość może wybrać "
            "adres w probe, dostęp może sprowadzić linię, a czas późniejszego odczytu pozwala "
            "próbować rozpoznać wybór. W przykładzie Spectre v1 granicą jest zakres funkcji; "
            "ofiara ma dostęp do danych poza tym zakresem. Wcześniejsze poprawne wejścia "
            "mogą wpłynąć na przewidywanie. Rozdzielmy te przyczyny, zanim przejdziemy dalej.",
            ("PRACA PRZEJŚCIOWA", "Przewidź → wykonaj → odrzuć", "KANAŁ", "Wartość → adres → cache → czas"),
        ),
        "distinction": (
            {
                "spectre",
                "meltdown",
                "distinction",
                "permissions",
                "addresses",
                "isolation",
                "transient",
                "encoding",
            },
            "Dwa mechanizmy, zanim pójdziemy dalej.",
            "W Spectre v1 ofiara przejściowo wykonuje niewłaściwą ścieżkę za warunkiem zakresu. "
            "Ma dostęp do danych, ale nie powinna ich ujawnić tą funkcją. W oryginalnym Meltdown "
            "odczyt narusza uprawnienia; na podatnym sprzęcie dane mogą zasilić zależną pracę "
            "przed architektonicznym skutkiem błędu. W obu konstrukcjach wartość może wybrać "
            "adres w probe, a pozostawiony ślad może zostać rozpoznany przez czas. "
            "Odrzucenie wyniku nie musi wymazać śladu. Podobny kanał nie oznacza tej samej przyczyny.",
            (
                "SPECTRE v1",
                "Niewłaściwa ścieżka ofiary",
                "ORYGINALNY MELTDOWN",
                "Odczyt naruszający uprawnienia",
            ),
        ),
    }
    for group, (covers, title, wording, cards) in bridge_groups.items():
        key = "bridge." + group
        beats[key] = Beat(
            key,
            "bridge",
            title,
            "Jawne uzupełnienie przed nową autorską kontynuacją.",
            "story:bridge",
            Script(
                title,
                title,
                wording,
                "Teraz wejdźmy w odpowiedni punkt wybranej trasy.",
                "Przypomnienie nie oznacza automatycznej oceny zrozumienia.",
            ),
            holds=(0.0, 2.0, 4.0),
            covers=frozenset(covers),
            detours=(),
            planned_seconds=60,
            diagram={"cards": cards},
        )
    for chapter in CHAPTERS:
        phase = chapter.id
        checkpoints[phase] = {}
        for canonical in routes:
            beat = beats[f"{canonical}.{phase}"]
            group = (
                "foundations"
                if phase
                in {"opening", "isolation", "bytes", "cache", "timing", "channel", "speculation", "bounds"}
                else "distinction"
                if phase in {"meltdown", "compare", "defenses", "recap"}
                else "transient"
            )
            checkpoints[phase][canonical] = Landing(canonical, beat.id, beat.requires, "bridge." + group)
    presentation = Presentation(
        "spectre-full",
        beats,
        routes,
        detours,
        checkpoints["opening"],
        initial,
        reduce,
        model_version="2",
        checkpoint_landings=checkpoints,
    )
    presentation.validate()
    return presentation
