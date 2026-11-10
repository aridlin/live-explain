"""Server-hosted Qt presentation with separate audience and presenter web views.

Bind to loopback by default. Production sits behind the portal's authenticated
HTTPS reverse proxy; this module does not expose the old unauthenticated LAN API.
"""

import argparse
from hashlib import sha256
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QTimer
from PySide6.QtWidgets import QApplication

from .app import build_presentation, build_scene, capture
from .preflight import load_fonts
from .protocol import CommandHost
from .remote import BoundedServer, GuiBridge
from .runtime import Session
from .visual import Transition

PAGES = Path(__file__).parent / "assets" / "web"


class WebInstrument:
    def __init__(self, app, args):
        self.app = app
        self.session = Session(build_presentation(args), args.canonical)
        self.scene = build_scene(self.session)
        self.recovery = Path(args.state_dir) / (args.presentation + ".json")
        if self.recovery.exists():
            try:
                self.session.recover(self.recovery)
            except ValueError:
                # A changed talk has a new fingerprint. Start its normal entry paused.
                self.session.status = "Zmieniona treść prezentacji; rozpoczęto od początku."
        self.previous = time.monotonic()
        self.frame = b""
        self.frame_etag = ""
        self.frame_key = None
        self.render_frame()
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(40)

    def remote_state(self):
        state = self.session.controller_state()
        transition = self.scene.transition
        state.update(
            blank=self.scene.blank,
            transitioning=bool(transition and transition.active),
            transition_paused=bool(transition and transition.paused),
            outputs=[],
        )
        return state

    def send(self, kind, value=None):
        if kind == "output":
            return False, "Wersja WWW nie używa lokalnego monitora serwera."
        transition = self.scene.transition
        if transition and transition.active:
            if kind in {"pause", "freeze"}:
                transition.paused = True
                self.session.command("freeze")
                return True, "Wstrzymano przejście."
            if kind == "play":
                transition.paused = False
                self.session._changed()
                return True, "Wznowiono przejście."
            if kind == "finish":
                transition.finish()
                self.session._changed()
                self.render_frame()
                return True, "Zakończono przejście."
            if kind not in {"undo", "blank", "reset"}:
                return False, "Trwa przejście; poczekaj lub wybierz Dokończ."
        old = self.session.beat.id
        previous = (
            capture(self.scene, None) if kind in {"advance", "detour", "depth", "return", "undo"} else None
        )
        if kind == "blank":
            if value not in (None, "on", "off"):
                return False, "Nieznany stan zasłony."
            self.session.command("freeze")
            self.scene.blank = value == "on" if value else not self.scene.blank
            if transition:
                transition.paused = True
            accepted, message = True, "Zmieniono zasłonę."
        else:
            accepted, message = self.session.command(kind, value)
        if old != self.session.beat.id and previous is not None:
            self.scene.previous_frame = previous
            self.scene.transition = Transition()
        if accepted and kind == "reset":
            self.scene.blank = False
            self.scene.transition = None
            self.scene.previous_frame = None
        self.scene.refresh()
        self.render_frame()
        if accepted:
            self.session.save(self.recovery)
        return accepted, message

    def tick(self):
        now = time.monotonic()
        delta, self.previous = now - self.previous, now
        self.session.tick(delta)
        if self.scene.transition and self.scene.transition.active:
            self.scene.transition.tick(delta)
        self.render_frame()

    def render_frame(self):
        transition = self.scene.transition
        key = (
            self.session.beat.id,
            self.session.state.playback.position,
            self.scene.blank,
            transition.position if transition else None,
        )
        if key == self.frame_key:
            return
        self.scene.refresh()
        image = capture(self.scene, None, 1600, 900)
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "JPEG", 85):
            raise RuntimeError("Could not encode audience frame")
        payload = bytes(data)
        self.frame, self.frame_etag = payload, '"' + sha256(payload).hexdigest() + '"'
        self.frame_key = key


class WebServer:
    def __init__(self, instrument, host="127.0.0.1", port=18766, origin=None):
        import threading

        self.instrument = instrument
        self.host = CommandHost(instrument.session, instrument.send, instrument.remote_state)
        self.bridge = GuiBridge(self.host)
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, status, data=b"", mime="application/json; charset=utf-8", headers=None):
                self.send_response(status)
                self.send_header("Content-Type", mime)
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header(
                    "Content-Security-Policy",
                    "default-src 'self'; img-src 'self' blob:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'",
                )
                for name, value in (headers or {}).items():
                    self.send_header(name, value)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                path = urlsplit(self.path).path
                static = {
                    "/": "audience.html",
                    "/presenter/": "presenter.html",
                    "/audience.js": "audience.js",
                    "/presenter.js": "presenter.js",
                    "/web.css": "web.css",
                }
                if path in static:
                    file = PAGES / static[path]
                    mime = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}[file.suffix]
                    self.reply(200, file.read_bytes(), mime + "; charset=utf-8")
                elif path == "/frame.jpg":
                    frame, etag = owner.instrument.frame, owner.instrument.frame_etag
                    if self.headers.get("If-None-Match") == etag:
                        self.reply(304, headers={"ETag": etag})
                    else:
                        self.reply(200, frame, "image/jpeg", {"ETag": etag})
                elif path == "/state":
                    result = owner.bridge.call(self.headers.get("X-Controller", "web"), None)
                    self.reply(200, json.dumps(result, ensure_ascii=False).encode())
                elif path == "/health":
                    self.reply(
                        200,
                        json.dumps(
                            {"status": "ok", "presentation": instrument.session.presentation.id}
                        ).encode(),
                    )
                else:
                    self.reply(404, b"{}")

            def do_POST(self):
                path = urlsplit(self.path).path
                if path not in {"/command", "/resolve"}:
                    self.reply(404, b"{}")
                    return
                expected = origin or "http://" + self.headers.get("Host", "")
                if self.headers.get("Origin") not in (None, expected):
                    self.reply(403, b'{"error":"origin"}')
                    return
                if self.headers.get_content_type() != "application/json":
                    self.reply(415, b"{}")
                    return
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 0 < size <= 4096:
                        raise ValueError()
                    raw = self.rfile.read(size).decode("utf-8")
                except (ValueError, UnicodeError):
                    self.reply(400, b"{}")
                    return
                result = owner.bridge.call(self.headers.get("X-Controller", "web"), raw, path == "/resolve")
                self.reply(200, json.dumps(result, ensure_ascii=False).encode())

        self.server = BoundedServer((host, port), Handler)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def main():
    parser = argparse.ArgumentParser(description="Live Explain web host; deploy behind authenticated HTTPS")
    parser.add_argument("--presentation", choices=("spectre", "recruitment"), default="recruitment")
    parser.add_argument("--canonical", choices=("simple", "normal", "deep"), default="normal")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18766)
    parser.add_argument(
        "--state-dir", default=os.environ.get("LIVE_EXPLAIN_STATE_DIR", "artifacts/web-state")
    )
    args = parser.parse_args()
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv[:1])
    load_fonts()
    instrument = WebInstrument(app, args)
    server = WebServer(instrument, args.host, args.port, os.environ.get("LIVE_EXPLAIN_ORIGIN"))
    app.aboutToQuit.connect(server.close)
    print(f"Live Explain web host listening on {args.host}:{server.port}", flush=True)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
