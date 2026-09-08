# Validation of the first desktop vertical slice

This is a bounded implementation of the approved first milestone, not the entire long-term test specification or the finished 20-minute talk.

## Verified

- 60 pure runtime/model/protocol and Qt integration tests passed locally, including three reviewed visual baselines.
- Exact detour return reproduces the original captured pixels and preserves stable item identities.
- A register moves and resizes while a token follows its deforming connector. Tests inspect 399 positions, endpoint attachment, token continuity, text width and byte-obstacle clearance.
- Three separately authored canonical entries, two-level nesting, the Deep bridge and fresh landing, undo and paused restoration are exercised.
- The audience disclosure projection conceals the selected byte in numeric/ASCII displays and secret-value tokens until the reveal marker.
- Lost command acknowledgments, duplicate IDs, reused-ID conflicts, stale revisions, unauthorized messages and changed host epochs are tested without exposing a network listener.
- Polish font/glyph preflight, three reviewed image baselines, multiple capture resolutions, and actual QGraphicsView heading rendering are tested.
- The audience window was launched on Hyprland and reported mapped/fullscreen. A local desktop screenshot was inspected; a discovered title/footer suppression bug was fixed and received a regression test.
- Source distribution and wheel build offline using cached build dependencies. Fonts and their license are packaged. The wheel was installed into a clean temporary environment, then rendered a frame with networking restricted. Initial dependency installation still requires network access or a prepared wheelhouse.
- Fallback stills export through the live renderer with a separately labelled private script.

## Performance evidence

These are initial, short target-laptop measurements, not universal performance claims. The live benchmark uses two windows and measures synchronous paint work and timer callbacks. It does not measure actual compositor presentation, display scanout, or input-to-photon latency.

| Workload | Median paint | p95 paint | Median callback interval | p95 interval |
|---|---:|---:|---:|---:|
| Dense fixture before caching, 240 live frames | 100 ms | 160 ms | 206 ms | 317 ms |
| Dense fixture after caching, 100 live frames | 55 ms | 76 ms | 83 ms | 112 ms |
| Authored Normal slice, 180 live frames | 9.2 ms | 15.2 ms | 16.3 ms | 24.1 ms |

The dense fixture contains 30 code lines, 128 bytes, 24 components, 40 connectors and 24 simultaneous tokens. It is a workload probe rather than an audience composition. Cached shaped text, stable panel caching, and avoiding unnecessary invalidation improved it but did not meet the provisional frame target.

The authored slice is responsive in the measured workload, but its p95 callback interval still exceeds the proposed 20 ms gate. Larger content should not be added on an assumption of unlimited headroom. Profile further, reduce unnecessary invalidation and test Qt Quick if rendering remains limiting. No native extension has been introduced.

Offscreen Normal scene rendering over 120 frames measured about 10.6 ms median / 16.5 ms p95. Offscreen and live measurements are different workloads and should not be interpreted as interchangeable FPS figures.

## Not yet verified or implemented

- HDMI projector mode changes, hotplug behavior, mixed-refresh outputs and actual room/back-row readability. HDMI was disconnected during the observed checks.
- Zero-frame privacy during OS mirroring: no application can guarantee this. Notes remain opt-in; known screen changes hide private UI and cover the audience scene.
- Full 20-minute rehearsal or all three full-length narratives. Current content is the compact proving sequence.
- Native Android app, TLS pairing UI, or WebSocket listener. Protocol behavior currently exists as an in-process boundary with fault-oriented tests.
- Large-dataset virtualization, a graphical authoring editor, rich arbitrary code editing, a general graph router, and real hardware measurements.
- A fully standalone platform installer containing Python and Qt, or testing on unrelated operating systems. The supported launch path uses the isolated locked environment; the wheel contains the application and fonts.
- Input-to-visible-freeze timing with a high-speed camera and long-session resource soak testing.

The proposed API in PLAN.md intentionally remains distinct from the smaller implemented API. TEST_PLAN.md is a roadmap; passing implemented tests does not imply every listed future acceptance condition has passed.
