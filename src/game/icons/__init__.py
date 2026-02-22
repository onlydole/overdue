"""High-fidelity pixel-vector icon system.

Provides 28 crisp SVG icons (24x24 grid) for use throughout the UI.
Replaces the old 16x16 bitmap system with vector paths that scale perfectly.

Public API:
    render_icon_svg(name, size, color) -> str
    get_icon_names() -> list[str]
"""

from __future__ import annotations

from src.game.icons._catalog import ICON_CATALOG
from src.game.icons._renderer import render_icon_svg as _render_icon_svg
from src.game.icons._renderer import render_icon_svg_bare as _render_icon_svg_bare


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_icon_svg(name: str, size: int = 24, color: str | None = None) -> str:
    """Return an inline SVG string for the given icon."""
    return _render_icon_svg(name, size=size, color=color, _catalog=ICON_CATALOG)


def render_icon_svg_bare(name: str, color: str | None = None) -> str | None:
    """Return a bare SVG string (no width/height/class) for static files."""
    return _render_icon_svg_bare(name, color=color, _catalog=ICON_CATALOG)


def get_icon_names() -> list[str]:
    """Return a sorted list of all available icon names."""
    return sorted(ICON_CATALOG.keys())
