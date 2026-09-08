# Test and acceptance specification

Status: planned tests; none are executable or claimed passing yet. Implementation is deliberately paused pending design approval. This specification is the initial test artifact for the requested public repository. Runnable tests will accompany the first implementation, not be replaced by documentation.

## Pure navigation and coverage

- NAV-01: Define three distinct canonical routes; selecting one never silently substitutes another.
- NAV-02: Suspend Normal at 42% of transfer, enter cache-location, resume. Compare domain state, event cursor, visual staging, route version, seed, code focus, and playback position. Expect paused mode and restored script continuation.
- NAV-03: Return to Deep with missing timing/cache-line coverage. Expect named bridge and Deep entry recipe, not Normal model snapshot transplantation.
- NAV-04: Test bridge completed, bridge skipped, missing bridge, explicit warning override, and earlier landing. Exposure never sets comprehension automatically.
- NAV-05: Two nested detours pop correctly; third entry rejected; canonical landing explicitly closes stack; undo history remains separate.
- NAV-06: Reject missing destinations and incompatible entries before playback. Required canonical beats must be reachable on their declared route.
- NAV-07: Double advance from one control revision performs one operation; repeat during transition never queues the next beat.
- NAV-08: Undo restores navigation but not wall-clock time, connection epoch, or historical record of delivered content.

## Domain model independently of Qt

- MOD-01: Reads, writes, selections, cache effects and illustrative instruction events follow declared assumptions.
- MOD-02: Discarded architectural result and preserved cache effect are separate assertions; no speculative store accidentally becomes committed.
- MOD-03: Bounds-check example and privilege-fault example have different event sequences.
- MOD-04: Model snapshot plus replay equals uninterrupted event application.
- MOD-05: Byte identity survives hex/decimal/binary/ASCII views; explicit width/endianness and unknown/unavailable states remain consistent.
- MOD-06: Audience concealment covers labels, numeric formats, annotations, tooltips, previews, accessibility text, and value-dependent styling until explicit disclosure.

## Animation and control

- ANI-01: Seek before, at, and after every event marker; ensure marker executes once and a visual tail need not imply a new event.
- ANI-02: Pause/resume mid-transfer, replay, finish transition, skip through named exit, and detour return preserve semantics.
- ANI-03: Cancel scene, then deliver delayed callback/worker result; old generation cannot mutate active state.
- ANI-04: A large timer gap pauses safely; dropped drawings do not skip model events or manual holds.
- ANI-05: Same seed/content/position reproduces model hash and evaluated scene; render does not consume randomness.
- ANI-06: Record accepted commands against logical playback positions and replay; verify state hashes and selected captures.

## Geometry and text

- GEO-01: Nested local/scene mappings attach ports correctly through translation, scale and group expansion.
- GEO-02: Arrowhead tip/base, endpoint normal, obstacle and label clearance satisfy numeric constraints.
- GEO-03: Text remains within content bounds and intended clips; verify Polish diacritics, technical symbols, dense source and varying numeric widths.
- GEO-04: Source semantic spans map to actual glyph rectangles; include Unicode indexing and multiline span cases.
- GEO-05: Offscreen byte/span ports require an explicit scroll/indicator/error; never attach to an invisible arbitrary point.
- GEO-06: Move and resize a component while a token is in flight. Require readable labels, continuously attached ports, stable topology, continuous P(u,t), and no intermediate obstacle crossing. Check intermediate frames and review motion manually.
- GEO-07: Impossible routes produce authoring diagnostics; debug information cannot enter live audience output.

## Protocol and fault injection

- PRO-01: Unauthorized/expired pairing, malformed/oversized payload and non-allowlisted commands are rejected. No eval, pickle, file loading or shell commands.
- PRO-02: Same command ID retransmitted before/after lost acknowledgment yields one effect and the original receipt.
- PRO-03: Dedupe lookup occurs before revision validation; different new command with old revision is rejected.
- PRO-04: Disconnect before receipt, after acceptance, and during completion. Reconnect fetches authoritative state and outstanding receipt; no stale tap backlog.
- PRO-05: Host restart changes epoch. Old command cannot apply to a recovered checkpoint even if its beat ID matches.
- PRO-06: Laptop input and remote input race; serialized acceptance and control revision permit one valid navigation result.
- PRO-07: Phone displays uncertain/pending/disconnected truthfully; haptics follow acknowledgment; accessibility remains usable without haptics.

## Visual, packaging and live acceptance

- VIS-01: Pin fonts, content, seed, viewport and renderer version. Review Normal/Simple/Deep entries, interrupted scene, detour, bridge and return.
- VIS-02: Capture 1080p, 720p and 4:3 layouts; strict geometry assertions plus perceptual raster diffs. Maintain reviewed platform baselines, never silently bless updates.
- VIS-03: Human review of composition, optical alignment, label hierarchy, Polish wording, in-flight motion, and projector/back-row readability. Passing collisions is insufficient.
- LIVE-01: Ordinary fullscreen audience window on HDMI under Hyprland, separate presenter window on laptop; known HDMI unplug/replug, mode change, placement recovery, single-monitor public/private modes. Record privacy limits of OS mirroring. No custom compositor infrastructure.
- LIVE-02: Fully offline clean-package launch; missing asset/font/glyph preflight; safe-checkpoint restart paused with fresh epoch.
- LIVE-03: Stress scene and metrics from PLAN K, including p95/p99 frame intervals, freeze latency, repeated detour memory behavior and both windows.
- LIVE-04: Disconnect phone and network during a sequence; keyboard remains usable and no unintended advance occurs.
- LIVE-05: Rehearse roughly 16-minute authored spine plus four-minute room allowance; record at least one exact-return route and one cross-depth bridge route.
- LIVE-06: Launch public-safe exported checkpoint stills in an external viewer with separate private script. No live exploit dependency.

## Planned automation boundaries

Pure Python tests run headlessly in CI. Qt geometry/capture integration runs in a pinned rendering environment. Actual HDMI, frame pacing, Android networking/haptics, and human visual review require target devices; headless green CI does not substitute for these.

No installable application or passing badge should appear until real executable tests exist. Baseline updates must include reviewed before/after evidence. Randomized command tests retain their failing seed and command trace.
