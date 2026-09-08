"""Representative workload, distinct from audience content and from GPU claims."""

import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import time
from PySide6.QtCore import QTimer, QRectF
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtWidgets import QApplication, QGraphicsScene
from .components import Card, CodePane, HexPane, Connector, DataToken, text
from .geometry import Box, Point, Route, smooth
from .app import Audience
from .preflight import load_fonts


class StressScene(QGraphicsScene):
    def __init__(self):
        super().__init__(0, 0, 3200, 1800)
        self.code = CodePane()
        self.code.place(Box(64, 180, 940, 1320))
        self.code.source(tuple(f"value_{i:02} = memory[index + {i}]; // żółć" for i in range(30)), {})
        self.memory = HexPane(columns=16, rows=8)
        self.memory.place(Box(1100, 180, 800, 560))
        self.nodes = [Card(f"node-{i}", f"COMPONENT {i:02}") for i in range(24)]
        self.links = [Connector(f"route-{i}") for i in range(40)]
        self.tokens = [DataToken(f"value-{i}") for i in range(24)]
        for item in [self.code, self.memory, *self.nodes, *self.links, *self.tokens]:
            self.addItem(item)
        self.frame(0)

    def frame(self, position):
        self.code.active = int(position * 4) % 30
        self.code.update()
        self.memory.values = [(i + int(position * 30)) % 256 for i in range(128)]
        self.memory.selected = int(position * 20) % 128
        self.memory.update()
        for i, node in enumerate(self.nodes):
            col, row = i % 6, i // 6
            move = smooth((position % 2) / 2) * 24 if i == 0 else 0
            node.place(Box(1100 + col * 335 + move, 900 + row * 190, 250 + move, 120))
            node.body = f"value {i:02}"
        routes = []
        for row in range(4):
            for col in range(5):
                a, b = (
                    self.nodes[row * 6 + col].box.port("right"),
                    self.nodes[row * 6 + col + 1].box.port("left"),
                )
                routes.append(Route(f"h-{row}-{col}", (a, b)))
        for row in range(3):
            for col in range(6):
                a, b = (
                    self.nodes[row * 6 + col].box.port("bottom"),
                    self.nodes[(row + 1) * 6 + col].box.port("top"),
                )
                mid = (a.y + b.y) / 2
                routes.append(Route(f"v-{row}-{col}", (a, Point(a.x, mid), Point(b.x, mid), b)))
        routes.extend(
            [
                Route("extra-a", (Point(2000, 300), Point(2200, 300), Point(2200, 650))),
                Route("extra-b", (Point(2400, 650), Point(2600, 650), Point(2600, 300))),
            ]
        )
        for link, route in zip(self.links, routes):
            link.set_route(route)
        for i, token in enumerate(self.tokens):
            point = routes[i].at((position / 2 + i / 24) % 1)
            token.setPos(point.x, point.y)
            token.label = f"{self.memory.values[i]:02X}"

    def drawBackground(self, p, rect):
        p.fillRect(rect, QColor("#f4f3ed"))
        text(
            p,
            (64, 50, 3000, 80),
            "STRESS SCENE — 30 code lines / 128 bytes / 24 components / 40 routes / 24 tokens",
            40,
        )


def summary(samples):
    samples = sorted(samples)
    return dict(
        median_ms=statistics.median(samples),
        p95_ms=samples[int(0.95 * (len(samples) - 1))],
        p99_ms=samples[int(0.99 * (len(samples) - 1))],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=240)
    parser.add_argument(
        "--live", action="store_true", help="Show two real windows and measure paint callbacks"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--slice",
        action="store_true",
        help="Benchmark the actual authored slice instead of the dense stress fixture",
    )
    args = parser.parse_args()
    if args.frames < 20:
        parser.error("Use at least 20 frames")
    if not args.live:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv[:1])
    load_fonts()
    if args.slice:
        from .runtime import Session
        from .presentations.spectre import build
        from .presentations.spectre_scene import SpectreScene

        session = Session(build())
        scene = SpectreScene(session)
    else:
        scene = StressScene()
    primary = Audience(scene)
    primary.resize(1920, 1080)
    secondary = Audience(scene)
    secondary.resize(800, 450)
    secondary.setWindowTitle("Live Explain — benchmark second view")
    if args.live:
        primary.show()
        secondary.show()
        app.processEvents()
    image = QImage(1920, 1080, QImage.Format.Format_ARGB32_Premultiplied)
    preview = QImage(800, 450, QImage.Format.Format_ARGB32_Premultiplied)
    costs = []
    intervals = []
    last = time.perf_counter()
    frame = 0

    def measure():
        nonlocal last, frame
        now = time.perf_counter()
        if frame >= 10:
            intervals.append((now - last) * 1000)
        last = now
        if args.slice:
            session.seek((frame / 60) % 6)
            scene.refresh()
        else:
            scene.frame(frame / 60)
        if args.live:
            primary.viewport().repaint()
            secondary.viewport().repaint()
        else:
            for target in (image, preview):
                target.fill(QColor("#f4f3ed"))
                p = QPainter(target)
                scene.render(p, QRectF(0, 0, target.width(), target.height()))
                p.end()
        if frame >= 10:
            costs.append((time.perf_counter() - now) * 1000)
        frame += 1
        if frame >= args.frames + 10:
            app.quit()

    if args.live:
        timer = QTimer()
        timer.timeout.connect(measure)
        timer.start(16)
        app.exec()
    else:
        for _ in range(args.frames + 10):
            measure()
    result = dict(
        mode="live_two_window_paint" if args.live else "offscreen_two_target_throughput",
        frames=len(costs),
        workload="authored_normal_slice"
        if args.slice
        else dict(code_lines=30, bytes=128, components=24, routes=40, tokens=24),
        paint_cost=summary(costs),
        callback_intervals=summary(intervals),
        limitation="Paint/callback timings do not measure compositor presentation or photon latency.",
    )
    output = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n")
    print(output)


if __name__ == "__main__":
    main()
