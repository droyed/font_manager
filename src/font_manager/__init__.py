"""
font_manager — Discover, inspect, and filter system fonts for matplotlib.

Usage
-----
    from font_manager import get_all_fonts, filter_fonts

    fonts = get_all_fonts()
    bold_mono = filter_fonts(fonts, is_bold=True, is_monospace=True)

    for f in bold_mono:
        print(f.family, f.full_name, f.weight)
"""

from __future__ import annotations

import logging
from typing import Callable

from .models import FontInfo
from .discovery import discover_fonts
from .metadata import extract_all_metadata
from .filters import filter_fonts as _filter_fonts

__all__ = [
    "FontInfo",
    "get_all_fonts",
    "filter_fonts",
    "get_font_families",
    "get_font_by_name",
    "clear_cache",
]

logger = logging.getLogger(__name__)

# ── Module-level cache ─────────────────────────────────────────
_cache: list[FontInfo] | None = None
_cache_latin_only: bool | None = None


def clear_cache() -> None:
    """Clear the cached font list, forcing a re-scan on next call."""
    global _cache, _cache_latin_only
    _cache = None
    _cache_latin_only = None


def get_all_fonts(latin_only: bool = True) -> list[FontInfo]:
    """
    Discover all fonts matplotlib can use and extract their full metadata.

    Parameters
    ----------
    latin_only : bool, default True
        If True, only return fonts that support the Latin script
        (English and most Western European languages).

    Returns
    -------
    list[FontInfo]
        Sorted list of font metadata objects.

    Notes
    -----
    Results are cached in memory.  Call ``clear_cache()`` to force a
    fresh scan (e.g. after installing new fonts).
    """
    global _cache, _cache_latin_only

    if _cache is not None and _cache_latin_only == latin_only:
        return list(_cache)  # return a copy

    logger.info("Scanning fonts (latin_only=%s) ...", latin_only)

    # Step 1: Discover font files via matplotlib
    discovered = discover_fonts()

    # Step 2: Extract deep metadata via fontTools
    all_fonts = extract_all_metadata(discovered)

    # Step 3: Optionally filter to Latin-only
    if latin_only:
        all_fonts = [f for f in all_fonts if f.supports_latin]

    # Step 4: Sort and cache
    all_fonts.sort()
    _cache = all_fonts
    _cache_latin_only = latin_only

    logger.info("Font scan complete: %d fonts available", len(all_fonts))
    return list(_cache)


def filter_fonts(
    fonts: list[FontInfo] | None = None,
    *,
    family: str | None = None,
    family_contains: str | None = None,
    full_name: str | None = None,
    postscript_name: str | None = None,
    is_bold: bool | None = None,
    is_italic: bool | None = None,
    is_oblique: bool | None = None,
    is_monospace: bool | None = None,
    weight_min: int | None = None,
    weight_max: int | None = None,
    weight: int | None = None,
    weight_name: str | None = None,
    width_class: int | None = None,
    format: str | None = None,
    supports_latin: bool | None = None,
    custom: Callable[[FontInfo], bool] | None = None,
) -> list[FontInfo]:
    """
    Filter fonts by any combination of criteria.

    If ``fonts`` is None, automatically calls ``get_all_fonts()`` first.

    See ``filters.filter_fonts`` for full parameter documentation.
    """
    if fonts is None:
        fonts = get_all_fonts()

    return _filter_fonts(
        fonts,
        family=family,
        family_contains=family_contains,
        full_name=full_name,
        postscript_name=postscript_name,
        is_bold=is_bold,
        is_italic=is_italic,
        is_oblique=is_oblique,
        is_monospace=is_monospace,
        weight_min=weight_min,
        weight_max=weight_max,
        weight=weight,
        weight_name=weight_name,
        width_class=width_class,
        format=format,
        supports_latin=supports_latin,
        custom=custom,
    )


def get_font_families(latin_only: bool = True) -> list[str]:
    """
    Return a sorted list of unique font family names.

    Parameters
    ----------
    latin_only : bool, default True
        If True, only include families with Latin script support.

    Returns
    -------
    list[str]
        Unique, sorted family names.
    """
    fonts = get_all_fonts(latin_only=latin_only)
    families = sorted({f.family for f in fonts})
    return families


def get_font_by_name(name: str) -> FontInfo | None:
    """
    Look up a single font by its full name (case-insensitive).

    Searches full_name first, then family name.

    Returns None if not found.
    """
    fonts = get_all_fonts()
    name_lower = name.lower()

    # Exact match on full_name
    for f in fonts:
        if f.full_name.lower() == name_lower:
            return f

    # Exact match on family (return first variant)
    for f in fonts:
        if f.family.lower() == name_lower:
            return f

    # Substring match on full_name (return first)
    for f in fonts:
        if name_lower in f.full_name.lower():
            return f

    return None
