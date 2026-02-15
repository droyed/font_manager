# font_manager — Usage Guide

A Python library for discovering, inspecting, and filtering system fonts that matplotlib can use.

---

## Overview

`font_manager` builds on top of matplotlib's font discovery and [fontTools](https://fonttools.readthedocs.io/) metadata extraction to give you a clean, filterable list of every font on your system. It answers questions like:

- Which monospace fonts are installed?
- What bold serif fonts are available in TrueType format?
- Which fonts have a weight between SemiBold and Black?

**Dependencies:** `matplotlib`, `fonttools`

---

## Installation / Requirements

```bash
pip install matplotlib fonttools
```

The package itself lives under `src/font_manager/`. Add `src/` to your `PYTHONPATH`, or install the package if a `pyproject.toml` is present.

---

## Quick Start

```python
from font_manager import get_all_fonts, filter_fonts

# Discover all Latin-capable fonts on the system
fonts = get_all_fonts()

# Filter to bold monospace fonts
bold_mono = filter_fonts(fonts, is_bold=True, is_monospace=True)

for f in bold_mono:
    print(f.family, f.full_name, f.weight)
```

---

## Core Concepts

### FontInfo

Every font is represented as a `FontInfo` dataclass — an **immutable** object (`frozen=True`) containing 15 fields covering identity, file location, style flags, weight/width metrics, and matplotlib integration data.

Sorting a list of `FontInfo` objects groups them naturally by `(family, weight, is_italic, is_bold)`.

### Caching

`get_all_fonts()` scans font files only once per process (separately for `latin_only=True` and `latin_only=False`). Subsequent calls return from the in-memory cache instantly. Call `clear_cache()` after installing new fonts to force a fresh scan.

---

## API Reference

### `get_all_fonts`

```python
def get_all_fonts(latin_only: bool = True) -> list[FontInfo]
```

Discover all fonts matplotlib can use and extract their full metadata.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latin_only` | `bool` | `True` | Return only fonts that support the Latin script (A–Z, a–z, common punctuation). Set to `False` to include CJK, Arabic, etc. |

**Returns:** Sorted `list[FontInfo]`.

**Example:**

```python
from font_manager import get_all_fonts

all_fonts = get_all_fonts()               # Latin fonts only (default)
all_fonts_incl = get_all_fonts(latin_only=False)  # All fonts on the system
print(f"Latin fonts: {len(all_fonts)}")
```

---

### `filter_fonts`

```python
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
) -> list[FontInfo]
```

Filter fonts by any combination of criteria. All non-`None` criteria must match (**AND logic**). String comparisons are case-insensitive.

If `fonts` is `None`, `get_all_fonts()` is called automatically.

**Returns:** Sorted `list[FontInfo]` matching all specified criteria.

---

### `get_font_families`

```python
def get_font_families(latin_only: bool = True) -> list[str]
```

Return a sorted list of unique font family names.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latin_only` | `bool` | `True` | Include only families with Latin script support. |

**Returns:** `list[str]` — sorted, deduplicated family names.

**Example:**

```python
from font_manager import get_font_families

families = get_font_families()
print(f"Available families: {len(families)}")
for name in families[:10]:
    print(f"  • {name}")
```

---

### `get_font_by_name`

```python
def get_font_by_name(name: str) -> FontInfo | None
```

Look up a single font by name (case-insensitive). Search order:

1. Exact match on `full_name`
2. Exact match on `family` (returns the first variant)
3. Substring match on `full_name` (returns the first match)

**Returns:** `FontInfo` if found, `None` otherwise.

**Example:**

```python
from font_manager import get_font_by_name

font = get_font_by_name("DejaVu Sans Bold")
if font:
    print(font.file_path)
else:
    print("Font not found")
```

---

### `clear_cache`

```python
def clear_cache() -> None
```

Clear the cached font list. The next call to `get_all_fonts()` (or any function that calls it internally) will perform a fresh file-system scan.

**Example:**

```python
from font_manager import clear_cache, get_all_fonts

# After installing a new font:
clear_cache()
fonts = get_all_fonts()
```

---

## Filtering Guide

All parameters to `filter_fonts` are keyword-only. Omit any you don't need. Every provided criterion must match (AND logic).

### Identity Filters

| Parameter | Match type | Example |
|-----------|-----------|---------|
| `family` | Exact (case-insensitive) | `family="DejaVu Sans"` |
| `family_contains` | Substring (case-insensitive) | `family_contains="mono"` |
| `full_name` | Exact (case-insensitive) | `full_name="Arial Bold Italic"` |
| `postscript_name` | Exact (case-insensitive) | `postscript_name="Arial-BoldItalic"` |

```python
# All variants of the DejaVu Sans family
dejavu = filter_fonts(family="DejaVu Sans")

# Any family whose name contains "mono"
mono_families = filter_fonts(family_contains="mono")
```

### Style Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `is_bold` | `bool` | Font has the bold style flag set |
| `is_italic` | `bool` | Font has the italic style flag set |
| `is_oblique` | `bool` | Font is oblique (slanted, not true italic) |
| `is_monospace` | `bool` | Font uses fixed-width (monospace) spacing |

```python
# Bold, non-italic fonts
bold = filter_fonts(is_bold=True, is_italic=False)

# Monospace fonts only
mono = filter_fonts(is_monospace=True)

# Bold monospace (e.g. for code editors)
bold_mono = filter_fonts(is_bold=True, is_monospace=True)
```

### Weight Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `weight` | `int` | Exact OS/2 `usWeightClass` value (100–900) |
| `weight_min` | `int` | Minimum weight (inclusive) |
| `weight_max` | `int` | Maximum weight (inclusive) |
| `weight_name` | `str` | Human-readable weight label (e.g. `"Bold"`, `"Light"`) |

```python
# Exactly Regular weight
regular = filter_fonts(weight=400)

# Heavy weights: SemiBold through Black
heavy = filter_fonts(weight_min=600)

# Light and below
light = filter_fonts(weight_max=300)

# SemiBold to Bold range
mid_heavy = filter_fonts(weight_min=600, weight_max=700)

# By name
bold_name = filter_fonts(weight_name="Bold")
```

### Width Filter

| Parameter | Type | Description |
|-----------|------|-------------|
| `width_class` | `int` | OS/2 `usWidthClass` value (1–9, see table below) |

```python
# Normal-width fonts only
normal_width = filter_fonts(width_class=5)

# Condensed fonts
condensed = filter_fonts(width_class=3)
```

### Format Filter

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | `str` | File extension: `".ttf"`, `".otf"`, `".ttc"` — leading dot is optional |

```python
# TrueType only
ttf_only = filter_fonts(format=".ttf")

# OpenType only
otf_only = filter_fonts(format="otf")   # leading dot added automatically
```

### Latin Support Filter

| Parameter | Type | Description |
|-----------|------|-------------|
| `supports_latin` | `bool` | Whether the font covers A–Z, a–z |

```python
# Useful when latin_only=False was used in get_all_fonts
all_fonts = get_all_fonts(latin_only=False)
latin = filter_fonts(all_fonts, supports_latin=True)
```

### Custom Predicate

| Parameter | Type | Description |
|-----------|------|-------------|
| `custom` | `Callable[[FontInfo], bool]` | Arbitrary filter function |

```python
# Fonts whose file name starts with "Ubuntu"
ubuntu = filter_fonts(custom=lambda f: f.file_path.name.startswith("Ubuntu"))

# Light fonts (weight < 400) that are not italic
light_upright = filter_fonts(is_italic=False, custom=lambda f: f.weight < 400)
```

---

## FontInfo Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `family` | `str` | `""` | Font family name, e.g. `"DejaVu Sans"` |
| `subfamily` | `str` | `""` | Style subfamily, e.g. `"Bold Italic"` |
| `full_name` | `str` | `""` | Full font name, e.g. `"DejaVu Sans Bold Italic"` |
| `postscript_name` | `str` | `""` | PostScript name, e.g. `"DejaVuSans-BoldOblique"` |
| `file_path` | `Path` | `Path()` | Absolute path to the font file |
| `format` | `str` | `""` | File extension: `".ttf"`, `".otf"`, or `".ttc"` |
| `is_bold` | `bool` | `False` | Bold style flag from the font's OS/2 table |
| `is_italic` | `bool` | `False` | Italic style flag |
| `is_oblique` | `bool` | `False` | Oblique style flag |
| `is_monospace` | `bool` | `False` | Fixed-width (monospace) spacing |
| `weight` | `int` | `400` | OS/2 `usWeightClass` (100–900) |
| `weight_name` | `str` | `"Regular"` | Human-readable weight label (see Weight Map below) |
| `width_class` | `int` | `5` | OS/2 `usWidthClass` (1–9) |
| `supports_latin` | `bool` | `True` | Font covers basic Latin codepoints (A–Z, a–z) |
| `matplotlib_name` | `str` | `""` | Name matplotlib uses internally to reference this font |

### `FontInfo` Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `to_dict()` | `() -> dict[str, Any]` | Convert to plain dict; `file_path` becomes a `str` |
| `field_names()` | `classmethod, () -> list[str]` | Return all field names as a list |
| `__str__()` | | `"Family [Style] (weight=N, path=file.ttf)"` |
| `__repr__()` | | `"FontInfo(family=..., full_name=..., weight=..., ...)"` |

---

## Weight & Width Class Tables

### Weight Map (`WEIGHT_MAP`)

| Value | Name |
|-------|------|
| 100 | Thin |
| 200 | ExtraLight |
| 300 | Light |
| 400 | Regular |
| 500 | Medium |
| 600 | SemiBold |
| 700 | Bold |
| 800 | ExtraBold |
| 900 | Black |

Non-standard values (e.g. 350) are rounded to the nearest standard stop when generating `weight_name`.

### Width Map (`WIDTH_MAP`)

| Value | Name |
|-------|------|
| 1 | UltraCondensed |
| 2 | ExtraCondensed |
| 3 | Condensed |
| 4 | SemiCondensed |
| 5 | Normal |
| 6 | SemiExpanded |
| 7 | Expanded |
| 8 | ExtraExpanded |
| 9 | UltraExpanded |

---

## Advanced Usage

### Custom Predicate Filters

Any function that accepts a `FontInfo` and returns `bool` can be passed as `custom`:

```python
from font_manager import filter_fonts
from pathlib import Path

# Fonts installed in /usr/share/fonts only
system_fonts = filter_fonts(
    custom=lambda f: str(f.file_path).startswith("/usr/share/fonts")
)

# Fonts whose PostScript name contains a hyphen (has style variant)
styled = filter_fonts(custom=lambda f: "-" in f.postscript_name)
```

### Export to DataFrame

`FontInfo.to_dict()` makes it trivial to load fonts into pandas:

```python
import pandas as pd
from font_manager import get_all_fonts

fonts = get_all_fonts()
df = pd.DataFrame([f.to_dict() for f in fonts])

print(df[["family", "weight", "is_bold", "is_monospace"]].head(10))
```

### Cache Invalidation

```python
from font_manager import clear_cache, get_all_fonts

# Install a new font, then:
clear_cache()
fonts = get_all_fonts()   # triggers a fresh scan
```

### Combining Filter Results

Since `filter_fonts` returns a plain list, use standard Python set/list operations to combine results:

```python
from font_manager import get_all_fonts, filter_fonts

fonts = get_all_fonts()

# Fonts that are either bold OR monospace
bold = set(filter_fonts(fonts, is_bold=True))
mono = set(filter_fonts(fonts, is_monospace=True))
bold_or_mono = sorted(bold | mono)
```

### Using with matplotlib

```python
import matplotlib.pyplot as plt
from font_manager import filter_fonts

mono_fonts = filter_fonts(is_monospace=True, weight=400)
if mono_fonts:
    font = mono_fonts[0]
    plt.rcParams["font.family"] = font.matplotlib_name
    plt.title("Hello with a monospace font")
    plt.show()
```

---

## Complete Examples

### 1. List All Bold Non-Italic Fonts

```python
from font_manager import get_all_fonts, filter_fonts

fonts = get_all_fonts()
bold = filter_fonts(fonts, is_bold=True, is_italic=False)

print(f"Bold (non-italic) fonts: {len(bold)}\n")
for f in bold:
    print(f"  {f.full_name:<40}  weight={f.weight}")
```

### 2. Find All Monospace Fonts

```python
from font_manager import filter_fonts

mono = filter_fonts(is_monospace=True)
for f in mono:
    print(f"{f.family:<30} {f.subfamily:<15} weight={f.weight}")
```

### 3. Search by Family Substring

```python
from font_manager import get_all_fonts, filter_fonts

fonts = get_all_fonts()
dejavu = filter_fonts(fonts, family_contains="dejavu")

for f in dejavu:
    print(
        f"{f.full_name:<40} "
        f"bold={f.is_bold}  italic={f.is_italic}  mono={f.is_monospace}"
    )
```

### 4. Weight Range: Heavy Fonts (≥ 700)

```python
from font_manager import filter_fonts

heavy = filter_fonts(weight_min=700)
for f in heavy:
    print(f"{f.full_name:<40} weight={f.weight} ({f.weight_name})")
```

### 5. Light Upright Fonts via Custom Lambda

```python
from font_manager import get_all_fonts, filter_fonts

fonts = get_all_fonts()
light = filter_fonts(fonts, is_italic=False, custom=lambda f: f.weight < 400)

for f in light:
    print(f"{f.full_name:<40} weight={f.weight} ({f.weight_name})")
```

### 6. Look Up a Font by Name

```python
from font_manager import get_font_by_name

for name in ["DejaVu Sans", "Liberation Mono Bold", "NonExistentFont"]:
    result = get_font_by_name(name)
    if result:
        print(f"  '{name}' → {result.full_name} ({result.file_path.name})")
    else:
        print(f"  '{name}' → NOT FOUND")
```

### 7. Multi-Criteria Filter

```python
from font_manager import get_all_fonts, filter_fonts

fonts = get_all_fonts()
specific = filter_fonts(
    fonts,
    is_bold=False,
    is_italic=False,
    is_monospace=False,
    weight=400,
    format=".ttf",
)
print(f"Regular-weight, upright, proportional .ttf fonts: {len(specific)}\n")
for f in specific:
    print(f"  {f.full_name:<40} {f.file_path.name}")
```

### 8. Export to Dict

```python
from font_manager import get_all_fonts

fonts = get_all_fonts()
if fonts:
    d = fonts[0].to_dict()
    for key, value in d.items():
        print(f"  {key:<20} = {value}")
```

### 9. List All Font Families

```python
from font_manager import get_font_families

families = get_font_families()
print(f"Total unique families: {len(families)}\n")
for name in families:
    print(f"  • {name}")
```

### 10. DataFrame Export and Analysis

```python
import pandas as pd
from font_manager import get_all_fonts

fonts = get_all_fonts()
df = pd.DataFrame([f.to_dict() for f in fonts])

# Weight distribution
print(df["weight_name"].value_counts())

# All monospace families
print(df[df["is_monospace"]]["family"].unique())
```
