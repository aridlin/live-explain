from math import hypot
import pytest
from PySide6.QtCore import QPointF
from PySide6.QtGui import QFontMetricsF
from live_explain.components import font
from live_explain.geometry import Point, Box, Route
from live_explain.presentations.spectre_scene import SpectreScene
from live_explain.app import capture, Audience, Presenter


def test_exact_return_pixels(app, session, tmp_path):
    scene = SpectreScene(session)
    session.seek(1.68)
    scene.refresh()
    original = capture(scene, tmp_path / "a.png")
    ids = {key: id(item) for key, item in scene.items_by_id.items()}
    session.command("detour", "cache-location")
    scene.refresh()
    session.command("step")
    scene.refresh()
    session.command("return")
    scene.refresh()
    restored = capture(scene, tmp_path / "b.png")
    assert original == restored
    assert ids == {key: id(item) for key, item in scene.items_by_id.items()}


def test_moving_resizing_endpoint_token_continuity(app, session):
    scene = SpectreScene(session)
    previous = None
    widths = []
    for i in range(1, 400):
        session.seek(i / 100)
        scene.refresh()
        reg = scene.register.box
        widths.append(reg.w)
        assert scene.link1.route.points[-1] == reg.port("left")
        assert scene.link2.route.points[0] == reg.port("right")
        for link in (scene.link1, scene.link2):
            link.route.validate()
        # Memory connector uses inter-row clearance, never runs through another byte.
        scene.link2.route.validate([scene.memory.byte_box(i) for i in range(32) if i != 12])
        current = scene.token.pos()
        if previous is not None:
            assert hypot(current.x() - previous.x(), current.y() - previous.y()) < 12
        previous = QPointF(current)
        assert QFontMetricsF(font(26)).horizontalAdvance(scene.register.body) < reg.w - 48
    assert max(widths) - min(widths) > 40


def test_polish_titles_and_code_fit(app, session):
    scene = SpectreScene(session)
    for beat in session.presentation.beats.values():
        session._entry(beat.id)
        scene.refresh()
        assert QFontMetricsF(font(48, bold=True)).horizontalAdvance(beat.title) < 1472
        assert QFontMetricsF(font(25)).horizontalAdvance(beat.subtitle) < 1472
        for line in beat.code:
            assert QFontMetricsF(font(22, True)).horizontalAdvance(line) < scene.code.box.w - 86


def test_code_span_anchor_and_clipping(app, session):
    scene = SpectreScene(session)
    port = scene.code.span_port("index")
    assert scene.code.box.contains(port)
    assert scene.link1.route.points[0] == port
    with pytest.raises(ValueError):
        scene.memory.byte_port(40)


def test_route_failure_visible():
    with pytest.raises(ValueError):
        Route("cross", (Point(0, 5), Point(20, 5))).validate([Box(5, 0, 10, 10)])


@pytest.mark.parametrize("size", [(1920, 1080), (1280, 720), (1024, 768)])
def test_capture_variants(app, session, tmp_path, size):
    scene = SpectreScene(session)
    image = capture(scene, tmp_path / f"{size[0]}.png", *size)
    assert (image.width(), image.height()) == size
    assert not image.isNull()


def test_blank_contains_no_audience_items(app, session, tmp_path):
    scene = SpectreScene(session)
    scene.blank = True
    scene.refresh()
    image = capture(scene, tmp_path / "blank.png")
    assert all(not item.isVisible() for item in scene.items_by_id.values())
    assert image.pixelColor(100, 100) == image.pixelColor(800, 450)


def test_private_two_windows_and_script_sync(app, session):
    scene = SpectreScene(session)
    audience = Audience(scene)
    presenter = Presenter(session, session.command, audience)
    audience.show()
    presenter.show()
    app.processEvents()
    assert audience.isVisible() and presenter.isVisible()
    session.command("detour", "cache-location")
    presenter.refresh()
    assert session.beat.script.cue in presenter.cue.text()
    assert "normal.timing" in presenter.return_label.text()
    assert "PRYWATNY" not in session.beat.title
    audience.close()
    presenter.close()


def test_centrally_clocked_transition():
    from live_explain.visual import Transition

    transition = Transition()
    transition.tick(0.1)
    opacity = transition.opacity
    transition.paused = True
    transition.tick(0.1)
    assert transition.opacity == opacity
    transition.paused = False
    transition.tick(0.05)
    assert transition.opacity < opacity
    transition.finish()
    assert not transition.active


def test_font_preflight(app, tmp_path):
    from live_explain.preflight import load_fonts

    assert "DejaVuSans.ttf" in load_fonts()
    (tmp_path / "manifest.json").write_text('{"missing.ttf":"invalid"}')
    with pytest.raises(FileNotFoundError):
        load_fonts(tmp_path)


def test_stress_inventory(app):
    from live_explain.benchmark import StressScene

    scene = StressScene()
    assert len(scene.code.lines) == 30
    assert len(scene.memory.values) == 128
    assert len(scene.links) == 40
    assert len(scene.tokens) == 24
    scene.frame(0.3)
    scene.memory.byte_port(127)


def test_actual_view_draws_scene_heading(app, session):
    from PySide6.QtCore import QRectF

    scene = SpectreScene(session)
    view = Audience(scene)
    view.show()
    app.processEvents()
    region = view.mapFromScene(QRectF(64, 98, 1472, 76)).boundingRect()
    image = view.viewport().grab(region).toImage()
    dark = 0
    for y in range(image.height()):
        for x in range(image.width()):
            c = image.pixelColor(x, y)
            dark += c.red() < 90 and c.green() < 120 and c.blue() < 150
    assert dark > 200
    view.close()


@pytest.mark.parametrize(
    "beat,position,name",
    [
        ("normal.timing", 1.68, "normal-mid.png"),
        ("shared.location", 3, "cache-location.png"),
        ("normal.branch", 6, "branch-discarded.png"),
    ],
)
def test_reviewed_visual_baseline(app, session, tmp_path, beat, position, name):
    from pathlib import Path
    from PySide6.QtGui import QImage

    session._entry(beat)
    session.seek(position)
    scene = SpectreScene(session)
    actual = capture(scene, tmp_path / name)
    expected = QImage(str(Path(__file__).parent / "golden" / name)).convertToFormat(actual.format())
    assert not expected.isNull() and expected.size() == actual.size()
    a = memoryview(actual.constBits()).cast("I")
    b = memoryview(expected.constBits()).cast("I")
    changed = sum(x != y for x, y in zip(a, b))
    # Small platform raster differences are allowed; geometry assertions remain strict.
    assert changed / len(a) < 0.005, f"{changed / len(a):.2%} pixels differ; review before updating baseline"
