"""Headless native-client rehearsal. Writes a PRIVATE ephemeral pairing file, never stdout."""

import argparse
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from live_explain.app import Instrument
from live_explain.preflight import load_fonts
from live_explain.remote import RemoteServer

parser = argparse.ArgumentParser()
parser.add_argument("--pairing-file", type=Path, required=True)
args = parser.parse_args()
app = QApplication([])
load_fonts()
instrument = Instrument(
    app,
    SimpleNamespace(
        slice=True,
        canonical="normal",
        beat=None,
        position=0,
        recover=False,
        debug=False,
        record=None,
        replay_file=None,
    ),
)
instrument.recovery = args.pairing_file.with_suffix(".recovery.json")
server = RemoteServer(instrument, port=8766)
args.pairing_file.parent.mkdir(parents=True, exist_ok=True)
fd = os.open(args.pairing_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as out:
    out.write(server.pairing_uri("10.0.2.2"))
app.aboutToQuit.connect(server.close)
app.aboutToQuit.connect(lambda: args.pairing_file.unlink(missing_ok=True))
print("Private Android rehearsal host ready", flush=True)
app.exec()
