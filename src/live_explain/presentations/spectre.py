"""Educational specimen, not a processor emulator or real timing measurement.

Technical basis: https://spectreattack.com/spectre.pdf (conditional branch example)
and https://meltdownattack.com/meltdown.pdf. No exploit executes on the host.
"""

from ..authoring import Beat, Event, Landing, Presentation, Script


def initial(beat):
    return dict(
        memory=[(i * 13 + 7) % 256 for i in range(32)],
        index=12,
        selected=None,
        issued=False,
        cached=False,
        result=None,
        predicted=False,
        discarded=False,
        revealed=False,
        probe=None,
        elapsed_units=None,
        events=[],
    )


def reduce(model, event):
    model["events"].append(event.kind)
    if event.kind == "issue":
        model["issued"] = True
    elif event.kind == "read":
        model["selected"] = model["index"]
        model["result"] = model["memory"][model["index"]]
        model["cached"] = True
        model["elapsed_units"] = 9
    elif event.kind == "repeat":
        model["elapsed_units"] = 2
    elif event.kind == "predict":
        model["predicted"] = True
    elif event.kind == "encode":
        model["probe"] = model["memory"][model["index"]]
        model["cached"] = True
    elif event.kind == "discard":
        model["discarded"] = True
        model["result"] = None
    elif event.kind == "reveal":
        model["revealed"] = True


def audience_model(model, secret=False):
    """One disclosure boundary for ALL audience widgets, including token labels."""
    from copy import deepcopy

    result = deepcopy(model)
    if secret and not result["revealed"]:
        result["memory"][result["index"]] = None
        result["result"] = None
        result["probe"] = None
    return result


def script(
    objective,
    cue,
    wording,
    next_sentence="Przejdźmy do następnego kroku.",
    boundary="Model poglądowy. Czasy są umowne, nie zmierzone na tym komputerze.",
):
    return Script(
        objective,
        cue,
        wording,
        next_sentence,
        boundary,
        recap="Wynik programu i ślad w pamięci podręcznej to różne rzeczy.",
    )


def build():
    timing_events = (Event(0.1, "issue"), Event(4, "read"), Event(6, "repeat"))
    timing_code = ("index = 12;", "value = memory[index];", "again = memory[index];")
    branch_code = (
        "// x pochodzi z zewnątrz",
        "if (x < length) {",
        "    value = data[x];",
        "    probe[value * stride];",
        "}",
    )
    beats = {}

    def add(beat):
        beats[beat.id] = beat

    add(
        Beat(
            "simple.timing",
            "cache-observable",
            "Ten sam adres. Inny czas.",
            "Najpierw obserwacja: drugi odczyt może zakończyć się szybciej.",
            "simple",
            script(
                "Powiązać adres, wartość i czas odczytu.",
                "Adres wybiera miejsce. Cache zmienia czas.",
                "Każde pokazane pole to jeden bajt. Adres wskazuje pole, a nie jego zawartość. "
                "Odczytujemy to samo miejsce dwa razy. Za drugim razem jego kopia jest już w cache.",
            ),
            events=timing_events,
            covers=frozenset({"addresses", "timing"}),
            code=timing_code,
            spans={"index": (1, "index")},
        )
    )
    add(
        Beat(
            "normal.timing",
            "cache-observable",
            "Odczyt zostawia ślad.",
            "Kod → adres → pamięć → obserwacja czasu",
            "timing",
            script(
                "Pokazać, dlaczego czas jest obserwacją stanu cache.",
                "Ten sam odczyt • inny stan cache • inny czas",
                "Wyrażenie index wskazuje adres. Wartość pod tym adresem nie jest adresem. "
                "Pierwszy odczyt pozostawia kopię danych w cache. Drugi korzysta z tej kopii. "
                "Różnica czasu pozwala wnioskować o wcześniejszym dostępie.",
                "A co, jeśli ten ślad zostawi praca, której wynik potem odrzucimy?",
            ),
            events=timing_events,
            covers=frozenset({"addresses", "timing"}),
            code=timing_code,
            spans={"index": (1, "index")},
        )
    )
    for canonical in ("simple", "normal"):
        add(
            Beat(
                f"{canonical}.branch",
                "transient-work",
                "Odrzucony wynik. Pozostały ślad.",
                "Przewidywanie ścieżki wykonania nie jest przewidywaniem sekretu.",
                "branch",
                script(
                    "Oddzielić wynik architektoniczny od efektu w cache.",
                    "Przewidź → użyj wartości → odrzuć wynik → zobacz ślad",
                    "Warunek jeszcze czeka na wynik. Procesor przewiduje wejście do gałęzi. "
                    "Dane wpływają na wybór miejsca w tablicy probe. Kiedy warunek okazuje się fałszywy, "
                    "wynik tej pracy nie zostaje zatwierdzony, ale efekt w cache może pozostać. "
                    "W tym przykładzie to ofiara ma dostęp do danych; nie jest to obejście uprawnień strony.",
                ),
                holds=(0.0, 2.0, 4.0, 6.0, 8.0),
                events=(
                    Event(0.1, "predict"),
                    Event(2, "issue"),
                    Event(4, "encode"),
                    Event(6, "discard"),
                    Event(8, "reveal"),
                ),
                code=branch_code,
                spans={"index": (2, "x")},
                covers=frozenset({"transient"}),
            )
        )
    add(
        Beat(
            "deep.lines",
            "cache-observable",
            "Adres wybiera bajt. Cache przechowuje linię.",
            "Rozdzielmy jednostkę danych, jednostkę transferu i obserwację.",
            "lines",
            script(
                "Ustalić założenia dokładniejszego przykładu.",
                "Bajt ≠ linia. To schemat, nie plan konkretnego CPU.",
                "W naszej ilustracji grupujemy bajty w krótkie linie. Rzeczywista długość linii zależy "
                "od układu. Zanim przejdziemy do probe, potrzebujemy rozróżnienia adresu i wartości "
                "oraz informacji, że czas odczytu może ujawnić stan cache.",
            ),
            events=timing_events,
            covers=frozenset({"addresses", "timing", "lines"}),
            code=timing_code,
            spans={"index": (1, "index")},
        )
    )
    add(
        Beat(
            "deep.probe",
            "secret-to-trace",
            "Wartość wybiera obserwowalne miejsce.",
            "Kodowanie sekretu w śladzie • oddzielne od późniejszego pomiaru",
            "probe",
            script(
                "Wyjaśnić zależność sekret → adres probe → czas.",
                "Wartość wybiera adres. Pomiar rozpoznaje ślad.",
                "Odczyt data[x] dostarcza wartość. Ta wartość wybiera odległe miejsce w probe. "
                "Po odrzuceniu błędnej ścieżki mierzymy dostęp do miejsc probe. "
                "Stride jest parametrem konstrukcji przykładu, a nie długością linii cache. "
                "Pokazujemy jedną ideę Spectre v1, bez twierdzenia o każdym wariancie.",
            ),
            holds=(0.0, 2.0, 4.0, 6.0, 8.0),
            events=(
                Event(0.1, "predict"),
                Event(2, "issue"),
                Event(4, "encode"),
                Event(6, "discard"),
                Event(8, "reveal"),
            ),
            requires=frozenset({"addresses", "timing", "lines"}),
            code=branch_code,
            spans={"index": (2, "x")},
            covers=frozenset({"transient"}),
        )
    )
    add(
        Beat(
            "shared.location",
            "cache-location",
            "Gdzie znajduje się cache?",
            "Pamięć podręczna jest częścią układu procesora. RAM to osobny poziom.",
            "location",
            script(
                "Umiejscowić cache bez rozbijania głównej historii.",
                "Procesor → rdzeń → cache. RAM obok.",
                "To schemat poglądowy organizacji. Część pamięci podręcznej jest blisko rdzenia, "
                "inne poziomy mogą być współdzielone. Nie rysujemy tu konkretnego procesora. "
                "Samo położenie nie tłumaczy jeszcze pomiaru czasu.",
                "Wróćmy do przerwanego odczytu albo dopowiedzmy brakujące podstawy.",
            ),
            detours=("cache-lines",),
            covers=frozenset({"location"}),
        )
    )
    add(
        Beat(
            "shared.lines",
            "cache-lines",
            "Cache przenosi grupy bajtów.",
            "Jedna linia obejmuje wiele kolejnych adresów.",
            "lines",
            script(
                "Odpowiedzieć na pytanie o linie cache.",
                "Wiele bajtów. Jedna linia.",
                "Wybranie pojedynczego bajtu może sprowadzić do cache całą linię. "
                "Krótka grupa pól na ekranie służy czytelności, nie podaje rzeczywistego rozmiaru linii.",
            ),
            covers=frozenset({"lines"}),
            detours=("cache-location",),
            code=timing_code,
            spans={"index": (1, "index")},
        )
    )
    add(
        Beat(
            "shared.bridge",
            "cache-observable",
            "Dwie rzeczy, zanim pójdziemy dalej.",
            "Czas ujawnia stan cache. Pojedynczy bajt należy do linii.",
            "bridge",
            script(
                "Uzupełnić jawnie założenia nowej kontynuacji.",
                "Dokończ obserwację czasu. Wyjaśnij linię.",
                "Przerwany przykład nie musiał jeszcze pokazać drugiego odczytu. "
                "Tutaj kończymy tę obserwację i dodajemy pojęcie linii cache. "
                "Następny przykład zacznie od własnego, określonego stanu.",
            ),
            events=timing_events,
            covers=frozenset({"addresses", "timing", "lines"}),
            code=timing_code,
            spans={"index": (1, "index")},
        )
    )
    add(
        Beat(
            "shared.recap",
            "attack-distinction",
            "Podobny ślad. Inny mechanizm.",
            "Spectre v1 i oryginalny Meltdown nie są tym samym atakiem.",
            "recap",
            script(
                "Zamknąć fragment bez zacierania różnic.",
                "Bounds check ≠ uprawnienia. Model ≠ exploit.",
                "Spectre v1 w naszym przykładzie wykorzystuje błędnie przewidzianą gałąź sprawdzającą "
                "zakres. Oryginalny Meltdown na podatnych układach wykorzystuje przejściowe użycie "
                "danych przy dostępie naruszającym uprawnienia, zanim błąd stanie się widoczny "
                "architektonicznie. Ten prototyp nie uruchamia żadnego ataku.",
                "Co chcielibyście odtworzyć lub zobaczyć dokładniej?",
            ),
            holds=(0.0, 2.0),
            detours=("cache-location",),
        )
    )
    presentation = Presentation(
        "spectre-slice",
        beats,
        {
            "simple": ("simple.timing", "simple.branch", "shared.recap"),
            "normal": ("normal.timing", "normal.branch", "shared.recap"),
            "deep": ("deep.lines", "deep.probe", "shared.recap"),
        },
        {"cache-location": "shared.location", "cache-lines": "shared.lines"},
        {
            "simple": Landing("simple", "simple.timing"),
            "normal": Landing("normal", "normal.timing"),
            "deep": Landing(
                "deep", "deep.probe", frozenset({"addresses", "timing", "lines"}), "shared.bridge"
            ),
        },
        initial,
        reduce,
    )
    presentation.validate()
    return presentation
