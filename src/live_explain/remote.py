"""Local HTTPS controller. Only the GUI thread touches the authoritative instrument."""

from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
from pathlib import Path
import ssl
import tempfile
import threading
from urllib.parse import urlencode

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtNetwork import QNetworkInterface
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit
import qrcode

from .protocol import CommandHost


class GuiBridge(QObject):
    requested = Signal(object)

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.requested.connect(self.execute, Qt.ConnectionType.QueuedConnection)

    def execute(self, request):
        controller, body, resolve, complete, result = request
        if self.host.controller not in (None, controller):
            result.append({"status": "unauthorized"})
        else:
            self.host.controller = controller
            if body is None:
                result.append({"status": "state", "state": self.host.state()})
            else:
                result.append(self.host.handle(body, self.host.token, controller, resolve=resolve))
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
    def __init__(self, instrument, port=8765):
        self.host = CommandHost(instrument.session, instrument.send, instrument.remote_state)
        self.bridge = GuiBridge(self.host)
        key = ec.generate_private_key(ec.SECP256R1())
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Live Explain session")])
        now = datetime.now(timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=30))
            .sign(key, hashes.SHA256())
        )
        self.fingerprint = certificate.fingerprint(hashes.SHA256()).hex()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        with tempfile.TemporaryDirectory(prefix="live-explain-tls-") as directory:
            certfile, keyfile = Path(directory) / "cert", Path(directory) / "key"
            certfile.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
            keyfile.write_bytes(
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
            keyfile.chmod(0o600)
            context.load_cert_chain(certfile, keyfile)
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
                token = self.headers.get("Authorization", "")
                controller = self.headers.get("X-Controller", "")
                if (
                    not hmac.compare_digest(token, "Bearer " + remote.host.token)
                    or not 1 <= len(controller) <= 128
                ):
                    self.send_error(401)
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
        self.server.socket = context.wrap_socket(
            self.server.socket, server_side=True, do_handshake_on_connect=False
        )
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.discovery = None
        if port != 0:  # Ephemeral loopback unit tests do not announce a room session.
            from .discovery import Discovery

            try:
                self.discovery = Discovery(self.host.session.epoch, self.fingerprint, self.port)
            except OSError:
                pass  # QR/direct connection remains available without multicast.

    def close(self):
        if self.discovery:
            self.discovery.close()
        self.server.shutdown()
        self.server.server_close()

    def pairing_uri(self, address):
        return "liveexplain://pair?" + urlencode(
            dict(host=address, port=self.port, pin=self.fingerprint, token=self.host.token)
        )

    def pairing_dialog(self, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle("Prywatne parowanie telefonu — przed prezentacją")
        layout = QVBoxLayout(dialog)
        title = QLabel(
            "Włącz hotspot telefonu i połącz z nim laptop.\n"
            "Wybierz adres Wi-Fi laptopa. W aplikacji Android zeskanuj kod.\n"
            "Kod daje dostęp do skryptu i sterowania — nie wyświetlaj go publicznie."
        )
        layout.addWidget(title)
        addresses = QComboBox()
        for interface in QNetworkInterface.allInterfaces():
            for entry in interface.addressEntries():
                ip = entry.ip().toString()
                if ":" not in ip and not ip.startswith("127."):
                    addresses.addItem(interface.humanReadableName() + " — " + ip, ip)
        layout.addWidget(addresses)
        qr, link = QLabel(), QLineEdit()
        link.setReadOnly(True)
        layout.addWidget(qr)
        layout.addWidget(link)

        def refresh():
            from io import BytesIO

            uri = self.pairing_uri(addresses.currentData() or "127.0.0.1")
            link.setText(uri)
            buffer = BytesIO()
            qrcode.make(uri, box_size=5, border=3).save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            qr.setPixmap(pixmap)

        addresses.currentIndexChanged.connect(refresh)
        refresh()
        dialog.setModal(False)
        dialog.winId()
        if parent.windowHandle():
            dialog.windowHandle().setScreen(parent.windowHandle().screen())
        dialog.show()
        return dialog
