"""Art-directed specimen composition. CPU-specific views live with the presentation."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsScene
from ..components import (
    Card,
    CodePane,
    HexPane,
    Connector,
    DataToken,
    text,
    PAPER,
    INK,
    MUTED,
    BLUE,
    TEAL,
    AMBER,
)
from ..geometry import Box, Point, Route, transfer_layout, smooth
from .spectre import audience_model


class SpectreScene(QGraphicsScene):
    def __init__(self, session):
        super().__init__(0, 0, 1600, 900)
        self.session = session
        self.debug = False
        self.transition = None
        self.previous_frame = None
        self.blank = False
        self.code = CodePane()
        self.memory = HexPane()
        self.register = Card("register", "REJESTR", BLUE)
        self.cache = Card("cache", "PAMIĘĆ PODRĘCZNA", TEAL)
        self.detail = Card("detail", "OBSERWACJA", AMBER)
        self.cpu = Card("cpu", "PROCESOR", BLUE)
        self.ram = Card("ram", "RAM", TEAL)
        self.core = Card("core", "RDZEŃ", BLUE)
        self.local_cache = Card("local-cache", "L1 / L2", TEAL)
        self.shared_cache = Card("shared-cache", "DALSZY CACHE", TEAL)
        self.ram_link = Connector("cpu-ram")
        self.link1 = Connector("expression-register")
        self.link2 = Connector("register-byte")
        self.decision = Card("decision", "WARUNEK", AMBER)
        self.path_yes = Connector("prediction-path")
        self.path_no = Connector("rejection-path")
        self.token = DataToken("read-17")
        self.value_token = DataToken("secret-value")
        self.value_link = Connector("value-probe")
        self.items_by_id = {
            x.identity: x
            for x in (
                self.code,
                self.memory,
                self.register,
                self.cache,
                self.detail,
                self.cpu,
                self.ram,
                self.core,
                self.local_cache,
                self.shared_cache,
                self.ram_link,
                self.decision,
                self.link1,
                self.link2,
                self.path_yes,
                self.path_no,
                self.token,
                self.value_token,
                self.value_link,
            )
        }
        for item in self.items_by_id.values():
            self.addItem(item)
        for child in (self.core, self.local_cache, self.shared_cache):
            child.setParentItem(self.cpu)
        from .talk_scene import StoryView

        self.story = StoryView(self)
        self.refresh()

    def refresh(self):
        beat, p = self.session.beat, self.session.state.playback.position
        composition = beat.composition
        branch = composition in ("branch", "probe")
        model = audience_model(self.session.model, secret=branch or beat.diagram.get("secret", False))
        if self.session.presentation.id == "spectre-full" and not model["revealed"]:
            model["memory"][12] = None
        for item in self.items_by_id.values():
            item.setVisible(not self.blank)
        if self.blank:
            self.update()
            return
        self.story.hide()
        if composition.startswith("story:"):
            for item in self.items_by_id.values():
                item.hide()
            self.story.refresh(beat, p, model)
            self.update()
            return
        location = composition == "location"
        recap = composition == "recap"
        self.cpu.setVisible(location or recap)
        self.ram.setVisible(location or recap)
        for item in (self.core, self.local_cache, self.shared_cache, self.ram_link):
            item.setVisible(location)
        for item in (self.code, self.memory, self.register, self.link1, self.link2):
            item.setVisible(not location and not recap)
        for item in (self.decision, self.path_yes, self.path_no):
            item.setVisible(branch)
        self.token.setVisible(not location and not recap and 0 < p < 4)
        self.value_token.setVisible(branch and 4 < p < 6)
        self.value_link.setVisible(branch and p >= 4)
        # Reveals use the sequence clock, so seeking and exact returns reproduce them.
        for connector, start in (
            (self.link1, 0),
            (self.link2, 0.25),
            (self.ram_link, 0),
            (self.path_yes, 0),
            (self.path_no, 0.25),
            (self.value_link, 4),
        ):
            connector.setOpacity(smooth((p - start) / 0.65))
        self.token.setOpacity(smooth(p / 0.45))
        self.value_token.setOpacity(smooth((p - 4) / 0.45))
        code, register, memory = transfer_layout(p if p < 2 else 2)
        if branch:
            code = Box(code.x, code.y, code.w, 294)
        if composition == "simple":
            code = Box(code.x, code.y, code.w, 230)
        self.code.place(code)
        self.code.source(beat.code, beat.spans)
        old_code = (self.code.active, self.code.discarded)
        self.code.active = 2 if branch else 1 if p < 4 else 2
        self.code.discarded = model["discarded"]
        if old_code != (self.code.active, self.code.discarded):
            self.code.update()
        self.register.place(register)
        self.register.body = f"x = {model['index']}" if branch else f"adres {model['index']}"
        self.memory.place(memory)
        old_memory = (self.memory.values, self.memory.selected, self.memory.show_lines)
        self.memory.values = model["memory"]
        self.memory.selected = model["selected"] if not branch else (model["index"] if p >= 4 else None)
        self.memory.show_lines = composition in ("lines", "bridge", "probe")
        if old_memory != (self.memory.values, self.memory.selected, self.memory.show_lines):
            self.memory.update()
        if beat.spans:
            source = self.code.span_port("index")
            dest = register.port("left")
            # First leg leaves the expression downward, then uses a reserved lower corridor.
            route = Route(
                "expression-register",
                (
                    source,
                    Point(code.x + code.w - 12, source.y),
                    Point(code.x + code.w - 12, code.y + code.h + 30),
                    Point(dest.x - 40, code.y + code.h + 30),
                    Point(dest.x - 40, dest.y),
                    dest,
                ),
            )
            self.link1.set_route(route)
            start = register.port("right")
            end = self.memory.byte_port(model["index"])
            route2 = Route(
                "register-byte",
                (start, Point(1060, start.y), Point(1060, end.y - 10), Point(end.x, end.y - 10), end),
            )
            self.link2.set_route(route2)
            active = Route("whole-transfer", route.points + route2.points)
            point = active.at(smooth(p / 4))
            self.token.setPos(point.x, point.y)
            self.token.label = str(model["index"])
        self.cache.title = "ŚLAD W CACHE" if branch else "PAMIĘĆ PODRĘCZNA"
        self.detail.title = "WYNIK PROGRAMU" if branch else "OBSERWACJA"
        self.cache.place(Box(64, 650, 700, 160))
        self.detail.place(Box(800, 650, 736, 160))
        if location:
            self.cpu.place(Box(180, 275, 760 + 80 * smooth(p / 6), 310))
            self.cpu.body = ""
            for i, child in enumerate((self.core, self.local_cache, self.shared_cache)):
                child.place(Box(24 + i * 248, 88, 230, 174))
            self.core.body = "Wykonuje\ninstrukcje"
            self.local_cache.body = "Kopie\ndanych"
            self.shared_cache.body = "Możliwy\nwspólny poziom"
            start = self.cpu.box.port("right")
            end = Point(1110, 432.5)
            self.ram_link.set_route(Route("cpu-ram", (start, Point(1050, start.y), Point(1050, end.y), end)))
            self.ram.place(Box(1110, 325, 320, 215))
            self.ram.body = "Pamięć główna\nPoza rdzeniem"
            self.cache.body = "Cache: kopie danych używane przez procesor."
            self.detail.body = "Schemat poglądowy. Organizacja zależy od układu."
        elif recap:
            self.cpu.place(Box(64, 280, 700, 305))
            self.cpu.title = "SPECTRE v1"
            self.cpu.body = "Błędnie przewidziana gałąź\n\nSprawdzenie zakresu w kodzie ofiary"
            self.ram.place(Box(800, 280, 736, 305))
            self.ram.title = "ORYGINALNY MELTDOWN"
            self.ram.body = "Dostęp naruszający uprawnienia\n\nPrzejściowe użycie danych na podatnym układzie"
            self.cache.body = "Wspólny motyw: obserwowalny efekt przejściowej pracy."
            self.detail.body = "Ten model nie sprawdza podatności komputera."
        elif branch:
            self.cache.body = (
                (
                    f"probe[{model['probe']} × stride] — ślad pozostał"
                    if model["revealed"]
                    else "probe[wartość × stride] — ślad pozostał"
                )
                if model["discarded"]
                else "Wybrany dostęp zmienia stan cache."
                if model["cached"]
                else "Przewidziana ścieżka czeka na rozstrzygnięcie."
            )
            self.detail.body = (
                "Wynik odrzucony ≠ wszystkie efekty usunięte"
                if model["discarded"]
                else "Wartość jest ukryta; pokażemy sposób jej kodowania."
            )
            origin = self.memory.byte_box(model["index"]).port("bottom")
            value_route = Route(
                "value-probe",
                (
                    origin,
                    Point(origin.x, origin.y + 6),
                    Point(1554, origin.y + 6),
                    Point(1554, 822),
                    Point(780, 822),
                    Point(780, 730),
                    Point(764, 730),
                ),
            )
            self.value_link.set_route(value_route)
            self.value_link.color = TEAL
            self.value_token.label = "··" if model["probe"] is None else str(model["probe"])
            point = value_route.at(smooth((p - 4) / 2))
            self.value_token.setPos(point.x, point.y)
            self.decision.place(Box(820, 465, 210, 108))
            self.decision.body = "12 < 8 ?"
            self.path_yes.set_route(
                Route(
                    "predicted",
                    (Point(820, 519), Point(780, 519), Point(780, 620), Point(624, 620), Point(624, 650)),
                )
            )
            self.path_no.set_route(
                Route(
                    "rejected",
                    (
                        Point(1030, 519),
                        Point(1060, 519),
                        Point(1060, 620),
                        Point(1130, 620),
                        Point(1130, 650),
                    ),
                )
            )
            self.path_yes.color = MUTED if model["discarded"] else AMBER
            self.path_yes.dashed = True
            self.path_no.color = BLUE if model["discarded"] else "#c9d4d6"
        else:
            self.cache.body = (
                "Kopia danych jest w cache." if model["cached"] else "Pierwszy odczyt: potrzebujemy danych."
            )
            self.detail.body = (
                "Pierwszy: 9 j.     Drugi: 2 j."
                if p >= 6
                else "Pierwszy odczyt: 9 jednostek"
                if p >= 4
                else "Porównujemy ten sam adres, nie dwa różne programy."
            )
        if beat.diagram.get("phase") == "bytes":
            self.cache.body = (
                f"Odczytana wartość: {model['result']}"
                if p >= 4
                else "Adres wskazuje miejsce; wartość to jego zawartość."
            )
            self.detail.body = "Adres 4 ≠ wartość 7. Kod korzysta z wartości spod wybranego adresu."
        if location:
            self.cpu.title = "PROCESOR"
            self.ram.title = "RAM"

        self.update()

    def drawBackground(self, p, rect):
        p.fillRect(rect, QColor(PAPER if not self.blank else "#172c38"))
        if self.blank:
            return
        text(p, (64, 40, 800, 28), "JAK DZIAŁA KOMPUTER  /  ŚLADY WYKONANIA", 17, TEAL, True)
        text(p, (64, 98, 1472, 76), self.session.beat.title, 48, INK, True)
        text(p, (64, 183, 1472, 44), self.session.beat.subtitle, 25, MUTED)
        p.setPen(QPen(QColor("#d7dfda"), 1.5))
        p.drawLine(QPointF(64, 240), QPointF(1536, 240))
        text(
            p,
            (64, 839, 1472, 28),
            "INFORMACJA POŚREDNIA  •  Historyczna relacja: TIME, 13.08.1990"
            if self.session.beat.diagram.get("phase") == "opening"
            else "MODEL POGLĄDOWY  •  Czasy umowne, nie pomiar sprzętu",
            17,
            MUTED,
        )

    def drawForeground(self, p, rect):
        if self.blank:
            return
        if self.session.beat.composition.startswith("story:"):
            self.story.foreground(p)
        if self.session.beat.composition in ("branch", "probe"):
            text(p, (405, 590, 330, 26), "TAK · przewidywanie", 18, AMBER, True)
            text(p, (1160, 604, 370, 26), "NIE · rozstrzygnięcie", 18, BLUE, True)
        if self.transition and self.transition.active and self.previous_frame is not None:
            p.save()
            p.setOpacity(self.transition.opacity)
            p.drawImage(self.sceneRect(), self.previous_frame)
            p.restore()
        if not self.debug:
            return
        p.setPen(QPen(QColor("#c03c74"), 1, Qt.PenStyle.DashLine))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(QRectF(64, 40, 1472, 820))
        for key, item in self.items_by_id.items():
            if item.isVisible():
                bounds = item.sceneBoundingRect()
                p.drawRect(bounds)
                text(p, (bounds.x(), bounds.y() - 20, 280, 20), key, 12, "#c03c74")
        for connector in (self.link1, self.link2):
            if connector.isVisible() and connector.route:
                for point in connector.route.points:
                    p.drawEllipse(QPointF(point.x, point.y), 5, 5)
