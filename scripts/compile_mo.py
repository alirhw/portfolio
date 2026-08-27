"""
Standalone helper to compile .po gettext files to binary .mo format
with full UTF-8 charset metadata header support and proper character preservation.
"""

import pathlib
import struct
import sys


def unescape(s: str) -> str:
    return (
        s.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\r", "\r")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def parse_po_file(po_path: pathlib.Path):
    lines = po_path.read_text(encoding="utf-8").splitlines()
    entries = {}
    current_msgid = None
    current_msgstr = None
    collecting = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            if current_msgid is not None and current_msgstr is not None:
                entries[unescape(current_msgid)] = unescape(current_msgstr)
                current_msgid = None
                current_msgstr = None
                collecting = None
            continue

        if line.startswith('msgid "'):
            current_msgid = line[7:-1]
            collecting = "msgid"
        elif line.startswith('msgstr "'):
            current_msgstr = line[8:-1]
            collecting = "msgstr"
        elif line.startswith('"') and line.endswith('"') and collecting:
            if collecting == "msgid":
                current_msgid += line[1:-1]
            elif collecting == "msgstr":
                current_msgstr += line[1:-1]

    if current_msgid is not None and current_msgstr is not None:
        entries[unescape(current_msgid)] = unescape(current_msgstr)

    if "" not in entries:
        entries[""] = (
            "Content-Type: text/plain; charset=UTF-8\n"
            "Content-Transfer-Encoding: 8bit\n"
            "Plural-Forms: nplurals=2; plural=(n > 1);\n"
        )

    return entries


def write_mo_file(entries: dict, mo_path: pathlib.Path):
    # Sort items by original msgid bytes (b"" first)
    raw_entries = [(k.encode("utf-8"), v.encode("utf-8")) for k, v in entries.items()]
    raw_entries.sort(key=lambda x: x[0])

    keys = [k for k, v in raw_entries]
    values = [v for k, v in raw_entries]

    keystr = b"\x00".join(keys) + b"\x00"
    valuestr = b"\x00".join(values) + b"\x00"

    koffsets = []
    ko = 0
    for k in keys:
        koffsets.append((len(k), ko))
        ko += len(k) + 1

    voffsets = []
    vo = 0
    for v in values:
        voffsets.append((len(v), vo))
        vo += len(v) + 1

    header_size = 7 * 4
    table_size = len(raw_entries) * 8
    key_table_offset = header_size
    val_table_offset = header_size + table_size
    strings_offset = val_table_offset + table_size

    koffsets = [(l, o + strings_offset) for l, o in koffsets]
    voffsets = [(l, o + strings_offset + len(keystr)) for l, o in voffsets]

    mo = bytearray()
    mo += struct.pack("<I", 0x950412DE)  # Magic
    mo += struct.pack("<I", 0)  # Version
    mo += struct.pack("<I", len(raw_entries))  # String count
    mo += struct.pack("<I", key_table_offset)  # Key table offset
    mo += struct.pack("<I", val_table_offset)  # Value table offset
    mo += struct.pack("<I", 0)  # Hash table size
    mo += struct.pack("<I", 0)  # Hash table offset

    for l, o in koffsets:
        mo += struct.pack("<II", l, o)
    for l, o in voffsets:
        mo += struct.pack("<II", l, o)

    mo += keystr
    mo += valuestr

    mo_path.write_bytes(mo)
    print(f"Compiled {len(raw_entries)} translation entries to {mo_path}")


if __name__ == "__main__":
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    locale_dir = base_dir / "locale"
    for po_file in locale_dir.glob("*/LC_MESSAGES/django.po"):
        mo_file = po_file.with_suffix(".mo")
        data = parse_po_file(po_file)
        write_mo_file(data, mo_file)
