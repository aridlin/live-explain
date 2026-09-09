# Validation: full authored talk and native Android preview

The complete authored talk is implemented. This record separates software checks from the remaining physical-phone, projector and spoken-rehearsal gates. It does not claim every long-term engine feature is complete.

## Current connection mode (Android 0.3.0)

At the user's request, QR/token/certificate pairing was removed. The desktop now starts
an open HTTP server on port 8080 by default, and Android connects through live DNS-SD
selection or a plain IPv4 address. Multiple controllers may read/control the same session;
per-controller command receipts and revision/epoch checks remain. Camera/ZXing, QR image
creation and TLS dependencies were removed. Earlier TLS/scanner validation below is
historical and does not describe the current connection mode.

The target laptop's saved UFW configuration enables default-deny input, permits TCP 8080
and mDNS, but did not permit the old port 8765. Port 8080 was checked free before adoption.
No firewall rules were changed. Physical phone routing remains an independent check.

Current checks (2026-09-09): all 82 Python tests passed, including real HTTP
multi-controller/receipt tests and full-talk typography checks. Eight Android JVM tests,
APK assembly and lint passed. A native Android API 35 emulator connected through the
actual address-entry dialog over HTTP, synchronized the reader, advanced, entered the
cache-location detour, returned to the captured paused position, and blanked/unblanked
the audience screen. The test compares the saved origin position, because an explicit
finish after a completed segment can select the next hold. This is emulator evidence,
not a physical hotspot-phone test.

The opening now allocates 105 seconds to Pentagon pizza activity, with separately
authored Polish scripts in all three canonicals. The rendered opening was visually
inspected and full-talk layout checks passed. Its historical source and inference limits
are documented in PRESENTATION.md. Fallback stills were regenerated through the same
renderer. The 20-minute allocation remains an authored budget pending spoken rehearsal.

## Earlier validation

- The full suite now includes 82 Python checks: all 48 canonical beats plus detours/bridges, Polish typography and rendering at every authored hold, audience disclosure, interrupted pixel restoration and matching-checkpoint depth changes, alongside the existing runtime, geometry and protocol tests.
- Eight Android JVM tests passed. Android lint passed with warnings (pinned dependency versions, deliberately durable command receipts, custom session-certificate pinning, and Polish-only string composition).
- A native Android API 35 emulator rehearsal passed: reader synchronization, advance and explicit segment completion, cache-location detour, exact paused return at position 2, and blank/unblank over TLS. Native DNS-SD discovery and matching-pin relocation compile and pass JVM checks; physical multicast discovery remains a room-device check. Reader and tray captures were inspected; timeline choices were compressed to one row so branches remain nearer the thumb.
- Exact detour return reproduces the original captured pixels and preserves stable item identities.
- A register moves and resizes while a token follows its deforming connector. Tests inspect 399 positions, endpoint attachment, token continuity, text width and byte-obstacle clearance.
- Three separately authored canonical entries, two-level nesting, the Deep bridge and fresh landing, undo and paused restoration are exercised.
- The audience disclosure projection conceals the selected byte in numeric/ASCII displays and secret-value tokens until the reveal marker.
- Lost command acknowledgments, duplicate IDs, reused-ID conflicts, stale revisions, unauthorized messages and changed host epochs are tested both at the command boundary and over a real local TLS socket. Unknown receipt resolution cancels late delivery.
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
- A timed, spoken 20-minute rehearsal. All three full-length narratives are authored; their planned 17:05 core leaves approximately 2:55 for detours and discussion. This is a budget, not a measured speaking duration.
- Physical Android phone/hotspot compatibility, prolonged radio-loss rehearsal, and touch-to-projector latency. The native preview uses HTTP polling rather than WebSockets; its emulator test does not prove vendor hotspot routing.
- Large-dataset virtualization, a graphical authoring editor, rich arbitrary code editing, a general graph router, and real hardware measurements.
- A fully standalone platform installer containing Python and Qt, or testing on unrelated operating systems. The supported launch path uses the isolated locked environment; the wheel contains the application and fonts.
- Input-to-visible-freeze timing with a high-speed camera and long-session resource soak testing.

The proposed API in PLAN.md intentionally remains distinct from the smaller implemented API. TEST_PLAN.md is a roadmap; passing implemented tests does not imply every listed future acceptance condition has passed.

## Full-talk and scanner follow-up (2026-09-08)

The default presentation has 16 corresponding chapters per canonical, 7 prepared detours
and 3 prerequisite bridges (58 authored beats total). The old specimen remains available
with `--slice`. All authored holds were rendered for typography/disclosure inspection;
representative code, line-cache, Spectre and Meltdown diagrams and the decode chart were
visually reviewed. The Normal route exports public fallback stills and a separate private script.
Human composition, pacing and back-row legibility remain independent from those checks.

Android 0.2.1 fixes missing AndroidX camera-permission helpers in the standalone APK.
Assemble, 8 JVM tests and lint passed. The standalone API 35 scan-button path requested
camera permission, resumed CaptureActivity and returned without a fatal exception.
The initial emulator cold boot suffered system/app ANR delays under heavy resource load;
the successful scanner run used the settled emulator with no instrumentation classpath.
A DEX-definition gate now prevents this particular packaging regression in CI. Real
projected QR decoding on the user's phone has not been verified.

Normal Spectre scene, 120 offscreen frames at 1920×1080: median 15.9 ms, p95 23.2 ms,
p99 25.7 ms on the target laptop. This includes model reconstruction and scene rendering;
it is not compositor FPS or a two-window benchmark. The existing performance caveats remain.

Desktop DNS-SD registration/removal now runs on a single worker, rather than blocking
the GUI thread. A regression test verifies worker ownership and orderly shutdown.

The running host was also discovered by a separate local DNS-SD browser. That verifies
the desktop advertisement, not multicast reachability from the physical Android phone.
