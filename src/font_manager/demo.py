#!/usr/bin/env python3
"""
demo.py — Demonstrates the font_manager module.

Exercises: discovery, metadata inspection, filtering, matplotlib integration.
"""

import sys
import os
import warnings

# Allow running from the same directory as font_manager/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress fontTools timestamp warnings
warnings.filterwarnings("ignore", message=".*timestamp seems very low.*")

from font_manager import get_all_fonts, filter_fonts, get_font_families, get_font_by_name, FontInfo


def separator(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    # ─────────────────────────────────────────────────────────────
    # 1. List all available Latin fonts
    # ─────────────────────────────────────────────────────────────
    separator("1. Discover All Latin Fonts")

    fonts = get_all_fonts(latin_only=True)
    print(f"Total Latin fonts found: {len(fonts)}\n")

    print(f"{'Family':<35} {'Subfamily':<18} {'Weight':<8} {'File'}")
    print(f"{'-'*35} {'-'*18} {'-'*8} {'-'*30}")
    for f in fonts[:15]:
        print(f"{f.family:<35} {f.subfamily:<18} {f.weight:<8} {f.file_path.name}")
    if len(fonts) > 15:
        print(f"  ... and {len(fonts) - 15} more fonts")

    # ─────────────────────────────────────────────────────────────
    # 2. Full metadata for a single font
    # ─────────────────────────────────────────────────────────────
    separator("2. Full Metadata Inspection")

    sample = fonts[0] if fonts else None
    if sample:
        print(f"  Family:          {sample.family}")
        print(f"  Subfamily:       {sample.subfamily}")
        print(f"  Full Name:       {sample.full_name}")
        print(f"  PostScript Name: {sample.postscript_name}")
        print(f"  File Path:       {sample.file_path}")
        print(f"  Format:          {sample.format}")
        print(f"  Bold:            {sample.is_bold}")
        print(f"  Italic:          {sample.is_italic}")
        print(f"  Oblique:         {sample.is_oblique}")
        print(f"  Monospace:       {sample.is_monospace}")
        print(f"  Weight:          {sample.weight} ({sample.weight_name})")
        print(f"  Width Class:     {sample.width_class}")
        print(f"  Latin Support:   {sample.supports_latin}")
        print(f"  Matplotlib Name: {sample.matplotlib_name}")

    # ─────────────────────────────────────────────────────────────
    # 3. Filter: Bold, non-italic fonts
    # ─────────────────────────────────────────────────────────────
    separator("3. Filter: Bold, Non-Italic Fonts")

    bold = filter_fonts(fonts, is_bold=True, is_italic=False)
    print(f"Found: {len(bold)}\n")
    for f in bold[:10]:
        print(f"  {f.full_name:<40} weight={f.weight}")
    if len(bold) > 10:
        print(f"  ... and {len(bold) - 10} more")

    # ─────────────────────────────────────────────────────────────
    # 4. Filter: Monospace fonts
    # ─────────────────────────────────────────────────────────────
    separator("4. Filter: Monospace Fonts")

    mono = filter_fonts(fonts, is_monospace=True)
    print(f"Found: {len(mono)}\n")
    for f in mono:
        print(f"  {f.family:<30} {f.subfamily:<15} weight={f.weight}")

    # ─────────────────────────────────────────────────────────────
    # 5. Filter: Substring family match
    # ─────────────────────────────────────────────────────────────
    separator("5. Filter: Family Contains 'dejavu'")

    dejavu = filter_fonts(fonts, family_contains="dejavu")
    print(f"Found: {len(dejavu)}\n")
    for f in dejavu:
        print(f"  {f.full_name:<40} bold={f.is_bold}  italic={f.is_italic}  mono={f.is_monospace}")

    # ─────────────────────────────────────────────────────────────
    # 6. Filter: Heavy weights (≥ 700)
    # ─────────────────────────────────────────────────────────────
    separator("6. Filter: Heavy Weights (≥700)")

    heavy = filter_fonts(fonts, weight_min=700)
    print(f"Found: {len(heavy)}\n")
    for f in heavy[:10]:
        print(f"  {f.full_name:<40} weight={f.weight} ({f.weight_name})")
    if len(heavy) > 10:
        print(f"  ... and {len(heavy) - 10} more")

    # ─────────────────────────────────────────────────────────────
    # 7. Filter: Light weights (< 400)
    # ─────────────────────────────────────────────────────────────
    separator("7. Filter: Light Weights (<400) with Custom Lambda")

    light = filter_fonts(fonts, is_italic=False, custom=lambda f: f.weight < 400)
    print(f"Found: {len(light)}\n")
    for f in light:
        print(f"  {f.full_name:<40} weight={f.weight} ({f.weight_name})")

    # ─────────────────────────────────────────────────────────────
    # 8. Unique font families
    # ─────────────────────────────────────────────────────────────
    separator("8. Unique Font Families")

    families = get_font_families()
    print(f"Total unique families: {len(families)}\n")
    for fam in families[:20]:
        print(f"  • {fam}")
    if len(families) > 20:
        print(f"  ... and {len(families) - 20} more")

    # ─────────────────────────────────────────────────────────────
    # 9. Look up a font by name
    # ─────────────────────────────────────────────────────────────
    separator("9. Look Up Font by Name")

    for name in ["DejaVu Sans", "Liberation Mono Bold", "NonExistentFont"]:
        result = get_font_by_name(name)
        if result:
            print(f"  '{name}' → {result.full_name} ({result.file_path.name})")
        else:
            print(f"  '{name}' → NOT FOUND")

    # ─────────────────────────────────────────────────────────────
    # 10. Combined multi-criteria filter
    # ─────────────────────────────────────────────────────────────
    separator("10. Combined Multi-Criteria Filter")

    specific = filter_fonts(
        fonts,
        is_bold=False,
        is_italic=False,
        is_monospace=False,
        weight=400,
        format=".ttf",
    )
    print(f"Regular-weight, non-bold, non-italic, proportional .ttf fonts: {len(specific)}\n")
    for f in specific[:10]:
        print(f"  {f.full_name:<40} {f.file_path.name}")
    if len(specific) > 10:
        print(f"  ... and {len(specific) - 10} more")

    # ─────────────────────────────────────────────────────────────
    # 11. Export to dict / DataFrame-ready
    # ─────────────────────────────────────────────────────────────
    separator("11. Export to Dict (DataFrame-ready)")

    if fonts:
        d = fonts[0].to_dict()
        for k, v in d.items():
            print(f"  {k:<20} = {v}")

    print("\n\n✅ All demos completed successfully!")


if __name__ == "__main__":
    main()
