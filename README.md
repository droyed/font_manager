# font_manager — Discover, inspect, and filter system fonts for matplotlib

A lightweight Python library for enumerating every font matplotlib can use,
extracting rich metadata from each font file via fontTools, and filtering the
results with composable, keyword-driven criteria.

## Overview

`font_manager` combines matplotlib's font-discovery engine with fontTools'
low-level table parsing to give you a clean, typed `FontInfo` object for every
font face on the system.  You can query by style flags, weight range, format,
family name, script support, or any custom predicate — all through a single
`filter_fonts()` call.  Results are cached in memory so repeated queries are
fast.

## Features

- **Full system scan** — finds all font files matplotlib knows about (`.ttf`, `.otf`, `.ttc`)
- **Rich metadata** — family, subfamily, full name, PostScript name, file path, format, style flags, OS/2 weight & width class, Latin script support, and matplotlib reference name
- **Flexible filtering** — filter by bold/italic/oblique/monospace flags, exact or range-based weight, width class, format, family substring, or a custom lambda
- **Latin-only mode** — optionally restrict results to fonts with Latin script coverage
- **In-memory cache** — scan runs once per process; `clear_cache()` forces a re-scan
- **DataFrame-ready export** — `FontInfo.to_dict()` serialises every field (Path → str) for pandas or any tabular tool
- **Zero boilerplate** — `filter_fonts()` calls `get_all_fonts()` automatically when no font list is supplied

## Requirements

- Python ≥ 3.10
- [matplotlib](https://matplotlib.org/)
- [fonttools](https://fonttools.readthedocs.io/)

## Installation / Setup

Install the dependencies:

```bash
pip install matplotlib fonttools
```

Add the `src/` directory to your Python path:

```bash
export PYTHONPATH="/path/to/FontsPackage/v1/src:$PYTHONPATH"
```

Or in code before importing:

```python
import sys
sys.path.insert(0, "/path/to/FontsPackage/v1/src")
```

## Quick Start

```python
from font_manager import get_all_fonts, filter_fonts

# Scan all system fonts (Latin-only by default, results cached)
fonts = get_all_fonts()
print(f"{len(fonts)} fonts found")

for f in fonts[:5]:
    print(f.family, f.subfamily, f.weight)
```

```python
from font_manager import filter_fonts

# Bold monospace fonts — no need to call get_all_fonts() first
bold_mono = filter_fonts(is_bold=True, is_monospace=True)

for f in bold_mono:
    print(f"{f.full_name:<40} weight={f.weight}  {f.file_path.name}")
```

More usage patterns (weight ranges, custom predicates, family lookup, dict
export) are shown in [`src/font_manager/demo.py`](src/font_manager/demo.py).

## API Summary

| Function | Description |
|---|---|
| `get_all_fonts(latin_only=True)` | Scan all system fonts and return a sorted `list[FontInfo]`; results are cached |
| `filter_fonts(fonts=None, **criteria)` | Filter a font list (or the cached full list) by any combination of criteria |
| `get_font_families(latin_only=True)` | Return a sorted list of unique font family name strings |
| `get_font_by_name(name)` | Look up a single font by full name or family (case-insensitive); returns `FontInfo \| None` |
| `clear_cache()` | Invalidate the in-memory cache so the next call rescans the system |
| `FontInfo` | Immutable dataclass holding all metadata for one font face |

Full parameter documentation for every function is in **[USAGE.md](USAGE.md)**.

## FontInfo at a Glance

| Field | Type | Description |
|---|---|---|
| `family` | `str` | Font family name (e.g. `"DejaVu Sans"`) |
| `subfamily` | `str` | Subfamily / style name (e.g. `"Bold Italic"`) |
| `full_name` | `str` | Full human-readable name (e.g. `"DejaVu Sans Bold Italic"`) |
| `postscript_name` | `str` | PostScript name (e.g. `"DejaVuSans-BoldOblique"`) |
| `file_path` | `Path` | Absolute path to the font file |
| `format` | `str` | File extension: `".ttf"`, `".otf"`, or `".ttc"` |
| `is_bold` | `bool` | Bold style flag |
| `is_italic` | `bool` | Italic style flag |
| `is_oblique` | `bool` | Oblique style flag |
| `is_monospace` | `bool` | Monospace / fixed-width flag |
| `weight` | `int` | OS/2 `usWeightClass` value (100 – 900) |
| `weight_name` | `str` | Human-readable weight label (e.g. `"Regular"`, `"Bold"`) |
| `width_class` | `int` | OS/2 `usWidthClass` value (1 – 9) |
| `supports_latin` | `bool` | `True` if the font covers the Latin script |
| `matplotlib_name` | `str` | Name string matplotlib uses to reference this font |

## Architecture

```
font_manager/
├── __init__.py       # Public API: get_all_fonts, filter_fonts,
│                     #   get_font_families, get_font_by_name, clear_cache
├── models.py         # FontInfo frozen dataclass (15 fields)
├── discovery.py      # Wraps matplotlib's font manager to enumerate font files
├── metadata.py       # Uses fontTools to extract per-face metadata
├── filters.py        # Composable keyword-based filter logic
└── demo.py           # Runnable demo covering all major use-cases
```

**Data flow:**

```
matplotlib font finder → discovery.py
        ↓
fontTools table parsing → metadata.py
        ↓
    list[FontInfo]  ←── cached in __init__.py
        ↓
filter_fonts() / get_font_families() / get_font_by_name()
```

## Further Reading

See **[USAGE.md](USAGE.md)** for the full API reference, detailed parameter
descriptions, and extended code examples.

## License

MIT License — Copyright (c) 2026 Divakar Roy.  See [LICENSE](LICENSE) for the
full text.
