# Android presenter — open local connection

[Download Android 0.4.0 APK](https://github.com/aridlin/live-explain/releases/download/android-v0.4.0/live-explain-android-0.4.0-preview.apk) · [Releases and checksums](https://github.com/aridlin/live-explain/releases)

Native Android 8+ script reader and remote. No QR code, camera permission, pairing token,
certificate enrollment or account is needed. Any client on a reachable local network can
read the presenter script and control the desktop. The desktop remains authoritative.

## Connect

1. Put the phone and laptop on the same Wi-Fi network, or connect the laptop to the phone hotspot.
2. Start the updated desktop with `./run`. Its local HTTP server starts automatically on TCP **8080**.
3. Open the app and select a discovered **Live Explain** presentation.
4. If discovery is unavailable, enter the laptop's IPv4 address and tap **Połącz z adresem**.
   An address alone uses port 8080; `http://192.168.0.39:8080` is also accepted.
   `./run --remote` displays the laptop address. Use that laptop's actual address.
5. Check **Połączono**, then rehearse Next/Pause, detour/return and blank/unblank before leaving the laptop.

Version 0.3.0 requires the updated desktop: the older TLS/code-pairing server is incompatible.
The same APK signing key is retained, so install over the existing preview. Old pairing
credentials are discarded. The app remembers the selected server and reconnects without
replaying obsolete taps. A failed connection displays its target and a Wi-Fi/firewall hint.

DNS-SD uses `_liveexplain._tcp`, advertising transport `http`, protocol version `2`, session
epoch and address/port. First connection requires no secret. Multiple app instances may
connect; commands are serialized on the desktop GUI thread. When an already-known session
moves to another IPv4 address, discovery can update the offline connection.

The target laptop's existing UFW configuration permits TCP 8080 and multicast UDP 5353;
its old presentation port 8765 was not allowed. Other installations must permit the chosen
port on their local interface. No firewall rule is changed by installing or starting the app.
Multicast-blocking networks can use the direct IP option; client isolation can block both.

## Live operation

The full Polish wording is the primary reader. Compact cues, font sizing and script scroll
positions support glancing while speaking. The expandable tray contains three canonical
continuations, prepared detours, return, undo, finish, replay, blanking and
fullscreen output recovery. A labelled vector icon accompanies each action. Current-route
selection is explicit and unavailable actions are disabled.

The primary controls stay visible, with a status and instruction above them:

- **Teraz mów · obraz czeka**: explain the current image, then **Uruchom animację**.
- **Animacja trwa**: it stops automatically at the next authored hold; **Zatrzymaj** freezes it early.
- **Animacja wstrzymana**: **Kontynuuj ruch** resumes from the interrupted position.
- **Zmiana sceny wstrzymana**: **Wznów przejście** completes the composition change.
- **Ten punkt jest zakończony**: **Następny punkt** enters the next beat only on a tap.
- **Odpowiedź zakończona**: the primary action returns to the interrupted explanation.
- A covered audience screen gets **Pokaż ekran** directly on the primary button.

The reader shows the current authored stage cue, stage count and upcoming visual cue.
The tray's **Pomiń trwający ruch** only applies to active or interrupted motion, so it
cannot accidentally skip a fresh segment at a speaking hold. The desktop remains the
source of stage position and content; the Android projection does not advance time.
Version 0.4.0 needs the current desktop for these richer stage cues.

 The screen stays awake and private
from screenshots/recent-app previews. Backup remains disabled.

HTTP is unencrypted and intentionally unauthenticated. Controller UUIDs identify retry
receipts, not permissions. Commands remain limited to presentation actions; there is no
Python evaluation, shell, filesystem or arbitrary command endpoint.

Each command includes host epoch, expected revision and UUID. One pending envelope is
saved before sending. Uncertain outcomes use `/resolve`; an unknown command is cancelled
so a delayed original cannot advance later. Receipts are scoped by controller and command
ID. A fresh authoritative snapshot follows resolution. No offline tap backlog exists.
Changing servers resolves the old pending envelope against the new epoch instead of
resubmitting it as a new action. Desktop recovery still starts paused at a safe checkpoint.

## Build and validation

Use JDK 17/21 and Android SDK 35:

```sh
android/gradlew -p android assembleDebug assembleDebugAndroidTest testDebugUnitTest lintDebug
python tools/check_android_apk.py android/app/build/outputs/apk/debug/app-debug.apk
```

The preview is debug-signed. CI artifacts may use a different signing key; use the published
release APK to update the previously distributed local preview. The scanner and AndroidX
Core runtime dependencies were removed with the QR flow.

For the isolated API 35 emulator rehearsal (clears only emulator app preferences):

```sh
.venv/bin/python tools/android_rehearsal_host.py --server-file /tmp/live-explain-server.txt
# In another terminal:
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb shell am start -n pl.aridlin.liveexplain/.MainActivity
adb shell run-as pl.aridlin.liveexplain mkdir -p files
adb shell 'run-as pl.aridlin.liveexplain sh -c "cat > files/server-test.txt"' < /tmp/live-explain-server.txt
adb shell am instrument -w -e class pl.aridlin.liveexplain.PresenterFlowTest pl.aridlin.liveexplain.test/androidx.test.runner.AndroidJUnitRunner
```

The test enters the server address through the actual native connection dialog, waits for
reader synchronization, advances, enters a detour, checks exact paused return, and toggles
audience blanking. It does not prove physical hotspot routing or projector legibility.
