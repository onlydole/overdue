#!/usr/bin/env python3
"""Pre-render all pixel art icons and avatars as static SVG files.

Writes bare SVGs (no width/height/class/style) to ``static/icons/`` so they
can be served as ``<img>`` tags and visually inspected in any file browser.

Tinted variants are generated only for icon/color combinations currently used
by templates:
  - ``{name}--green.svg`` (#5cdb5c): ``checkmark``, ``play``
  - ``{name}--gold.svg``  (#f0c543): ``book-open``, ``books``, ``chart``,
    ``crown``, ``fire``, ``gamepad``, ``house``, ``award``
  - ``{name}--flame.svg`` (#f07a3e): ``fire``

Usage:
    python scripts/build_icons.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.game.avatars import AVATAR_CATALOG, render_avatar_svg_bare  # noqa: E402
from src.game.icons import get_icon_names, render_icon_svg_bare  # noqa: E402

TINTS: dict[str, str] = {
    "green": "#5cdb5c",
    "gold": "#f0c543",
    "flame": "#f07a3e",
}

TINTED_ICON_NAMES: dict[str, set[str]] = {
    "green": {"checkmark", "play"},
    "gold": {"book-open", "books", "chart", "crown", "fire", "gamepad", "house", "award"},
    "flame": {"fire"},
}

OUT_DIR = ROOT / "static" / "icons"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    names = get_icon_names()
    count = 0
    expected_tint_paths: set[Path] = set()

    for name in names:
        # Base (original palette)
        svg = render_icon_svg_bare(name)
        if svg is None:
            continue
        (OUT_DIR / f"{name}.svg").write_text(svg)
        count += 1

        # Selected tinted variants used by templates.
        for label, hex_color in TINTS.items():
            if name not in TINTED_ICON_NAMES[label]:
                continue
            tinted = render_icon_svg_bare(name, color=hex_color)
            if tinted is not None:
                target = OUT_DIR / f"{name}--{label}.svg"
                target.write_text(tinted)
                expected_tint_paths.add(target)
                count += 1

    # Avatars
    for avatar_id in AVATAR_CATALOG:
        avatar_svg = render_avatar_svg_bare(avatar_id)
        if avatar_svg is not None:
            (OUT_DIR / f"{avatar_id}.svg").write_text(avatar_svg)
            count += 1

    # Prune stale tint files that are no longer referenced by templates.
    stale_tints: list[Path] = []
    for label in TINTS:
        for path in OUT_DIR.glob(f"*--{label}.svg"):
            if path not in expected_tint_paths:
                stale_tints.append(path)
    for path in stale_tints:
        path.unlink(missing_ok=True)

    print(f"Wrote {count} SVG files to {OUT_DIR.relative_to(ROOT)}/")
    print(f"Pruned {len(stale_tints)} stale tinted SVG files")


if __name__ == "__main__":
    main()
