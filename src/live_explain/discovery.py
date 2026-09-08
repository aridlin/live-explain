"""Public mDNS locator. Never publishes the private pairing token or script."""

import socket
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QTimer
from PySide6.QtNetwork import QNetworkInterface
from zeroconf import IPVersion, ServiceInfo, Zeroconf

SERVICE_TYPE = "_liveexplain._tcp.local."


def advertisement(epoch, pin, port, addresses):
    return ServiceInfo(
        SERVICE_TYPE,
        f"Live Explain {epoch[:6]}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(ip) for ip in addresses],
        port=port,
        properties={"version": "1", "pin": pin},
        server=f"live-explain-{epoch[:8]}.local.",
    )


class Discovery:
    def __init__(self, epoch, pin, port):
        self.epoch, self.pin, self.port = epoch, pin, port
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.info = None
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="live-discovery")
        self.addresses = ()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)
        self.refresh()

    def refresh(self):
        addresses = tuple(
            sorted(
                {
                    entry.ip().toString()
                    for interface in QNetworkInterface.allInterfaces()
                    if interface.type()
                    in (QNetworkInterface.InterfaceType.Wifi, QNetworkInterface.InterfaceType.Ethernet)
                    for entry in interface.addressEntries()
                    if ":" not in entry.ip().toString() and not entry.ip().toString().startswith("127.")
                }
            )
        )
        if addresses == self.addresses:
            return
        self.addresses = addresses
        self.worker.submit(self.publish, addresses)

    def publish(self, addresses):
        if self.info is not None:
            self.zeroconf.unregister_service(self.info)
            self.info = None
        if addresses:
            self.info = advertisement(self.epoch, self.pin, self.port, addresses)
            self.zeroconf.register_service(self.info)

    def close(self):
        self.timer.stop()
        self.worker.submit(self.publish, ())
        self.worker.shutdown(wait=True)
        self.zeroconf.close()
