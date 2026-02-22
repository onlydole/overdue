"""Pixel art monster librarian avatar system.

Provides 12 selectable 48x48 monster librarian portraits rendered as SVG.
Avatars are built from species-specific rigs to maximize silhouette variety,
while preserving consistent readability at small sizes.
"""

from __future__ import annotations

import math
from typing import Callable

from src.game.icons._palette import blend_colors, darken, lighten

_CANVAS_MAX = 47
_CANVAS_MIN = 0
_OUTLINE = "#11131a"
_PUPIL = "#07080d"
_EYE_SCLERA = "#f6f8ff"

Pixel = tuple[int, int, str]
Ramp = dict[str, str]
AvatarBuilder = Callable[[list[Pixel], dict[str, Ramp], dict], None]


def _tone_ramp(base: str) -> Ramp:
    """Build a five-step color ramp for directional lighting."""
    return {
        "highlight": lighten(base, 0.30),
        "light": lighten(base, 0.16),
        "base": base,
        "shadow": darken(base, 0.20),
        "deep": darken(base, 0.36),
    }


def _eye_ramp(base: str) -> Ramp:
    """Build a compact eye ramp for iris/glow rendering."""
    return {
        "glow": lighten(base, 0.36),
        "light": lighten(base, 0.18),
        "base": base,
        "shadow": darken(base, 0.18),
        "deep": darken(base, 0.32),
    }


def _put(pixels: list[Pixel], x: int, y: int, color: str) -> None:
    """Place a pixel inside the avatar canvas."""
    if _CANVAS_MIN <= x <= _CANVAS_MAX and _CANVAS_MIN <= y <= _CANVAS_MAX:
        pixels.append((x, y, color))


def _fill_rect(
    pixels: list[Pixel],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str,
) -> None:
    """Fill a rectangle with inclusive bounds."""
    lo_x, hi_x = sorted((x1, x2))
    lo_y, hi_y = sorted((y1, y2))
    for y in range(lo_y, hi_y + 1):
        for x in range(lo_x, hi_x + 1):
            _put(pixels, x, y, color)


def _fill_rect_shaded(
    pixels: list[Pixel],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    ramp: Ramp,
    material: str = "matte",
) -> None:
    """Fill a rectangle with upper-left lighting and optional material texture."""
    lo_x, hi_x = sorted((x1, x2))
    lo_y, hi_y = sorted((y1, y2))
    width = max(1, hi_x - lo_x)
    height = max(1, hi_y - lo_y)

    for y in range(lo_y, hi_y + 1):
        ny = (y - lo_y) / height
        for x in range(lo_x, hi_x + 1):
            nx = (x - lo_x) / width
            tone = ramp["base"]
            if nx <= 0.16:
                tone = ramp["highlight"]
            elif nx <= 0.30:
                tone = ramp["light"]
            elif nx >= 0.82:
                tone = ramp["shadow"]
            if ny >= 0.78:
                tone = ramp["deep"]

            if material == "stone" and (x + (y * 2)) % 11 == 0:
                tone = ramp["shadow"]
            if material == "chitin" and (x - y) % 9 == 0:
                tone = ramp["light"]
            if material == "cloth" and y % 3 == 0 and 0.32 < nx < 0.68:
                tone = blend_colors(tone, ramp["light"], 0.35)

            _put(pixels, x, y, tone)


def _fill_ellipse(
    pixels: list[Pixel],
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    color: str,
) -> None:
    """Fill an ellipse centered at ``(cx, cy)``."""
    if rx <= 0 or ry <= 0:
        return

    for y in range(cy - ry, cy + ry + 1):
        ny = (y - cy) / ry
        span_sq = 1.0 - (ny * ny)
        if span_sq < 0:
            continue
        span = int(math.sqrt(span_sq) * rx)
        for x in range(cx - span, cx + span + 1):
            _put(pixels, x, y, color)


def _fill_ellipse_shaded(
    pixels: list[Pixel],
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    ramp: Ramp,
    material: str = "matte",
) -> None:
    """Fill an ellipse with material-aware directional shading."""
    if rx <= 0 or ry <= 0:
        return

    for y in range(cy - ry, cy + ry + 1):
        ny = (y - cy) / ry
        span_sq = 1.0 - (ny * ny)
        if span_sq < 0:
            continue
        span = int(math.sqrt(span_sq) * rx)
        for x in range(cx - span, cx + span + 1):
            nx = (x - cx) / rx
            tone = ramp["base"]
            if nx <= -0.36:
                tone = ramp["highlight"]
            elif nx <= -0.14:
                tone = ramp["light"]
            elif nx >= 0.38:
                tone = ramp["shadow"]
            if ny >= 0.62:
                tone = ramp["deep"]

            if material == "gelatin":
                if ny < -0.20 and abs(nx) < 0.24:
                    tone = ramp["highlight"]
                if (x + (y * 2)) % 13 == 0 and ny < 0.25:
                    tone = blend_colors(tone, ramp["light"], 0.42)
            elif material == "fur":
                if y % 3 == 0 and abs(nx) > 0.42:
                    tone = ramp["shadow"]
                if y % 4 == 0 and abs(nx) < 0.12:
                    tone = ramp["light"]
            elif material == "stone":
                if (x + y) % 10 == 0:
                    tone = ramp["shadow"]
            elif material == "spectral":
                if ny < -0.25:
                    tone = blend_colors(ramp["highlight"], "#ffffff", 0.45)
                elif (x + y) % 12 == 0:
                    tone = blend_colors(ramp["light"], ramp["highlight"], 0.40)
            elif material == "scale":
                if (x - y) % 8 == 0:
                    tone = ramp["light"]
            elif material == "chitin":
                if (x + y) % 9 == 0:
                    tone = ramp["shadow"]

            _put(pixels, x, y, tone)


def _draw_line(
    pixels: list[Pixel],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str,
    thickness: int = 1,
) -> None:
    """Draw a Bresenham line with optional thickness."""
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy

    x = x1
    y = y1
    while True:
        for ox in range(-(thickness // 2), (thickness // 2) + 1):
            for oy in range(-(thickness // 2), (thickness // 2) + 1):
                _put(pixels, x + ox, y + oy, color)
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def _draw_diamond(
    pixels: list[Pixel],
    cx: int,
    cy: int,
    radius: int,
    color: str,
) -> None:
    """Draw a filled diamond for gems, runes, and clasps."""
    for dy in range(-radius, radius + 1):
        span = radius - abs(dy)
        for dx in range(-span, span + 1):
            _put(pixels, cx + dx, cy + dy, color)


def _fill_triangle_up(
    pixels: list[Pixel],
    cx: int,
    top_y: int,
    height: int,
    color: str,
) -> None:
    """Draw an upward-pointing triangle."""
    for step in range(height):
        y = top_y + step
        for x in range(cx - step, cx + step + 1):
            _put(pixels, x, y, color)


def _fill_triangle_down(
    pixels: list[Pixel],
    cx: int,
    bottom_y: int,
    height: int,
    color: str,
) -> None:
    """Draw a downward-pointing triangle."""
    for step in range(height):
        y = bottom_y - step
        for x in range(cx - step, cx + step + 1):
            _put(pixels, x, y, color)


def _draw_ring(
    pixels: list[Pixel],
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    color: str,
) -> None:
    """Draw a rough ellipse ring."""
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            nx = (x - cx) / max(1, rx)
            ny = (y - cy) / max(1, ry)
            d = (nx * nx) + (ny * ny)
            if 0.80 <= d <= 1.25:
                _put(pixels, x, y, color)


def _draw_robe(
    pixels: list[Pixel],
    robe_ramp: Ramp,
    accent_ramp: Ramp,
    *,
    center: int = 24,
    y_top: int = 33,
    y_bottom: int = 47,
    width_top: int = 7,
    width_bottom: int = 16,
) -> None:
    """Draw a robe block with collar and central clasp."""
    span_growth = max(1, y_bottom - y_top)
    for y in range(y_top, y_bottom + 1):
        t = (y - y_top) / span_growth
        half = int(width_top + (width_bottom - width_top) * t)
        lo = center - half
        hi = center + half
        for x in range(lo, hi + 1):
            tone = robe_ramp["base"]
            if x <= lo + 2:
                tone = robe_ramp["light"]
            elif x >= hi - 2:
                tone = robe_ramp["shadow"]
            if y >= y_bottom - 2:
                tone = robe_ramp["deep"]
            if y % 3 == 0 and lo + 4 < x < hi - 4:
                tone = blend_colors(tone, robe_ramp["light"], 0.20)
            _put(pixels, x, y, tone)

    for row in range(4):
        y = y_top + row
        _fill_rect(pixels, center - (4 + row), y, center - 2, y, robe_ramp["highlight"])
        _fill_rect(pixels, center + 2, y, center + (4 + row), y, robe_ramp["highlight"])

    _draw_diamond(pixels, center, min(46, y_top + 6), 2, accent_ramp["base"])
    _draw_diamond(pixels, center, min(46, y_top + 6), 1, accent_ramp["highlight"])


def _draw_eye_pair(
    pixels: list[Pixel],
    left_x: int,
    right_x: int,
    y: int,
    iris_ramp: Ramp,
    *,
    slit: bool = False,
    wide: bool = False,
) -> None:
    """Draw two eyes with optional slit pupils and wider sclera."""
    rx = 4 if wide else 3
    ry = 2
    for eye_x in (left_x, right_x):
        _fill_ellipse(pixels, eye_x, y, rx, ry, _EYE_SCLERA)
        _fill_ellipse(pixels, eye_x, y, max(1, rx - 1), ry, iris_ramp["base"])
        _put(pixels, eye_x - 1, y - 1, iris_ramp["glow"])
        if slit:
            for sy in range(y - 1, y + 2):
                _put(pixels, eye_x, sy, _PUPIL)
        else:
            _put(pixels, eye_x, y, _PUPIL)


def _draw_single_eye(
    pixels: list[Pixel],
    x: int,
    y: int,
    iris_ramp: Ramp,
) -> None:
    """Draw a large cyclopean eye."""
    _fill_ellipse(pixels, x, y, 7, 4, _EYE_SCLERA)
    _fill_ellipse(pixels, x, y, 5, 3, iris_ramp["base"])
    _fill_ellipse(pixels, x, y, 2, 2, _PUPIL)
    _put(pixels, x - 2, y - 2, iris_ramp["glow"])
    _draw_ring(pixels, x, y, 8, 5, darken(iris_ramp["shadow"], 0.2))


def _draw_compound_eyes(
    pixels: list[Pixel],
    left_x: int,
    right_x: int,
    y: int,
    iris_ramp: Ramp,
) -> None:
    """Draw textured eyes for insectoid species."""
    for base_x in (left_x, right_x):
        _fill_ellipse(pixels, base_x, y, 4, 3, iris_ramp["shadow"])
        for offset_x in (-2, -1, 0, 1, 2):
            for offset_y in (-1, 0, 1):
                if (offset_x + offset_y) % 2 == 0:
                    _put(pixels, base_x + offset_x, y + offset_y, iris_ramp["base"])
        _put(pixels, base_x - 1, y - 1, iris_ramp["glow"])


def _draw_mouth(
    pixels: list[Pixel],
    species: str,
    y: int,
    body_ramp: Ramp,
    accent_ramp: Ramp,
) -> None:
    """Draw species-specific mouths and fangs."""
    if species in {"slime", "imp"}:
        for x in range(18, 31):
            _put(pixels, x, y + abs(24 - x) // 6, body_ramp["deep"])
        return

    if species in {"gargoyle", "batfolk"}:
        for x in range(18, 31):
            _put(pixels, x, y + abs(24 - x) // 7, body_ramp["deep"])
        _fill_rect(pixels, 21, y + 1, 22, y + 3, accent_ramp["highlight"])
        _fill_rect(pixels, 26, y + 1, 27, y + 3, accent_ramp["highlight"])
        return

    if species == "cyclops":
        _fill_rect(pixels, 19, y, 29, y + 1, body_ramp["deep"])
        for x in range(20, 30, 2):
            _put(pixels, x, y, accent_ramp["highlight"])
        return

    if species in {"kobold", "basilisk"}:
        _fill_rect(pixels, 20, y, 29, y + 1, body_ramp["deep"])
        _draw_line(pixels, 24, y + 1, 24, y + 3, accent_ramp["highlight"])
        if species == "basilisk":
            _draw_line(pixels, 24, y + 3, 22, y + 5, accent_ramp["highlight"])
            _draw_line(pixels, 24, y + 3, 26, y + 5, accent_ramp["highlight"])
        return

    if species == "kraken":
        _fill_rect(pixels, 19, y, 29, y + 1, body_ramp["deep"])
        _draw_diamond(pixels, 24, y + 1, 1, accent_ramp["highlight"])
        return

    if species == "golem":
        _fill_rect(pixels, 18, y, 30, y + 2, body_ramp["deep"])
        for x in range(19, 31, 2):
            _put(pixels, x, y + 1, accent_ramp["highlight"])
        return

    if species == "ghost":
        _fill_ellipse(pixels, 24, y + 1, 4, 2, body_ramp["deep"])
        _fill_ellipse(pixels, 24, y + 1, 2, 1, darken(body_ramp["deep"], 0.1))
        return

    if species == "myconid":
        _fill_rect(pixels, 21, y, 27, y + 1, body_ramp["shadow"])
        return

    _fill_rect(pixels, 20, y, 29, y + 1, body_ramp["deep"])


def _draw_accessory(
    pixels: list[Pixel],
    species: str,
    accessory: str,
    accent_ramp: Ramp,
) -> None:
    """Draw glasses/visor/chains around focal zones."""
    left, right, eye_y = _ACCESSORY_EYES.get(species, (18, 30, 22))

    if accessory == "spectacles":
        _fill_rect(pixels, left - 3, eye_y - 2, left + 3, eye_y + 2, _OUTLINE)
        _fill_rect(pixels, right - 3, eye_y - 2, right + 3, eye_y + 2, _OUTLINE)
        _fill_rect(pixels, left - 2, eye_y - 1, left + 2, eye_y + 1, "#7aa6c8")
        _fill_rect(pixels, right - 2, eye_y - 1, right + 2, eye_y + 1, "#7aa6c8")
        _fill_rect(pixels, left + 4, eye_y, right - 4, eye_y, _OUTLINE)

    if accessory == "monocle":
        target_x = right + 1 if species != "cyclops" else 24
        target_y = eye_y
        _draw_ring(pixels, target_x, target_y, 4, 3, _OUTLINE)
        _fill_ellipse(pixels, target_x, target_y, 3, 2, "#7aa6c8")
        _draw_line(pixels, target_x + 3, target_y + 2, target_x + 4, target_y + 8, accent_ramp["base"])

    if accessory == "visor":
        _fill_rect(pixels, left - 5, eye_y - 2, right + 5, eye_y + 2, _OUTLINE)
        _fill_rect(pixels, left - 4, eye_y - 1, right + 4, eye_y + 1, "#5a7fa3")

    if accessory == "chain":
        chain_y = min(44, eye_y + 15)
        for x in range(16, 33, 2):
            _draw_diamond(pixels, x, chain_y, 1, accent_ramp["base"])


def _draw_prop(
    pixels: list[Pixel],
    species: str,
    prop: str,
    accent_ramp: Ramp,
) -> None:
    """Draw tiny librarian props near the chest focal zone."""
    x, y = _PROP_ANCHORS.get(species, (24, 41))

    if prop == "book":
        _fill_rect(pixels, x - 5, y - 3, x + 5, y + 3, "#f0e6d3")
        _fill_rect(pixels, x - 1, y - 3, x + 1, y + 3, darken("#f0e6d3", 0.25))
        _fill_rect(pixels, x - 5, y - 3, x + 5, y - 2, accent_ramp["shadow"])

    if prop == "tablet":
        _fill_rect(pixels, x - 4, y - 4, x + 4, y + 4, accent_ramp["shadow"])
        _fill_rect(pixels, x - 3, y - 3, x + 3, y + 3, accent_ramp["light"])
        for row in (-1, 1):
            _fill_rect(pixels, x - 2, y + row, x + 2, y + row, accent_ramp["shadow"])

    if prop == "lantern":
        _fill_rect(pixels, x - 2, y - 3, x + 2, y + 3, accent_ramp["shadow"])
        _fill_rect(pixels, x - 1, y - 2, x + 1, y + 2, accent_ramp["highlight"])
        _draw_line(pixels, x, y - 5, x, y - 3, accent_ramp["base"])

    if prop == "orb":
        _fill_ellipse(pixels, x, y, 3, 3, accent_ramp["light"])
        _draw_ring(pixels, x, y, 4, 4, accent_ramp["base"])

    if prop == "scroll":
        _fill_rect(pixels, x - 5, y - 2, x + 5, y + 2, "#f0e6d3")
        _fill_ellipse(pixels, x - 6, y, 1, 2, accent_ramp["shadow"])
        _fill_ellipse(pixels, x + 6, y, 1, 2, accent_ramp["shadow"])

    if prop == "stamp":
        _fill_rect(pixels, x - 3, y - 1, x + 3, y + 2, accent_ramp["shadow"])
        _fill_rect(pixels, x - 1, y - 4, x + 1, y - 1, accent_ramp["base"])

    if prop == "jar":
        _fill_rect(pixels, x - 3, y - 3, x + 3, y + 3, "#8fd9cf")
        _fill_rect(pixels, x - 2, y - 4, x + 2, y - 3, accent_ramp["shadow"])
        _put(pixels, x - 1, y - 1, accent_ramp["highlight"])

    if prop == "atlas":
        _fill_rect(pixels, x - 5, y - 3, x + 5, y + 3, "#252a4f")
        for point in ((x - 2, y), (x, y - 1), (x + 2, y), (x, y + 1)):
            _draw_diamond(pixels, point[0], point[1], 1, accent_ramp["highlight"])


def _draw_features(
    pixels: list[Pixel],
    species: str,
    feature_set: list[str],
    body_ramp: Ramp,
    accent_ramp: Ramp,
) -> None:
    """Apply optional feature overlays for additional uniqueness."""
    for feature in feature_set:
        if feature == "slime_drip":
            for x, h in ((13, 5), (24, 7), (35, 4)):
                _fill_rect(pixels, x, 30, x + 1, 30 + h, body_ramp["light"])
                _put(pixels, x, 31 + h, body_ramp["highlight"])

        if feature == "catalog_tag":
            _fill_rect(pixels, 30, 34, 35, 37, accent_ramp["light"])
            _draw_line(pixels, 29, 33, 30, 34, accent_ramp["base"])

        if feature == "horn_crown":
            _fill_triangle_up(pixels, 12, 4, 7, accent_ramp["base"])
            _fill_triangle_up(pixels, 36, 4, 7, accent_ramp["base"])
            _fill_triangle_up(pixels, 12, 5, 5, accent_ramp["highlight"])
            _fill_triangle_up(pixels, 36, 5, 5, accent_ramp["highlight"])

        if feature == "stone_wings":
            for y in range(12, 33):
                left = max(0, 8 - ((y - 12) // 2))
                right = min(47, 40 + ((y - 12) // 2))
                _fill_rect(pixels, left, y, 12, y, accent_ramp["shadow"])
                _fill_rect(pixels, 36, y, right, y, accent_ramp["shadow"])
                if y % 2 == 0:
                    _put(pixels, 10, y, accent_ramp["light"])
                    _put(pixels, 38, y, accent_ramp["light"])

        if feature == "rune_cracks":
            for segment in ((16, 16, 20, 20), (31, 15, 28, 21), (23, 24, 26, 28)):
                _draw_line(pixels, segment[0], segment[1], segment[2], segment[3], accent_ramp["shadow"])

        if feature == "antennae":
            _draw_line(pixels, 19, 14, 14, 4, accent_ramp["shadow"])
            _draw_line(pixels, 29, 14, 34, 4, accent_ramp["shadow"])
            _draw_diamond(pixels, 14, 3, 1, accent_ramp["highlight"])
            _draw_diamond(pixels, 34, 3, 1, accent_ramp["highlight"])

        if feature == "wing_eyespots":
            for cx, cy in ((9, 24), (39, 24), (12, 29), (36, 29)):
                _draw_ring(pixels, cx, cy, 2, 2, accent_ramp["highlight"])

        if feature == "dust_trail":
            for x, y in ((8, 12), (12, 9), (36, 10), (40, 13), (24, 5)):
                _draw_diamond(pixels, x, y, 1, accent_ramp["highlight"])

        if feature == "runic_aura":
            _draw_ring(pixels, 24, 21, 17, 12, accent_ramp["base"])
            for x, y in ((9, 21), (39, 21), (24, 8), (24, 34)):
                _draw_diamond(pixels, x, y, 1, accent_ramp["highlight"])

        if feature == "index_orbit":
            for x, y in ((16, 16), (32, 17), (34, 26), (14, 27)):
                _fill_ellipse(pixels, x, y, 2, 1, accent_ramp["highlight"])

        if feature == "quill_behind_ear":
            _draw_line(pixels, 12, 16, 7, 7, accent_ramp["base"])
            _fill_triangle_up(pixels, 7, 4, 3, accent_ramp["light"])

        if feature == "ink_stains":
            for x, y in ((15, 39), (19, 41), (30, 40), (33, 43)):
                _fill_ellipse(pixels, x, y, 1, 1, darken(body_ramp["deep"], 0.1))

        if feature == "sucker_rows":
            for base_x in (11, 17, 23, 29, 35):
                for y in range(32, 46, 3):
                    _draw_ring(pixels, base_x + ((y // 2) % 2), y, 1, 1, accent_ramp["light"])

        if feature == "tentacle_fan":
            for idx, start_x in enumerate((8, 13, 18, 23, 28, 33, 38)):
                for y in range(29, 47):
                    sway = ((idx + y) % 4) - 2
                    _put(pixels, start_x + sway, y, body_ramp["shadow"])
                    _put(pixels, start_x + sway + 1, y, body_ramp["deep"])

        if feature == "crystal_spines":
            for x, y, h in ((11, 8, 6), (24, 4, 7), (37, 9, 5)):
                _fill_triangle_up(pixels, x, y, h, accent_ramp["base"])
                _fill_triangle_up(pixels, x, y + 1, max(2, h - 2), accent_ramp["highlight"])

        if feature == "engraved_tablet":
            for x in range(19, 30, 2):
                _put(pixels, x, 39, accent_ramp["shadow"])

        if feature == "wisp_tail":
            for y in range(35, 47):
                span = max(2, 12 - ((y - 35) // 1))
                _fill_rect(pixels, 24 - span, y, 24 + span, y, body_ramp["light"])
                if y % 2 == 0:
                    _put(pixels, 24 - span, y, body_ramp["highlight"])
                    _put(pixels, 24 + span, y, body_ramp["highlight"])

        if feature == "spectral_whorl":
            _draw_line(pixels, 10, 24, 4, 30, accent_ramp["light"])
            _draw_line(pixels, 38, 24, 44, 30, accent_ramp["light"])

        if feature == "spore_cloud":
            for x, y in ((8, 8), (13, 6), (18, 5), (31, 5), (36, 7), (40, 9)):
                _draw_diamond(pixels, x, y, 1, accent_ramp["highlight"])

        if feature == "mushroom_spots":
            for x, y, r in ((14, 9, 2), (24, 7, 2), (33, 10, 2), (20, 12, 1), (29, 13, 1)):
                _fill_ellipse(pixels, x, y, r, r, accent_ramp["light"])

        if feature == "hood_scales":
            for y in range(15, 29, 2):
                left = 9 + ((y - 15) // 3)
                right = 39 - ((y - 15) // 3)
                for x in range(left, right + 1, 3):
                    _put(pixels, x, y, body_ramp["light"])

        if feature == "forked_tongue":
            _draw_line(pixels, 24, 33, 24, 36, accent_ramp["highlight"])
            _draw_line(pixels, 24, 36, 22, 38, accent_ramp["highlight"])
            _draw_line(pixels, 24, 36, 26, 38, accent_ramp["highlight"])

        if feature == "star_cloak":
            for x, y in ((13, 35), (18, 38), (24, 40), (31, 37), (36, 35)):
                _draw_diamond(pixels, x, y, 1, accent_ramp["highlight"])

        if feature == "bat_cloak":
            for y in range(20, 37):
                _fill_rect(pixels, 4, y, 10, y, accent_ramp["shadow"])
                _fill_rect(pixels, 38, y, 44, y, accent_ramp["shadow"])
                if y % 3 == 0:
                    _put(pixels, 7, y, accent_ramp["light"])
                    _put(pixels, 41, y, accent_ramp["light"])

        if feature == "ember_horns":
            _fill_triangle_up(pixels, 10, 5, 8, accent_ramp["base"])
            _fill_triangle_up(pixels, 38, 5, 8, accent_ramp["base"])
            _fill_triangle_up(pixels, 10, 6, 6, accent_ramp["highlight"])
            _fill_triangle_up(pixels, 38, 6, 6, accent_ramp["highlight"])

        if feature == "cinder_tail":
            _draw_line(pixels, 34, 32, 42, 43, body_ramp["shadow"])
            _draw_diamond(pixels, 43, 44, 2, accent_ramp["highlight"])

        if feature == "ember_runes":
            for x, y in ((17, 17), (24, 14), (30, 18), (22, 27), (28, 26)):
                _draw_diamond(pixels, x, y, 1, accent_ramp["highlight"])


def _build_slime_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 24, 23, 15, 12, body, material="gelatin")

    for y in range(35, 48):
        span = 13 + ((y - 35) * 2 // 3)
        _fill_rect(pixels, 24 - span, y, 24 + span, y, body["shadow"] if y > 42 else body["base"])

    _draw_robe(pixels, robe, accent, y_top=31, y_bottom=44, width_top=6, width_bottom=12)
    _draw_eye_pair(pixels, 18, 30, 22, ramps["eye"], wide=True)
    _draw_mouth(pixels, "slime", 31, body, accent)


def _build_gargoyle_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_rect_shaded(pixels, 10, 11, 38, 31, body, material="stone")
    _fill_rect_shaded(pixels, 7, 18, 15, 30, body, material="stone")
    _fill_rect_shaded(pixels, 33, 18, 41, 30, body, material="stone")
    _fill_rect_shaded(pixels, 14, 29, 34, 36, body, material="stone")

    _draw_robe(pixels, robe, accent, y_top=34, y_bottom=47, width_top=5, width_bottom=10)
    _draw_eye_pair(pixels, 17, 31, 20, ramps["eye"], slit=True)
    _draw_mouth(pixels, "gargoyle", 30, body, accent)


def _build_mothfolk_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 9, 26, 9, 11, accent, material="chitin")
    _fill_ellipse_shaded(pixels, 34, 20, 8, 10, accent, material="chitin")
    _fill_ellipse_shaded(pixels, 38, 31, 6, 7, accent, material="chitin")
    _fill_ellipse_shaded(pixels, 24, 22, 8, 12, body, material="fur")

    _draw_robe(pixels, robe, accent, y_top=34, y_bottom=47, width_top=5, width_bottom=11)
    _draw_compound_eyes(pixels, 18, 30, 22, ramps["eye"])
    _draw_mouth(pixels, "myconid", 31, body, accent)


def _build_cyclops_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 20, 21, 10, 13, body, material="matte")
    _fill_rect_shaded(pixels, 13, 30, 28, 37, body, material="matte")
    _fill_rect_shaded(pixels, 29, 30, 36, 36, body, material="matte")

    _draw_line(pixels, 12, 16, 27, 14, accent["shadow"], thickness=2)
    _draw_robe(pixels, robe, accent, center=20, y_top=34, y_bottom=47, width_top=4, width_bottom=8)
    _draw_single_eye(pixels, 20, 21, ramps["eye"])
    _draw_mouth(pixels, "cyclops", 32, body, accent)


def _build_kobold_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 22, 23, 11, 11, body, material="scale")
    _fill_rect_shaded(pixels, 26, 22, 37, 29, body, material="scale")
    _fill_triangle_up(pixels, 14, 8, 8, body["shadow"])
    _fill_triangle_up(pixels, 30, 7, 9, body["shadow"])
    _fill_triangle_up(pixels, 14, 10, 5, body["light"])
    _fill_triangle_up(pixels, 30, 9, 6, body["light"])

    _draw_robe(pixels, robe, accent, y_top=33, y_bottom=47, width_top=6, width_bottom=12)
    _draw_eye_pair(pixels, 18, 27, 22, ramps["eye"], slit=True)
    _draw_mouth(pixels, "kobold", 31, body, accent)


def _build_kraken_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 22, 16, 11, 9, body, material="gelatin")
    _fill_rect_shaded(pixels, 12, 21, 32, 27, body, material="gelatin")
    _fill_rect_shaded(pixels, 16, 27, 28, 32, body, material="gelatin")

    for y in range(29, 47):
        sway_l = ((y + 1) % 4) - 2
        sway_r = (y % 4) - 1
        _put(pixels, 4 + sway_l, y, body["shadow"])
        _put(pixels, 5 + sway_l, y, body["deep"])
        _put(pixels, 41 + sway_r, y, body["shadow"])
        _put(pixels, 42 + sway_r, y, body["deep"])

    _draw_robe(pixels, robe, accent, center=22, y_top=29, y_bottom=38, width_top=7, width_bottom=10)
    _draw_eye_pair(pixels, 18, 26, 18, ramps["eye"], slit=False)
    _draw_mouth(pixels, "kraken", 26, body, accent)


def _build_golem_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_rect_shaded(pixels, 12, 10, 44, 31, body, material="stone")
    _fill_rect_shaded(pixels, 4, 15, 15, 28, body, material="stone")
    _fill_rect_shaded(pixels, 41, 15, 47, 28, body, material="stone")
    _fill_rect_shaded(pixels, 17, 30, 39, 39, body, material="stone")

    _draw_robe(pixels, robe, accent, center=28, y_top=35, y_bottom=47, width_top=4, width_bottom=8)
    _draw_eye_pair(pixels, 22, 34, 21, ramps["eye"], slit=True)
    _draw_mouth(pixels, "golem", 30, body, accent)


def _build_ghost_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 28, 16, 10, 8, body, material="spectral")
    _fill_ellipse_shaded(pixels, 28, 25, 12, 10, body, material="spectral")

    for y in range(32, 48):
        span = max(3, 10 - ((y - 32) // 2))
        drift = (y - 32) // 4
        center = 28 + drift
        left = center - span
        right = center + span
        _fill_rect(pixels, left, y, right, y, body["light"] if y < 43 else body["base"])
        if y % 2 == 1:
            _put(pixels, left, y, body["highlight"])
            _put(pixels, right, y, body["highlight"])

    _draw_line(pixels, 16, 24, 8, 31, accent["light"])
    _draw_line(pixels, 37, 22, 45, 30, accent["light"])
    _draw_eye_pair(pixels, 24, 32, 19, ramps["eye"], wide=False)
    _draw_mouth(pixels, "ghost", 28, body, accent)


def _build_myconid_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 24, 10, 20, 7, accent, material="matte")
    _fill_rect_shaded(pixels, 6, 11, 42, 15, accent, material="matte")

    for x in range(8, 41, 3):
        _draw_line(pixels, x, 12, x + 1, 15, accent["shadow"])

    _fill_ellipse_shaded(pixels, 24, 24, 9, 12, body, material="matte")
    _draw_robe(pixels, robe, accent, y_top=34, y_bottom=47, width_top=6, width_bottom=12)
    _draw_eye_pair(pixels, 20, 28, 25, ramps["eye"], wide=False)
    _draw_mouth(pixels, "myconid", 31, body, accent)


def _build_basilisk_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    hood_ramp = _tone_ramp(blend_colors(accent["base"], body["base"], 0.45))
    _fill_ellipse_shaded(pixels, 20, 21, 17, 11, hood_ramp, material="scale")
    _fill_rect_shaded(pixels, 14, 23, 26, 40, body, material="scale")
    _fill_ellipse_shaded(pixels, 20, 42, 12, 5, body, material="scale")

    _draw_robe(pixels, robe, accent, center=20, y_top=34, y_bottom=46, width_top=4, width_bottom=9)
    _draw_eye_pair(pixels, 14, 24, 22, ramps["eye"], slit=True)
    _draw_mouth(pixels, "basilisk", 32, body, accent)


def _build_batfolk_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_triangle_up(pixels, 9, 5, 12, body["shadow"])
    _fill_triangle_up(pixels, 39, 5, 12, body["shadow"])
    _fill_triangle_up(pixels, 9, 7, 8, body["light"])
    _fill_triangle_up(pixels, 39, 7, 8, body["light"])

    _fill_ellipse_shaded(pixels, 24, 22, 10, 11, body, material="fur")
    _fill_rect_shaded(pixels, 8, 20, 15, 36, accent, material="chitin")
    _fill_rect_shaded(pixels, 33, 20, 40, 36, accent, material="chitin")

    _draw_robe(pixels, robe, accent, y_top=33, y_bottom=47, width_top=8, width_bottom=15)
    _draw_eye_pair(pixels, 18, 30, 22, ramps["eye"], slit=False)
    _draw_mouth(pixels, "batfolk", 31, body, accent)


def _build_imp_rig(pixels: list[Pixel], ramps: dict[str, Ramp], avatar_def: dict) -> None:
    body = ramps["body"]
    robe = ramps["robe"]
    accent = ramps["accent"]

    _fill_ellipse_shaded(pixels, 24, 23, 9, 10, body, material="matte")
    _fill_rect_shaded(pixels, 15, 27, 33, 34, body, material="matte")

    _draw_robe(pixels, robe, accent, y_top=34, y_bottom=47, width_top=5, width_bottom=10)
    _draw_eye_pair(pixels, 19, 29, 23, ramps["eye"], slit=False)
    _draw_mouth(pixels, "imp", 31, body, accent)


_SPECIES_BUILDERS: dict[str, AvatarBuilder] = {
    "slime": _build_slime_rig,
    "gargoyle": _build_gargoyle_rig,
    "mothfolk": _build_mothfolk_rig,
    "cyclops": _build_cyclops_rig,
    "kobold": _build_kobold_rig,
    "kraken": _build_kraken_rig,
    "golem": _build_golem_rig,
    "ghost": _build_ghost_rig,
    "myconid": _build_myconid_rig,
    "basilisk": _build_basilisk_rig,
    "batfolk": _build_batfolk_rig,
    "imp": _build_imp_rig,
}


_ACCESSORY_EYES: dict[str, tuple[int, int, int]] = {
    "slime": (18, 30, 22),
    "gargoyle": (17, 31, 20),
    "mothfolk": (18, 30, 22),
    "cyclops": (16, 24, 20),
    "kobold": (18, 27, 22),
    "kraken": (18, 26, 18),
    "golem": (22, 34, 21),
    "ghost": (24, 32, 19),
    "myconid": (20, 28, 25),
    "basilisk": (14, 24, 22),
    "batfolk": (18, 30, 22),
    "imp": (19, 29, 23),
}


_PROP_ANCHORS: dict[str, tuple[int, int]] = {
    "slime": (28, 40),
    "gargoyle": (24, 41),
    "mothfolk": (24, 40),
    "cyclops": (20, 41),
    "kobold": (25, 41),
    "kraken": (22, 38),
    "golem": (28, 41),
    "ghost": (29, 38),
    "myconid": (24, 41),
    "basilisk": (20, 41),
    "batfolk": (24, 41),
    "imp": (24, 41),
}


AVATAR_CATALOG: dict[str, dict] = {
    "avatar_01": {
        "name": "Mossquill",
        "description": "A gelatinous archivist who files spores by scent and shelf humidity.",
        "species": "slime",
        "body_plan": "amorphous_blob",
        "material": "gelatin",
        "body_color": "#3f9d68",
        "eye_color": "#dff7ff",
        "robe_color": "#2f5d3a",
        "accent_color": "#9de28f",
        "primary_anchor": "cascading_slime_cowl",
        "feature_set": ["slime_drip", "catalog_tag"],
        "accessory": "spectacles",
        "prop": "jar",
        "role_title": "Mucus Archivist",
        "specialty": "Spore taxonomies",
        "quirk": "Labels every vial twice",
    },
    "avatar_02": {
        "name": "Basaltor",
        "description": "A gargoyle vault-warden who memorizes forbidden index pages.",
        "species": "gargoyle",
        "body_plan": "winged_stone_bastion",
        "material": "stone",
        "body_color": "#6d6f7e",
        "eye_color": "#f0c543",
        "robe_color": "#2b3242",
        "accent_color": "#adb5ca",
        "primary_anchor": "cathedral_horn_crown",
        "feature_set": ["horn_crown", "stone_wings", "rune_cracks"],
        "accessory": "chain",
        "prop": "book",
        "role_title": "Vault Warden",
        "specialty": "Forbidden ledgers",
        "quirk": "Never blinks during audits",
    },
    "avatar_03": {
        "name": "Lumen Moth",
        "description": "A mothfolk conservator that repairs brittle margins under moonlight.",
        "species": "mothfolk",
        "body_plan": "mantled_insectoid",
        "material": "chitin",
        "body_color": "#77649e",
        "eye_color": "#c5e9ff",
        "robe_color": "#392656",
        "accent_color": "#ffdca2",
        "primary_anchor": "inked_wing_mantle",
        "feature_set": ["antennae", "wing_eyespots", "dust_trail"],
        "accessory": "monocle",
        "prop": "lantern",
        "role_title": "Dust Conservator",
        "specialty": "Moonlit footnotes",
        "quirk": "Flutters when citing sources",
    },
    "avatar_04": {
        "name": "Indexar",
        "description": "A cyclopean reference master with impossible one-glance recall.",
        "species": "cyclops",
        "body_plan": "single_eye_colossus",
        "material": "matte",
        "body_color": "#8e4f83",
        "eye_color": "#b6ffd8",
        "robe_color": "#4a1f48",
        "accent_color": "#d59cdf",
        "primary_anchor": "orbital_index_eye",
        "feature_set": ["runic_aura", "index_orbit"],
        "accessory": "visor",
        "prop": "orb",
        "role_title": "Reference Master",
        "specialty": "Misfile recovery",
        "quirk": "Recites call numbers in reverse",
    },
    "avatar_05": {
        "name": "Scalescribe",
        "description": "A kobold margin-scribe who tracks every annotation trail.",
        "species": "kobold",
        "body_plan": "snouted_scholar",
        "material": "scale",
        "body_color": "#b4713d",
        "eye_color": "#f9f6d2",
        "robe_color": "#5b3921",
        "accent_color": "#ebb57c",
        "primary_anchor": "quill_hooked_ears",
        "feature_set": ["quill_behind_ear", "ink_stains"],
        "accessory": "spectacles",
        "prop": "scroll",
        "role_title": "Margin Scribe",
        "specialty": "Edge annotations",
        "quirk": "Chews quills while thinking",
    },
    "avatar_06": {
        "name": "Tentra",
        "description": "A deep-ocean binder who rethreads drowned manuscripts by hand.",
        "species": "kraken",
        "body_plan": "cephalic_fan",
        "material": "gelatin",
        "body_color": "#367a8c",
        "eye_color": "#d2f9ff",
        "robe_color": "#1f4d59",
        "accent_color": "#75cae0",
        "primary_anchor": "splayed_tentacle_fan",
        "feature_set": ["tentacle_fan", "sucker_rows"],
        "accessory": "chain",
        "prop": "book",
        "role_title": "Abyss Binder",
        "specialty": "Waterlogged folios",
        "quirk": "Keeps six bookmarks per chapter",
    },
    "avatar_07": {
        "name": "Archivolith",
        "description": "A seismic golem conservator built to stabilize collapsing stacks.",
        "species": "golem",
        "body_plan": "blockwork_titan",
        "material": "stone",
        "body_color": "#7b7361",
        "eye_color": "#fff2ae",
        "robe_color": "#4a4032",
        "accent_color": "#d8c69a",
        "primary_anchor": "crystal_spine_citadel",
        "feature_set": ["crystal_spines", "engraved_tablet"],
        "accessory": "monocle",
        "prop": "tablet",
        "role_title": "Seismic Conservator",
        "specialty": "Shelf reinforcement",
        "quirk": "Taps stacks to hear stress fractures",
    },
    "avatar_08": {
        "name": "Whisper Wisp",
        "description": "A ghostly circulation clerk that patrols silent aisles after dusk.",
        "species": "ghost",
        "body_plan": "spectral_shroud",
        "material": "spectral",
        "body_color": "#b8d5ff",
        "eye_color": "#84fffa",
        "robe_color": "#5a6f95",
        "accent_color": "#d7f2ff",
        "primary_anchor": "torn_wisp_tail",
        "feature_set": ["wisp_tail", "spectral_whorl"],
        "accessory": "chain",
        "prop": "stamp",
        "role_title": "Night Circulation Clerk",
        "specialty": "After-hours returns",
        "quirk": "Stamps books without touching them",
    },
    "avatar_09": {
        "name": "Sporelia",
        "description": "A myconid cataloger who indexes fungi by drift pattern and bloom.",
        "species": "myconid",
        "body_plan": "cap_stalk_librarian",
        "material": "matte",
        "body_color": "#92735b",
        "eye_color": "#f5efc0",
        "robe_color": "#4d3426",
        "accent_color": "#d8a673",
        "primary_anchor": "oversized_cap_canopy",
        "feature_set": ["spore_cloud", "mushroom_spots"],
        "accessory": "spectacles",
        "prop": "jar",
        "role_title": "Fungi Cataloger",
        "specialty": "Field-note spores",
        "quirk": "Sneezes glittering pollen",
    },
    "avatar_10": {
        "name": "Vireon",
        "description": "A basilisk hunter-librarian with a stare tuned for disorder.",
        "species": "basilisk",
        "body_plan": "hooded_serpent",
        "material": "scale",
        "body_color": "#4f8a48",
        "eye_color": "#f7ffb8",
        "robe_color": "#2d4f2a",
        "accent_color": "#a7db78",
        "primary_anchor": "cobra_hood_index",
        "feature_set": ["hood_scales", "forked_tongue"],
        "accessory": "visor",
        "prop": "tablet",
        "role_title": "Chaos Hunter",
        "specialty": "Runaway classifications",
        "quirk": "Hisses when sorting by date",
    },
    "avatar_11": {
        "name": "Noxwing",
        "description": "A batfolk star-reader mapping constellations to shelf routes.",
        "species": "batfolk",
        "body_plan": "eared_nocturne",
        "material": "fur",
        "body_color": "#5b4d79",
        "eye_color": "#ffe5bc",
        "robe_color": "#33284a",
        "accent_color": "#bca6e8",
        "primary_anchor": "cathedral_ear_spires",
        "feature_set": ["bat_cloak", "star_cloak"],
        "accessory": "monocle",
        "prop": "atlas",
        "role_title": "Star Reader",
        "specialty": "Astral wayfinding",
        "quirk": "Navigates by moon phase",
    },
    "avatar_12": {
        "name": "Cinderimp",
        "description": "A volcanic clerk who marks overdue slips with ember precision.",
        "species": "imp",
        "body_plan": "horned_trickster",
        "material": "matte",
        "body_color": "#b24d3a",
        "eye_color": "#ffe7b0",
        "robe_color": "#5a251d",
        "accent_color": "#ff9e54",
        "primary_anchor": "ember_horn_arc",
        "feature_set": ["ember_horns", "cinder_tail", "ember_runes"],
        "accessory": "spectacles",
        "prop": "stamp",
        "role_title": "Overdue Clerk",
        "specialty": "Penalty seals",
        "quirk": "Leaves warm fingerprints on cards",
    },
}


def _build_avatar_pixels(avatar_def: dict) -> list[Pixel]:
    """Build a complete 48x48 monster librarian portrait."""
    body_ramp = _tone_ramp(avatar_def["body_color"])
    robe_ramp = _tone_ramp(avatar_def["robe_color"])
    accent_seed = blend_colors(avatar_def["accent_color"], avatar_def["robe_color"], 0.08)
    accent_ramp = _tone_ramp(accent_seed)
    eye_ramp = _eye_ramp(avatar_def["eye_color"])

    ramps = {
        "body": body_ramp,
        "robe": robe_ramp,
        "accent": accent_ramp,
        "eye": eye_ramp,
    }

    species = avatar_def.get("species", "slime")
    builder = _SPECIES_BUILDERS.get(species, _build_slime_rig)

    pixels: list[Pixel] = []
    builder(pixels, ramps, avatar_def)
    _draw_features(
        pixels,
        species,
        list(avatar_def.get("feature_set", [])),
        body_ramp,
        accent_ramp,
    )
    _draw_accessory(pixels, species, avatar_def.get("accessory", ""), accent_ramp)
    _draw_prop(pixels, species, avatar_def.get("prop", ""), accent_ramp)

    return pixels


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------


def _build_rects(pixels: list[Pixel]) -> str:
    """De-duplicate pixels (later wins) and return joined ``<rect>`` elements."""
    seen: dict[tuple[int, int], str] = {}
    for x, y, color in pixels:
        seen[(x, y)] = color

    parts: list[str] = []
    for (x, y), color in sorted(seen.items()):
        parts.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{color}"/>')
    return "".join(parts)


def render_avatar_svg(avatar_id: str, size: int = 32) -> str:
    """Return an inline SVG string for the given avatar."""
    avatar_def = AVATAR_CATALOG.get(avatar_id)
    if avatar_def is None:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"'
            f' width="{size}" height="{size}" style="image-rendering: pixelated;">'
            f'<rect width="48" height="48" fill="#1f1f2e"/>'
            f'<text x="24" y="30" text-anchor="middle" font-size="16" fill="#f0c543">?</text>'
            f"</svg>"
        )

    rect_block = _build_rects(_build_avatar_pixels(avatar_def))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"'
        f' width="{size}" height="{size}" class="pixel-icon" role="img" aria-hidden="true"'
        f' style="image-rendering: pixelated;">'
        f"{rect_block}"
        f"</svg>"
    )


def render_avatar_svg_bare(avatar_id: str) -> str | None:
    """Return a bare SVG string (no width/height/class/style) for static files."""
    avatar_def = AVATAR_CATALOG.get(avatar_id)
    if avatar_def is None:
        return None

    rect_block = _build_rects(_build_avatar_pixels(avatar_def))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">{rect_block}</svg>'


# ---------------------------------------------------------------------------
# Avatar picker helpers
# ---------------------------------------------------------------------------


def get_avatar_choices() -> list[dict[str, str]]:
    """Return avatar choices for registration and settings pickers."""
    return [
        {
            "id": avatar_id,
            "name": meta["name"],
            "description": meta["description"],
            "species": str(meta["species"]),
            "role_title": str(meta["role_title"]),
            "specialty": str(meta["specialty"]),
        }
        for avatar_id, meta in AVATAR_CATALOG.items()
    ]
