"""Reusable Qt diagram components. Domain semantics are supplied by scene composition."""

from functools import lru_cache
from math import atan2, cos, sin, hypot
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QTextLayout,
    QTextCharFormat,
    QStaticText,
    QTextOption,
    QTransform,
)
from PySide6.QtWidgets import QGraphicsObject
from pygments import lex
from pygments.lexers import CLexer
from pygments.token import Token
from .geometry import Box, Point

INK = "#172c38"
MUTED = "#60727a"
BLUE = "#156a99"
AMBER = "#a26618"
TEAL = "#23786b"
PAPER = "#f4f3ed"
LINE = "#d5dfdd"


@lru_cache(maxsize=64)
def font(size=24, mono=False, bold=False):
    f = QFont("DejaVu Sans Mono" if mono else "DejaVu Sans")
    f.setPixelSize(size)
    f.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
    return f


@lru_cache(maxsize=2048)
def shaped_text(value, width, size, mono, bold, wrap, scale_x, scale_y):
    static = QStaticText(value)
    static.setTextFormat(Qt.TextFormat.PlainText)
    option = QTextOption()
    option.setWrapMode(QTextOption.WrapMode.WordWrap if wrap else QTextOption.WrapMode.NoWrap)
    static.setTextOption(option)
    if wrap:
        static.setTextWidth(width)
    static.prepare(QTransform().scale(scale_x, scale_y), font(size, mono, bold))
    return static


def text(p, rect, value, size=24, color=INK, bold=False, mono=False, wrap=False):
    p.setFont(font(size, mono, bold))
    p.setPen(QColor(color))
    transform = p.worldTransform()
    static = shaped_text(value, rect[2], size, mono, bold, wrap, transform.m11(), transform.m22())
    p.drawStaticText(QPointF(rect[0], rect[1] + (rect[3] - static.size().height()) / 2), static)


class Card(QGraphicsObject):
    def __init__(self, identity, title, accent=BLUE):
        super().__init__()
        self.identity, self.title, self.accent = identity, title, accent
        self.box = Box(0, 0, 100, 100)
        self.body = ""
        self.setCacheMode(QGraphicsObject.CacheMode.DeviceCoordinateCache)

    @property
    def body(self):
        return getattr(self, "_body", "")

    @body.setter
    def body(self, value):
        if getattr(self, "_body", None) != value:
            self._body = value
            self.update()

    @property
    def title(self):
        return getattr(self, "_title", "")

    @title.setter
    def title(self, value):
        if getattr(self, "_title", None) != value:
            self._title = value
            self.update()

    def place(self, box):
        if self.box == box:
            return
        if (box.w, box.h) != (self.box.w, self.box.h):
            self.prepareGeometryChange()
        self.box = box
        self.setPos(box.x, box.y)
        self.update()

    def boundingRect(self):
        return QRectF(-2, -2, self.box.w + 4, self.box.h + 4)

    def paint(self, p, option, widget=None):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(LINE), 1.5))
        p.setBrush(QColor("#ffffff"))
        p.drawRoundedRect(QRectF(0, 0, self.box.w, self.box.h), 16, 16)
        p.setPen(QPen(QColor(self.accent), 4))
        p.drawLine(QPointF(24, 30), QPointF(44, 30))
        text(p, (56, 12, self.box.w - 76, 36), self.title, 18, MUTED, True)
        if self.body:
            text(p, (24, 60, self.box.w - 48, self.box.h - 76), self.body, 26, wrap=True)


class CodePane(Card):
    def __init__(self, identity="code"):
        super().__init__(identity, "KOD / PSEUDOKOD")
        self.lines = ()
        self.layouts = []
        self.spans = {}
        self.active = 1
        self.discarded = False

    def source(self, lines, spans):
        if self.lines == lines and self.spans == spans:
            return
        self.lines, self.spans = lines, spans
        self.layouts = []
        for line in lines:
            layout = QTextLayout(line, font(22, True))
            formats = []
            offset = 0
            for token, value in lex(line, CLexer(stripnl=False, ensurenl=False)):
                item = QTextLayout.FormatRange()
                item.start = offset
                item.length = len(value.encode("utf-16-le")) // 2
                item.format = QTextCharFormat()
                color = (
                    MUTED
                    if token in Token.Comment
                    else BLUE
                    if token in Token.Keyword
                    else AMBER
                    if token in Token.Literal.Number
                    else INK
                )
                item.format.setForeground(QColor(color))
                formats.append(item)
                offset += item.length
            layout.setFormats(formats)
            layout.beginLayout()
            row = layout.createLine()
            row.setLineWidth(10000)
            layout.endLayout()
            self.layouts.append(layout)
        self.update()

    def span_port(self, name):
        line, expression = self.spans[name]
        prefix = self.lines[line][: self.lines[line].index(expression) + len(expression)]
        index = len(prefix.encode("utf-16-le")) // 2
        x = self.layouts[line].lineAt(0).cursorToX(index)[0]
        return Point(self.box.x + 62 + x, self.box.y + 73 + line * 36 + 26)

    def paint(self, p, option, widget=None):
        super().paint(p, option, widget)
        p.save()
        p.setClipRect(QRectF(18, 62, self.box.w - 36, self.box.h - 74))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#e8f1f5" if not self.discarded else "#eeeeeb"))
        p.drawRoundedRect(QRectF(20, 68 + self.active * 36, self.box.w - 40, 34), 5, 5)
        for i, layout in enumerate(self.layouts):
            text(p, (22, 70 + i * 36, 28, 30), str(i + 1), 18, MUTED, mono=True)
            layout.draw(p, QPointF(62, 73 + i * 36))
        if self.discarded:
            p.setPen(QPen(QColor(MUTED), 2))
            p.drawLine(QPointF(60, 89 + self.active * 36), QPointF(self.box.w - 24, 89 + self.active * 36))
        p.restore()


class HexPane(Card):
    def __init__(self, identity="memory", columns=8, rows=4):
        super().__init__(identity, "PAMIĘĆ / BAJTY", TEAL)
        self.columns, self.rows = columns, rows
        self.values = [0] * (columns * rows)
        self.selected = None
        self.show_lines = False

    def byte_box(self, index):
        if not 0 <= index < len(self.values) or index >= self.columns * self.rows:
            raise ValueError("Byte outside visible window")
        return Box(
            self.box.x + 76 + (index % self.columns) * 40,
            self.box.y + 82 + (index // self.columns) * 48,
            36,
            36,
        )

    def byte_port(self, index):
        return self.byte_box(index).port("top")

    def paint(self, p, option, widget=None):
        super().paint(p, option, widget)
        p.save()
        p.setClipRect(QRectF(16, 62, self.box.w - 32, self.box.h - 78))
        for row in range(self.rows):
            text(p, (18, 82 + row * 48, 56, 36), f"{row * self.columns:04X}", 16, MUTED, mono=True)
            if self.show_lines:
                p.setPen(QPen(QColor("#a4c6b8"), 2))
                p.setBrush(QColor("#f2f7f2"))
                p.drawRoundedRect(QRectF(72, 79 + row * 48, self.columns * 40 + 6, 40), 6, 6)
        for i, value in enumerate(self.values[: self.columns * self.rows]):
            box = self.byte_box(i)
            x, y = box.x - self.box.x, box.y - self.box.y
            selected = i == self.selected
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(TEAL if selected else "#f2f4f1"))
            p.drawRoundedRect(QRectF(x, y, 36, 36), 5, 5)
            text(
                p,
                (x + 4, y, 32, 36),
                "··" if value is None else f"{value:02X}",
                19,
                "#ffffff" if selected else INK,
                mono=True,
            )
        ascii_value = "".join(
            "?" if v is None else chr(v) if 32 <= v < 127 else "·" for v in self.values[:16]
        )
        text(p, (24, 88 + self.rows * 48, self.box.w - 48, 32), f"ASCII  {ascii_value}", 17, MUTED, mono=True)
        p.restore()


class Connector(QGraphicsObject):
    def __init__(self, identity):
        super().__init__()
        self.identity = identity
        self.route = None
        self.color = BLUE
        self.dashed = False
        self.setZValue(4)

    def set_route(self, route):
        if self.route == route:
            return
        self.prepareGeometryChange()
        self.route = route
        self.update()

    def boundingRect(self):
        if not self.route:
            return QRectF()
        xs, ys = [p.x for p in self.route.points], [p.y for p in self.route.points]
        return QRectF(min(xs) - 15, min(ys) - 15, max(xs) - min(xs) + 30, max(ys) - min(ys) + 30)

    def paint(self, p, option, widget=None):
        if not self.route:
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(self.color), 3)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        if self.dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        path = QPainterPath(QPointF(self.route.points[0].x, self.route.points[0].y))
        for point in self.route.points[1:]:
            path.lineTo(point.x, point.y)
        p.drawPath(path)
        end, previous = self.route.points[-1], self.route.points[-2]
        angle = atan2(end.y - previous.y, end.x - previous.x)
        head = min(12, hypot(end.x - previous.x, end.y - previous.y))
        half = min(6, head * 0.5)
        poly = QPolygonF(
            [
                QPointF(end.x, end.y),
                QPointF(
                    end.x - head * cos(angle) + half * sin(angle),
                    end.y - head * sin(angle) - half * cos(angle),
                ),
                QPointF(
                    end.x - head * cos(angle) - half * sin(angle),
                    end.y - head * sin(angle) + half * cos(angle),
                ),
            ]
        )
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.color))
        p.drawPolygon(poly)


class DataToken(QGraphicsObject):
    def __init__(self, identity):
        super().__init__()
        self.identity = identity
        self.label = "12"
        self.setZValue(8)

    def boundingRect(self):
        return QRectF(-34, -20, 68, 40)

    def paint(self, p, option, widget=None):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(BLUE))
        p.setPen(QPen(QColor("#ffffff"), 3))
        p.drawRoundedRect(self.boundingRect().adjusted(2, 2, -2, -2), 10, 10)
        text(p, (-24, -18, 52, 36), self.label, 20, "#ffffff", True, True)


def check_text_fits(value, width, size=24, mono=False):
    return QFontMetricsF(font(size, mono)).horizontalAdvance(value) <= width
