"""Recruitment navigation, private script, assets, and rendered layout contracts."""

from copy import deepcopy
from hashlib import sha256
import json
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QRectF

from live_explain.app import build_presentation, build_scene, capture
from live_explain.components import shaped_text
from live_explain.presentations.recruitment import CHAPTERS, build
from live_explain.presentations.recruitment_scene import ASSETS, RecruitmentScene
from live_explain.runtime import Session


@pytest.mark.parametrize("canonical,seconds", [("simple", 180), ("normal", 300), ("deep", 480)])
def test_whole_route_and_private_script(canonical, seconds):
    session = Session(build(), canonical)
    assert len(session.presentation.routes[canonical]) == 6
    assert session.controller_state()["route_seconds"] == seconds
    words = 0
    for index, key in enumerate(session.presentation.routes[canonical]):
        assert session.beat.id == key
        state = session.controller_state()
        assert state["script"]["wording"] == session.beat.script.wording
        assert len(state["script"]["wording"].split("\n\n")) == 2
        words += len(state["script"]["wording"].split())
        assert session.command("advance")[0]
        # Small positive ticks stop at the hold and do not advance chapters automatically.
        for _ in range(14):
            session.tick(0.1)
        assert session.beat.id == key
        assert not session.state.playback.playing
        assert session.model["revealed"]
        if index < 5:
            assert session.command("advance")[0]
    # Shorter wording is valid; the budget must not require hurried delivery.
    assert words / (seconds / 60) <= 120
    assert session.controller_state()["playback_phase"] == "finished"
    assert not session.command("advance")[0]


@pytest.mark.parametrize("chapter", [c[0] for c in CHAPTERS])
def test_all_corresponding_route_changes_and_undo(chapter):
    session = Session(build())
    session._entry("normal." + chapter)
    session.seek(0.47)
    before = session.digest()
    for canonical in ("simple", "deep", "normal"):
        assert session.command("depth", canonical)[0]
        assert session.beat.id == canonical + "." + chapter
        assert session.state.playback.position == 0
        assert not session.state.playback.playing
    for _ in range(3):
        assert session.command("undo")[0]
    assert session.digest() == before


@pytest.mark.parametrize(
    "chapter,detour", [("ft", "ft-detail"), ("kalwer", "kalwer-detail"), ("voice", "voice-detail")]
)
def test_detour_restores_interrupted_state_and_pixels(app, chapter, detour):
    session = Session(build())
    session._entry("normal." + chapter)
    session.seek(0.47)
    scene = build_scene(session)
    before = capture(scene, None)
    playback = deepcopy(session.state.playback)
    assert session.command("detour", detour)[0]
    assert session.controller_state()["return_to"] == "normal." + chapter
    assert session.landing_for("deep").beat == "deep." + chapter
    assert session.command("step")[0]
    assert session.command("return")[0]
    scene.refresh()
    assert session.state.playback == playback
    assert capture(scene, None) == before


def test_defaults_and_explicit_presentation_selection():
    assert build_presentation(SimpleNamespace()).id == "spectre-full"
    assert build_presentation(SimpleNamespace(presentation="recruitment")).id == "igor-recruitment"


def test_recruitment_assets_are_local_unmodified_public_sources():
    sources = json.loads((ASSETS / "sources.json").read_text())
    assert len(sources) == 10
    for item in sources:
        assert item["source"].startswith("https://github.com/aridlin/")
        assert sha256((ASSETS / item["file"]).read_bytes()).hexdigest() == item["sha256"]


def test_all_scenes_fit_and_audience_has_no_private_script(app):
    session = Session(build())
    scene = build_scene(session)
    assert isinstance(scene, RecruitmentScene)
    for beat in session.presentation.beats.values():
        session._entry(beat.id)
        for position in (0, 0.6, 1.2):
            session.seek(position)
            scene.refresh()
            assert not capture(scene, None, 1280, 720).isNull()
            for rect, value, size, bold in scene.text_regions:
                shaped = shaped_text(value, rect[2], size, False, bold, True, 1, 1).size()
                assert shaped.height() <= rect[3], (beat.id, value, shaped.height(), rect[3])
                assert shaped.width() <= rect[2] + 1, (beat.id, value, shaped.width(), rect[2])
                assert scene.sceneRect().contains(QRectF(*rect)), (beat.id, value)
            audience_text = "\n".join(region[1] for region in scene.text_regions)
            assert beat.script.wording not in audience_text
            assert "TERAZ:" not in audience_text
    scene.blank = True
    scene.refresh()
    capture(scene, None)
    assert not scene.text_regions


def test_intro_treats_age_as_metadata_and_preserves_authored_lines(app):
    scene = build_scene(Session(build()))
    capture(scene, None)
    labels = {value: (rect, size, bold) for rect, value, size, bold in scene.text_regions}
    assert "17" not in labels
    assert labels["17 lat · trzecia klasa liceum"][1] == 25
    assert not labels["17 lat · trzecia klasa liceum"][2]
    assert "Programowanie" in labels and "Cyberbezpieczeństwo" in labels
    assert labels["Programowanie"][0][1] < labels["Cyberbezpieczeństwo"][0][1]


@pytest.mark.parametrize("canonical", ["simple", "normal", "deep"])
def test_reset_clears_detour_progress_and_undo_preserving_version(canonical):
    session = Session(build(), canonical)
    session._entry(canonical + ".ft")
    assert session.command("detour", "ft-detail")[0]
    session.command("play")
    session.delivered.add("example")
    session.assessments["example"] = "yes"
    session.elapsed = 123
    revision, epoch = session.revision, session.epoch
    assert session.command("reset")[0]
    assert session.beat.id == canonical + ".about"
    assert session.state.narrative.canonical == canonical
    assert session.state.playback.position == 0 and not session.state.playback.playing
    assert not session.state.detours and not session.history
    assert not session.delivered and not session.assessments and session.elapsed == 0
    assert session.revision > revision and session.epoch == epoch
