"""Nature-themed 16x16 pixel art icons.

GBA-era fidelity (Golden Sun style) with 4-step shading ramps, 1px dark
outlines, anti-aliased diagonal edges, and rich color gradients.
"""

from __future__ import annotations

from src.game.icons._palette import (
    DARK,
    FLAME,
    GOLD,
    PARCHMENT,
    WHITE,
    blend_colors,
)

# Convenience aliases for ramp steps -----------------------------------------
_gold_hi = GOLD[0]  # #ffe9a0 - highlight
_gold_base = GOLD[1]  # #f0c543 - base
_gold_sh = GOLD[2]  # #c49b22 - shadow
_gold_deep = GOLD[3]  # #8a6b10 - deep shadow / outline

_flame_hi = FLAME[0]  # #ff9e6e - highlight
_flame_base = FLAME[1]  # #e8563e - base
_flame_sh = FLAME[2]  # #b33a25 - shadow
_flame_deep = FLAME[3]  # #7a2214 - deep shadow / outline

_parch_hi = PARCHMENT[0]  # #fffaf0
_parch_base = PARCHMENT[1]
_parch_sh = PARCHMENT[2]

# Anti-alias blends -----------------------------------------------------------
_aa_gold_bg = blend_colors(_gold_deep, DARK, 0.5)
_aa_flame_bg = blend_colors(_flame_deep, DARK, 0.5)
_aa_gold_flame = blend_colors(_gold_base, _flame_base, 0.5)
_aa_gold_hi_base = blend_colors(_gold_hi, _gold_base, 0.5)
_aa_flame_hi_base = blend_colors(_flame_hi, _flame_base, 0.5)


def register_icons(register) -> None:  # noqa: ANN001
    """Register all nature-themed icons."""

    # ------------------------------------------------------------------
    # FIRE -- asymmetrical layered flame with hot core and ember edges
    # ------------------------------------------------------------------
    _fire_white_core = blend_colors(WHITE, _gold_hi, 0.2)
    _fire_core = blend_colors(_gold_hi, _gold_base, 0.35)
    _fire_gold_orange = blend_colors(_gold_sh, _flame_hi, 0.6)
    _fire_orange_red = blend_colors(_flame_base, _flame_sh, 0.45)

    register(
        "fire",
        [
            # --- upper tip and white-hot center ---
            (8, 0, _aa_gold_bg),
            (7, 1, _aa_gold_bg),
            (8, 1, _gold_hi),
            (9, 1, _aa_gold_bg),
            (7, 2, _gold_deep),
            (8, 2, _fire_white_core),
            (9, 2, _gold_deep),
            (6, 3, _aa_gold_bg),
            (7, 3, _gold_deep),
            (8, 3, WHITE),
            (9, 3, _fire_white_core),
            (10, 3, _aa_gold_bg),
            # --- inner tongues ---
            (6, 4, _gold_deep),
            (7, 4, _gold_hi),
            (8, 4, _fire_white_core),
            (9, 4, _gold_hi),
            (10, 4, _gold_deep),
            (5, 5, _aa_gold_bg),
            (6, 5, _gold_deep),
            (7, 5, _gold_hi),
            (8, 5, _fire_core),
            (9, 5, _gold_hi),
            (10, 5, _gold_sh),
            (11, 5, _aa_flame_bg),
            # --- gold to orange transition ---
            (4, 6, _aa_flame_bg),
            (5, 6, _flame_deep),
            (6, 6, _gold_sh),
            (7, 6, _gold_base),
            (8, 6, _gold_hi),
            (9, 6, _gold_base),
            (10, 6, _fire_gold_orange),
            (11, 6, _flame_sh),
            (12, 6, _aa_flame_bg),
            (4, 7, _flame_deep),
            (5, 7, _flame_sh),
            (6, 7, _fire_gold_orange),
            (7, 7, _gold_base),
            (8, 7, _fire_core),
            (9, 7, _fire_gold_orange),
            (10, 7, _flame_base),
            (11, 7, _flame_sh),
            (12, 7, _flame_deep),
            # --- broad lower body ---
            (3, 8, _aa_flame_bg),
            (4, 8, _flame_deep),
            (5, 8, _flame_base),
            (6, 8, _flame_hi),
            (7, 8, _fire_gold_orange),
            (8, 8, _gold_base),
            (9, 8, _fire_gold_orange),
            (10, 8, _flame_hi),
            (11, 8, _flame_base),
            (12, 8, _flame_sh),
            (13, 8, _aa_flame_bg),
            (3, 9, _flame_deep),
            (4, 9, _flame_sh),
            (5, 9, _flame_base),
            (6, 9, _flame_hi),
            (7, 9, _aa_flame_hi_base),
            (8, 9, _fire_gold_orange),
            (9, 9, _flame_hi),
            (10, 9, _flame_base),
            (11, 9, _flame_sh),
            (12, 9, _flame_deep),
            (13, 9, _aa_flame_bg),
            (2, 10, _aa_flame_bg),
            (3, 10, _flame_deep),
            (4, 10, _flame_sh),
            (5, 10, _flame_base),
            (6, 10, _flame_hi),
            (7, 10, _flame_base),
            (8, 10, _fire_gold_orange),
            (9, 10, _flame_base),
            (10, 10, _flame_sh),
            (11, 10, _fire_orange_red),
            (12, 10, _flame_deep),
            (13, 10, _aa_flame_bg),
            # --- ember-heavy base ---
            (2, 11, _aa_flame_bg),
            (3, 11, _flame_deep),
            (4, 11, _flame_deep),
            (5, 11, _flame_sh),
            (6, 11, _flame_base),
            (7, 11, _aa_flame_hi_base),
            (8, 11, _flame_base),
            (9, 11, _flame_sh),
            (10, 11, _flame_deep),
            (11, 11, _flame_deep),
            (12, 11, _aa_flame_bg),
            (3, 12, _aa_flame_bg),
            (4, 12, _flame_deep),
            (5, 12, _flame_sh),
            (6, 12, _flame_sh),
            (7, 12, _flame_base),
            (8, 12, _flame_sh),
            (9, 12, _flame_deep),
            (10, 12, _flame_deep),
            (11, 12, _aa_flame_bg),
            (4, 13, _aa_flame_bg),
            (5, 13, _flame_deep),
            (6, 13, _flame_deep),
            (7, 13, _flame_sh),
            (8, 13, _flame_deep),
            (9, 13, _aa_flame_bg),
            (10, 13, _aa_flame_bg),
            (6, 14, _aa_flame_bg),
            (7, 14, _flame_deep),
            (8, 14, _aa_flame_bg),
            # --- ambient sparks / heat shimmer ---
            (3, 6, _aa_flame_bg),
            (11, 4, _aa_gold_bg),
            (13, 7, _aa_flame_bg),
            (1, 10, _aa_flame_bg),
            (12, 5, _aa_flame_bg),
        ],
    )

    # ------------------------------------------------------------------
    # MOON -- crescent moon with surface craters and sparkle dots
    # ------------------------------------------------------------------
    _moon_lit = blend_colors(_gold_hi, WHITE, 0.3)
    _moon_term = blend_colors(_gold_base, _gold_sh, 0.4)
    _aa_moon_bg = blend_colors(_gold_sh, DARK, 0.6)
    _crater = blend_colors(_gold_sh, _gold_deep, 0.5)
    _crater_rim = blend_colors(_gold_base, _gold_sh, 0.7)
    _moon_edge_aa = blend_colors(_gold_deep, DARK, 0.4)
    _sparkle_bright = blend_colors(WHITE, _gold_hi, 0.5)
    _moon_inner = blend_colors(_gold_hi, _gold_base, 0.3)

    register(
        "moon",
        [
            # --- outline top arc ---
            (8, 0, _aa_moon_bg),
            (9, 0, _moon_edge_aa),
            (10, 0, _gold_deep),
            (11, 0, _moon_edge_aa),
            (12, 0, _aa_moon_bg),
            # --- upper crescent row 1 ---
            (7, 1, _aa_moon_bg),
            (8, 1, _gold_deep),
            (9, 1, _moon_lit),
            (10, 1, _gold_hi),
            (11, 1, _gold_base),
            (12, 1, _gold_deep),
            (13, 1, _aa_moon_bg),
            # --- row 2 ---
            (6, 2, _aa_moon_bg),
            (7, 2, _gold_deep),
            (8, 2, _moon_lit),
            (9, 2, _gold_hi),
            (10, 2, _moon_inner),
            (11, 2, _moon_term),
            (12, 2, _gold_deep),
            (13, 2, _moon_edge_aa),
            # --- row 3 (wider) ---
            (5, 3, _aa_moon_bg),
            (6, 3, _gold_deep),
            (7, 3, _moon_lit),
            (8, 3, _gold_hi),
            (9, 3, _gold_base),
            (10, 3, _moon_inner),
            (11, 3, _gold_deep),
            # --- row 4 (crater 1) ---
            (4, 4, _moon_edge_aa),
            (5, 4, _gold_deep),
            (6, 4, _gold_hi),
            (7, 4, _gold_hi),
            (8, 4, _gold_base),
            (9, 4, _crater),
            (10, 4, _crater_rim),
            (11, 4, _gold_deep),
            # --- row 5 ---
            (4, 5, _aa_moon_bg),
            (5, 5, _gold_deep),
            (6, 5, _moon_lit),
            (7, 5, _gold_hi),
            (8, 5, _gold_base),
            (9, 5, _moon_term),
            (10, 5, _gold_deep),
            # --- row 6 (widest) ---
            (3, 6, _moon_edge_aa),
            (4, 6, _gold_deep),
            (5, 6, _moon_lit),
            (6, 6, _gold_hi),
            (7, 6, _moon_inner),
            (8, 6, _crater),
            (9, 6, _crater_rim),
            (10, 6, _gold_deep),
            # --- row 7 ---
            (3, 7, _aa_moon_bg),
            (4, 7, _gold_deep),
            (5, 7, _gold_hi),
            (6, 7, _gold_base),
            (7, 7, _gold_base),
            (8, 7, _moon_term),
            (9, 7, _gold_deep),
            (10, 7, _moon_edge_aa),
            # --- row 8 ---
            (4, 8, _aa_moon_bg),
            (5, 8, _gold_deep),
            (6, 8, _gold_hi),
            (7, 8, _moon_inner),
            (8, 8, _gold_sh),
            (9, 8, _gold_deep),
            # --- row 9 (crater 2) ---
            (4, 9, _moon_edge_aa),
            (5, 9, _gold_deep),
            (6, 9, _gold_base),
            (7, 9, _crater),
            (8, 9, _crater_rim),
            (9, 9, _gold_deep),
            (10, 9, _aa_moon_bg),
            # --- row 10 (narrowing) ---
            (5, 10, _aa_moon_bg),
            (6, 10, _gold_deep),
            (7, 10, _gold_base),
            (8, 10, _moon_term),
            (9, 10, _gold_deep),
            (10, 10, _moon_edge_aa),
            # --- row 11 ---
            (6, 11, _aa_moon_bg),
            (7, 11, _gold_deep),
            (8, 11, _gold_sh),
            (9, 11, _gold_deep),
            (10, 11, _aa_moon_bg),
            # --- bottom arc ---
            (6, 12, _moon_edge_aa),
            (7, 12, _aa_moon_bg),
            (8, 12, _gold_deep),
            (9, 12, _gold_deep),
            (10, 12, _aa_moon_bg),
            (8, 13, _moon_edge_aa),
            (9, 13, _aa_moon_bg),
            # --- sparkle dots near the moon ---
            (2, 2, _sparkle_bright),
            (1, 3, WHITE),
            (0, 4, _gold_hi),
            (3, 1, _gold_base),
            (13, 10, _sparkle_bright),
            (14, 11, WHITE),
            (15, 12, _gold_hi),
            (12, 14, _gold_base),
            (14, 9, _gold_sh),
            # --- extra faint stars ---
            (1, 8, _gold_sh),
            (0, 12, _gold_deep),
            (14, 5, _gold_deep),
            (2, 14, _aa_moon_bg),
        ],
    )

    # ------------------------------------------------------------------
    # STAR -- 5-pointed star with faceted GBA-style shading
    # ------------------------------------------------------------------
    _aa_star_bg = blend_colors(_gold_deep, DARK, 0.5)
    _star_gleam = blend_colors(WHITE, _gold_hi, 0.5)
    _star_mid_hi = blend_colors(_gold_hi, _gold_base, 0.3)

    register(
        "star",
        [
            # --- top point ---
            (7, 0, _aa_star_bg),
            (8, 0, _aa_star_bg),
            (7, 1, _gold_deep),
            (8, 1, _gold_deep),
            (6, 2, _aa_star_bg),
            (7, 2, _gold_hi),
            (8, 2, _gold_base),
            (9, 2, _aa_star_bg),
            (6, 3, _gold_deep),
            (7, 3, _gold_hi),
            (8, 3, _star_mid_hi),
            (9, 3, _gold_deep),
            # --- upper body widens ---
            (5, 4, _gold_deep),
            (6, 4, _gold_hi),
            (7, 4, _star_gleam),
            (8, 4, _gold_base),
            (9, 4, _gold_sh),
            (10, 4, _gold_deep),
            # --- left arm + center + right arm (row 5) ---
            (0, 5, _aa_star_bg),
            (1, 5, _gold_deep),
            (2, 5, _gold_hi),
            (3, 5, _gold_hi),
            (4, 5, _star_mid_hi),
            (5, 5, _gold_hi),
            (6, 5, _star_gleam),
            (7, 5, _gold_hi),
            (8, 5, _gold_base),
            (9, 5, _gold_base),
            (10, 5, _gold_sh),
            (11, 5, _gold_sh),
            (12, 5, _gold_sh),
            (13, 5, _gold_deep),
            (14, 5, _gold_deep),
            (15, 5, _aa_star_bg),
            # --- arms row 6 ---
            (0, 6, _aa_star_bg),
            (1, 6, _aa_star_bg),
            (2, 6, _gold_deep),
            (3, 6, _gold_hi),
            (4, 6, _star_mid_hi),
            (5, 6, _gold_hi),
            (6, 6, _star_gleam),
            (7, 6, WHITE),
            (8, 6, _gold_hi),
            (9, 6, _gold_base),
            (10, 6, _gold_sh),
            (11, 6, _gold_sh),
            (12, 6, _gold_deep),
            (13, 6, _gold_deep),
            (14, 6, _aa_star_bg),
            # --- narrowing below center (row 7) ---
            (3, 7, _aa_star_bg),
            (4, 7, _gold_deep),
            (5, 7, _gold_hi),
            (6, 7, _star_mid_hi),
            (7, 7, _star_gleam),
            (8, 7, _gold_base),
            (9, 7, _gold_sh),
            (10, 7, _gold_sh),
            (11, 7, _gold_deep),
            (12, 7, _aa_star_bg),
            # --- lower body (row 8) ---
            (4, 8, _gold_deep),
            (5, 8, _gold_hi),
            (6, 8, _star_mid_hi),
            (7, 8, _gold_base),
            (8, 8, _gold_sh),
            (9, 8, _gold_sh),
            (10, 8, _gold_deep),
            (11, 8, _gold_deep),
            # --- V splits (row 9) ---
            (3, 9, _aa_star_bg),
            (4, 9, _gold_deep),
            (5, 9, _gold_base),
            (6, 9, _star_mid_hi),
            (7, 9, _gold_sh),
            (8, 9, _gold_sh),
            (9, 9, _gold_deep),
            (10, 9, _gold_deep),
            (11, 9, _aa_star_bg),
            # --- lower left and right legs (row 10) ---
            (2, 10, _aa_star_bg),
            (3, 10, _gold_deep),
            (4, 10, _gold_base),
            (5, 10, _gold_sh),
            (6, 10, _gold_deep),
            (9, 10, _gold_deep),
            (10, 10, _gold_sh),
            (11, 10, _gold_deep),
            (12, 10, _aa_star_bg),
            # --- row 11 ---
            (2, 11, _gold_deep),
            (3, 11, _gold_base),
            (4, 11, _gold_sh),
            (5, 11, _gold_deep),
            (10, 11, _gold_deep),
            (11, 11, _gold_sh),
            (12, 11, _gold_deep),
            # --- bottom left point (row 12) ---
            (1, 12, _aa_star_bg),
            (2, 12, _gold_deep),
            (3, 12, _gold_sh),
            (4, 12, _gold_deep),
            (11, 12, _gold_deep),
            (12, 12, _gold_deep),
            (13, 12, _aa_star_bg),
            # --- bottom tips (row 13) ---
            (1, 13, _gold_deep),
            (2, 13, _gold_deep),
            (3, 13, _aa_star_bg),
            (12, 13, _gold_deep),
            (13, 13, _aa_star_bg),
            # --- very tips ---
            (0, 14, _aa_star_bg),
            (1, 14, _gold_deep),
            (13, 14, _aa_star_bg),
        ],
    )

    # ------------------------------------------------------------------
    # SPARKLES -- cluster of 3 sparkle/shine effects
    # ------------------------------------------------------------------
    _sparkle_glow = blend_colors(WHITE, _gold_hi, 0.4)
    _sparkle_mid = blend_colors(_gold_hi, _gold_base, 0.5)
    _sparkle_fade = blend_colors(_gold_base, DARK, 0.4)
    _sparkle_far = blend_colors(_gold_sh, DARK, 0.3)
    _sparkle_tip = blend_colors(_gold_base, _gold_sh, 0.5)
    _sparkle_warm = blend_colors(_gold_hi, _flame_hi, 0.2)
    _sparkle_cool = blend_colors(_gold_hi, _parch_hi, 0.3)

    register(
        "sparkles",
        [
            # =============================================================
            # Main sparkle (center-left, large 4-armed cross with halo)
            # =============================================================
            # vertical arm (up)
            (5, 0, _sparkle_far),
            (5, 1, _gold_sh),
            (5, 2, _sparkle_tip),
            (5, 3, _gold_hi),
            # halo glow around upper arm
            (4, 1, _sparkle_far),
            (6, 1, _sparkle_far),
            (4, 2, _sparkle_far),
            (6, 2, _sparkle_far),
            # center row (horizontal arm)
            (0, 4, _sparkle_far),
            (1, 4, _gold_sh),
            (2, 4, _sparkle_tip),
            (3, 4, _sparkle_mid),
            (4, 4, _sparkle_glow),
            (5, 4, WHITE),
            (6, 4, _sparkle_glow),
            (7, 4, _sparkle_mid),
            (8, 4, _sparkle_tip),
            (9, 4, _gold_sh),
            (10, 4, _sparkle_far),
            # halo glow around horizontal arm
            (1, 3, _sparkle_far),
            (2, 3, _sparkle_far),
            (8, 3, _sparkle_far),
            (9, 3, _sparkle_far),
            (1, 5, _sparkle_far),
            (2, 5, _sparkle_far),
            (8, 5, _sparkle_far),
            (9, 5, _sparkle_far),
            # vertical arm (down)
            (5, 5, _sparkle_glow),
            (5, 6, _sparkle_mid),
            (5, 7, _sparkle_tip),
            (5, 8, _gold_sh),
            (5, 9, _sparkle_far),
            # halo glow around lower arm
            (4, 6, _sparkle_far),
            (6, 6, _sparkle_far),
            (4, 7, _sparkle_far),
            (6, 7, _sparkle_far),
            # diagonal accent pixels (X shape through center)
            (4, 3, _sparkle_fade),
            (6, 3, _sparkle_fade),
            (3, 3, _sparkle_far),
            (7, 3, _sparkle_far),
            (4, 5, _sparkle_fade),
            (6, 5, _sparkle_fade),
            (3, 5, _sparkle_far),
            (7, 5, _sparkle_far),
            # =============================================================
            # Second sparkle (upper-right, medium cross with warm tint)
            # =============================================================
            # vertical arm (up)
            (13, 0, _sparkle_far),
            (13, 1, _sparkle_tip),
            (13, 2, _sparkle_warm),
            # horizontal arm
            (10, 3, _sparkle_far),
            (11, 3, _sparkle_tip),
            (12, 3, _sparkle_glow),
            (13, 3, WHITE),
            (14, 3, _sparkle_glow),
            (15, 3, _sparkle_far),
            # vertical arm (down)
            (13, 4, _sparkle_warm),
            (13, 5, _sparkle_tip),
            (13, 6, _sparkle_far),
            # halo around second sparkle
            (12, 2, _sparkle_far),
            (14, 2, _sparkle_far),
            (12, 4, _sparkle_far),
            (14, 4, _sparkle_far),
            # =============================================================
            # Third sparkle (lower-right, small cool-tinted cross)
            # =============================================================
            # vertical arm (up)
            (11, 8, _sparkle_far),
            (11, 9, _sparkle_tip),
            (11, 10, _sparkle_cool),
            # horizontal arm
            (8, 11, _sparkle_far),
            (9, 11, _sparkle_tip),
            (10, 11, _sparkle_glow),
            (11, 11, WHITE),
            (12, 11, _sparkle_glow),
            (13, 11, _sparkle_tip),
            (14, 11, _sparkle_far),
            # vertical arm (down)
            (11, 12, _sparkle_cool),
            (11, 13, _sparkle_tip),
            (11, 14, _sparkle_far),
            # halo around third sparkle
            (10, 10, _sparkle_far),
            (12, 10, _sparkle_far),
            (10, 12, _sparkle_far),
            (12, 12, _sparkle_far),
            # =============================================================
            # Extended glow halos and ambient light
            # =============================================================
            # Main sparkle extended glow
            (3, 2, _sparkle_far),
            (7, 2, _sparkle_far),
            (3, 6, _sparkle_far),
            (7, 6, _sparkle_far),
            (3, 7, _sparkle_far),
            (7, 7, _sparkle_far),
            # Second sparkle extended glow
            (11, 1, _sparkle_far),
            (15, 1, _sparkle_far),
            (11, 5, _sparkle_far),
            (15, 5, _sparkle_far),
            # Third sparkle extended glow
            (9, 9, _sparkle_far),
            (13, 9, _sparkle_far),
            (9, 13, _sparkle_far),
            (13, 13, _sparkle_far),
            # =============================================================
            # Scattered tiny light particles
            # =============================================================
            (0, 0, _sparkle_far),
            (15, 7, _gold_sh),
            (0, 10, _gold_deep),
            (7, 14, _sparkle_far),
            (2, 8, _gold_deep),
            (15, 14, _gold_deep),
            (8, 0, _sparkle_far),
            (1, 13, _gold_deep),
            (14, 8, _gold_sh),
            (3, 11, _sparkle_far),
            (0, 15, _gold_deep),
            (7, 8, _sparkle_far),
            (15, 15, _sparkle_far),
        ],
    )

    # ------------------------------------------------------------------
    # ZAP -- lightning bolt with electric energy
    # ------------------------------------------------------------------
    _aa_zap_bg = blend_colors(_gold_deep, DARK, 0.5)
    _spark_color = blend_colors(WHITE, _gold_hi, 0.3)
    _zap_core = blend_colors(WHITE, _gold_hi, 0.5)
    _zap_edge = blend_colors(_gold_sh, _gold_deep, 0.4)
    _zap_glow = blend_colors(_gold_hi, _gold_base, 0.3)

    register(
        "zap",
        [
            # --- top of bolt (upper right) ---
            (9, 0, _aa_zap_bg),
            (10, 0, _gold_deep),
            (11, 0, _gold_deep),
            (12, 0, _aa_zap_bg),
            (13, 0, _aa_zap_bg),
            (8, 1, _aa_zap_bg),
            (9, 1, _gold_deep),
            (10, 1, _gold_hi),
            (11, 1, _zap_glow),
            (12, 1, _gold_sh),
            (13, 1, _gold_deep),
            # --- row 2 ---
            (7, 2, _aa_zap_bg),
            (8, 2, _gold_deep),
            (9, 2, _gold_hi),
            (10, 2, _zap_core),
            (11, 2, _gold_base),
            (12, 2, _zap_edge),
            (13, 2, _gold_deep),
            # --- first zig (rows 3-4) ---
            (6, 3, _aa_zap_bg),
            (7, 3, _gold_deep),
            (8, 3, _gold_hi),
            (9, 3, _zap_core),
            (10, 3, _gold_base),
            (11, 3, _zap_edge),
            (12, 3, _gold_deep),
            (5, 4, _aa_zap_bg),
            (6, 4, _gold_deep),
            (7, 4, _gold_hi),
            (8, 4, _zap_glow),
            (9, 4, _gold_sh),
            (10, 4, _zap_edge),
            (11, 4, _gold_deep),
            # --- horizontal zag (rows 5-6) -- bolt widens ---
            (3, 5, _aa_zap_bg),
            (4, 5, _gold_deep),
            (5, 5, _gold_deep),
            (6, 5, _gold_hi),
            (7, 5, _zap_core),
            (8, 5, _gold_base),
            (9, 5, _gold_base),
            (10, 5, _gold_sh),
            (11, 5, _zap_edge),
            (12, 5, _gold_deep),
            (13, 5, _aa_zap_bg),
            (4, 6, _aa_zap_bg),
            (5, 6, _gold_deep),
            (6, 6, _zap_edge),
            (7, 6, _gold_hi),
            (8, 6, WHITE),
            (9, 6, _zap_glow),
            (10, 6, _gold_sh),
            (11, 6, _zap_edge),
            (12, 6, _gold_deep),
            # --- second zig down (rows 7-8) ---
            (5, 7, _aa_zap_bg),
            (6, 7, _gold_deep),
            (7, 7, _gold_deep),
            (8, 7, _gold_hi),
            (9, 7, _zap_core),
            (10, 7, _gold_base),
            (11, 7, _gold_deep),
            (12, 7, _aa_zap_bg),
            (6, 8, _gold_deep),
            (7, 8, _zap_edge),
            (8, 8, _gold_base),
            (9, 8, _gold_sh),
            (10, 8, _zap_edge),
            (11, 8, _gold_deep),
            # --- lower zig (rows 9-10) ---
            (5, 9, _aa_zap_bg),
            (6, 9, _gold_deep),
            (7, 9, _gold_hi),
            (8, 9, _zap_glow),
            (9, 9, _zap_edge),
            (10, 9, _gold_deep),
            (4, 10, _aa_zap_bg),
            (5, 10, _gold_deep),
            (6, 10, _gold_hi),
            (7, 10, _gold_base),
            (8, 10, _zap_edge),
            (9, 10, _gold_deep),
            # --- final segment down (rows 11-12) ---
            (3, 11, _aa_zap_bg),
            (4, 11, _gold_deep),
            (5, 11, _gold_hi),
            (6, 11, _zap_glow),
            (7, 11, _zap_edge),
            (8, 11, _gold_deep),
            (3, 12, _gold_deep),
            (4, 12, _gold_deep),
            (5, 12, _gold_base),
            (6, 12, _zap_edge),
            (7, 12, _gold_deep),
            # --- bottom tip (rows 13-15) ---
            (3, 13, _aa_zap_bg),
            (4, 13, _gold_deep),
            (5, 13, _gold_sh),
            (6, 13, _gold_deep),
            (3, 14, _gold_deep),
            (4, 14, _zap_edge),
            (5, 14, _gold_deep),
            (4, 15, _aa_zap_bg),
            # --- electric sparks radiating from bend points ---
            (14, 1, _spark_color),
            (15, 0, _gold_hi),
            (14, 4, _spark_color),
            (15, 3, _gold_sh),
            (2, 6, _spark_color),
            (1, 7, _gold_hi),
            (13, 7, _spark_color),
            (14, 8, _gold_sh),
            (2, 11, _spark_color),
            (1, 12, _gold_sh),
            (8, 14, _gold_sh),
            (9, 13, _spark_color),
        ],
    )
