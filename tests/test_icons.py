"""Tests for the high-fidelity SVG icon system."""

from __future__ import annotations

import pytest

from src.game.icons import get_icon_names, render_icon_svg


# The exact set of 28 icon names that must be present
EXPECTED_ICONS = sorted([
    "books", "book-open", "book-closed", "scroll", "bookmark", "clipboard",
    "fire", "moon", "star", "sparkles", "zap",
    "trophy", "crown", "award", "chart",
    "clock", "search", "key", "hourglass", "gear", "house", "library", "construction",
    "person", "robot", "gamepad", "play", "checkmark",
])
assert len(EXPECTED_ICONS) == 28


def test_all_28_icons_registered():
    """All 28 icons must be present in the catalog."""
    names = get_icon_names()
    assert names == EXPECTED_ICONS


@pytest.mark.parametrize("name", EXPECTED_ICONS)
def test_render_produces_svg(name: str):
    """Each icon renders to a non-empty SVG string."""
    svg = render_icon_svg(name)
    assert svg.startswith("<svg")
    assert "</svg>" in svg
    assert "<path" in svg


@pytest.mark.parametrize("name", EXPECTED_ICONS)
def test_viewbox_is_24x24(name: str):
    """Each icon must use a 24x24 viewBox."""
    svg = render_icon_svg(name)
    assert 'viewBox="0 0 24 24"' in svg


def test_color_override():
    """Passing a color should inject a style attribute."""
    svg = render_icon_svg("star", color="#ff0000")
    assert 'style="color: #ff0000;"' in svg


def test_fallback_for_unknown_icon():
    """Unknown icon name should return a fallback SVG, not crash."""
    svg = render_icon_svg("nonexistent_icon_xyz")
    assert svg.startswith("<svg")
    assert 'viewBox="0 0 24 24"' in svg


def test_size_parameter():
    """The size parameter should set width and height."""
    svg = render_icon_svg("star", size=48)
    assert 'width="48"' in svg
    assert 'height="48"' in svg


def test_import_from_package():
    """The package import must work identically to the old module import."""
    from src.game.icons import render_icon_svg as fn1
    from src.game.icons import get_icon_names as fn2

    assert callable(fn1)
    assert callable(fn2)
