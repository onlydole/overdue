---
title: Pixel Art System
category: architecture
freshness:
  ttl_days: 180
  sources:
    - "src/game/avatars.py"
    - "src/game/icons/_catalog.py"
    - "src/game/icons/_renderer.py"
    - "src/game/icons/__init__.py"
    - "scripts/build_icons.py"
    - "src/web/templates.py"
---

# Pixel Art System

Every decorative visual in Overdue is a custom-built pixel art SVG. There are no emoji and no raster images. Two parallel systems power this: icons and avatars.

## Icons (24x24)

26 icons are declared as SVG path strings in `src/game/icons/_catalog.py`. The catalog uses two private helpers:

| Symbol | Role |
|---|---|
| `_path` | Wraps a raw `d=` attribute string into a full `<path>` element |
| `_scaled_paths` | Scales a tuple of path strings for high-resolution sources (e.g. 1200x1200 Noun Project icons scaled to 24x24) |

Icons are rendered for the templates through two public functions in `_renderer.py`:

| Symbol | Returns |
|---|---|
| `render_icon_svg` | Full `<svg>` element with optional `color` and `size` overrides |
| `render_icon_svg_bare` | Path content only -- used by the static asset build |

`__init__.py` re-exports `render_icon_svg` and `get_icon_names`. Jinja2 binds the renderer as a global called `render_icon` in `src/web/templates.py`, so templates write `{{ render_icon("star", 24) }}`.

## Avatars (32x32)

Eight heroic librarian silhouettes live in `src/game/avatars.py`. Each entry includes `name`, `role_title`, `description`, `material`, and the SVG path data (`path` for the main silhouette, `accents` for details like scarves and armor), plus `primary`, `secondary`, and `outline` colors.

| Symbol | Role |
|---|---|
| `render_avatar_svg` | Full `<svg>` with size override |
| `render_avatar_svg_bare` | Path content only (for static export) |
| `get_avatar_choices` | List of `{id, name, description}` records for the settings carousel |
| `_get_avatar_svg_content` | Private helper that assembles path + accents from the catalog |

## Static Asset Build

`scripts/build_icons.py` pre-renders every icon and avatar to `static/icons/` as a standalone SVG file. The script also generates tinted variants for a small set of icon+color pairs (so templates can ship `<img src="...star--gold.svg">` instead of inlining the whole SVG) and prunes any tint that's no longer in the catalog. Run it after any icon or avatar change:

```bash
python scripts/build_icons.py
```

## Rendering Pipeline

```
SVG path string (catalog)
  -> wrapped in <svg> with viewBox + styling (_renderer.py / avatars.py)
  -> registered as a Jinja2 global in src/web/templates.py
  -> called in templates: {{ render_icon("star", 24) }} / {{ render_avatar("avatar_01", 32) }}
```
