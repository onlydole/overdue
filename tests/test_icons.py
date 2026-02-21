"""Tests for the 16x16 pixel art icon system."""

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


def test_all_27_icons_registered():
    """All 27 icons must be present in the catalog."""
    names = get_icon_names()
    assert names == EXPECTED_ICONS


def test_icon_name_set_unchanged():
    """The icon name set must exactly match the original 28."""
    assert len(get_icon_names()) == 28


@pytest.mark.parametrize("name", EXPECTED_ICONS)
def test_render_produces_svg(name: str):
    """Each icon renders to a non-empty SVG string."""
    svg = render_icon_svg(name)
    assert svg.startswith("<svg")
    assert "</svg>" in svg


@pytest.mark.parametrize("name", EXPECTED_ICONS)
def test_viewbox_is_16x16(name: str):
    """Each icon must use a 16x16 viewBox."""
    svg = render_icon_svg(name)
    assert 'viewBox="0 0 16 16"' in svg


@pytest.mark.parametrize("name", EXPECTED_ICONS)
def test_pixel_bounds_within_0_15(name: str):
    """All pixel coordinates must be within the 0-15 range."""
    from src.game.icons import _ICON_CATALOG

    pixels = _ICON_CATALOG[name]
    for x, y, _color in pixels:
        assert 0 <= x <= 15, f"Icon {name}: x={x} out of range"
        assert 0 <= y <= 15, f"Icon {name}: y={y} out of range"


@pytest.mark.parametrize("name", EXPECTED_ICONS)
def test_icon_has_reasonable_pixel_count(name: str):
    """Each 16x16 icon should have a reasonable number of pixels (30+)."""
    from src.game.icons import _ICON_CATALOG

    pixels = _ICON_CATALOG[name]
    assert len(pixels) >= 30, f"Icon {name} has only {len(pixels)} pixels"


def test_color_override():
    """Passing a color should tint all pixels to that color."""
    svg = render_icon_svg("star", color="#ff0000")
    assert "#ff0000" in svg
    # Should not contain the original gold color
    assert "#f0c543" not in svg


def test_fallback_for_unknown_icon():
    """Unknown icon name should return a fallback SVG, not crash."""
    svg = render_icon_svg("nonexistent_icon_xyz")
    assert svg.startswith("<svg")
    assert 'viewBox="0 0 16 16"' in svg


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
