from copy import deepcopy
from dataclasses import replace
import json
import math
import pytest
from live_explain.runtime import Session
from live_explain.presentations.spectre import build, audience_model


def finish_beat(s):
    while s.state.playback.position < s.beat.holds[-1]:
        assert s.command("step")[0]


def test_three_distinct_routes():
    p = build()
    assert len({p.routes[k][0] for k in p.routes}) == 3
    assert p.beats["simple.timing"].script != p.beats["normal.timing"].script
    assert p.beats["deep.lines"].composition != p.beats["normal.timing"].composition


def test_exact_return_including_domain_and_pending_playback(session):
    session.command("advance")
    for _ in range(4):
        session.tick(0.42)
    before = session.snapshot()
    model = session.model
    session.command("detour", "cache-location")
    finish_beat(session)
    assert session.command("return")[0]
    assert session.state.playback.position == before.playback.position
    assert session.state.playback.target == before.playback.target
    assert not session.state.playback.playing
    assert session.model == model
    assert "location" in session.delivered
    assert session.elapsed == 1.68


def test_deep_bridge_does_not_transplant_model(session):
    session.seek(1.68)
    session.command("detour", "cache-location")
    assert session.command("depth", "deep")[0]
    assert session.beat.id == "shared.bridge"
    assert session.state.narrative.canonical == "normal"
    finish_beat(session)
    assert session.command("advance")[0]
    assert session.beat.id == "deep.probe"
    assert session.state.narrative.canonical == "deep"
    assert not session.state.detours
    assert session.state.playback.position == 0
    assert not session.model["issued"]


def test_bridge_not_required_after_real_coverage(session):
    session.command("depth", "deep")
    finish_beat(session)
    session.command("advance")
    session.command("depth", "normal")
    session.command("depth", "deep")
    assert session.beat.id == "deep.probe"


def test_seek_does_not_assert_exposure(session):
    session.seek(6)
    assert not session.delivered
    assert session.landing_gaps("deep")


def test_nested_return_and_bound(session):
    session.seek(1.4)
    session.command("detour", "cache-location")
    session.seek(2.4)
    session.command("detour", "cache-lines")
    assert not session.command("detour", "cache-location")[0]
    assert len(session.state.detours) == 2
    session.command("return")
    assert session.beat.id == "shared.location"
    assert session.state.playback.position == 2.4
    session.command("return")
    assert session.beat.id == "normal.timing"
    assert session.state.playback.position == 1.4


def test_undo_navigation_not_time_or_connection(session):
    session.tick(0.25)
    epoch = session.epoch
    session.command("detour", "cache-location")
    session.tick(0.25)
    session.command("undo")
    assert session.beat.id == "normal.timing"
    assert session.elapsed == 0.5
    assert session.epoch == epoch


def test_double_advance_and_stale_revision(session):
    revision = session.revision
    assert session.command("advance", expected_revision=revision)[0]
    assert not session.command("advance", expected_revision=revision)[0]
    assert not session.command("advance")[0]
    for _ in range(5):
        session.tick(0.4)
    assert session.state.playback.position == 2
    assert not session.state.playback.playing


def test_old_generation_cannot_advance_detour(session):
    session.command("advance")
    generation = session.generation
    session.command("detour", "cache-location")
    session.tick(0.2, generation=generation)
    assert session.state.playback.position == 0


def test_stall_pauses_instead_of_catchup(session):
    session.command("advance")
    session.tick(5)
    assert session.state.playback.position == 0
    assert not session.state.playback.playing


@pytest.mark.parametrize("position", [0, 0.099, 0.1, 1.68, 2, 3.999, 4, 4.1, 6])
def test_seek_matches_event_evaluation(session, position):
    session.seek(position)
    expected = session.model
    session.seek(6)
    session.seek(0)
    session.seek(position)
    assert session.model == expected
    assert len(session.model["events"]) == len(set(session.model["events"]))


@pytest.mark.parametrize("position", [-1, 7, math.nan, math.inf, "oops"])
def test_bad_seek(session, position):
    with pytest.raises(ValueError):
        session.seek(position)


def test_discard_retains_cache_without_committed_result(session):
    session._entry("normal.branch")
    session.seek(6)
    assert session.model["discarded"]
    assert session.model["cached"]
    assert session.model["result"] is None


def test_disclosure_all_views(session):
    session._entry("normal.branch")
    session.seek(6)
    private = session.model
    public = audience_model(private, True)
    assert private["memory"][12] == 163
    assert public["memory"][12] is None
    assert public["probe"] is None and public["result"] is None
    session.seek(8)
    assert audience_model(session.model, True)["memory"][12] == 163


def test_safe_recovery_and_reject_changed_content(session, tmp_path):
    file = tmp_path / "recovery.json"
    session.save(file)
    old = session.epoch
    session.command("detour", "cache-location")
    session.recover(file)
    assert session.beat.id == "normal.timing"
    assert session.epoch != old
    assert not session.state.playback.playing
    value = json.loads(file.read_text())
    value["content"] = "wrong"
    file.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        session.recover(file)


def test_missing_destination_and_span_fail_validation():
    p = build()
    p.routes["normal"] = ("missing",)
    with pytest.raises(ValueError):
        p.validate()
    p = build()
    p.beats["normal.timing"] = replace(p.beats["normal.timing"], spans={"bad": (1, "absent")})
    with pytest.raises(ValueError):
        p.validate()


def test_unreachable_beat_fails():
    p = build()
    p.beats["orphan"] = replace(p.beats["normal.timing"], id="orphan")
    with pytest.raises(ValueError):
        p.validate()


def test_invalid_commands_do_not_mutate(session):
    original = deepcopy(session.state)
    for kind, value in [("detour", "missing"), ("depth", "missing"), ("return", None), ("exec", "print(1)")]:
        assert not session.command(kind, value)[0]
        assert session.state == original


def test_rehearsal_replay(session):
    session.command("advance")
    session.tick(0.4)
    session.command("pause")
    session.command("detour", "cache-location")
    session.command("step")
    session.command("return")
    clone = Session(build())
    clone.replay_recording(session.export_recording())
    assert clone.digest() == session.digest()


def test_controller_explains_hold_interruption_and_end(session):
    state = session.controller_state()
    assert state["playback_phase"] == "hold"
    assert state["stage_index"] == 0
    session.command("advance")
    session.tick(0.3)
    assert session.controller_state()["playback_phase"] == "running"
    session.command("pause")
    assert session.controller_state()["playback_phase"] == "paused"
    session.command("detour", "cache-location")
    assert session.controller_state()["return_title"] == session.presentation.beats["normal.timing"].title
    session.seek(session.beat.holds[-1])
    assert session.controller_state()["playback_phase"] == "beat_end"
    assert session.controller_state()["next_kind"] == "return"
    session.command("return")
    assert session.controller_state()["playback_phase"] == "paused"
    session._entry(session.presentation.routes["normal"][-1])
    session.seek(session.beat.holds[-1])
    assert session.controller_state()["playback_phase"] == "finished"
