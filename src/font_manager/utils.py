"""
Utility helpers for font metadata extraction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fontTools.ttLib import TTFont

# ── Weight class → human-readable name ─────────────────────────

WEIGHT_MAP: dict[int, str] = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black",
}


def weight_class_to_name(val: int) -> str:
    """
    Map an OS/2 usWeightClass integer (100-900) to a human-readable name.
    Values between standard stops are rounded to the nearest standard stop.
    """
    if val <= 0:
        return "Unknown"
    # Find the closest standard weight
    stops = sorted(WEIGHT_MAP.keys())
    closest = min(stops, key=lambda s: abs(s - val))
    return WEIGHT_MAP[closest]


# ── Width class → human-readable name ──────────────────────────

WIDTH_MAP: dict[int, str] = {
    1: "UltraCondensed",
    2: "ExtraCondensed",
    3: "Condensed",
    4: "SemiCondensed",
    5: "Normal",
    6: "SemiExpanded",
    7: "Expanded",
    8: "ExtraExpanded",
    9: "UltraExpanded",
}


def width_class_to_name(val: int) -> str:
    """Map an OS/2 usWidthClass integer (1-9) to a human-readable name."""
    return WIDTH_MAP.get(val, "Unknown")


# ── English name extraction from the name table ───────────────

# Priority order for finding English strings:
#   1. Windows / Unicode BMP / English-US  (3, 1, 0x0409)
#   2. Mac / Roman / English               (1, 0, 0)
#   3. Unicode / any                        (0, *, 0)
_PLATFORM_PRIORITY = [
    (3, 1, 0x0409),   # Windows, Unicode BMP, en-US
    (1, 0, 0),        # Macintosh, Roman, English
]


def extract_english_name(name_table, name_id: int) -> str:
    """
    Pull the English-language string for a given nameID from the name table.

    Falls back through platform priorities, then accepts the first available
    record for that nameID if no English-specific record is found.
    """
    if name_table is None:
        return ""

    # First pass: check preferred platforms in order
    for plat_id, enc_id, lang_id in _PLATFORM_PRIORITY:
        for record in name_table.names:
            if (
                record.nameID == name_id
                and record.platformID == plat_id
                and record.platEncID == enc_id
                and record.langID == lang_id
            ):
                try:
                    return record.toUnicode()
                except Exception:
                    continue

    # Second pass: any Unicode platform (platformID 0)
    for record in name_table.names:
        if record.nameID == name_id and record.platformID == 0:
            try:
                return record.toUnicode()
            except Exception:
                continue

    # Third pass: take whatever is available
    for record in name_table.names:
        if record.nameID == name_id:
            try:
                return record.toUnicode()
            except Exception:
                continue

    return ""


# ── Latin support detection ────────────────────────────────────

# Basic Latin codepoints: A-Z, a-z, 0-9, space, common punctuation
_BASIC_LATIN_CODEPOINTS = set(range(0x0020, 0x007F))  # ASCII printable
_REQUIRED_SAMPLE = set(range(0x0041, 0x005B)) | set(range(0x0061, 0x007B))  # A-Z + a-z


def is_latin_font(tt: "TTFont") -> bool:
    """
    Determine whether a font supports the Latin script.

    Strategy:
      1. Check OS/2 ulCodePageRange1 bit 0 (Latin 1 / Code Page 1252).
      2. Fallback: inspect the cmap table for basic Latin codepoints (A-Z, a-z).
    """
    # Method 1: OS/2 codepage range
    try:
        os2 = tt.get("OS/2")
        if os2 is not None:
            cp_range = getattr(os2, "ulCodePageRange1", 0)
            if cp_range & 1:  # bit 0 = Latin 1
                return True
    except Exception:
        pass

    # Method 2: cmap inspection
    try:
        cmap = tt.getBestCmap()
        if cmap is not None:
            mapped = set(cmap.keys())
            # Require at least all A-Z and a-z
            if _REQUIRED_SAMPLE.issubset(mapped):
                return True
    except Exception:
        pass

    return False
