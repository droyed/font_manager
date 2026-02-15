"""
Font metadata extraction using fontTools.

Opens each discovered font file, reads internal OpenType tables,
and produces a fully-populated FontInfo object.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fontTools.ttLib import TTFont

from .discovery import DiscoveredFont
from .models import FontInfo
from .utils import (
    extract_english_name,
    is_latin_font,
    weight_class_to_name,
)

logger = logging.getLogger(__name__)

# Suppress noisy fontTools timestamp warnings
logging.getLogger("fontTools.ttLib.tables._h_e_a_d").setLevel(logging.ERROR)

# ── OS/2 fsSelection bit masks ─────────────────────────────────
_FS_ITALIC  = 1 << 0   # bit 0
_FS_BOLD    = 1 << 5   # bit 5
_FS_OBLIQUE = 1 << 9   # bit 9

# ── head macStyle bit masks (fallback) ─────────────────────────
_MAC_BOLD   = 1 << 0
_MAC_ITALIC = 1 << 1


def _extract_single(tt: TTFont, discovered: DiscoveredFont) -> FontInfo:
    """
    Extract metadata from an already-opened TTFont instance.
    """
    path = discovered.file_path
    suffix = path.suffix.lower()

    # ── name table ─────────────────────────────────────────────
    name_table = tt.get("name")
    family      = extract_english_name(name_table, 1)   # nameID 1: Font Family
    subfamily   = extract_english_name(name_table, 2)   # nameID 2: Font Subfamily
    full_name   = extract_english_name(name_table, 4)   # nameID 4: Full Name
    ps_name     = extract_english_name(name_table, 6)   # nameID 6: PostScript Name

    # Prefer nameID 16 (Typographic Family) if available — it's more reliable
    # for grouping variants under one family.
    typo_family = extract_english_name(name_table, 16)
    if typo_family:
        family = typo_family

    # ── OS/2 table ─────────────────────────────────────────────
    os2 = tt.get("OS/2")
    weight_class = 400
    width_class = 5
    fs_selection = 0

    if os2 is not None:
        weight_class = getattr(os2, "usWeightClass", 400) or 400
        width_class  = getattr(os2, "usWidthClass", 5) or 5
        fs_selection = getattr(os2, "fsSelection", 0) or 0

    # ── head table (fallback for style bits) ───────────────────
    head = tt.get("head")
    mac_style = 0
    if head is not None:
        mac_style = getattr(head, "macStyle", 0) or 0

    # ── Determine bold / italic / oblique ──────────────────────
    is_bold    = bool(fs_selection & _FS_BOLD)    or bool(mac_style & _MAC_BOLD)
    is_italic  = bool(fs_selection & _FS_ITALIC)  or bool(mac_style & _MAC_ITALIC)
    is_oblique = bool(fs_selection & _FS_OBLIQUE)

    # ── Monospace detection (post table) ───────────────────────
    post = tt.get("post")
    is_monospace = False
    if post is not None:
        is_monospace = bool(getattr(post, "isFixedPitch", 0))

    # ── Latin support ──────────────────────────────────────────
    supports_latin = is_latin_font(tt)

    # ── Build FontInfo ─────────────────────────────────────────
    return FontInfo(
        family=family or discovered.matplotlib_family,
        subfamily=subfamily,
        full_name=full_name or family,
        postscript_name=ps_name,
        file_path=path,
        format=suffix,
        is_bold=is_bold,
        is_italic=is_italic,
        is_oblique=is_oblique,
        is_monospace=is_monospace,
        weight=weight_class,
        weight_name=weight_class_to_name(weight_class),
        width_class=width_class,
        supports_latin=supports_latin,
        matplotlib_name=discovered.matplotlib_name,
    )


def extract_metadata(discovered: DiscoveredFont) -> list[FontInfo]:
    """
    Given a DiscoveredFont, open the file and extract FontInfo objects.

    For .ttc/.otc collections, each sub-font is returned as a separate entry.
    For .ttf/.otf files, a single-element list is returned.

    Returns an empty list if the file cannot be parsed.
    """
    path = discovered.file_path
    suffix = path.suffix.lower()
    results: list[FontInfo] = []

    try:
        if suffix in (".ttc", ".otc"):
            # TrueType / OpenType collection — iterate sub-fonts
            from fontTools.ttLib import TTCollection

            try:
                collection = TTCollection(str(path))
                for i, tt in enumerate(collection.fonts):
                    try:
                        info = _extract_single(tt, discovered)
                        results.append(info)
                    except Exception as exc:
                        logger.warning(
                            "Failed to extract sub-font %d from %s: %s", i, path, exc
                        )
                collection.close()
            except Exception:
                # Fallback: try opening as a regular TTFont with fontNumber=0
                try:
                    tt = TTFont(str(path), fontNumber=0)
                    info = _extract_single(tt, discovered)
                    results.append(info)
                    tt.close()
                except Exception as exc:
                    logger.warning("Failed to parse collection %s: %s", path, exc)
        else:
            tt = TTFont(str(path))
            info = _extract_single(tt, discovered)
            results.append(info)
            tt.close()

    except Exception as exc:
        logger.warning("Failed to open font file %s: %s", path, exc)

    return results


def extract_all_metadata(
    discovered_fonts: list[DiscoveredFont],
) -> list[FontInfo]:
    """
    Extract metadata for a list of discovered fonts.
    Skips fonts that fail to parse. Deduplicates by (full_name, file_size)
    to handle symlinks and multiple copies of the same font.
    """
    all_fonts: list[FontInfo] = []
    seen: set[tuple[str, str, int]] = set()  # (full_name, subfamily, weight)

    for d in discovered_fonts:
        fonts = extract_metadata(d)
        for f in fonts:
            key = (f.full_name, f.subfamily, f.weight)
            if key not in seen:
                seen.add(key)
                all_fonts.append(f)

    logger.info(
        "Extracted metadata for %d unique font faces (from %d files)",
        len(all_fonts),
        len(discovered_fonts),
    )
    return all_fonts
