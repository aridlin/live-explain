"""Art-directed live compositions for the full talk; no independent rendering engine."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsObject
from ..components import Card, Connector, DataToken, text, BLUE, TEAL, AMBER, MUTED, INK
from ..geometry import Box, Point, Route, smooth

RED = "#a4453c"


class ProbeChart(QGraphicsObject):
    """Four authored candidate views of the same model measurement event."""

    def __init__(self):
        super().__init__()
        self.identity = "probe-observations"
        self.values = None
        self.revealed = False
        self.noise = False
        self.progress = 0

    def boundingRect(self):
        return QRectF(0, 0, 1472, 350)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        for index in range(4):
            x = index * 372
            painter.setPen(QPen(QColor("#d7dfda"), 1.5))
            painter.setBrush(QColor("#ffffff"))
            painter.drawRoundedRect(QRectF(x, 0, 350, 330), 16, 16)
            text(painter, (x + 24, 16, 300, 36), f"wartość {index}", 28, INK, True, True)
            rows = self.values if self.noise else [self.values]
            if self.values is None:
                text(painter, (x + 24, 120, 290, 70), "jeszcze bez pomiaru", 23, MUTED, wrap=True)
            else:
                for trial, row in enumerate(rows):
                    if self.noise and self.progress < 4 and trial > 0:
                        continue
                    value = row[index]
                    width = 74 if self.noise else 130
                    bx = x + 35 + trial * 95 if self.noise else x + 110
                    height = value * 16 * smooth(self.progress / 2)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(TEAL if self.revealed and index == 2 else BLUE))
                    painter.drawRoundedRect(QRectF(bx, 250 - height, width, height), 6, 6)
                    text(painter, (bx, 265, width, 32), f"{value} j.", 25, INK, True, True)
            if self.revealed and index == 2:
                text(painter, (x + 24, 62, 300, 32), "rozpoznany wybór", 21, TEAL, True)


class StoryView:
    def __init__(self, scene):
        self.scene = scene
        self.cards = {
            key: Card("story-" + key, "", BLUE)
            for key in ("input", "gate", "result", "trace", "victim", "observer", "note", "aux")
        }
        self.links = [Connector(f"story-link-{i}") for i in range(6)]
        self.tokens = [DataToken(f"story-token-{i}") for i in range(2)]
        self.chart = ProbeChart()
        self.items = [*self.cards.values(), *self.links, *self.tokens, self.chart]
        for item in self.items:
            scene.addItem(item)
            scene.items_by_id[item.identity] = item
        self.phase = ""
        self.caption = ""
        self.hide()

    def hide(self):
        for item in self.items:
            item.hide()
        self.caption = ""

    def card(self, key, title, body, box, color=BLUE, opacity=1):
        item = self.cards[key]
        item.title, item.body = title, body
        if item.accent != color:
            item.accent = color
            item.update()
        item.place(box)
        item.setOpacity(opacity)
        item.show()
        return item

    def connect(self, index, start, end, p, reveal=0, color=BLUE, dashed=False, waypoints=()):
        route = Route(f"story-route-{index}", (start, *waypoints, end))
        item = self.links[index]
        item.set_route(route)
        item.color, item.dashed = color, dashed
        item.setOpacity(smooth((p - reveal) / 0.6))
        item.show()
        item.update()
        return route

    def travel(self, index, route, label, position, start, end):
        item = self.tokens[index]
        item.setVisible(start < position < end)
        point = route.at(smooth((position - start) / (end - start)))
        item.label = label
        item.setPos(point.x, point.y)
        item.setOpacity(smooth((position - start) / 0.35))

    def refresh(self, beat, p, model):
        self.phase = beat.composition.removeprefix("story:")
        phase = self.phase
        left, right = Box(64, 300, 700, 270), Box(836, 300, 700, 270)
        foot = Box(64, 675, 1472, 135)
        if phase == "opening":
            self.card("result", "OFICJALNY WYNIK", "Program nie oddaje sekretu.", left)
            self.card(
                "trace",
                "OSOBNA OBSERWACJA",
                "Czas może zależeć od wcześniejszej pracy.",
                right,
                TEAL,
                smooth(p / 0.65),
            )
            self.card(
                "note",
                "PYTANIE",
                "Czy odmowa wyniku oznacza brak informacji?",
                foot,
                AMBER,
                smooth((p - 2) / 0.65),
            )
        elif phase in {"isolation", "bounds"}:
            self.card(
                "victim",
                "PROGRAM / OFIARA",
                "Udostępniany fragment: 0–7\nInne dane programu: poza tym zakresem"
                if phase == "bounds"
                else "Kod użytkownika nie otrzymuje swobodnego dostępu do chronionych danych.",
                left,
            )
            self.card(
                "gate",
                "REGUŁA FUNKCJI" if phase == "bounds" else "UPRAWNIENIA SPRZĘTOWE",
                "x < 8" if phase == "bounds" else "Dozwolone mapowanie ≠ dowolny dostęp",
                right,
                AMBER,
            )
            allowed = model["allowed"]
            self.card(
                "result",
                "ŻĄDANIE" if phase == "bounds" else "ODCZYT",
                "Jeszcze bez rozstrzygnięcia"
                if allowed is None
                else (
                    "4 < 8  →  dozwolony element"
                    if phase == "bounds"
                    else "Dozwolony odczyt → wartość dla programu"
                )
                if allowed
                else "12 < 8  →  pomiń odczyt"
                if phase == "bounds"
                else "Brak uprawnień → brak dozwolonego wyniku",
                foot,
                RED if allowed is False else TEAL,
            )
            route = self.connect(0, left.port("right"), right.port("left"), p)
            self.travel(
                0,
                route,
                ("4" if p < 2 else "12") if phase == "bounds" else "odczyt",
                p,
                0 if p < 2 else 2,
                2 if p < 2 else 4,
            )
        elif phase in {"channel", "speculation", "training", "recap"}:
            boxes = [Box(64 + i * 520, 330, 432, 245) for i in range(3)]
            if phase == "channel":
                titles = ("PUBLICZNA WARTOŚĆ", "WYBÓR ADRESU", "ŚLAD W CACHE")
                bodies = (
                    str(model["public_value"]),
                    f"probe[{model['public_value']} × stride]",
                    "Wybrany obszar może być szybszy przy kolejnym odczycie.",
                )
                label = str(model["public_value"])
                self.caption = "To jawny przykład kodowania. Sekret ofiary pojawi się w osobnej sytuacji."
            elif phase == "speculation":
                titles = ("WARUNEK", "PRZEWIDYWANIE", "ROZSTRZYGNIĘCIE")
                bodies = (
                    "Czeka na dane",
                    "Wejdź do gałęzi" if model["predicted"] else "Jeszcze bez wyboru",
                    "NIE — niewłaściwa droga" if model["discarded"] else "Jeszcze niegotowe",
                )
                label = "praca"
                self.caption = "Przewidywany jest kierunek. Odczytane dane nie muszą być zgadywane."
            elif phase == "training":
                titles = ("HISTORIA WEJŚĆ", "PRZEWIDYWANY KIERUNEK", "NOWE ŻĄDANIE")
                bodies = (
                    "  ".join(str(v) for v in model["history"]) or "Poprawne indeksy: 0–7",
                    "TAK — wejście do warunku",
                    "12: poza zakresem" if p >= 6 else "Jeszcze nie wysłane",
                )
                label = str(model["history"][-1]) if model["history"] else "1"
                self.caption = (
                    "Schemat przygotowania. Nie emulujemy predyktora ani gwarantowanej liczby prób."
                )
            else:
                titles = ("DANE", "PRACA PRZEJŚCIOWA", "OBSERWACJA")
                bodies = (
                    "Wartość wpływa na wybór adresu.",
                    "Oficjalny wynik może zostać odrzucony.",
                    "Pozostały ślad może wpływać na czas.",
                )
                label = "ślad"
                self.caption = "Do którego połączenia chcecie wrócić?"
            for i, (title, body, box) in enumerate(zip(titles, bodies, boxes)):
                self.card(
                    ("input", "gate", "trace")[i],
                    title,
                    body,
                    box,
                    TEAL if i == 2 else BLUE,
                    1 if i == 0 else smooth((p - (i - 1) * 1.5) / 0.65),
                )
            for i in range(2):
                route = self.connect(i, boxes[i].port("right"), boxes[i + 1].port("left"), p, i * 1.5)
                self.travel(i, route, label, p, i * 2, i * 2 + 2)
            if phase == "speculation":
                self.card(
                    "result",
                    "WYNIK",
                    "Odrzucony; wracamy na właściwą drogę."
                    if model["discarded"]
                    else "Praca jest tymczasowa.",
                    foot,
                    RED if model["discarded"] else AMBER,
                )
            elif phase == "channel":
                self.card(
                    "note",
                    "ZAŁOŻENIE KANAŁU",
                    "Różne wartości wybierają rozdzielone miejsca, które obserwator może rozróżniać.",
                    foot,
                    TEAL,
                )
        elif phase == "rollback":
            self.card(
                "result",
                "ZATWIERDZONY WYNIK",
                "Niewłaściwy wynik odrzucony" if model["discarded"] else "Wynik jeszcze tymczasowy",
                Box(64, 285, 1472, 190),
                RED if model["discarded"] else BLUE,
            )
            self.card(
                "trace",
                "OSOBNY STAN CACHE",
                "Ślad pozostaje do obserwacji" if model["cached"] else "Jeszcze bez nowego śladu",
                Box(64, 585, 1472, 190),
                TEAL,
            )
            route = self.connect(0, Point(800, 475), Point(800, 585), p, color=TEAL)
            self.travel(0, route, "dostęp", p, 0, 2)
            self.caption = "Odrzucenie wyniku nie jest odwróceniem każdego fizycznego skutku wykonania."
        elif phase == "decode":
            self.chart.setPos(64, 330)
            self.chart.values = model["measurements"]
            self.chart.revealed = model["revealed"]
            self.chart.noise = beat.diagram.get("noise", False)
            self.chart.progress = p
            self.chart.show()
            self.chart.update()
            self.card(
                "note",
                "WNIOSKOWANIE",
                "Rozpoznany wybór: 2. W modelu ukryty bajt wynosi 2."
                if model["revealed"]
                else "Najpierw pomiary. Wartość pozostaje zasłonięta.",
                Box(64, 690, 1472, 120),
                TEAL,
            )
            self.caption = (
                "Trzy próby w jednostkach umownych: pierwszy wynik może mylić."
                if self.chart.noise
                else "Kandydaci wybierają rozdzielone obszary probe. Pokazujemy 4 z 256. Czasy umowne."
            )
        elif phase == "cache-line":
            self.card(
                "input", "LINIA CACHE", "Kopia obejmuje grupę sąsiednich bajtów.", Box(64, 300, 650, 240)
            )
            memory = self.scene.memory
            memory.place(Box(1100, 285, 436, 340))
            memory.values, memory.selected, memory.show_lines = model["memory"], 4, True
            memory.show()
            memory.update()
            route = self.connect(
                0,
                Point(714, 420),
                memory.byte_port(4),
                p,
                waypoints=(Point(1060, 420), Point(1060, memory.byte_port(4).y)),
            )
            self.travel(0, route, "adres 4", p, 0, 2)
            self.card(
                "note",
                "ROZDZIELENIE KANDYDATÓW",
                "Kandydaci probe muszą wybierać rozróżnialne obszary, a nie sąsiednie bajty tej samej linii.",
                foot,
                TEAL,
            )
            self.caption = (
                "Kolorowane grupy są schematem linii; ich rozmiar nie opisuje konkretnego procesora."
            )
        elif phase == "meltdown":
            code = self.scene.code
            code.place(Box(64, 280, 660, 285))
            code.source(beat.code, beat.spans)
            code.active = 0 if p < 2 else 1
            code.discarded = model["discarded"]
            code.show()
            code.update()
            memory = self.scene.memory
            memory.place(Box(1100, 280, 436, 320))
            memory.values, memory.selected, memory.show_lines = model["memory"], 12, False
            memory.show()
            memory.update()
            self.card("gate", "UPRAWNIENIA", "Brak dostępu", Box(780, 320, 270, 165), RED)
            self.card(
                "result", "OFICJALNY WYNIK", "Brak dozwolonego wyniku odczytu", Box(64, 665, 660, 145), RED
            )
            target = Box(780, 665, 756, 145)
            self.card(
                "trace",
                "ŚLAD ZALEŻNEGO DOSTĘPU",
                "probe[2 × stride] — wynik pomiaru"
                if model["revealed"]
                else "Ślad może pozostać po błędzie"
                if model["cached"]
                else "Praca przejściowa na podatnym układzie",
                target,
                TEAL,
            )
            start = memory.byte_box(12).port("bottom")
            end = target.port("top", 0.7)
            route = self.connect(
                0,
                start,
                end,
                p,
                reveal=2,
                color=AMBER,
                dashed=True,
                waypoints=(
                    Point(start.x, start.y + 7),
                    Point(1554, start.y + 7),
                    Point(1554, 630),
                    Point(end.x, 630),
                ),
            )
            self.travel(0, route, "··", p, 2, 4)
            self.caption = (
                "Brak ifa do błędnego przewidzenia. Pokazujemy niedozwolony przejściowy wpływ danych."
            )
        elif phase in {"compare", "bridge"}:
            cards = beat.diagram.get(
                "cards",
                (
                    "SPECTRE v1",
                    "Niewłaściwa ścieżka programu-ofiary\n\nDane dostępne ofierze",
                    "ORYGINALNY MELTDOWN",
                    "Odczyt naruszający uprawnienia\n\nPodatny układ",
                ),
            )
            self.card("victim", cards[0], cards[1], left)
            self.card("gate", cards[2], cards[3], right, AMBER)
            self.card(
                "trace",
                "WSPÓLNY MOTYW" if phase == "compare" else "POWRÓT DO KONTYNUACJI",
                "Wartość → adres → cache → czas"
                if phase == "compare"
                else "Nowa trasa zacznie od jawnego, autorskiego stanu.",
                foot,
                TEAL,
                smooth((p - 2) / 0.65),
            )
        elif phase == "defenses":
            self.card(
                "victim",
                "KOD I PLATFORMA",
                "Ogranicz użyteczny przejściowy dostęp.\nBariery / ograniczanie indeksów.",
                left,
            )
            self.card(
                "gate",
                "SYSTEM I MAPOWANIA",
                "PTI: ogranicz mapowania jądra używane przez kod użytkownika.",
                right,
                TEAL,
                smooth(p / 0.65),
            )
            self.card(
                "note",
                "SPRZĘT",
                "Poufność danych ma obowiązywać także podczas pracy przejściowej.",
                foot,
                AMBER,
                smooth((p - 2) / 0.65),
            )
        else:
            raise ValueError(f"Unknown authored composition {phase}")

    def foreground(self, painter):
        if self.caption:
            text(painter, (64, 245, 1472, 38), self.caption, 20, MUTED)
