#!/usr/bin/env python3
"""Pre-render all pixel art icons as static SVG files.

Writes bare SVGs (no width/height/class/style) to ``static/icons/`` so they
can be served as ``<img>`` tags and visually inspected in any file browser.

Also generates color-tinted variants:
  - ``{name}--green.svg`` (#5cdb5c)
  - ``{name}--gold.svg``  (#f0c543)

Usage:
    python scripts/build_icons.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.game.icons import get_icon_names, render_icon_svg_bare  # noqa: E402

TINTS: dict[str, str] = {
    "green": "#5cdb5c",
    "gold": "#f0c543",
}

OUT_DIR = ROOT / "static" / "icons"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    names = get_icon_names()
    count = 0

    for name in names:
        # Base (original palette)
        svg = render_icon_svg_bare(name)
        if svg is None:
            continue
        (OUT_DIR / f"{name}.svg").write_text(svg)
        count += 1

        # Tinted variants
        for label, hex_color in TINTS.items():
            tinted = render_icon_svg_bare(name, color=hex_color)
            if tinted is not None:
                (OUT_DIR / f"{name}--{label}.svg").write_text(tinted)
                count += 1

    print(f"Wrote {count} SVG files to {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
