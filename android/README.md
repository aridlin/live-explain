# Android presenter

A genuinely native Java/Android application. The full Polish script is the main screen;
a collapsible, scrollable tray holds the three canonical continuations, current detours,
return, undo, play, step, finish, replay, blanking, and fullscreen output recovery.
No WebView, browser, cloud account, Google Play Services, or Bluetooth is required. Local-network discovery uses native Android NSD.
The small platform-widget implementation deliberately replaces the earlier proposed
Kotlin/Compose foundation; presentation logic remains in Python.

## Before the talk

1. Install the preview APK on Android 8 or newer.
2. Enable the phone's hotspot and connect the laptop to it. Internet access is unnecessary.
3. Start the laptop with `./run --remote`. Alternatively open the private presenter
   with **P**, then **Połącz telefon**. Pair before projecting private UI.
4. In the private pairing window choose the laptop's Wi-Fi interface/address.
5. On Android choose **Połączenie → Skanuj kod QR** and scan that window. Pasting the
   complete private pairing link is an alternative if camera permission is unavailable.
6. Check **Połączono**, exercise pause/next, open the controls tray, test blank/unblank,
   and select the HDMI output before leaving the laptop. Keep the phone app in the foreground.

The phone is the primary operating surface during the talk. Next/Pause remain visible;
the tray provides all routine control and output recovery without opening laptop notes.
Depth changes and output reassignment have explicit confirmation. Output recovery
selects a fullscreen audience window, leaves it covered and paused, then lets you choose
**Pokaż publiczny ekran**. This cannot restart a crashed desktop process or repair an OS/driver hang.

The reader keeps the last synchronized script when disconnected and remembers per-beat
scroll positions during the activity lifetime. Font size and full-wording/cue preference
persist. Android keeps the screen awake while this activity is visible. Secure-window
flags hide it in screenshots and recent-app previews; backups are disabled. Do not cast
or mirror the phone during a presentation.

## Local connection

HTTPS on TCP **8765**, with a new certificate and 256-bit bearer token for each desktop
process. The private QR binds the exact certificate SHA-256 fingerprint and address;
certificate identity is checked even though there is no public DNS/CA. Pairing credentials
are private app storage on Android and ephemeral memory on the desktop. No trust-all
fallback, HTTP downgrade, arbitrary expressions, filesystem API, or shell commands exist.
Only one paired controller identity may read/control the session. Reinstallation changes
that identity and requires a fresh desktop pairing session.

The app polls complete state every 500 ms while foregrounded. Commands send immediately
when the connection worker is free. This is intentionally simpler than a WebSocket
channel; the desktop's animation clock does not depend on the polling rate.

- Every command has host epoch, expected revision, controller identity and a UUID.
- Only one pending command is permitted, stored before transmission.
- A duplicate envelope returns its original receipt; changed payloads under the same ID fail.
- After an uncertain result the phone uses `/resolve`, never sends a new `advance`.
  An unknown ID is recorded as cancelled, so even late original delivery cannot execute it.
- Fresh `/state` follows receipt resolution. Old receipt snapshots never replace fresh state.
- Restarting the phone resolves its saved pending command. No offline tap backlog exists.
- Reconnection does not overwrite desktop state. A changed desktop process needs a new QR.
- After an app restart with an unknown old result, explicitly pairing another session
  requires acknowledging that the old result remains unknown.

The desktop advances only to the next authored hold. Loss of the phone connection does
not advance the narrative; an already-running segment can finish its hold. This is not
an independent emergency-stop radio. Network timeout detection can take several seconds.

Hotspot routing varies by phone vendor. If pairing fails, check the selected laptop IP,
VPN routing, and whether the laptop firewall allows TCP 8765 on that private interface.
Do not open the port to the internet. A trusted shared Wi-Fi network is also supported;
Android DNS-SD discovers `_liveexplain._tcp` sessions on normal local networks. First pairing still requires the private QR; discovery never authorizes access. Already-paired sessions can be relocated to a changed IPv4 address only when their certificate pin matches. Multicast-blocking networks can still use QR/direct connection. Bluetooth remains deferred. Actual hotspot and HDMI rehearsal remain
required on the physical devices.

## Build and tests

Use JDK 17 or 21 and Android SDK platform 35. Set `ANDROID_HOME` to that SDK:

```sh
./gradlew assembleDebug testDebugUnitTest
```

The checked-in Gradle wrapper verifies its distribution checksum. Dependency versions
are pinned; building initially needs Maven/Google repositories. The installed app works
offline. The preview APK uses the build machine's debug signing key; it is a sideloadable
rehearsal build, not a Play Store release. CI-built APKs may use another debug key.

`CommandLedgerTest` covers process restart, duplicate taps, mismatched acknowledgments,
new host epochs and uncertain results. Python tests exercise the actual HTTPS transport,
authentication, GUI-thread dispatch, receipt lookup/cancellation, and scene controls.

For the opt-in Android API 35 emulator rehearsal (host alias 10.0.2.2):

```sh
# From repository root; keep running during the test. Pairing file is PRIVATE.
.venv/bin/python tools/android_rehearsal_host.py --pairing-file /tmp/live-explain-pairing.txt
# In another terminal after booting an isolated emulator:
android/gradlew -p android assembleDebug assembleDebugAndroidTest
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb shell am start -n pl.aridlin.liveexplain/.MainActivity
adb shell run-as pl.aridlin.liveexplain mkdir -p files
adb shell 'run-as pl.aridlin.liveexplain sh -c "cat > files/pairing-test.txt"' < /tmp/live-explain-pairing.txt
adb shell am instrument -w pl.aridlin.liveexplain.test/androidx.test.runner.AndroidJUnitRunner
```

Instrumentation reads the script, advances one segment, enters cache-location, verifies
exact paused return at position 2, and covers/uncovers the audience. Test-only view captures
are stored in private app files, bypassing secure-window capture solely from instrumentation.
The production app contains no screenshot bypass or automatic pairing intent.

Foundations: [Android TLS guidance](https://developer.android.com/privacy-and-security/security-ssl),
[ZXing Android Embedded](https://github.com/journeyapps/zxing-android-embedded).
Session QR pinning differs from hard-coded public-service pins: it can be renewed locally
without shipping an app update. Dependency notices are in `THIRD_PARTY.md`.

### Scanner regression gate

Version 0.2.1 explicitly packages AndroidX Core. ZXing's scanner invokes its camera
permission helpers, but the scanner dependency alone did not package those classes in
0.2.0. Instrumentation dependencies can mask that omission. CI now checks **definitions
in the actual APK DEX files**, including `ContextCompat` and `ActivityCompat`:

```sh
python tools/check_android_apk.py android/app/build/outputs/apk/debug/app-debug.apk
# Isolated emulator only: revokes camera permission, opens scanner, grants permission, returns.
python tools/android_scanner_smoke.py
```

The standalone API 35 scanner open/permission/Back path passed on 2026-09-08.
This is separate from decoding a real projected QR on a physical phone.
