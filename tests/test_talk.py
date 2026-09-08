"""Full-route pedagogical contracts, corresponding landings and hidden-value boundaries."""

from copy import deepcopy
import pytest
from live_explain.presentations.talk import build
from live_explain.presentations.talk_text import CHAPTERS
from live_explain.runtime import Session


@pytest.mark.parametrize("canonical", ["simple", "normal", "deep"])
def test_complete_authored_route_can_be_delivered(canonical):
    presentation = build()
    session = Session(presentation, canonical)
    assert len(presentation.routes[canonical]) == 16
    assert (
        900 <= sum(presentation.beats[key].planned_seconds for key in presentation.routes[canonical]) <= 1080
    )
    for index, key in enumerate(presentation.routes[canonical]):
        assert session.beat.id == key
        assert len(session.beat.script.wording.split()) >= 80
        while session.state.playback.position < session.beat.holds[-1]:
            assert session.command("step")[0]
        if index < 15:
            assert session.command("advance")[0]
    assert {"spectre", "meltdown", "distinction", "mitigation"} <= session.delivered


def test_three_authored_scripts_and_corresponding_chapters():
    presentation = build()
    for chapter in CHAPTERS:
        variants = [presentation.beats[f"{route}.{chapter.id}"] for route in presentation.routes]
        assert len({beat.script.wording for beat in variants}) == 3
        assert {beat.checkpoint for beat in variants} == {chapter.id}
        for route, landing in presentation.checkpoint_landings[chapter.id].items():
            assert landing.beat == f"{route}.{chapter.id}"


def test_question_keeps_checkpoint_and_returns_precisely():
    session = Session(build())
    session._entry("normal.timing")
    session.seek(1.37)
    before = deepcopy(session.state.playback)
    assert session.command("detour", "cache-location")[0]
    assert session.landing_for("deep").beat == "deep.timing"
    assert session.command("return")[0]
    assert session.state.playback == before
    assert session.beat.id == "normal.timing"


def test_bridge_remembers_destination_after_leaving_origin_checkpoint():
    session = Session(build())
    session._entry("normal.spectre")
    session.seek(1.1)
    assert session.command("detour", "cache-location")[0]
    assert session.command("depth", "deep")[0]
    assert session.beat.id == "bridge.transient"
    assert session.state.narrative.bridge_target == "deep:deep.spectre"
    while session.state.playback.position < session.beat.holds[-1]:
        session.command("step")
    assert session.command("advance")[0]
    assert session.beat.id == "deep.spectre"
    assert not session.state.detours and session.state.playback.position == 0


def test_public_example_differs_from_victim_secret_and_encoder():
    session = Session(build())
    session._entry("normal.bytes")
    assert session.model["index"] == 4 and session.model["memory"][4] == 7
    session._entry("normal.channel")
    session.seek(2)
    assert session.model["probe"] == 1
    session._entry("normal.spectre")
    session.seek(8)
    assert session.model["index"] == 12 and session.model["probe"] == 2
    assert not session.model["revealed"]
    session._entry("normal.decode")
    session.seek(2)
    assert session.model["measurements"] == [9, 9, 2, 9]
    assert not session.model["revealed"]
    session.seek(4)
    assert session.model["revealed"]


def test_meltdown_has_fault_and_no_mispredicted_if():
    session = Session(build())
    session._entry("normal.meltdown")
    session.seek(6)
    assert session.model["fault"] and session.model["discarded"]
    assert not session.model["predicted"]
    assert not any("if (" in line for line in session.beat.code)


def test_all_authored_compositions_fit_polish_type_and_render(app, tmp_path):
    from PySide6.QtGui import QFontMetricsF
    from live_explain.app import capture
    from live_explain.components import Card, CodePane, font, shaped_text
    from live_explain.presentations.spectre_scene import SpectreScene

    session = Session(build())
    scene = SpectreScene(session)
    for beat in session.presentation.beats.values():
        session._entry(beat.id)
        for hold in beat.holds:
            session.seek(hold)
            scene.refresh()
            assert QFontMetricsF(font(48, bold=True)).horizontalAdvance(beat.title) <= 1472, beat.id
            assert QFontMetricsF(font(25)).horizontalAdvance(beat.subtitle) <= 1472, beat.id
            for item in scene.items_by_id.values():
                if not item.isVisible() or not isinstance(item, Card):
                    continue
                label = (beat.id, hold, item.identity)
                assert QFontMetricsF(font(18, bold=True)).horizontalAdvance(item.title) <= item.box.w - 76, (
                    label
                )
                if item.body:
                    size = shaped_text(item.body, item.box.w - 48, 26, False, False, True, 1, 1).size()
                    assert size.height() <= item.box.h - 76, label
                if isinstance(item, CodePane):
                    for line in item.lines:
                        assert QFontMetricsF(font(22, True)).horizontalAdvance(line) <= item.box.w - 86, label
        assert not capture(scene, tmp_path / (beat.id + ".png"), 1280, 720).isNull()


def test_full_talk_secret_stays_hidden_in_every_audience_memory_view(app):
    from live_explain.presentations.spectre_scene import SpectreScene

    session = Session(build())
    scene = SpectreScene(session)
    for beat in session.presentation.beats.values():
        session._entry(beat.id)
        for hold in beat.holds:
            session.seek(hold)
            scene.refresh()
            if scene.memory.isVisible() and not session.model["revealed"]:
                assert scene.memory.values[12] is None, (beat.id, hold)
            if beat.checkpoint == "spectre":
                assert scene.value_token.label == "··", (beat.id, hold)


def test_interrupted_full_talk_restores_pixels_and_authored_return_script(app, tmp_path):
    from live_explain.app import capture
    from live_explain.presentations.spectre_scene import SpectreScene

    session = Session(build())
    session._entry("normal.timing")
    session.seek(1.37)
    scene = SpectreScene(session)
    before = capture(scene, tmp_path / "before.png")
    session.command("detour", "cache-location")
    scene.refresh()
    session.command("return")
    scene.refresh()
    assert capture(scene, tmp_path / "after.png") == before
    assert "ten sam adres" in session.controller_state()["return_sentence"]
    session.command("depth", "simple")
    while session.state.narrative.bridge_target:
        while session.state.playback.position < session.beat.holds[-1]:
            session.command("step")
        session.command("advance")
    assert session.beat.id == "simple.timing"
    assert session.state.return_sentence == session.beat.script.entry_sentence


def test_changing_mind_mid_bridge_preserves_the_conceptual_checkpoint():
    session = Session(build())
    session._entry("normal.timing")
    session.command("depth", "deep")
    assert session.beat.id == "bridge.foundations"
    assert session.landing_for("simple").beat == "simple.timing"
    session.command("depth", "simple")
    while session.state.playback.position < session.beat.holds[-1]:
        session.command("step")
    session.command("advance")
    assert session.beat.id == "simple.timing"


def test_public_encoder_and_travelling_value_share_model_data(app):
    from live_explain.authoring import Event
    from live_explain.presentations.talk import reduce
    from live_explain.presentations.spectre_scene import SpectreScene

    session = Session(build())
    session._entry("normal.channel")
    model = session.model
    model["public_value"] = 3
    reduce(model, Event(2, "encode-public"))
    assert model["probe"] == 3
    scene = SpectreScene(session)
    scene.story.refresh(session.beat, 3, model)
    assert scene.story.cards["input"].body == "3"
    assert scene.story.cards["gate"].body == "probe[3 × stride]"
    assert scene.story.tokens[1].label == "3"
