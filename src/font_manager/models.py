"""
Data models for font metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, asdict
from pathlib import Path
from typing import Any


@dataclass(frozen=True, order=True)
class FontInfo:
    """
    Immutable representation of a single font face and its metadata.

    Ordering is by (family, weight, is_italic, is_bold) so that sorting
    a list of FontInfo objects produces a natural grouping.
    """

    # ── Identity ───────────────────────────────────────────────
    family: str = ""
    subfamily: str = ""          # e.g. "Bold Italic"
    full_name: str = ""          # e.g. "Arial Bold Italic"
    postscript_name: str = ""    # e.g. "Arial-BoldItalic"

    # ── File ───────────────────────────────────────────────────
    file_path: Path = Path()
    format: str = ""             # ".ttf", ".otf", ".ttc"

    # ── Style flags ────────────────────────────────────────────
    is_bold: bool = False
    is_italic: bool = False
    is_oblique: bool = False
    is_monospace: bool = False

    # ── Numeric metrics ────────────────────────────────────────
    weight: int = 400            # OS/2 usWeightClass  (100-900)
    weight_name: str = "Regular" # human-readable weight label
    width_class: int = 5         # OS/2 usWidthClass   (1-9)

    # ── Character-set / script support ─────────────────────────
    supports_latin: bool = True

    # ── Matplotlib integration ─────────────────────────────────
    matplotlib_name: str = ""    # name matplotlib uses to reference the font

    # ── Convenience helpers ────────────────────────────────────
    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dict (Path becomes str)."""
        d = asdict(self)
        d["file_path"] = str(d["file_path"])
        return d

    @classmethod
    def field_names(cls) -> list[str]:
        """Return the list of field names."""
        return [f.name for f in fields(cls)]

    def __str__(self) -> str:
        style_parts: list[str] = []
        if self.is_bold:
            style_parts.append("Bold")
        if self.is_italic:
            style_parts.append("Italic")
        if self.is_oblique:
            style_parts.append("Oblique")
        if self.is_monospace:
            style_parts.append("Mono")
        style = ", ".join(style_parts) if style_parts else "Regular"
        return f"{self.family} [{style}] (weight={self.weight}, path={self.file_path.name})"

    def __repr__(self) -> str:
        return (
            f"FontInfo(family={self.family!r}, full_name={self.full_name!r}, "
            f"weight={self.weight}, is_bold={self.is_bold}, is_italic={self.is_italic})"
        )
