"""Real HTTP, Qt-frame privacy and WAN command/retry boundaries."""

import http.client
import importlib.util
import json
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import uuid

from PySide6.QtGui import QImage
import pytest

from live_explain.web import WebInstrument, WebServer


@pytest.fixture
def web(app, tmp_path):
    instrument = WebInstrument(
        app, SimpleNamespace(presentation="recruitment", canonical="normal", state_dir=tmp_path)
    )
    instrument.timer.stop()
    try:
        server = WebServer(instrument, port=0, origin="https://prol.aridlin.pl")
    except PermissionError:
        pytest.skip("Loopback sockets require an unsandboxed test run")
    yield instrument, server
    server.close()


def request(app, web, path, body=None, headers=None):
    _, server = web
    result, errors = [], []

    def run():
        try:
            client = http.client.HTTPConnection("127.0.0.1", server.port, timeout=5)
            client.request("GET" if body is None else "POST", path, body, headers or {})
            response = client.getresponse()
            result.append((response.status, dict(response.getheaders()), response.read()))
            client.close()
        except Exception as error:
            errors.append(error)

    thread = threading.Thread(target=run)
    thread.start()
    deadline = time.monotonic() + 8
    while thread.is_alive() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.003)
    thread.join(timeout=0.1)
    assert not thread.is_alive() and not errors
    return result[0]


def command(app, web, kind, value=None, raw=None):
    session = web[0].session
    raw = raw or json.dumps(
        dict(epoch=session.epoch, revision=session.revision, id=uuid.uuid4().hex, kind=kind, value=value)
    )
    response = request(
        app, web, "/command", raw, {"Content-Type": "application/json", "Origin": "https://prol.aridlin.pl"}
    )
    return json.loads(response[2]), raw


def test_audience_view_and_frame_do_not_include_private_script(app, web):
    status, headers, html = request(app, web, "/")
    assert status == 200
    assert b"presenter.js" not in html and b"/state" not in html
    assert web[0].session.beat.script.wording.encode() not in html
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    status, headers, frame = request(app, web, "/frame.jpg")
    assert status == 200 and headers["Content-Type"] == "image/jpeg"
    assert not QImage.fromData(frame).isNull()
    etag = headers["ETag"]
    assert request(app, web, "/frame.jpg", headers={"If-None-Match": etag})[0] == 304
    assert request(app, web, "/presenter/")[0] == 200
    assert request(app, web, "/../PRIVATE-presenter-script.txt")[0] == 404


def test_web_reader_commands_retries_reconnect_and_blank(app, web):
    instrument, _ = web
    state = json.loads(request(app, web, "/state")[2])["state"]
    assert state["script"]["wording"] and len(state["routes"]) == 3
    first, raw = command(app, web, "advance")
    again, _ = command(app, web, "advance", raw=raw)
    assert first == again and len(instrument.session.recording) == 1
    command(app, web, "pause")
    assert not instrument.session.state.playback.playing
    result, _ = command(app, web, "depth", "deep")
    assert result["state"]["beat"] == "deep.about"
    instrument.scene.transition.finish()
    instrument.session._entry("deep.ft")
    instrument.render_frame()
    result, _ = command(app, web, "detour", "ft-detail")
    assert result["state"]["return_to"] == "deep.ft"
    instrument.scene.transition.finish()
    result, _ = command(app, web, "return")
    assert result["state"]["beat"] == "deep.ft"
    instrument.scene.transition.finish()
    before = instrument.frame
    result, _ = command(app, web, "blank", "on")
    assert result["state"]["blank"] and instrument.frame != before
    assert Path(instrument.recovery).exists()


def test_rejects_cross_origin_and_form_posts_before_commands(app, web):
    session = web[0].session
    raw = json.dumps(dict(epoch=session.epoch, revision=0, id="csrf", kind="advance", value=None))
    assert (
        request(
            app,
            web,
            "/command",
            raw,
            {"Content-Type": "application/json", "Origin": "https://untrusted.example"},
        )[0]
        == 403
    )
    assert request(app, web, "/command", raw, {"Content-Type": "text/plain"})[0] == 415
    assert not session.recording


def test_portal_edits_preserve_auth_existing_routes_and_index_links():
    spec = importlib.util.spec_from_file_location("portal", Path(__file__).parents[1] / "deploy/portal.py")
    portal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(portal)
    caddy_patch, index_patch = portal.caddy_patch, portal.index_patch

    original = '(media_auth) {\n basic_auth { user hash }\n}\nhttps://prol.aridlin.pl {\n handle /other/* { respond "other" }\n}\n'
    updated = caddy_patch(original)
    assert caddy_patch(updated) == updated
    assert 'handle /other/* { respond "other" }' in updated
    assert "handle_path /live-explain/* {\n        import media_auth" in updated
    with pytest.raises(ValueError):
        caddy_patch("https://prol.aridlin.pl {\n}\n")
    index = '<nav><a class="tool" href="/plan/">Plan</a><a href="/other/">Other</a></nav>'
    changed = index_patch(index)
    assert index_patch(changed) == changed
    assert changed.count('<a class="tool" href="/plan/">Plan</a>') == 1
    assert changed.count('<a href="/other/">Other</a>') == 1
    assert 'class="tool" href="/live-explain/"' in changed
    assert 'href="/live-explain/presenter/"' in changed
    with pytest.raises(ValueError):
        index_patch('<main id="portal-app"></main>')


def test_reset_during_transition_unblanks_and_duplicate_is_not_reapplied(app, web):
    instrument, _ = web
    instrument.session._entry("normal.ft")
    command(app, web, "detour", "ft-detail")
    command(app, web, "blank", "on")
    result, raw = command(app, web, "reset")
    assert result["status"] == "accepted"
    assert result["state"]["beat"] == "normal.about"
    assert not result["state"]["blank"] and not result["state"]["transitioning"]
    assert not result["state"]["can_undo"] and not result["state"]["return_to"]
    command(app, web, "advance")
    position = instrument.session.state.playback.position
    again, _ = command(app, web, "reset", raw=raw)
    assert again == result
    assert instrument.session.state.playback.playing
    assert instrument.session.state.playback.position == position
