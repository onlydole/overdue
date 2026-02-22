"""Tests for the 48x48 monster librarian avatar system."""

from __future__ import annotations

from itertools import combinations

import pytest

from src.game.avatars import AVATAR_CATALOG, get_avatar_choices, render_avatar_svg


EXPECTED_AVATAR_IDS = [f"avatar_{i:02d}" for i in range(1, 13)]
REQUIRED_META_KEYS = {
    "name",
    "description",
    "species",
    "body_plan",
    "material",
    "body_color",
    "eye_color",
    "robe_color",
    "accent_color",
    "primary_anchor",
    "accessory",
    "feature_set",
    "prop",
    "role_title",
    "specialty",
    "quirk",
}
LEGACY_HUMAN_KEYS = {"skin_tone", "hair_style", "hair_color", "glasses", "outfit_color"}
ALLOWED_MATERIALS = {"gelatin", "stone", "chitin", "matte", "scale", "spectral", "fur"}


def test_all_12_avatars_registered() -> None:
    """All 12 stable avatar IDs must remain available."""
    for avatar_id in EXPECTED_AVATAR_IDS:
        assert avatar_id in AVATAR_CATALOG, f"Missing avatar: {avatar_id}"


def test_avatar_count() -> None:
    """Exactly 12 selectable monster avatars must exist."""
    assert len(AVATAR_CATALOG) == 12


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_render_produces_svg(avatar_id: str) -> None:
    """Each avatar renders to a non-empty SVG string."""
    svg = render_avatar_svg(avatar_id)
    assert svg.startswith("<svg")
    assert "</svg>" in svg


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_viewbox_is_48x48(avatar_id: str) -> None:
    """Each avatar must use a 48x48 viewBox."""
    svg = render_avatar_svg(avatar_id)
    assert 'viewBox="0 0 48 48"' in svg


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_pixel_bounds_within_0_47(avatar_id: str) -> None:
    """All pixel coordinates must stay inside the 48x48 canvas."""
    from src.game.avatars import _build_avatar_pixels

    avatar_def = AVATAR_CATALOG[avatar_id]
    pixels = _build_avatar_pixels(avatar_def)
    for x, y, _color in pixels:
        assert 0 <= x <= 47, f"Avatar {avatar_id}: x={x} out of range"
        assert 0 <= y <= 47, f"Avatar {avatar_id}: y={y} out of range"


@pytest.mark.parametrize("avatar_id", EXPECTED_AVATAR_IDS)
def test_avatar_has_reasonable_pixel_count(avatar_id: str) -> None:
    """Each avatar should have enough pixels to read clearly at small sizes."""
    from src.game.avatars import _build_avatar_pixels

    avatar_def = AVATAR_CATALOG[avatar_id]
    pixels = _build_avatar_pixels(avatar_def)
    assert len(pixels) >= 180, f"Avatar {avatar_id} has only {len(pixels)} pixels"


def test_monster_metadata_schema() -> None:
    """Catalog entries should use monster-focused metadata keys only."""
    for avatar_id in EXPECTED_AVATAR_IDS:
        meta = AVATAR_CATALOG[avatar_id]

        missing = REQUIRED_META_KEYS - meta.keys()
        assert not missing, f"{avatar_id} missing keys: {sorted(missing)}"

        leaked = LEGACY_HUMAN_KEYS & meta.keys()
        assert not leaked, f"{avatar_id} has human-focused keys: {sorted(leaked)}"

        assert isinstance(meta["feature_set"], list)
        assert len(meta["feature_set"]) >= 2, f"{avatar_id} needs at least 2 unique features"
        assert meta["material"] in ALLOWED_MATERIALS
        assert meta["species"]
        assert meta["body_plan"]
        assert meta["primary_anchor"]
        assert meta["prop"]
        assert meta["role_title"]
        assert meta["specialty"]
        assert meta["quirk"]
        assert meta["name"]
        assert meta["description"]


def test_species_are_diverse() -> None:
    """Avatar roster should include a broad spread of monster species."""
    species = {meta["species"] for meta in AVATAR_CATALOG.values()}
    assert len(species) == len(EXPECTED_AVATAR_IDS)


def test_body_plans_and_anchors_are_unique() -> None:
    """Silhouette drivers should be unique across the 12 avatars."""
    body_plans = {meta["body_plan"] for meta in AVATAR_CATALOG.values()}
    anchors = {meta["primary_anchor"] for meta in AVATAR_CATALOG.values()}
    assert len(body_plans) == len(EXPECTED_AVATAR_IDS)
    assert len(anchors) == len(EXPECTED_AVATAR_IDS)


def test_silhouette_overlap_stays_below_threshold() -> None:
    """No two avatars should have near-identical occupancy silhouettes."""
    from src.game.avatars import _build_avatar_pixels

    occupancies = {
        avatar_id: {(x, y) for x, y, _ in _build_avatar_pixels(meta)}
        for avatar_id, meta in AVATAR_CATALOG.items()
    }

    max_iou = 0.0
    for a_id, b_id in combinations(EXPECTED_AVATAR_IDS, 2):
        a = occupancies[a_id]
        b = occupancies[b_id]
        intersection = len(a & b)
        union = len(a | b)
        iou = intersection / union if union else 0.0
        max_iou = max(max_iou, iou)

    assert max_iou < 0.74, f"Silhouette overlap too high: {max_iou:.3f}"


def test_coarse_silhouette_distance() -> None:
    """Coarse 12x12 occupancy masks should remain clearly separated."""
    from src.game.avatars import _build_avatar_pixels

    occupancies = {
        avatar_id: {(x, y) for x, y, _ in _build_avatar_pixels(meta)}
        for avatar_id, meta in AVATAR_CATALOG.items()
    }

    signatures: dict[str, list[int]] = {}
    for avatar_id, pixels in occupancies.items():
        bits: list[int] = []
        for gy in range(12):
            for gx in range(12):
                count = 0
                for y in range(gy * 4, gy * 4 + 4):
                    for x in range(gx * 4, gx * 4 + 4):
                        if (x, y) in pixels:
                            count += 1
                bits.append(1 if count >= 4 else 0)
        signatures[avatar_id] = bits

    min_distance = 144
    for a_id, b_id in combinations(EXPECTED_AVATAR_IDS, 2):
        dist = sum(
            1
            for a_bit, b_bit in zip(signatures[a_id], signatures[b_id], strict=True)
            if a_bit != b_bit
        )
        min_distance = min(min_distance, dist)

    assert min_distance >= 18, f"Coarse silhouettes too close: {min_distance}"


def test_fallback_for_unknown_avatar() -> None:
    """Unknown avatar ID should return a fallback SVG, not crash."""
    svg = render_avatar_svg("nonexistent_avatar")
    assert svg.startswith("<svg")
    assert 'viewBox="0 0 48 48"' in svg


def test_size_parameter() -> None:
    """The size parameter should set width and height."""
    svg = render_avatar_svg("avatar_01", size=64)
    assert 'width="64"' in svg
    assert 'height="64"' in svg


def test_get_avatar_choices() -> None:
    """get_avatar_choices() must provide picker-friendly metadata."""
    choices = get_avatar_choices()
    assert len(choices) == 12
    for choice in choices:
        assert "id" in choice
        assert "name" in choice
        assert "description" in choice
        assert "species" in choice
        assert "role_title" in choice
        assert "specialty" in choice


def test_imports_resolve() -> None:
    """Public avatar API exports should remain importable."""
    from src.game.avatars import AVATAR_CATALOG as catalog
    from src.game.avatars import get_avatar_choices as get_choices
    from src.game.avatars import render_avatar_svg as render

    assert isinstance(catalog, dict)
    assert callable(get_choices)
    assert callable(render)
