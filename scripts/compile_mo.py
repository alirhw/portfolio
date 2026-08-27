"""
Standalone helper to compile .po gettext files to binary .mo format
without requiring GNU gettext/msgfmt on the host OS.
"""

import pathlib
import struct
import sys


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
                if current_msgid != "":
                    entries[current_msgid] = current_msgstr
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

    if current_msgid is not None and current_msgstr is not None and current_msgid != "":
        entries[current_msgid] = current_msgstr

    return entries


def write_mo_file(entries: dict, mo_path: pathlib.Path):
    sorted_items = sorted(
        [(k.encode("utf-8"), v.encode("utf-8")) for k, v in entries.items()]
    )

    keys = [k for k, v in sorted_items]
    values = [v for k, v in sorted_items]

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
    table_size = len(sorted_items) * 8
    key_table_offset = header_size
    val_table_offset = header_size + table_size
    strings_offset = val_table_offset + table_size

    koffsets = [(l, o + strings_offset) for l, o in koffsets]
    voffsets = [(l, o + strings_offset + len(keystr)) for l, o in voffsets]

    mo = bytearray()
    mo += struct.pack("<I", 0x950412DE)  # GNU gettext magic number (little endian)
    mo += struct.pack("<I", 0)  # Format revision
    mo += struct.pack("<I", len(sorted_items))  # N strings
    mo += struct.pack("<I", key_table_offset)
    mo += struct.pack("<I", val_table_offset)
    mo += struct.pack("<I", 0)  # Hashing table size
    mo += struct.pack("<I", 0)  # Hashing table offset

    for l, o in koffsets:
        mo += struct.pack("<II", l, o)
    for l, o in voffsets:
        mo += struct.pack("<II", l, o)

    mo += keystr
    mo += valuestr

    mo_path.write_bytes(mo)
    print(f"Compiled {len(sorted_items)} translation entries to {mo_path}")


if __name__ == "__main__":
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    po_file = base_dir / "locale" / "fa" / "LC_MESSAGES" / "django.po"
    mo_file = base_dir / "locale" / "fa" / "LC_MESSAGES" / "django.mo"

    if po_file.exists():
        data = parse_po_file(po_file)
        write_mo_file(data, mo_file)
    else:
        print(f"PO file not found: {po_file}", file=sys.stderr)
        sys.exit(1)
