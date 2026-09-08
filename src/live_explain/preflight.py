"""Offline font inventory and glyph checks, before opening audience output."""

from hashlib import sha256
import json
from pathlib import Path
from PySide6.QtGui import QFontDatabase, QFontMetricsF
from .components import font


def load_fonts(directory=None):
    directory = Path(directory) if directory else Path(__file__).parent / "assets/fonts"
    manifest = json.loads((directory / "manifest.json").read_text())
    for name, expected in manifest.items():
        if Path(name).name != name:
            raise ValueError("Invalid font manifest filename")
        path = directory / name
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Font asset changed: {name}")
        if name.endswith(".ttf") and QFontDatabase.addApplicationFont(str(path)) < 0:
            raise ValueError(f"Cannot load font: {name}")
    for mono in (False, True):
        metrics = QFontMetricsF(font(24, mono))
        for character in "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ→≠×":
            if not metrics.inFontUcs4(ord(character)):
                raise ValueError(f"Missing glyph: {character}")
    return tuple(manifest)
