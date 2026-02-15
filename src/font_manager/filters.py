"""
Font filtering engine.

Provides a flexible filter_fonts() function that accepts multiple criteria
and returns only the fonts matching ALL specified conditions.
"""

from __future__ import annotations

from typing import Callable

from .models import FontInfo


def filter_fonts(
    fonts: list[FontInfo],
    *,
    # ── Identity filters ───────────────────────────────────────
    family: str | None = None,
    family_contains: str | None = None,
    full_name: str | None = None,
    postscript_name: str | None = None,
    # ── Style filters ──────────────────────────────────────────
    is_bold: bool | None = None,
    is_italic: bool | None = None,
    is_oblique: bool | None = None,
    is_monospace: bool | None = None,
    # ── Weight / width range filters ───────────────────────────
    weight_min: int | None = None,
    weight_max: int | None = None,
    weight: int | None = None,
    weight_name: str | None = None,
    width_class: int | None = None,
    # ── Format / support filters ───────────────────────────────
    format: str | None = None,
    supports_latin: bool | None = None,
    # ── Custom predicate ───────────────────────────────────────
    custom: Callable[[FontInfo], bool] | None = None,
) -> list[FontInfo]:
    """
    Filter a list of FontInfo objects by any combination of criteria.

    All non-None criteria must match (AND logic).  String comparisons
    are case-insensitive.

    Parameters
    ----------
    fonts : list[FontInfo]
        The font list to filter (e.g. from get_all_fonts()).
    family : str, optional
        Exact match on the font family name (case-insensitive).
    family_contains : str, optional
        Substring match on the font family name (case-insensitive).
    full_name : str, optional
        Exact match on the full font name (case-insensitive).
    postscript_name : str, optional
        Exact match on the PostScript name (case-insensitive).
    is_bold, is_italic, is_oblique, is_monospace : bool, optional
        Filter by style flags.
    weight_min, weight_max : int, optional
        Inclusive range for OS/2 usWeightClass (100-900).
    weight : int, optional
        Exact match on weight class.
    weight_name : str, optional
        Exact match on weight name, e.g. "Bold" (case-insensitive).
    width_class : int, optional
        Exact match on OS/2 usWidthClass (1-9).
    format : str, optional
        File extension filter, e.g. ".ttf" or ".otf" (case-insensitive).
        A leading dot is added if missing.
    supports_latin : bool, optional
        Filter by Latin script support.
    custom : callable, optional
        An arbitrary predicate: ``custom(font) -> bool``.

    Returns
    -------
    list[FontInfo]
        Fonts matching ALL specified criteria, sorted naturally.
    """
    # Build a list of predicate functions from the provided criteria
    predicates: list[Callable[[FontInfo], bool]] = []

    # ── String matchers ────────────────────────────────────────
    if family is not None:
        _fam = family.lower()
        predicates.append(lambda f, v=_fam: f.family.lower() == v)

    if family_contains is not None:
        _sub = family_contains.lower()
        predicates.append(lambda f, v=_sub: v in f.family.lower())

    if full_name is not None:
        _fn = full_name.lower()
        predicates.append(lambda f, v=_fn: f.full_name.lower() == v)

    if postscript_name is not None:
        _ps = postscript_name.lower()
        predicates.append(lambda f, v=_ps: f.postscript_name.lower() == v)

    if weight_name is not None:
        _wn = weight_name.lower()
        predicates.append(lambda f, v=_wn: f.weight_name.lower() == v)

    # ── Boolean matchers ───────────────────────────────────────
    if is_bold is not None:
        predicates.append(lambda f, v=is_bold: f.is_bold == v)

    if is_italic is not None:
        predicates.append(lambda f, v=is_italic: f.is_italic == v)

    if is_oblique is not None:
        predicates.append(lambda f, v=is_oblique: f.is_oblique == v)

    if is_monospace is not None:
        predicates.append(lambda f, v=is_monospace: f.is_monospace == v)

    if supports_latin is not None:
        predicates.append(lambda f, v=supports_latin: f.supports_latin == v)

    # ── Numeric matchers ───────────────────────────────────────
    if weight is not None:
        predicates.append(lambda f, v=weight: f.weight == v)

    if weight_min is not None:
        predicates.append(lambda f, v=weight_min: f.weight >= v)

    if weight_max is not None:
        predicates.append(lambda f, v=weight_max: f.weight <= v)

    if width_class is not None:
        predicates.append(lambda f, v=width_class: f.width_class == v)

    # ── Format matcher ─────────────────────────────────────────
    if format is not None:
        _fmt = format.lower()
        if not _fmt.startswith("."):
            _fmt = "." + _fmt
        predicates.append(lambda f, v=_fmt: f.format.lower() == v)

    # ── Custom predicate ───────────────────────────────────────
    if custom is not None:
        predicates.append(custom)

    # ── Apply all predicates (AND logic) ───────────────────────
    if not predicates:
        return sorted(fonts)

    return sorted(
        f for f in fonts if all(p(f) for p in predicates)
    )
