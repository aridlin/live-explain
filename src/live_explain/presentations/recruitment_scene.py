"""Audience-only recruitment scenes using original local project screenshots."""

from pathlib import Path

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QGraphicsScene

from ..components import PAPER, INK, MUTED, TEAL, text

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "recruitment"


class RecruitmentScene(QGraphicsScene):
    def __init__(self, session):
        super().__init__(0, 0, 1600, 900)
        self.session = session
        self.blank = False
        self.debug = False
        self.transition = None
        self.previous_frame = None
        self.items_by_id = {}
        self.text_regions = []
        self.images = {p.stem: QImage(str(p)) for p in ASSETS.glob("*.png")}
        required = {
            "ft-example-gui",
            "ft-example-tui",
            "ft-example-web",
            "kalwer-search",
            "kalwer-calculator",
            "voice-builder",
            "voice-editor",
        }
        if not required <= self.images.keys() or any(image.isNull() for image in self.images.values()):
            raise ValueError("Missing or unreadable recruitment screenshots")

    def refresh(self):
        self.update()

    def label(self, painter, rect, value, size=28, color=INK, bold=False):
        # QStaticText normalizes embedded newlines; lay out authored lines explicitly.
        lines = value.split("\n")
        if len(lines) > 1:
            line_height = rect[3] / len(lines)
            for index, line in enumerate(lines):
                self.label(
                    painter,
                    (rect[0], rect[1] + index * line_height, rect[2], line_height),
                    line,
                    size,
                    color,
                    bold,
                )
            return
        self.text_regions.append((rect, value, size, bold))
        text(painter, rect, value, size, color, bold, wrap=True)

    def picture(self, painter, name, target, source=None):
        image = self.images[name]
        source = source or QRectF(image.rect())
        target = QRectF(*target)
        scale = min(target.width() / source.width(), target.height() / source.height())
        fitted = QRectF(0, 0, source.width() * scale, source.height() * scale)
        fitted.moveCenter(target.center())
        painter.drawImage(fitted, image, source)

    def heading(self, painter, context, message):
        # Context is subordinate; the message is the first thing the audience reads.
        self.label(painter, (64, 52, 1400, 38), context, 24, TEAL)
        self.label(painter, (64, 112, 1472, 134), message, 48, INK, True)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor("#172c38" if self.blank else PAPER))
        self.text_regions = []
        if self.blank:
            return
        beat = self.session.beat
        chapter = beat.diagram["chapter"]
        reveal = self.session.model["revealed"]

        if chapter == "about":
            self.label(painter, (64, 100, 1472, 90), "Igor Zwierzchowski", 48, INK, True)
            self.label(painter, (64, 202, 1472, 48), "17 lat · trzecia klasa liceum", 25, MUTED)
            self.label(painter, (64, 340, 1360, 144), "Programowanie\nCyberbezpieczeństwo", 44, INK, True)
            self.label(
                painter, (64, 514, 1472, 50), "Projekty: C++, Python, interfejsy i synteza mowy", 30, MUTED
            )
            if reveal:
                projects = (
                    (64, "FT", "Interfejsy aplikacji"),
                    (564, "Kalwer", "Launcher aplikacji"),
                    (1064, "vctts / Phonomenal", "Synteza mowy"),
                )
                for x, title, description in projects:
                    self.label(painter, (x, 660, 472, 60), title, 32, TEAL, True)
                    self.label(painter, (x, 724, 472, 64), description, 26, MUTED)
        elif chapter == "ft":
            self.heading(painter, "FT · biblioteka C++", "Interfejsy GUI, TUI i WWW")
            if reveal:
                self.picture(painter, "ft-example-tui", (64, 320, 704, 390), QRectF(0, 0, 1000, 390))
                self.picture(painter, "ft-example-web", (832, 320, 704, 390), QRectF(60, 15, 1130, 405))
                self.label(painter, (64, 726, 704, 60), "Interfejs terminalowy (TUI)", 28)
                self.label(painter, (832, 726, 704, 60), "Interfejs przeglądarkowy (WWW)", 28)
            else:
                self.picture(painter, "ft-example-gui", (150, 290, 1300, 470), QRectF(0, 0, 1000, 390))
                self.label(painter, (150, 778, 1300, 44), "Natywny interfejs graficzny (GUI)", 28, MUTED)
        elif chapter == "kalwer":
            self.heading(
                painter,
                "Kalwer",
                "Kalkulator z obsługą ułamków" if reveal else "Wyszukiwanie i uruchamianie aplikacji",
            )
            name = "kalwer-calculator" if reveal else "kalwer-search"
            image = self.images[name]
            # Exclude unrelated desktop wallpaper and chrome; keep the useful interface.
            crop = QRectF(
                image.width() * 0.255,
                image.height() * 0.108,
                image.width() * 0.49,
                image.height() * (0.41 if reveal else 0.50),
            )
            self.picture(painter, name, (170, 280, 1260, 490), crop)
            self.label(
                painter,
                (170, 786, 1260, 46),
                "Wynik dziesiętny, ułamek i procent" if reveal else "Frontend GTK3 dla backendu Elephant",
                28,
                MUTED,
            )
        elif chapter == "voice":
            if not reveal:
                self.heading(painter, "vctts / Phonomenal", "Synteza mowy i wyjścia audio")
                self.label(painter, (64, 345, 680, 70), "vctts", 38, TEAL, True)
                self.label(
                    painter,
                    (64, 435, 680, 140),
                    "Zamiana tekstu na mowę\nWybór głosu i wyjść audio",
                    32,
                )
                self.label(painter, (856, 345, 680, 70), "Phonomenal", 38, TEAL, True)
                self.label(painter, (856, 435, 680, 140), "Generowanie mowy\nz fragmentów nagrań", 32)
                self.label(
                    painter,
                    (64, 690, 1472, 100),
                    "vctts obsługuje paczki głosu Phonomenal (.vcpack).",
                    30,
                    MUTED,
                )
            else:
                self.heading(painter, "Phonomenal", "Przygotowanie paczki głosu")
                self.picture(painter, "voice-builder", (64, 300, 1080, 430), QRectF(182, 410, 1076, 450))
                self.label(
                    painter, (1192, 340, 344, 190), "Nagrania\nGranice słów i głosek\nPaczka .vcpack", 30
                )
                self.label(
                    painter,
                    (64, 765, 1472, 66),
                    "Profil językowy: angielski (ARPABET)",
                    28,
                    MUTED,
                )
        elif chapter == "learning":
            if not reveal:
                self.heading(painter, "Mój sposób nauki", "Doświadczenie w nauce indywidualnej")
                self.label(painter, (64, 340, 430, 74), "Od 1 klasy SP", 30, TEAL)
                self.label(painter, (550, 340, 986, 74), "Nauka indywidualna", 36, INK, True)
                self.label(painter, (64, 480, 430, 74), "Od 4 klasy SP", 30, TEAL)
                self.label(painter, (550, 480, 986, 74), "Również online", 36, INK, True)
                self.label(
                    painter,
                    (64, 690, 1472, 100),
                    "Materiały: dokumentacja techniczna i zasoby edukacyjne",
                    30,
                    MUTED,
                )
            else:
                self.heading(painter, "Dlaczego Chmura", "Organizacja nauki w Chmurze")
                self.label(painter, (64, 340, 680, 70), "Obowiązki szkolne", 34, TEAL, True)
                self.label(
                    painter, (64, 436, 680, 124), "Podstawa programowa\ni przygotowanie do egzaminów", 32
                )
                self.label(painter, (856, 340, 680, 70), "Projekty informatyczne", 34, TEAL, True)
                self.label(painter, (856, 436, 680, 124), "Programowanie\ni cyberbezpieczeństwo", 32)
                self.label(
                    painter,
                    (64, 690, 1472, 110),
                    "Zaległości: zmiana harmonogramu i wsparcie rodziny",
                    30,
                    MUTED,
                )
        else:
            if not reveal:
                self.heading(painter, "Najbliższy rok", "Plany na najbliższy rok")
                self.label(
                    painter, (64, 350, 1472, 100), "Ukończenie klasy i przygotowanie do matury", 36, INK, True
                )
                self.label(painter, (64, 492, 1472, 100), "Rozwój FT, Kalwera oraz vctts i Phonomenal", 32)
                self.label(painter, (64, 692, 1472, 84), "Planowanie nauki i terminów egzaminów", 30, MUTED)
            else:
                self.heading(painter, "Dalszy kierunek", "Studia związane z cyberbezpieczeństwem")
                self.label(
                    painter,
                    (64, 360, 1472, 160),
                    "Planowane studia:\nPolitechnika Warszawska",
                    38,
                    INK,
                    True,
                )
                self.label(painter, (64, 700, 1472, 90), "Chętnie odpowiem na pytania.", 30, MUTED)

    def drawForeground(self, painter, rect):
        if self.blank:
            return
        if self.transition and self.transition.active and self.previous_frame is not None:
            painter.save()
            painter.setOpacity(self.transition.opacity)
            painter.drawImage(self.sceneRect(), self.previous_frame)
            painter.restore()
