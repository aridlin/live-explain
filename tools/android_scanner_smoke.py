"""Standalone emulator UI smoke: avoids instrumentation dependencies hiding missing APK classes."""

import re
import subprocess
import time
import xml.etree.ElementTree as ET

DEVICE = "emulator-5554"


def adb(*args):
    return subprocess.check_output(["adb", "-s", DEVICE, *args], text=True, timeout=55)


def nodes():
    result = adb("shell", "uiautomator", "dump", "/sdcard/live-explain-ui.xml")
    if "dumped to" not in result:
        return []
    return ET.fromstring(adb("shell", "cat", "/sdcard/live-explain-ui.xml")).iter("node")


def tap(match):
    for attempt in range(5):
        for node in nodes():
            if match(node.attrib):
                x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.attrib["bounds"]))
                adb("shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))
                return
        time.sleep(3)
    raise AssertionError("Requested native control was not present")


for attempt in range(60):
    if adb("shell", "getprop", "sys.boot_completed").strip() == "1":
        break
    time.sleep(1)
else:
    raise SystemExit("Emulator did not finish booting")
adb("shell", "am", "force-stop", "pl.aridlin.liveexplain")
adb("shell", "pm", "revoke", "pl.aridlin.liveexplain", "android.permission.CAMERA")
adb("logcat", "-c")
adb("shell", "input", "keyevent", "82")
adb("shell", "am", "start", "-n", "pl.aridlin.liveexplain/.MainActivity")
time.sleep(2)
tap(lambda a: a.get("text") == "Połączenie")
tap(lambda a: a.get("text") == "Skanuj kod QR")
time.sleep(2)
tap(lambda a: "permission_allow_foreground_only_button" in a.get("resource-id", ""))
time.sleep(3)
activity = adb("shell", "dumpsys", "activity", "activities")
errors = adb("logcat", "-d", "-s", "AndroidRuntime")
assert "FATAL EXCEPTION" not in errors, errors
assert any(
    "CaptureActivity" in line and ("mResumed" in line or "topResumed" in line)
    for line in activity.splitlines()
), "Scanner not resumed"
adb("shell", "input", "keyevent", "4")
time.sleep(1)
assert "FATAL EXCEPTION" not in adb("logcat", "-d", "-s", "AndroidRuntime")
print("Standalone scanner opened, requested permission, stayed alive, and returned to the reader.")
