"""Tests for the GBA-style Heroic Librarian avatar system."""

from __future__ import annotations

import pytest

from src.game.avatars import AVATAR_CATALOG, get_avatar_choices, render_avatar_svg


EXPECTED_AVATAR_IDS = [f"avatar_{i:02d}" for i in range(1, 9)]
REQUIRED_META_KEYS = {
    "name",
    "role_title",
    "description",
    "material",
    "primary",
    "secondary",
    "outline",
    "path",
    "accents"
}

def test_all_8_avatars_registered() -> None:
    """All 8 stable avatar IDs must remain available."""
    for avatar_id in EXPECTED_AVATAR_IDS:
        assert avatar_id in AVATAR_CATALOG, f"Missing avatar: {avatar_id}"


def test_avatar_count() -> None:
    """Exactly 8 selectable GBA-style avatars must exist."""
    assert len(AVATAR_CATALOG) == 8


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_render_produces_svg(avatar_id: str) -> None:
    """Each avatar renders to a non-empty SVG string."""
    svg = render_avatar_svg(avatar_id)
    assert svg.startswith("<svg")
    assert "</svg>" in svg


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_viewbox_is_32x32(avatar_id: str) -> None:
    """Each avatar must use a 32x32 viewBox."""
    svg = render_avatar_svg(avatar_id)
    assert 'viewBox="0 0 32 32"' in svg


def test_heroic_metadata_schema() -> None:
    """Catalog entries should use heroic-focused metadata keys."""
    for avatar_id in EXPECTED_AVATAR_IDS:
        meta = AVATAR_CATALOG[avatar_id]

        missing = REQUIRED_META_KEYS - meta.keys()
        assert not missing, f"{avatar_id} missing keys: {sorted(missing)}"

        assert meta["material"]
        assert meta["role_title"]
        assert meta["name"]
        assert meta["description"]


def test_fallback_for_unknown_avatar() -> None:
    """Unknown avatar ID should return a fallback SVG (Sun-Scribe Isaac), not crash."""
    svg = render_avatar_svg("nonexistent_avatar")
    assert svg.startswith("<svg")
    assert 'viewBox="0 0 32 32"' in svg
    # Should default to avatar_01 colors
    assert '#f0c543' in svg # Isaac primary


def test_size_parameter() -> None:
    """The size parameter should set width and height."""
    svg = render_avatar_svg("avatar_01", size=64)
    assert 'width="64"' in svg
    assert 'height="64"' in svg


def test_get_avatar_choices() -> None:
    """get_avatar_choices() must provide picker-friendly metadata."""
    choices = get_avatar_choices()
    assert len(choices) == 8
    for choice in choices:
        assert "id" in choice
        assert "name" in choice
        assert "description" in choice
        assert "role_title" in choice
        assert "material" in choice


def test_imports_resolve() -> None:
    """Public avatar API exports should remain importable."""
    from src.game.avatars import AVATAR_CATALOG as catalog
    from src.game.avatars import get_avatar_choices as get_choices
    from src.game.avatars import render_avatar_svg as render

    assert isinstance(catalog, dict)
    assert callable(get_choices)
    assert callable(render)
