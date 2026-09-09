"""Check actual DEX definitions, not compile-time references or instrumentation classpaths."""

import argparse
import struct
import zipfile


def definitions(apk):
    result = set()
    with zipfile.ZipFile(apk) as archive:
        for name in archive.namelist():
            if not name.endswith(".dex"):
                continue
            data = archive.read(name)
            string_count, string_offset, type_count, type_offset = struct.unpack_from("<4I", data, 56)
            class_count, class_offset = struct.unpack_from("<2I", data, 96)
            for index in range(class_count):
                type_index = struct.unpack_from("<I", data, class_offset + index * 32)[0]
                string_index = struct.unpack_from("<I", data, type_offset + type_index * 4)[0]
                offset = struct.unpack_from("<I", data, string_offset + string_index * 4)[0]
                while data[offset] & 128:
                    offset += 1
                offset += 1
                result.add(data[offset : data.index(0, offset)].decode("utf-8"))
    return result


REQUIRED = {
    "Lpl/aridlin/liveexplain/MainActivity;",
    "Lpl/aridlin/liveexplain/ControlState;",
    "Lpl/aridlin/liveexplain/ControlIcon;",
    "Lpl/aridlin/liveexplain/Connection;",
    "Lpl/aridlin/liveexplain/Discovery;",
    "Lpl/aridlin/liveexplain/CommandLedger;",
}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("apk")
    args = parser.parse_args()
    missing = REQUIRED - definitions(args.apk)
    if missing:
        raise SystemExit("Missing APK runtime classes: " + ", ".join(sorted(missing)))
    print("Reader, local connection, discovery and command ledger are defined in the APK.")
