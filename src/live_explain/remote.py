"""Open local HTTP controller. Only the GUI thread touches the authoritative instrument."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtNetwork import QNetworkInterface
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit

from .protocol import CommandHost


class GuiBridge(QObject):
    requested = Signal(object)

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.requested.connect(self.execute, Qt.ConnectionType.QueuedConnection)

    def execute(self, request):
        controller, body, resolve, complete, result = request
        self.host.controller = controller
        if body is None:
            result.append({"status": "state", "state": self.host.state()})
        else:
            result.append(self.host.handle(body, controller, resolve=resolve))
        complete.set()

    def call(self, controller, body, resolve=False):
        complete, result = threading.Event(), []
        self.requested.emit((controller, body, resolve, complete, result))
        if not complete.wait(4):
            return {"status": "pending"}  # Client must retry the SAME command identity.
        return result[0]


class BoundedServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, *args):
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(*args)

    def process_request(self, request, address):
        if not self.slots.acquire(False):
            self.shutdown_request(request)
            return
        request.settimeout(5)
        super().process_request(request, address)

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        pass  # Malformed LAN traffic must not print secrets or appear on the projector.


class RemoteServer:
    def __init__(self, instrument, port=8080):
        self.host = CommandHost(instrument.session, instrument.send, instrument.remote_state)
        self.bridge = GuiBridge(self.host)
        remote = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                self.respond(None)

            def do_POST(self):
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= 4096:
                        self.send_error(413)
                        return
                    body = self.rfile.read(length).decode("utf-8")
                except (ValueError, UnicodeError):
                    self.send_error(400)
                    return
                self.respond(body)

            def respond(self, body):
                if self.path not in (("/state",) if body is None else ("/command", "/resolve")):
                    self.send_error(404)
                    return
                controller = self.headers.get("X-Controller", "anonymous")
                if not 1 <= len(controller) <= 128:
                    self.send_error(400)
                    return
                data = json.dumps(
                    remote.bridge.call(controller, body, self.path == "/resolve"), ensure_ascii=False
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = BoundedServer(("0.0.0.0", port), Handler)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.discovery = None
        if port != 0:  # Ephemeral loopback unit tests do not announce a room session.
            from .discovery import Discovery

            try:
                self.discovery = Discovery(self.host.session.epoch, self.port)
            except OSError:
                pass  # Direct IP connection remains available without multicast.

    def close(self):
        if self.discovery:
            self.discovery.close()
        self.server.shutdown()
        self.server.server_close()

    def connection_url(self, address):
        return f"http://{address}:{self.port}"

    def connection_dialog(self, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle("Live Explain — połączenie przez Wi-Fi")
        layout = QVBoxLayout(dialog)
        layout.addWidget(
            QLabel(
                "Telefon i laptop muszą być w tej samej sieci.\n"
                "W aplikacji wybierz znalezioną prezentację. Bez kodu i parowania.\n"
                "Jeśli wykrywanie nie działa, wpisz poniższy adres laptopa."
            )
        )
        addresses = QComboBox()
        for interface in QNetworkInterface.allInterfaces():
            if not interface.flags() & QNetworkInterface.InterfaceFlag.IsRunning:
                continue
            if interface.type() not in (
                QNetworkInterface.InterfaceType.Wifi,
                QNetworkInterface.InterfaceType.Ethernet,
            ):
                continue
            for entry in interface.addressEntries():
                ip = entry.ip().toString()
                if ":" not in ip and not ip.startswith("127."):
                    addresses.addItem(interface.humanReadableName() + " — " + ip, ip)
        layout.addWidget(addresses)
        link = QLineEdit()
        link.setReadOnly(True)
        layout.addWidget(link)

        def refresh():
            link.setText(self.connection_url(addresses.currentData() or "127.0.0.1"))

        addresses.currentIndexChanged.connect(refresh)
        refresh()
        dialog.setModal(False)
        dialog.show()
        return dialog
