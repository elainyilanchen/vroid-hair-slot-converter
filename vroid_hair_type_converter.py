#!/usr/bin/env python3
"""
vroid_hair_type_converter.py
============================
Convert a .vroidcustomitem hair part from one VRoid hair slot to another.

VRoid Studio locks every exported custom item to the slot it was created in.
This tool patches all slot-specific strings in both the JSON metadata and the
binary Protocol-Buffer data files inside the archive.

Usage:
    python vroid_hair_type_converter.py <input.vroidcustomitem> <target_slot>

    target_slot is one of:
        Front | Back | Sideburns | Ahoge | Extensions | Extra | Overall_Hair

Example:
    python vroid_hair_type_converter.py earphone.vroidcustomitem Front
    → writes earphone_Front.vroidcustomitem in the same folder

Slot → internal VRoid identifier mapping (verified from real .vroidcustomitem files):
    Front        → HairFront      (前髪)
    Back         → HairBack       (後ろ髪)
    Sideburns    → HairSideburns  (横髪)
    Ahoge        → HairAhoge      (アホ毛)
    Extensions   → HairTied       (エクステ)
    Extra        → HairHanege     (ハネ毛)
    Overall_Hair → AllHair        (全体)
"""

import sys, os, zipfile, json, io, re

# ── Verified slot definitions (from real .vroidcustomitem example files) ────
# "version" = the canonical path-segment VRoid Studio expects for each slot,
# verified by inspecting the transferablegroup binary in real exported items.
SLOTS = {
    "Front":        {"key": "HairFront",     "path": "Front",     "display": "Front",        "version": "032"},
    "Back":         {"key": "HairBack",      "path": "Back",      "display": "Back",         "version": "141"},
    "Sideburns":    {"key": "HairSideburns", "path": "Sideburns", "display": "Side",         "version": "Initial"},
    "Ahoge":        {"key": "HairAhoge",     "path": "Ahoge",     "display": "Ahoge",        "version": "Initial"},
    "Extensions":   {"key": "HairTied",      "path": "Tied",      "display": "Extensions",   "version": "Initial"},
    "Extra":        {"key": "HairHanege",    "path": "Hanege",    "display": "Extra",        "version": "571"},
    "Overall_Hair": {"key": "AllHair",       "path": "AllHair",   "display": "Overall Hair", "version": "249"},
}

# ── Auto-detect slot from a typeId string ────────────────────────────────────
def detect_slot(type_id: str):
    for name, info in SLOTS.items():
        if info["key"] in type_id:
            return name
    return None

# ── protobuf varint helpers ──────────────────────────────────────────────────
def read_varint(data: bytes, pos: int):
    result, shift = 0, 0
    while True:
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7

def encode_varint(v: int) -> bytes:
    out = []
    while True:
        byte = v & 0x7F; v >>= 7
        out.append(byte | (0x80 if v else 0))
        if not v:
            return bytes(out)

# ── Recursive protobuf message patcher ──────────────────────────────────────
def patch_protobuf(data: bytes, replacements: dict) -> bytes:
    """
    Walk a protobuf message at the wire level and replace target strings,
    rebuilding every length-delimited field from the inside out so that ALL
    ancestor container lengths are automatically correct.

    Why recursive is necessary: a target string often lives inside a nested
    sub-message (e.g. the slot path is inside a 183-byte field 7).  A flat
    search-and-replace updates the string's own length prefix but leaves the
    outer container's stated size stale, causing VRoid's parser to over-read
    and consume bytes that belong to the next field — corrupting everything
    that follows (InitialId, revision UUID, etc.).

    Guard: we only recurse into a sub-message whose raw bytes actually contain
    one of the target byte sequences.  This prevents recursing into opaque
    identifiers (InitialId-…, bare revision UUIDs) that happen to be valid
    UTF-8 but are not protobuf sub-messages.
    """
    target_bytes = [k.encode("utf-8") for k in replacements]
    out = b""
    pos = 0
    while pos < len(data):
        try:
            tag, pos = read_varint(data, pos)
        except Exception:
            break

        wire = tag & 0x07

        if wire == 0:                           # varint
            val, pos = read_varint(data, pos)
            out += encode_varint(tag) + encode_varint(val)

        elif wire == 1:                         # 64-bit fixed
            out += encode_varint(tag) + data[pos:pos+8]
            pos += 8

        elif wire == 2:                         # length-delimited
            length, pos = read_varint(data, pos)
            content = data[pos:pos+length]
            pos += length

            new_content = None
            # Step 1: exact UTF-8 string replacement
            try:
                s = content.decode("utf-8")
                if s in replacements:
                    new_content = replacements[s].encode("utf-8")
            except (UnicodeDecodeError, AttributeError):
                pass

            if new_content is None:
                # Step 2: recurse only if a target byte sequence is present —
                # this correctly skips opaque strings like InitialId-… and
                # bare revision UUIDs whose bytes never contain our targets.
                if any(t in content for t in target_bytes):
                    try:
                        new_content = patch_protobuf(content, replacements)
                    except Exception:
                        new_content = content
                else:
                    new_content = content

            out += encode_varint(tag) + encode_varint(len(new_content)) + new_content

        elif wire == 5:                         # 32-bit fixed
            out += encode_varint(tag) + data[pos:pos+4]
            pos += 4

        else:                                   # unknown — copy rest verbatim
            out += data[pos:]
            break

    return out


# ── Extract the version segment from an existing path string ────────────────
def extract_version(path_str: str) -> str:
    """
    From a path like  pixiv/VRoid/Hair/N00/Sideburns/Initial/TransferableGroupType...
    extract the version segment ('Initial', '032', '141', …).
    Falls back to 'Initial' if parsing fails.
    """
    # Pattern: pixiv/VRoid/Hair/N00/<TypeFolder>/<VERSION>/...
    m = re.search(r'pixiv/VRoid/Hair/N00/[^/]+/([^/]+)/', path_str)
    if m:
        return m.group(1)
    return "Initial"


# ── Build the replacement dict for src → dst ─────────────────────────────────
def build_replacements(src: dict, dst: dict, src_version: str) -> dict:
    """
    src_version  – the version segment actually found in the source binary
                   (e.g. 'Initial' for a Sideburns earphone).
    dst["version"] – the canonical version VRoid expects for the target slot
                   (e.g. '032' for Front, '141' for Back, '571' for Hanege …).
    Using the wrong target version is what made VRoid reject items previously.
    """
    sk, sp, sd = src["key"], src["path"], src["display"]
    dk, dp, dd, dv = dst["key"], dst["path"], dst["display"], dst["version"]
    r = {}

    # Display name  ("Side" → "Front", etc.)
    r[sd] = dd

    # Bare key  ("HairSideburns" → "HairFront")
    r[sk] = dk

    # transferablegroup type strings
    r[f"Model.N00.TransferableGroup.Level1.{sk}"] = \
        f"Model.N00.TransferableGroup.Level1.{dk}"
    r[f"TransferableGroupType.N00.Level1.{sk}"] = \
        f"TransferableGroupType.N00.Level1.{dk}"
    # Path: use src_version to find the source path, dv (dst canonical) for target
    r[f"pixiv/VRoid/Hair/N00/{sp}/{src_version}/TransferableGroupType.N00.Level1.{sk}.transferablegroup"] = \
        f"pixiv/VRoid/Hair/N00/{dp}/{dv}/TransferableGroupType.N00.Level1.{dk}.transferablegroup"

    # transferable type strings
    r[f"Model.N00.Transferable.{sk}"] = \
        f"Model.N00.Transferable.{dk}"
    r[f"TransferableType.N00.{sk}"] = \
        f"TransferableType.N00.{dk}"
    r[f"pixiv/VRoid/Hair/N00/{sp}/{src_version}/TransferableType.N00.{sk}.transferable"] = \
        f"pixiv/VRoid/Hair/N00/{dp}/{dv}/TransferableType.N00.{dk}.transferable"

    return r


# ── JSON meta patcher ────────────────────────────────────────────────────────
def patch_json(raw: bytes, replacements: dict) -> bytes:
    obj = json.loads(raw.decode("utf-8"))
    def walk(o):
        if isinstance(o, dict):
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(i) for i in o]
        if isinstance(o, str) and o in replacements:
            return replacements[o]
        return o
    return json.dumps(walk(obj), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


# ── Main conversion ──────────────────────────────────────────────────────────
def convert(input_path: str, target_slot_name: str) -> str:
    if target_slot_name not in SLOTS:
        raise ValueError(
            f"Unknown slot '{target_slot_name}'.\n"
            f"Valid options: {', '.join(SLOTS)}"
        )

    # Detect source slot
    with zipfile.ZipFile(input_path, "r") as zf:
        meta = json.loads(zf.read("v1customitem/meta.json"))
    type_id = meta.get("rootTransferableGroupTypeId", "")
    src_slot_name = detect_slot(type_id)
    if src_slot_name is None:
        raise ValueError(f"Cannot detect source slot from typeId: '{type_id}'")

    print(f"  Source slot : {src_slot_name:12s}  ({SLOTS[src_slot_name]['key']})")
    print(f"  Target slot : {target_slot_name:12s}  ({SLOTS[target_slot_name]['key']})")

    if src_slot_name == target_slot_name:
        print("  Already in the target slot – nothing to do.")
        return input_path

    # Extract path version from the source binary
    version = "Initial"
    with zipfile.ZipFile(input_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".transferablegroup"):
                data = zf.read(name)
                # scan for the path string
                m = re.search(
                    rb'pixiv/VRoid/Hair/N00/[^/\x00]+/([^/\x00]+)/',
                    data
                )
                if m:
                    version = m.group(1).decode("utf-8", errors="replace")
                break
    print(f"  Path version: {version}")

    replacements = build_replacements(SLOTS[src_slot_name], SLOTS[target_slot_name], version)

    print(f"\n  Replacement map ({len(replacements)} entries):")
    for k, v in replacements.items():
        print(f"    {k!r:65s} → {v!r}")

    # Build patched zip
    in_buf  = io.BytesIO(open(input_path, "rb").read())
    out_buf = io.BytesIO()

    with zipfile.ZipFile(in_buf, "r") as zin, \
         zipfile.ZipFile(out_buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:

        for item in zin.infolist():
            raw = zin.read(item.filename)
            label = ""

            if item.filename.endswith(".json"):
                raw = patch_json(raw, replacements)
                label = " [JSON patched]"

            elif item.filename.endswith((".transferablegroup", ".transferable")):
                raw = patch_protobuf(raw, replacements)
                label = " [binary patched]"

            print(f"  + {item.filename}{label}")
            zout.writestr(item, raw)

    # Write output next to input; fall back to cwd if read-only
    base = os.path.splitext(os.path.basename(input_path))[0]
    out_name = f"{base}_{target_slot_name}.vroidcustomitem"
    try:
        candidate = os.path.join(os.path.dirname(os.path.abspath(input_path)), out_name)
        open(candidate, "wb").close()
        out_path = candidate
    except OSError:
        out_path = os.path.join(os.getcwd(), out_name)

    with open(out_path, "wb") as f:
        f.write(out_buf.getvalue())

    print(f"\n  ✓ Saved → {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
