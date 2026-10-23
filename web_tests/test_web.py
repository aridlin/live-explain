"""Headless browser host contract; no Qt or third-party test dependencies."""

import json
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from live_explain.web_server import WebHost, make_server


class HostTests(unittest.TestCase):
    def setUp(self):
        self.host = WebHost()
        self.s = self.host.session

    def test_every_route_runs_to_completion(self):
        for route in ("simple", "normal", "deep"):
            h = WebHost(route)
            visited = []
            for beat in h.session.presentation.routes[route]:
                self.assertEqual(h.session.beat.id, beat)
                visited.append(beat)
                for _ in h.session.beat.holds[1:]:
                    self.assertTrue(h.dispatch("step", None)[0])
                    self.assertIsInstance(h.audience()["model"], dict)
                h.dispatch("advance", None)
            self.assertEqual(len(visited), 16)
            self.assertEqual(h.session.controller_state()["playback_phase"], "finished")

    def test_public_state_has_no_private_script_or_secret(self):
        self.s._entry("normal.spectre")
        self.s.seek(5)
        public = self.host.audience()
        self.assertNotIn("script", public)
        self.assertNotIn("cue", public)
        self.assertIsNone(public["model"]["memory"][12])
        self.assertIsNone(public["model"]["probe"])
        self.assertNotIn(self.s.beat.script.wording, json.dumps(public))
        self.s._entry("normal.decode")
        self.s.seek(2)
        self.assertEqual(self.host.audience()["model"]["measurements"], [9, 9, 2, 9])
        self.assertIsNone(self.host.audience()["model"]["memory"][12])
        self.s.seek(4)
        self.assertEqual(self.host.audience()["model"]["memory"][12], 2)

    def test_detour_restores_exact_interrupted_position_and_target(self):
        self.s._entry("normal.timing")
        self.s.command("advance")
        self.s.tick(0.3)
        before = self.s.snapshot()
        self.host.dispatch("detour", "cache-location")
        self.host.dispatch("step", None)
        self.host.dispatch("return", None)
        self.assertEqual(self.s.beat.id, "normal.timing")
        self.assertEqual(self.s.state.playback.position, before.playback.position)
        self.assertEqual(self.s.state.playback.target, before.playback.target)
        self.assertFalse(self.s.state.playback.playing)

    def test_jump_requires_bridge_and_undo_restores_position(self):
        self.s.seek(1.25)
        self.assertTrue(self.host.dispatch("chapter", "spectre")[0])
        self.assertTrue(self.s.beat.id.startswith("bridge."))
        self.assertEqual(self.s.state.narrative.bridge_target, "normal:normal.spectre")
        self.host.dispatch("undo", None)
        self.assertEqual(self.s.beat.id, "normal.opening")
        self.assertEqual(self.s.state.playback.position, 1.25)
        self.host.dispatch("chapter", "spectre")
        self.host.dispatch("step", None)
        self.host.dispatch("step", None)
        self.host.dispatch("advance", None)
        self.assertEqual(self.s.beat.id, "normal.spectre")

    def test_blank_pauses_and_blocks_advancing(self):
        self.host.dispatch("advance", None)
        self.host.dispatch("blank", None)
        self.assertFalse(self.s.state.playback.playing)
        self.assertFalse(self.host.dispatch("advance", None)[0])
        self.host.dispatch("blank", None)
        self.assertTrue(self.host.dispatch("advance", None)[0])

    def test_receipts_and_invalid_commands(self):
        body = dict(epoch=self.s.epoch, revision=self.s.revision, id="one", kind="step", value=None)
        original = json.dumps(body)
        receipt = self.host.protocol.handle(original, "phone")
        self.assertEqual(receipt["status"], "accepted")
        self.assertEqual(self.host.protocol.handle(original, "phone"), receipt)
        self.assertEqual(self.s.state.playback.position, 2)
        body["id"] = "two"
        self.assertEqual(self.host.protocol.handle(json.dumps(body), "phone")["status"], "rejected")
        for v in ("NaN", "Infinity", "-1", "900", "wat"):
            self.assertFalse(self.host.dispatch("seek", v)[0])
        self.assertFalse(self.host.dispatch("chapter", "../../secret")[0])

    def test_web_journal_includes_chapter_and_blanking(self):
        self.host.dispatch("chapter", "spectre")
        self.host.dispatch("blank", None)
        recording = self.host.recording()
        self.assertEqual(recording["format"], "live-explain-web-v1")
        self.assertEqual([c["kind"] for c in recording["commands"]], ["chapter", "blank"])
        self.assertTrue(recording["commands"][-1]["blank"])


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.stop_clock.set()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_browser_assets_and_no_source_exposure(self):
        for path in (
            "/",
            "/presenter",
            "/app.js",
            "/scene.js",
            "/style.css",
            "/sources.json",
            "/fonts/DejaVuSans.ttf",
        ):
            with urlopen(self.url + path) as r:
                self.assertEqual(r.status, 200)
                self.assertTrue(r.read())
        for path in ("/../runtime.py", "/runtime.py", "/talk_text.py"):
            with self.assertRaises(HTTPError) as e:
                urlopen(self.url + path)
            self.assertEqual(e.exception.code, 404)
            e.exception.close()

    def test_android_envelope_and_audience_privacy(self):
        with urlopen(self.url + "/state") as r:
            state = json.load(r)
        self.assertEqual(state["status"], "state")
        self.assertIn("script", state["state"])
        with urlopen(self.url + "/api/audience") as r:
            public = json.load(r)
        self.assertNotIn("script", public)
        self.assertEqual(public["epoch"], state["state"]["epoch"])

    def test_cross_origin_write_rejected(self):
        req = Request(self.url + "/command", data=b"{}", headers={"Origin": "https://unrelated.example"})
        with self.assertRaises(HTTPError) as e:
            urlopen(req)
        self.assertEqual(e.exception.code, 403)
        e.exception.close()


if __name__ == "__main__":
    unittest.main()
