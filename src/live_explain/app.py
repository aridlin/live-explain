"""Two-window Qt desktop instrument. No compositor integration or remote shell."""

import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import time

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from .runtime import Session
from .visual import Transition
from .preflight import load_fonts
from .presentations.spectre import build
from .presentations.spectre_scene import SpectreScene


class Audience(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setWindowTitle("Live Explain — audience")
        self.setObjectName("live-explain-audience")
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.resize(1280, 720)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class Presenter(QMainWindow):
    def __init__(self, session, send, audience):
        super().__init__()
        self.session, self.send, self.audience = session, send, audience
        self.setWindowTitle("Live Explain — private presenter")
        self.resize(1050, 820)
        self.setStyleSheet("""
            QMainWindow,QWidget {background:#152833;color:#edf2ed;font-family:"DejaVu Sans";font-size:14px;}
            QLabel#eyebrow {color:#91c9b6;font-size:12px;font-weight:bold;}
            QLabel#cue {font-size:26px;font-weight:bold;}
            QPushButton {background:#253e4a;border:1px solid #3b5560;border-radius:8px;padding:12px;}
            QPushButton:hover {background:#365a69;} QPushButton:disabled {color:#788b92;}
            QPushButton#primary {background:#287d71;font-weight:bold;}
            QComboBox {padding:10px;background:#253e4a;border:1px solid #3b5560;border-radius:6px;}
            QTextBrowser {background:#1c333f;border:0;border-radius:8px;padding:12px;font-size:17px;}
            QSlider::groove:horizontal {height:5px;background:#39515b;}
            QSlider::handle:horizontal {background:#93d1bb;width:16px;margin:-6px 0;border-radius:8px;}
        """)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        self.context = QLabel()
        self.context.setObjectName("eyebrow")
        self.cue = QLabel()
        self.cue.setObjectName("cue")
        self.cue.setWordWrap(True)
        self.objective = QLabel()
        self.objective.setWordWrap(True)
        self.return_label = QLabel()
        self.return_label.setWordWrap(True)
        for w in (self.context, self.cue, self.objective, self.return_label):
            layout.addWidget(w)
        self.script = QTextBrowser()
        self.script.verticalScrollBar().valueChanged.connect(self.remember_script_scroll)
        layout.addWidget(self.script, 1)
        controls = QHBoxLayout()
        for title, kind in [
            ("Dalej  →", "advance"),
            ("Pauza  Spacja", "pause"),
            ("Krok  ↓", "step"),
            ("Dokończ  F", "finish"),
            ("Powtórz  R", "replay"),
            ("Cofnij  U", "undo"),
        ]:
            button = QPushButton(title)
            if kind == "advance":
                button.setObjectName("primary")
            button.clicked.connect(lambda checked=False, k=kind: send(k))
            controls.addWidget(button)
        layout.addLayout(controls)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderPressed.connect(lambda: send("pause"))
        self.slider.sliderReleased.connect(lambda: send("seek", self.slider.value() / 1000))
        layout.addWidget(self.slider)
        self.time_label = QLabel()
        layout.addWidget(self.time_label)
        detour_row = QHBoxLayout()
        self.detour = QComboBox()
        detour_row.addWidget(self.detour, 1)
        open_detour = QPushButton("Wyjaśnij")
        open_detour.clicked.connect(lambda: send("detour", self.detour.currentData()))
        detour_row.addWidget(open_detour)
        self.return_button = QPushButton("Powrót  Backspace")
        self.return_button.clicked.connect(lambda: send("return"))
        detour_row.addWidget(self.return_button)
        layout.addLayout(detour_row)
        depth_row = QHBoxLayout()
        self.depth = QComboBox()
        for label, key in [("Super prosta", "simple"), ("Normalna", "normal"), ("Szczegółowa", "deep")]:
            self.depth.addItem(label, key)
        self.depth.setCurrentIndex(1)
        depth_row.addWidget(self.depth)
        self.gaps = QLabel()
        self.gaps.setWordWrap(True)
        depth_row.addWidget(self.gaps, 1)
        land = QPushButton("Przejdź do tej kontynuacji")
        land.clicked.connect(lambda: send("depth", self.depth.currentData()))
        depth_row.addWidget(land)
        layout.addLayout(depth_row)
        self.depth.currentIndexChanged.connect(lambda: self.refresh(force=True))
        output_row = QHBoxLayout()
        self.screens = QComboBox()
        self.refresh_screens()
        output_row.addWidget(self.screens, 1)
        output = QPushButton("Pełny ekran na wyjściu")
        output.clicked.connect(self.assign_output)
        output_row.addWidget(output)
        blank = QPushButton("Zasłoń / pokaż  B")
        blank.clicked.connect(lambda: send("blank"))
        output_row.addWidget(blank)
        layout.addLayout(output_row)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self._last_beat = None
        self.refresh()

    def remember_script_scroll(self, value):
        self.session.state.cue_index = value

    def refresh_screens(self):
        self.screens.clear()
        for i, screen in enumerate(QApplication.screens()):
            self.screens.addItem(
                f"{i + 1}: {screen.name()} — {screen.size().width()}×{screen.size().height()}", i
            )

    def assign_output(self):
        index = self.screens.currentData()
        screens = QApplication.screens()
        if index is None or index >= len(screens):
            return
        self.send("pause")
        self.audience.hide()
        self.audience.windowHandle().setScreen(screens[index])
        self.audience.setGeometry(screens[index].geometry())
        self.audience.showFullScreen()
        self.audience.scene().blank = False
        self.audience.scene().refresh()

    def refresh(self, force=False):
        s = self.session
        n, p = s.state.narrative, s.state.playback
        self.context.setText(f"PRYWATNY PULPIT  /  {n.canonical.upper()}  /  {s.beat.checkpoint}")
        self.cue.setText(s.beat.script.cue)
        self.objective.setText("Cel: " + s.beat.script.objective)
        origin = s.state.detours[-1].narrative.beat if s.state.detours else "główna narracja"
        pending = f" • Po moście: {n.bridge_target}" if n.bridge_target else ""
        self.return_label.setText(f"Powrót: {origin}{pending}\n{s.state.return_sentence}")
        if self._last_beat != s.beat.id or force:
            import html

            script = s.beat.script
            scroll_position = s.state.cue_index
            self.script.blockSignals(True)
            self.script.verticalScrollBar().blockSignals(True)
            self.script.setHtml(
                "<p>"
                + html.escape(script.wording)
                + "</p><p><b>Następne zdanie</b><br>"
                + html.escape(script.next_sentence)
                + "</p><p><b>Granice wyjaśnienia</b><br>"
                + html.escape(script.boundary)
                + "</p><p><b>Krótki powrót</b><br>"
                + html.escape(script.recap)
                + "</p>"
            )
            self.script.verticalScrollBar().setValue(scroll_position)
            self.script.verticalScrollBar().blockSignals(False)
            self.script.blockSignals(False)
            self.detour.clear()
            names = {"cache-location": "Gdzie jest cache?", "cache-lines": "Co to jest linia cache?"}
            for key in s.beat.detours:
                self.detour.addItem(names.get(key, key), key)
            self._last_beat = s.beat.id
        self.return_button.setEnabled(bool(s.state.detours))
        if not self.slider.isSliderDown():
            self.slider.setMaximum(int(s.beat.holds[-1] * 1000))
            self.slider.setValue(int(p.position * 1000))
        self.time_label.setText(
            f"{'ODTWARZANIE' if p.playing else 'WSTRZYMANE'}   {p.position:.2f} / {s.beat.holds[-1]:.0f} s sekwencji"
            f"     •     Czas wystąpienia {int(s.elapsed) // 60:02}:{int(s.elapsed) % 60:02}"
        )
        missing = s.landing_gaps(self.depth.currentData())
        self.gaps.setText(
            "Most wymagany: " + ", ".join(sorted(missing)) if missing else "Gotowy autorski punkt wejścia"
        )
        self.status.setText(s.status + "   |   P: pulpit • Esc: zamknij pełny ekran")


class Instrument:
    def __init__(self, app, args):
        self.app = app
        self.session = Session(build(), args.canonical)
        self.scene = SpectreScene(self.session)
        self.audience = Audience(self.scene)
        self.presenter = Presenter(self.session, self.send, self.audience)
        self.recovery = Path.home() / ".local/state/live-explain/recovery.json"
        if args.beat:
            if args.beat not in self.session.presentation.routes[args.canonical]:
                raise ValueError("Interactive --beat must belong to the selected canonical")
            self.session._entry(args.beat)
        if args.position:
            self.session.seek(args.position)
        if args.recover and self.recovery.exists():
            self.session.recover(self.recovery)
        self.shortcuts = []
        for key, kind in [
            ("Right", "advance"),
            ("Down", "step"),
            ("F", "finish"),
            ("R", "replay"),
            ("U", "undo"),
            ("Backspace", "return"),
            ("B", "blank"),
            ("P", "presenter"),
            ("Space", "toggle"),
            ("Escape", "windowed"),
            ("F11", "fullscreen"),
        ]:
            shortcut = QShortcut(QKeySequence(key), self.audience)
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(lambda k=kind: self.send(k))
            self.shortcuts.append(shortcut)
        if args.debug:
            self.scene.debug = True
        for screen in app.screens():
            screen.geometryChanged.connect(self.display_changed)
        app.screenRemoved.connect(self.display_changed)
        app.screenAdded.connect(self.display_changed)
        self.previous = time.monotonic()
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)
        app.aboutToQuit.connect(lambda: self.session.save(self.recovery))
        if args.record:

            def save_recording():
                args.record.parent.mkdir(parents=True, exist_ok=True)
                args.record.write_text(
                    json.dumps(self.session.export_recording(), ensure_ascii=False, indent=2) + "\n"
                )

            app.aboutToQuit.connect(save_recording)
        if args.replay_file:
            self.session.replay_recording(json.loads(args.replay_file.read_text()))
            self.session.state.playback.playing = False
            self.scene.refresh()
            self.presenter.refresh()

    def display_changed(self, *args):
        self.session.command("freeze")
        self.scene.transition = None
        self.scene.blank = True
        self.presenter.hide()
        self.presenter.refresh_screens()
        self.scene.refresh()
        self.session.status = "Wyjście zmieniło się. P otwiera prywatny pulpit do ponownego wyboru ekranu."

    def send(self, kind, value=None):
        transition = self.scene.transition
        if transition and transition.active:
            if kind in {"pause", "freeze", "toggle"}:
                transition.paused = not transition.paused if kind == "toggle" else True
                self.session.command("freeze")
                return
            if kind == "play":
                transition.paused = False
                return
            if kind == "finish":
                transition.finish()
                self.scene.update()
                return
            if kind not in {"undo", "blank", "presenter", "windowed", "fullscreen"}:
                self.session.status = "Trwa zmiana kompozycji. Pauza zatrzymuje; F kończy."
                self.presenter.refresh()
                return
        old_beat = self.session.beat.id
        previous_frame = (
            capture(self.scene, None) if kind in {"advance", "detour", "depth", "return", "undo"} else None
        )
        if kind == "toggle":
            kind = "pause" if self.session.state.playback.playing else "play"
        if kind == "blank":
            self.session.command("freeze")
            self.scene.blank = not self.scene.blank
            if self.scene.transition:
                self.scene.transition.paused = True
        elif kind == "presenter":
            self.presenter.setVisible(not self.presenter.isVisible())
            if self.presenter.isVisible():
                self.presenter.raise_()
        elif kind == "fullscreen":
            if self.audience.isFullScreen():
                self.audience.showNormal()
            else:
                self.audience.showFullScreen()
        elif kind == "windowed":
            self.audience.showNormal()
        else:
            self.session.command(kind, value)
        self.scene.refresh()
        if self.session.beat.id != old_beat and previous_frame is not None:
            self.scene.previous_frame = previous_frame
            self.scene.transition = Transition()
        self.presenter.refresh()
        self.session.save(self.recovery)

    def tick(self):
        now = time.monotonic()
        delta = now - self.previous
        self.previous = now
        was = self.session.state.playback.playing
        self.session.tick(delta)
        if self.scene.transition and self.scene.transition.active:
            self.scene.transition.tick(delta)
            if not self.scene.transition.active:
                self.scene.previous_frame = None
            self.scene.update()
        if was:
            self.scene.refresh()
        self.presenter.refresh()


def capture(scene, path, width=1600, height=900):
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor("#f4f3ed"))
    painter = QPainter(image)
    scene.render(painter, QRectF(0, 0, width, height), scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    painter.end()
    if path is not None and not image.save(str(path)):
        raise OSError(f"Could not save {path}")
    return image


def main():
    parser = argparse.ArgumentParser(description="Live Explain — live presentation instrument")
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument(
        "--presenter", action="store_true", help="Show private notes (rehearsal only on a single screen)"
    )
    parser.add_argument("--canonical", choices=("simple", "normal", "deep"), default="normal")
    parser.add_argument("--screen", type=int, help="Zero-based audience output")
    parser.add_argument("--debug", action="store_true", help="Authoring geometry overlay")
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--record", type=Path, help="Save accepted rehearsal commands on exit")
    parser.add_argument(
        "--replay-file", type=Path, help="Restore the result of a deterministic rehearsal trace"
    )
    parser.add_argument(
        "--export", type=Path, help="Export public fallback stills and a separately labelled private script"
    )
    parser.add_argument("--capture", type=Path, help="Offscreen screenshot, no private UI")
    parser.add_argument("--beat", help="Named beat for capture/rehearsal")
    parser.add_argument("--position", type=float, default=0)
    parser.add_argument(
        "--benchmark", type=int, metavar="FRAMES", help="Measure offscreen render throughput, not display FPS"
    )
    args = parser.parse_args()
    if args.capture or args.benchmark or args.export:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv[:1])
    app.setApplicationName("Live Explain")
    app.setDesktopFileName("pl.aridlin.LiveExplain")
    load_fonts()
    if args.capture or args.benchmark or args.export:
        session = Session(build(), args.canonical)
        if args.beat:
            if args.beat not in session.presentation.beats:
                parser.error("Unknown beat")
            session._entry(args.beat)
        session.seek(args.position)
        scene = SpectreScene(session)
        scene.debug = args.debug
        if args.export:
            public = args.export / "public"
            public.mkdir(parents=True, exist_ok=True)
            private = args.export / "PRIVATE-presenter-script.txt"
            notes = []
            for index, key in enumerate(session.presentation.routes[args.canonical]):
                session._entry(key)
                for hold_index, hold in enumerate(session.beat.holds):
                    session.seek(hold)
                    scene.refresh()
                    capture(scene, public / f"{index + 1:02}-{hold_index:02}-{key}.png")
                notes.append(
                    session.beat.title
                    + "\n"
                    + session.beat.script.wording
                    + "\n"
                    + session.beat.script.next_sentence
                )
            private.write_text(
                "PRYWATNY SKRYPT — NIE WYŚWIETLAĆ PUBLICZNIE\n\n" + "\n\n".join(notes), encoding="utf-8"
            )
            print(str(public))
        if args.capture:
            args.capture.parent.mkdir(parents=True, exist_ok=True)
            capture(scene, args.capture)
            print(str(args.capture))
        if args.benchmark:
            if args.benchmark < 2:
                parser.error("Benchmark needs at least two frames")
            samples = []
            image = QImage(1920, 1080, QImage.Format.Format_ARGB32_Premultiplied)
            for i in range(args.benchmark + 10):
                start = time.perf_counter()
                session.seek((i % 120) / 120 * session.beat.holds[-1])
                scene.refresh()
                image.fill(QColor("#f4f3ed"))
                p = QPainter(image)
                scene.render(p, QRectF(0, 0, 1920, 1080))
                p.end()
                if i >= 10:
                    samples.append((time.perf_counter() - start) * 1000)
            samples.sort()
            print(
                json.dumps(
                    dict(
                        kind="offscreen_scene_cpu_throughput_not_display_fps",
                        frames=len(samples),
                        median_ms=statistics.median(samples),
                        p95_ms=samples[int(0.95 * (len(samples) - 1))],
                        p99_ms=samples[int(0.99 * (len(samples) - 1))],
                    ),
                    indent=2,
                )
            )
        return 0
    instrument = Instrument(app, args)
    screens = app.screens()
    index = (
        args.screen
        if args.screen is not None
        else next((i for i, s in enumerate(screens) if "HDMI" in s.name()), 0)
    )
    if not 0 <= index < len(screens):
        parser.error("Screen index unavailable")
    instrument.audience.winId()
    instrument.audience.windowHandle().setScreen(screens[index])
    instrument.audience.setGeometry(screens[index].geometry())
    if args.windowed:
        instrument.audience.resize(1280, 720)
        instrument.audience.show()
    else:
        instrument.audience.showFullScreen()
    # Private notes are opt-in; never auto-open on a potentially mirrored desktop.
    laptop = next((screen for screen in screens if "eDP" in screen.name()), screens[0])
    instrument.presenter.winId()
    instrument.presenter.windowHandle().setScreen(laptop)
    if args.presenter:
        instrument.presenter.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
