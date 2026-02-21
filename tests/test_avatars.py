"""Tests for the 32x32 pixel art avatar system."""

from __future__ import annotations

import pytest

from src.game.avatars import AVATAR_CATALOG, get_avatar_choices, render_avatar_svg


EXPECTED_AVATAR_IDS = [f"avatar_{i:02d}" for i in range(1, 13)]

EXPECTED_HAIR_STYLES = [
    "short_cropped", "curly", "bald", "long_straight", "short_afro",
    "mohawk", "braids", "ponytail", "bob_cut", "undercut", "locs", "spiky",
]


def test_all_12_avatars_registered():
    """All 12 avatar IDs must be present in the catalog."""
    for avatar_id in EXPECTED_AVATAR_IDS:
        assert avatar_id in AVATAR_CATALOG, f"Missing avatar: {avatar_id}"


def test_avatar_count():
    """Exactly 12 avatars must be defined."""
    assert len(AVATAR_CATALOG) == 12


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_render_produces_svg(avatar_id: str):
    """Each avatar renders to a non-empty SVG string."""
    svg = render_avatar_svg(avatar_id)
    assert svg.startswith("<svg")
    assert "</svg>" in svg


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_viewbox_is_32x32(avatar_id: str):
    """Each avatar must use a 32x32 viewBox."""
    svg = render_avatar_svg(avatar_id)
    assert 'viewBox="0 0 32 32"' in svg


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_pixel_bounds_within_0_31(avatar_id: str):
    """All pixel coordinates must be within the 0-31 range."""
    from src.game.avatars import _build_avatar_pixels

    avatar_def = AVATAR_CATALOG[avatar_id]
    pixels = _build_avatar_pixels(avatar_def)
    for x, y, _color in pixels:
        assert 0 <= x <= 31, f"Avatar {avatar_id}: x={x} out of range"
        assert 0 <= y <= 31, f"Avatar {avatar_id}: y={y} out of range"


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_avatar_has_reasonable_pixel_count(avatar_id: str):
    """Each 32x32 avatar should have a substantial number of pixels."""
    from src.game.avatars import _build_avatar_pixels

    avatar_def = AVATAR_CATALOG[avatar_id]
    pixels = _build_avatar_pixels(avatar_def)
    assert len(pixels) >= 100, f"Avatar {avatar_id} has only {len(pixels)} pixels"


def test_fallback_for_unknown_avatar():
    """Unknown avatar ID should return a fallback SVG, not crash."""
    svg = render_avatar_svg("nonexistent_avatar")
    assert svg.startswith("<svg")
    assert 'viewBox="0 0 32 32"' in svg


def test_size_parameter():
    """The size parameter should set width and height."""
    svg = render_avatar_svg("avatar_01", size=64)
    assert 'width="64"' in svg
    assert 'height="64"' in svg


def test_get_avatar_choices():
    """get_avatar_choices() must return a list of 12 dicts with id, name, description."""
    choices = get_avatar_choices()
    assert len(choices) == 12
    for choice in choices:
        assert "id" in choice
        assert "name" in choice
        assert "description" in choice


def test_all_hair_builders_present():
    """All 12 hair builder functions must be registered."""
    from src.game.avatars import _HAIR_BUILDERS

    for style in EXPECTED_HAIR_STYLES:
        assert style in _HAIR_BUILDERS, f"Missing hair builder: {style}"


def test_avatar_catalog_keys_unchanged():
    """AVATAR_CATALOG must have the same keys and metadata fields."""
    for avatar_id in EXPECTED_AVATAR_IDS:
        meta = AVATAR_CATALOG[avatar_id]
        assert "name" in meta
        assert "description" in meta
        assert "skin_tone" in meta
        assert "hair_style" in meta
        assert "hair_color" in meta
        assert "glasses" in meta
        assert "outfit_color" in meta


def test_imports_resolve():
    """All public API imports must work."""
    from src.game.avatars import render_avatar_svg as fn1
    from src.game.avatars import AVATAR_CATALOG as cat
    from src.game.avatars import get_avatar_choices as fn2

    assert callable(fn1)
    assert callable(fn2)
    assert isinstance(cat, dict)
