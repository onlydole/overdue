"""Pixel art icon system -- 16x16 GBA-era icons rendered as inline SVG.

Provides 28 pixel art icons for use throughout the UI, replacing native emoji
with a cohesive retro aesthetic. Each icon is a 16x16 grid of colored pixels
rendered as SVG ``<rect>`` elements with GBA-era multi-step shading.

Public API (unchanged from the original single-file module):
    render_icon_svg(name, size, color) -> str
    get_icon_names() -> list[str]
"""

from __future__ import annotations

from src.game.icons._achievements import (  # noqa: E402
    register_icons as _register_achievements,
)
from src.game.icons._books import register_icons as _register_books  # noqa: E402
from src.game.icons._characters import (  # noqa: E402
    register_icons as _register_characters,
)
from src.game.icons._nature import register_icons as _register_nature  # noqa: E402
from src.game.icons._objects import register_icons as _register_objects  # noqa: E402
from src.game.icons._renderer import render_icon_svg as _render_icon_svg
from src.game.icons._renderer import render_icon_svg_bare as _render_icon_svg_bare

# ---------------------------------------------------------------------------
# Unified icon catalog — populated by category modules
# ---------------------------------------------------------------------------
_ICON_CATALOG: dict[str, list[tuple[int, int, str]]] = {}


def _register(name: str, pixels: list[tuple[int, int, str]]) -> None:
    """Register an icon in the global catalog."""
    _ICON_CATALOG[name] = pixels


_register_books(_register)
_register_nature(_register)
_register_achievements(_register)
_register_objects(_register)
_register_characters(_register)


# ---------------------------------------------------------------------------
# Public API — identical signatures to the old icons.py
# ---------------------------------------------------------------------------


def render_icon_svg(name: str, size: int = 16, color: str | None = None) -> str:
    """Return an inline SVG string for the given icon."""
    return _render_icon_svg(name, size=size, color=color, _catalog=_ICON_CATALOG)


def render_icon_svg_bare(name: str, color: str | None = None) -> str | None:
    """Return a bare SVG string (no width/height/class) for static files."""
    return _render_icon_svg_bare(name, color=color, _catalog=_ICON_CATALOG)


def get_icon_names() -> list[str]:
    """Return a sorted list of all available icon names."""
    return sorted(_ICON_CATALOG.keys())
