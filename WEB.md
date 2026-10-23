# Browser presentation

`./run` now starts an HTML/SVG audience view and a web presenter instead of Qt windows. Python 3.12+ runs the existing deterministic session engine; the browser frontend uses plain JavaScript and CSS. There is no frontend build, npm installation, CDN or Qt requirement for presenting.

```sh
./run                         # opens the presenter at http://127.0.0.1:8080/presenter
./run --remote                # phone browser on the same trusted LAN / hotspot
./run --canonical deep        # choose the starting route
./run --no-open --port 8765    # start without launching a browser
```

Open `/` in a separate browser window, move it to the projector and use the Fullscreen button. Keep `/presenter` on the laptop or phone. Extended displays are required to keep notes off the projector; mirrored displays show whatever is on the laptop. Audience responses contain no private script. Presenter mode separates the UI, not access permissions: the open LAN mode intentionally has no authentication, matching the existing project's direct-connect design. Use the laptop's IP on a phone, not `127.0.0.1`. No firewall rules are changed.

The phone layout puts the script first and keeps playback controls at the bottom. No APK is required. The previous Android app can still use the `/state`, `/command` and `/resolve` protocol with a manually entered address; this host does not advertise mDNS. Physical Android compatibility has not been rehearsed for this change.

## What's improved

- Scalable SVG scenes for all 16 chapters, three authored Polish routes, two cache detours, five other detours and three prerequisite bridges.
- A dedicated audience composition with code focus, address/value separation, cache copies, simulated timing bars, predictor history, and a side-by-side distinction between architectural results and microarchitectural traces.
- The speculation scene compares waiting with executing while the condition is pending. The decode scene pauses before the answer so the audience can interpret the timing evidence.
- A presenter workspace with current/next cues, full original script, larger text, chapter navigation, route selection, timing, and contextual detours. Missing prerequisites insert the original authored bridge.
- Server-authoritative playback, pause, scrub, replay, nested detour return, navigation undo, blanking, and recording download. Browser animation interpolates token position between server updates; semantic events remain server-authored.
- Stable command IDs on network retries, stale-revision rejection, reconnect status and disabled controls during failed connections. Blanking pauses playback and blocks advancement until uncovered.
- Bundled fonts and assets. Presentation works without internet after checkout; external research links are optional.

## Controls

| Key | Action |
| --- | --- |
| Right | Next animation step / next chapter |
| Space | Play / pause |
| Down | Complete a semantic step |
| F | Finish current step |
| R | Replay from the preceding hold |
| U | Undo narrative navigation |
| Backspace | Return from detour, paused at the saved position |
| B | Cover / uncover audience and pause |
| P | Open presenter in a separate window |
| F11 | Fullscreen |

The web scrubber intentionally pauses. Chapter selection can insert a prerequisite bridge; finish it and choose Next to enter the requested chapter. Seeking does not count as having delivered prerequisites. The presenter timer starts with the server session. Reopening a browser reconnects to that session; restarting the server starts a fresh one.

The original native application's output selection, still-image export, recovery UI and replay-file CLI are available through `./run-native` after `uv sync --frozen --extra native`. Native and web hosts are separate sessions; do not run them on the same port. The web interface downloads a versioned action journal (including web chapter selection and blanking); this is a diagnostic record, not a native replay file. It does not yet import/replay recordings from the UI. None of the diagrams execute an exploit or measure host-memory access.

## Validation

```sh
PYTHONPATH=src python3 -m unittest discover -s web_tests -v
node --test web_tests/scene.test.mjs
node --check src/live_explain/web/app.js
uv sync --frozen --extra native
uv run --extra native pytest -q
uv run --extra native ruff check src tests web_tests
uv run --extra native ruff format --check src tests web_tests
uv build
```

On 2026-10-23: 83 legacy tests, 10 web-host tests and 3 SVG tests passed. SVG tests reconstruct all 58 authored beats at holds and midpoints. Build and Python style checks passed. Browser rehearsal verified chapter bridges, scrub to 3.25 seconds, cache detour and exact paused return, synchronized audience/presenter views, and inspected desktop/fullscreen and 390-pixel phone layouts. These are software checks, not physical phone/hotspot or back-row/projector verification. No universal FPS claim is made.

See [VIDEO_RESEARCH.md](VIDEO_RESEARCH.md) for source selection, popularity measurements and the specific ideas used.
