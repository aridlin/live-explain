"""Dependency-free browser host for the existing authored presentation/runtime."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import mimetypes
import threading
import time
import webbrowser

from .presentations.talk import build
from .presentations.spectre import audience_model
from .protocol import CommandHost
from .runtime import Session, Narrative

ASSETS = Path(__file__).parent / "web"
FONTS = Path(__file__).parent / "assets" / "fonts"


class WebHost:
    def __init__(self, canonical="normal"):
        self.session = Session(build(), canonical)
        self.lock = threading.RLock()
        self.blank = False
        self.journal = []
        self.protocol = CommandHost(self.session, self.dispatch, self.presenter)
        self.protocol.ALLOWED = self.protocol.ALLOWED | {"seek", "chapter"}

    def dispatch(self, kind, value):
        accepted, message = self._dispatch(kind, value)
        if accepted:
            self.journal.append(
                dict(
                    kind=kind,
                    value=value,
                    elapsed=self.session.elapsed,
                    beat=self.session.beat.id,
                    position=self.session.state.playback.position,
                    canonical=self.session.state.narrative.canonical,
                    blank=self.blank,
                )
            )
        return accepted, message

    def recording(self):
        return dict(
            format="live-explain-web-v1",
            presentation=self.session.presentation.fingerprint,
            initial_canonical=self.session.initial_canonical,
            commands=self.journal,
        )

    def _dispatch(self, kind, value):
        if kind == "blank":
            self.blank = not self.blank
            self.session.command("pause")
            return True, "Ekran zasłonięty." if self.blank else "Ekran odsłonięty."
        if kind == "output":
            return False, "Przenieś okno przeglądarki na wybrany ekran."
        if kind == "seek":
            try:
                return self.session.command("seek", float(value))
            except (TypeError, ValueError):
                return False, "Nieprawidłowa pozycja."
        if kind == "chapter":
            canonical = self.session.state.narrative.canonical
            destination = f"{canonical}.{value}"
            if destination not in self.session.presentation.routes[canonical]:
                return False, "Nieznany rozdział."
            # Chapter selection is deliberate navigation, with the same prerequisites
            # as a route change. Jumping is not evidence of delivered material.
            landing = self.session.presentation.checkpoint_landings[value][canonical]
            missing = landing.requires - self.session.delivered
            self.session._remember()
            self.session.state.detours.clear()
            self.session.state.narrative = Narrative(canonical, destination)
            if missing:
                self.session._entry(landing.bridge)
                self.session.state.narrative.bridge_target = canonical + ":" + destination
            else:
                self.session._entry(destination)
            return True, "Najpierw krótkie przypomnienie." if missing else "Wybrano rozdział."
        if self.blank and kind in {"advance", "play", "step", "finish"}:
            return False, "Najpierw odsłoń ekran."
        try:
            return self.session.command(kind, value)
        except (ValueError, TypeError):
            return False, "Nieprawidłowe polecenie."

    def audience(self):
        s, b = self.session, self.session.beat
        model = audience_model(s.model, b.diagram.get("secret", False))
        # Before the measurement chapter, never send the concealed probe value.
        # Measurement is the intentionally observable channel, not private narration.
        return dict(
            epoch=s.epoch,
            revision=s.revision,
            beat=b.id,
            title=b.title,
            subtitle=b.subtitle,
            checkpoint=b.checkpoint,
            composition=b.composition,
            diagram=b.diagram,
            code=b.code,
            holds=b.holds,
            position=s.state.playback.position,
            playing=s.state.playback.playing,
            target=s.state.playback.target,
            canonical=s.state.narrative.canonical,
            model=model,
            blank=self.blank,
            duration=b.holds[-1],
            elapsed=s.elapsed,
        )

    def presenter(self):
        return {**self.session.controller_state(), "audience": self.audience(), "blank": self.blank}

    def catalog(self):
        p = self.session.presentation
        return [
            dict(id=p.beats[k].checkpoint, title=p.beats[k].title, seconds=p.beats[k].planned_seconds)
            for k in p.routes["normal"]
        ]


def make_server(host="127.0.0.1", port=8080, canonical="normal"):
    app = WebHost(canonical)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, code, data, mime="application/json; charset=utf-8"):
            if not isinstance(data, bytes):
                data = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'self'",
            )
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            with app.lock:
                if path == "/api/audience":
                    return self.reply(200, app.audience())
                if path == "/state":
                    return self.reply(200, {"status": "state", "state": app.presenter()})
                if path == "/api/catalog":
                    return self.reply(200, app.catalog())
                if path == "/api/recording":
                    return self.reply(200, app.recording())
            if path in ("/", "/presenter"):
                return self.reply(200, (ASSETS / "index.html").read_bytes(), "text/html; charset=utf-8")
            # Explicit asset allowlist: never serve the Python package or private scripts.
            file = (
                ASSETS / path[1:] if path in ("/app.js", "/style.css", "/scene.js", "/sources.json") else None
            )
            if path in ("/fonts/DejaVuSans.ttf", "/fonts/DejaVuSans-Bold.ttf", "/fonts/DejaVuSansMono.ttf"):
                file = FONTS / path.rsplit("/", 1)[-1]
            if file and file.is_file():
                return self.reply(
                    200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                )
            self.reply(404, {"error": "Not found"})

        def do_POST(self):
            if self.path not in ("/command", "/resolve"):
                return self.reply(404, {"error": "Not found"})
            # No cross-origin writes to a presenter session from unrelated websites.
            origin = self.headers.get("Origin")
            if origin and origin != "http://" + self.headers.get("Host", ""):
                return self.reply(403, {"error": "Origin rejected"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    return self.reply(413, {"error": "Body too large"})
                raw = self.rfile.read(length).decode("utf-8")
            except (ValueError, UnicodeError):
                return self.reply(400, {"error": "Invalid body"})
            with app.lock:
                result = app.protocol.handle(
                    raw, self.headers.get("X-Controller", "browser"), self.path == "/resolve"
                )
            self.reply(200, result)

    class Server(ThreadingHTTPServer):
        daemon_threads = True

        def get_request(self):
            sock, address = super().get_request()
            sock.settimeout(5)
            return sock, address

    server = Server((host, port), Handler)
    server.app = app
    server.stop_clock = threading.Event()

    def clock():
        previous = time.monotonic()
        while not server.stop_clock.wait(1 / 60):
            now = time.monotonic()
            with app.lock:
                app.session.tick(now - previous)
            previous = now

    server.clock_thread = threading.Thread(target=clock, daemon=True)
    server.clock_thread.start()
    return server


def main():
    parser = argparse.ArgumentParser(description="Live Explain — browser audience and presenter")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--remote", action="store_true", help="Listen on the LAN for a phone presenter")
    parser.add_argument("--canonical", choices=("simple", "normal", "deep"), default="normal")
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    server = make_server("0.0.0.0" if args.remote else "127.0.0.1", args.port, args.canonical)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Audience: {url}\nPresenter: {url}/presenter", flush=True)
    if args.remote:
        print(
            "Phone: open http://<laptop-LAN-IP>:"
            + str(server.server_port)
            + "/presenter on the same trusted Wi-Fi. No pairing.",
            flush=True,
        )
    if not args.no_open:
        webbrowser.open(url + "/presenter")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop_clock.set()
        server.server_close()


if __name__ == "__main__":
    main()
