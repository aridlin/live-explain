import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase


@pytest.fixture(scope="session")
def app():
    application = QApplication.instance() or QApplication([])
    import live_explain

    for file in (Path(live_explain.__file__).parent / "assets/fonts").glob("*.ttf"):
        assert QFontDatabase.addApplicationFont(str(file)) >= 0
    return application


@pytest.fixture
def session():
    from live_explain.runtime import Session
    from live_explain.presentations.spectre import build

    return Session(build())
