"""
Font discovery: find all font files that matplotlib can use.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from matplotlib.font_manager import fontManager

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredFont:
    """Lightweight record from matplotlib's font manager."""

    file_path: Path
    matplotlib_family: str
    matplotlib_style: str   # "normal", "italic", "oblique"
    matplotlib_weight: str | int  # e.g. "bold", 400, 700

    @property
    def matplotlib_name(self) -> str:
        return self.matplotlib_family


def discover_fonts() -> list[DiscoveredFont]:
    """
    Iterate matplotlib's font manager and return one DiscoveredFont per
    registered font file.

    Deduplicates by file path so each physical file appears only once.
    """
    seen_paths: set[str] = set()
    results: list[DiscoveredFont] = []

    for entry in fontManager.ttflist:
        path_str = entry.fname
        if path_str in seen_paths:
            continue
        seen_paths.add(path_str)

        path = Path(path_str)
        if not path.exists():
            logger.debug("Font file does not exist, skipping: %s", path)
            continue

        # Only process TrueType / OpenType files
        suffix = path.suffix.lower()
        if suffix not in (".ttf", ".otf", ".ttc", ".otc"):
            logger.debug("Skipping non-TrueType/OpenType file: %s", path)
            continue

        results.append(
            DiscoveredFont(
                file_path=path,
                matplotlib_family=entry.name,
                matplotlib_style=entry.style,
                matplotlib_weight=entry.weight,
            )
        )

    logger.info("Discovered %d unique font files from matplotlib", len(results))
    return results
