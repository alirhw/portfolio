"""
Python-based PO to MO compiler for environments without gettext msgfmt installed.
Based on standard GNU gettext MO binary specifications.
"""

import ast
import os
import struct
import sys


def parse_po_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    entries = {}
    current_msgid = None
    current_msgstr = None
    state = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("msgid "):
            if current_msgid is not None and current_msgstr is not None:
                entries[current_msgid] = current_msgstr
            raw_val = line[6:].strip()
            current_msgid = ast.literal_eval(raw_val)
            current_msgstr = None
            state = "msgid"
        elif line.startswith("msgstr "):
            raw_val = line[7:].strip()
            current_msgstr = ast.literal_eval(raw_val)
            state = "msgstr"
        elif line.startswith('"'):
            val = ast.literal_eval(line)
            if state == "msgid":
                current_msgid += val
            elif state == "msgstr":
                current_msgstr += val

    if current_msgid is not None and current_msgstr is not None:
        entries[current_msgid] = current_msgstr

    return entries


def make_mo(entries, outfile):
    keys = sorted(entries.keys())
    offsets = []
    ids = b""
    strs = b""

    for key in keys:
        encoded_key = key.encode("utf-8")
        encoded_val = entries[key].encode("utf-8")

        # Key offset & length
        offsets.append((len(ids), len(encoded_key), len(strs), len(encoded_val)))
        ids += encoded_key + b"\x00"
        strs += encoded_val + b"\x00"

    num_strings = len(keys)
    keystart = 7 * 4
    valuestart = keystart + num_strings * 8
    keyoffsets_start = valuestart + num_strings * 8
    valueoffsets_start = keyoffsets_start + len(ids)

    # Magic: 0x950412de
    header = struct.pack(
        "<Iiiiiii",
        0x950412DE,  # Magic number
        0,  # Format revision
        num_strings,  # Number of strings
        keystart,  # Offset of table with original strings
        valuestart,  # Offset of table with translation strings
        0,  # Size of hashing table
        0,  # Offset of hashing table
    )

    with open(outfile, "wb") as f:
        f.write(header)
        for o1, l1, _o2, _l2 in offsets:
            f.write(struct.pack("<ii", l1, keyoffsets_start + o1))
        for _o1, _l1, o2, l2 in offsets:
            f.write(struct.pack("<ii", l2, valueoffsets_start + o2))
        f.write(ids)
        f.write(strs)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    po_file = os.path.join(base_dir, "locale", "fa", "LC_MESSAGES", "django.po")
    mo_file = os.path.join(base_dir, "locale", "fa", "LC_MESSAGES", "django.mo")

    if not os.path.exists(po_file):
        print(f"File not found: {po_file}")
        sys.exit(1)

    entries = parse_po_file(po_file)
    make_mo(entries, mo_file)
    print(f"Compiled {len(entries)} translation messages into {mo_file}")


if __name__ == "__main__":
    main()
