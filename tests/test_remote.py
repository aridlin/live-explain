"""Exercise real HTTPS plus GUI-thread dispatch, including uncertain command resolution."""

import http.client
import json
import ssl
import threading
import time
from types import SimpleNamespace

import pytest

from live_explain.remote import RemoteServer
from live_explain.protocol import CommandHost
from live_explain.geometry import Point, Route
from live_explain.presentations.spectre_scene import SpectreScene
from live_explain.app import Instrument


def envelope(session, identity="tap", kind="advance", value=None):
    return json.dumps(
        dict(epoch=session.epoch, revision=session.revision, id=identity, kind=kind, value=value)
    )


def test_resolve_unknown_reserves_cancellation_against_late_delivery(session):
    host = CommandHost(session)
    raw = envelope(session)
    receipt = host.handle(raw, host.token, resolve=True)
    assert receipt["status"] == "rejected"
    assert host.handle(raw, host.token) == receipt
    assert not session.state.playback.playing
    assert not session.recording


def test_resolve_known_returns_original_receipt(session):
    host = CommandHost(session)
    raw = envelope(session)
    receipt = host.handle(raw, host.token)
    assert host.handle(raw, host.token, resolve=True) == receipt
    assert len(session.recording) == 1


def test_full_reader_projection_contains_no_subject_secrets(session):
    state = session.controller_state()
    assert {r["id"] for r in state["routes"]} == {"simple", "normal", "deep"}
    assert state["script"]["wording"] == session.beat.script.wording
    assert state["branches"][0]["id"] in session.beat.detours
    assert "memory" not in state


def test_rounding_shared_by_token_and_path():
    route = Route("corner", (Point(0, 0), Point(100, 0), Point(100, 100)))
    assert route.at(0) == Point(0, 0) and route.at(1) == Point(100, 100)
    assert 185 < route.length < 200
    middle = route.at(0.5)
    assert 90 < middle.x < 100 and 0 < middle.y < 10


def test_fades_restore_at_interrupted_position(app, session):
    scene = SpectreScene(session)
    assert scene.link1.opacity() == 0
    session.seek(0.3)
    scene.refresh()
    opacity, point = scene.link1.opacity(), scene.token.pos()
    assert 0 < opacity < 1
    session.command("detour", "cache-location")
    scene.refresh()
    session.command("return")
    scene.refresh()
    assert scene.link1.opacity() == opacity and scene.token.pos() == point


def test_remote_dispatch_controls_composition_and_blank(app, tmp_path):
    args = SimpleNamespace(
        slice=True,
        canonical="normal",
        beat=None,
        position=0,
        recover=False,
        debug=False,
        record=None,
        replay_file=None,
    )
    instrument = Instrument(app, args)
    instrument.timer.stop()
    instrument.recovery = tmp_path / "recovery.json"
    host = CommandHost(instrument.session, instrument.send, instrument.remote_state)
    try:
        response = host.handle(envelope(instrument.session, "detour", "detour", "cache-location"), host.token)
        assert response["status"] == "accepted" and response["state"]["transitioning"]
        assert host.handle(envelope(instrument.session, "pause", "pause"), host.token)["status"] == "accepted"
        assert instrument.scene.transition.paused
        assert (
            host.handle(envelope(instrument.session, "finish", "finish"), host.token)["status"] == "accepted"
        )
        assert not instrument.scene.transition.active
        raw = envelope(instrument.session, "blank", "blank", "on")
        first = host.handle(raw, host.token)
        assert first["state"]["blank"]
        assert host.handle(raw, host.token) == first
        assert instrument.scene.blank
    finally:
        instrument.audience.close()
        instrument.presenter.close()


def test_https_authentication_resolution_and_gui_ownership(app, session):
    gui_thread = threading.get_ident()

    def dispatch(kind, value):
        assert threading.get_ident() == gui_thread
        return session.command(kind, value)

    instrument = SimpleNamespace(session=session, send=dispatch, remote_state=session.controller_state)
    try:
        server = RemoteServer(instrument, port=0)
    except PermissionError:
        pytest.skip("Sandbox disallows loopback sockets; run this test outside the sandbox")
    results, errors = [], []
    raw = envelope(session)

    def client():
        # Test client deliberately uses a private context, then checks the actual certificate pin.
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        def request(path, body=None, token=None):
            import hashlib

            c = http.client.HTTPSConnection("127.0.0.1", server.port, context=context, timeout=5)
            c.connect()
            assert hashlib.sha256(c.sock.getpeercert(binary_form=True)).hexdigest() == server.fingerprint
            headers = {
                "Authorization": "Bearer " + (token or server.host.token),
                "X-Controller": "test-phone",
            }
            c.request("GET" if body is None else "POST", path, body, headers)
            response = c.getresponse()
            status, data = response.status, response.read()
            c.close()
            return status, json.loads(data) if status == 200 else None

        try:
            results.append(request("/state", token="bad")[0])
            results.append(request("/state")[1])
            results.append(request("/command", raw)[1])
            results.append(request("/resolve", raw)[1])
            results.append(request("/state")[1])
        except Exception as error:
            errors.append(error)

    worker = threading.Thread(target=client)
    worker.start()
    deadline = time.monotonic() + 15
    while worker.is_alive() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    worker.join(timeout=0.1)
    server.close()
    assert not worker.is_alive() and not errors
    assert results[0] == 401
    assert results[1]["state"]["script"]["wording"]
    assert results[2] == results[3]
    assert results[4]["state"]["playing"]
    assert len(session.recording) == 1


def test_discovery_exposes_only_locator_and_public_pin():
    from live_explain.discovery import advertisement

    info = advertisement("session-id", "a" * 64, 8765, ["192.168.1.4"])
    assert info.port == 8765
    assert info.parsed_addresses() == ["192.168.1.4"]
    assert set(info.properties) == {b"pin", b"version"}
    assert b"token" not in info.properties


def test_discovery_publication_and_shutdown_run_off_gui_thread(app, monkeypatch):
    import live_explain.discovery as discovery

    calls = []
    main_thread = threading.get_ident()

    class FakeZeroconf:
        def __init__(self, **kwargs):
            pass

        def register_service(self, info):
            calls.append(("register", threading.get_ident()))

        def unregister_service(self, info):
            calls.append(("unregister", threading.get_ident()))

        def close(self):
            calls.append(("close", threading.get_ident()))

    monkeypatch.setattr(discovery, "Zeroconf", FakeZeroconf)
    monkeypatch.setattr(discovery.QNetworkInterface, "allInterfaces", lambda: [])
    instance = discovery.Discovery("session", "a" * 64, 8765)
    instance.worker.submit(instance.publish, ("192.168.1.4",)).result(timeout=2)
    instance.close()
    assert [kind for kind, _ in calls] == ["register", "unregister", "close"]
    assert all(thread != main_thread for kind, thread in calls if kind != "close")
