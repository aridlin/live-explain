import json
import pytest
from live_explain.protocol import CommandHost


def envelope(s, id="c42", kind="advance", value=None):
    return dict(epoch=s.epoch, id=id, revision=s.revision, kind=kind, value=value)


def test_lost_ack_retry_never_advances_twice(session):
    host = CommandHost(session)
    raw = json.dumps(envelope(session))
    first = host.handle(raw)
    session.tick(0.3)
    position = session.state.playback.position
    second = host.handle(raw)
    assert first == second
    assert session.state.playback.position == position
    assert len(session.recording) == 1


def test_stale_new_command_is_not_rebased(session):
    host = CommandHost(session)
    a = envelope(session)
    host.handle(json.dumps(a))
    a["id"] = "c43"
    assert host.handle(json.dumps(a))["status"] == "rejected"


def test_new_epoch_rejects_old_command(session, tmp_path):
    host = CommandHost(session)
    raw = json.dumps(envelope(session))
    session.save(tmp_path / "save")
    session.recover(tmp_path / "save")
    assert host.handle(raw)["status"] == "wrong_epoch"


def test_id_reuse_different_payload_rejected(session):
    host = CommandHost(session)
    a = envelope(session)
    host.handle(json.dumps(a))
    a["kind"] = "pause"
    assert host.handle(json.dumps(a))["status"] == "id_conflict"


@pytest.mark.parametrize(
    "raw",
    [
        "null",
        "[]",
        "{",
        "x" * 4097,
        json.dumps({"kind": "eval"}),
        json.dumps({"epoch": "x", "id": [], "revision": 0, "kind": "advance", "value": None}),
    ],
)
def test_malformed_rejected(session, raw):
    host = CommandHost(session)
    assert host.handle(raw)["status"] == "invalid"


def test_multiple_controllers_need_no_enrollment(session):
    host = CommandHost(session)
    raw = json.dumps(envelope(session))
    assert host.handle(raw, "first")["status"] == "accepted"
    second = json.dumps(envelope(session, kind="pause"))
    assert host.handle(second, "second")["status"] == "accepted"
    assert not session.state.playback.playing
    assert host.handle(raw, "first")["status"] == "accepted"
    assert len(session.recording) == 2
    assert host.handle(raw, "")["status"] == "invalid"


def test_reconnect_sync_has_no_side_effect(session):
    host = CommandHost(session)
    host.handle(json.dumps(envelope(session)))
    session.tick(0.3)
    state = session.digest()
    assert host.synchronize()["position"] == 0.3
    assert session.digest() == state
