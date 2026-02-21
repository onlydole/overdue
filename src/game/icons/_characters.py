"""Character-themed 16x16 pixel art icons.

GBA-era fidelity: 1px dark outlines, 4-step shading ramps, anti-aliased
diagonal edges via ``blend_colors``, and 8-16 unique colors per icon.
"""

from __future__ import annotations

from src.game.icons._palette import (
    BLUE,
    DARK,
    FLAME,
    GOLD,
    GREEN,
    INK,
    PARCHMENT,
    WHITE,
    blend_colors,
)

# Shorthand aliases for the 4-step ramps ---------------------------------
_Ih, _Ib, _Is, _Id = INK  # highlight, base, shadow, deep
_Ph, _Pb, _Ps, _Pd = PARCHMENT
_Gh, _Gb, _Gs, _Gd = GREEN
_Fh, _Fb, _Fs, _Fd = FLAME
_Bh, _Bb, _Bs, _Bd = BLUE
_Oh, _Ob, _Os, _Od = GOLD  # "O" for gold/Or

# Anti-alias blends -------------------------------------------------------
_ink_dark = blend_colors(_Id, DARK, 0.5)  # outline softener
_ink_bg = blend_colors(_Is, DARK, 0.6)  # AA at body-to-bg edge
_green_dark = blend_colors(_Gd, DARK, 0.5)  # green outline softener
_green_bg = blend_colors(_Gs, DARK, 0.5)  # green AA edge

# Skin / face tones for person icon (warm parchment-based) ----------------
_skin_hi = blend_colors(_Ph, _Oh, 0.3)  # warm highlight
_skin_base = blend_colors(_Pb, _Ob, 0.25)  # warm mid-tone
_skin_shadow = blend_colors(_Ps, _Os, 0.3)  # warm shadow

# Inner glow for play button (lighter green center) -----------------------
_green_glow = blend_colors(_Gh, WHITE, 0.35)  # bright inner glow
_green_mid = blend_colors(_Gb, _Gh, 0.5)  # between base and highlight
_green_edge = blend_colors(_Gd, _Gs, 0.5)  # soft outer edge


def register_icons(register) -> None:  # noqa: C901 — intentionally long
    """Register all character-themed icons."""

    # ------------------------------------------------------------------
    # person — upper-body bust / user silhouette
    #
    # Round head (5px diameter), short neck, broadening shoulders.
    # INK palette with full 4-step shading: highlight left, shadow right.
    # Two dark eye dots.  Ear bumps on sides.
    # ------------------------------------------------------------------
    register(
        "person",
        [
            # --- outline top of head ---
            (6, 0, _ink_bg),
            (7, 0, _Id),
            (8, 0, _Id),
            (9, 0, _ink_bg),
            # --- head row 1 (top curve, hair) ---
            (5, 1, _Id),
            (6, 1, _Is),
            (7, 1, _Is),
            (8, 1, _Is),
            (9, 1, _Is),
            (10, 1, _Id),
            # --- head row 2 (forehead, skin shows) ---
            (5, 2, _Id),
            (6, 2, _skin_hi),
            (7, 2, _skin_hi),
            (8, 2, _skin_base),
            (9, 2, _skin_base),
            (10, 2, _skin_shadow),
            (11, 2, _Id),
            # --- head row 3 (eyes) ---
            (4, 3, _ink_bg),
            (5, 3, _Id),
            (6, 3, _skin_hi),
            (7, 3, DARK),  # left eye
            (8, 3, _skin_base),
            (9, 3, DARK),  # right eye
            (10, 3, _skin_shadow),
            (11, 3, _Id),
            # --- head row 4 (lower face / ears) ---
            (4, 4, _Id),
            (5, 4, _skin_shadow),  # left ear
            (6, 4, _skin_hi),
            (7, 4, _skin_base),
            (8, 4, _skin_base),
            (9, 4, _skin_shadow),
            (10, 4, _skin_shadow),  # right ear
            (11, 4, _Id),
            # --- head row 5 (chin) ---
            (5, 5, _ink_bg),
            (6, 5, _Id),
            (7, 5, _skin_base),
            (8, 5, _skin_base),
            (9, 5, _skin_shadow),
            (10, 5, _Id),
            (11, 5, _ink_bg),
            # --- neck ---
            (7, 6, _Id),
            (8, 6, _skin_shadow),
            (9, 6, _Id),
            # --- shoulders row 1 (blue shirt/tunic) ---
            (3, 7, _ink_bg),
            (4, 7, _Id),
            (5, 7, _Bh),
            (6, 7, _Bh),
            (7, 7, _Bb),
            (8, 7, _Bb),
            (9, 7, _Bs),
            (10, 7, _Bs),
            (11, 7, _Id),
            (12, 7, _ink_bg),
            # --- shoulders row 2 ---
            (2, 8, _Id),
            (3, 8, _Bh),
            (4, 8, _Bh),
            (5, 8, _Bh),
            (6, 8, _Bb),
            (7, 8, _Bb),
            (8, 8, _Bb),
            (9, 8, _Bs),
            (10, 8, _Bs),
            (11, 8, _Bs),
            (12, 8, _Id),
            (13, 8, _ink_bg),
            # --- torso row 1 ---
            (1, 9, _Id),
            (2, 9, _Bh),
            (3, 9, _Bh),
            (4, 9, _Bh),
            (5, 9, _Bb),
            (6, 9, _Bb),
            (7, 9, _Bb),
            (8, 9, _Bb),
            (9, 9, _Bs),
            (10, 9, _Bs),
            (11, 9, _Bs),
            (12, 9, _Bs),
            (13, 9, _Id),
            # --- torso row 2 ---
            (1, 10, _Id),
            (2, 10, _Bh),
            (3, 10, _Bh),
            (4, 10, _Bb),
            (5, 10, _Bb),
            (6, 10, _Bb),
            (7, 10, _Bb),
            (8, 10, _Bs),
            (9, 10, _Bs),
            (10, 10, _Bs),
            (11, 10, _Bs),
            (12, 10, _Bd),
            (13, 10, _Id),
            # --- torso row 3 ---
            (1, 11, _ink_bg),
            (2, 11, _Id),
            (3, 11, _Bh),
            (4, 11, _Bb),
            (5, 11, _Bb),
            (6, 11, _Bb),
            (7, 11, _Bb),
            (8, 11, _Bs),
            (9, 11, _Bs),
            (10, 11, _Bs),
            (11, 11, _Bd),
            (12, 11, _Id),
            (13, 11, _ink_bg),
            # --- torso bottom / cut-off ---
            (2, 12, _ink_bg),
            (3, 12, _Id),
            (4, 12, _Bb),
            (5, 12, _Bb),
            (6, 12, _Bb),
            (7, 12, _Bs),
            (8, 12, _Bs),
            (9, 12, _Bs),
            (10, 12, _Bs),
            (11, 12, _Id),
            (12, 12, _ink_bg),
            # --- bottom outline ---
            (3, 13, _ink_bg),
            (4, 13, _Id),
            (5, 13, _Id),
            (6, 13, _Id),
            (7, 13, _Id),
            (8, 13, _Id),
            (9, 13, _Id),
            (10, 13, _Id),
            (11, 13, _ink_bg),
        ],
    )

    # ------------------------------------------------------------------
    # robot — robot face / head with antenna, glowing eyes, teeth grid
    #
    # Boxy head, antenna on top (circle on a stick), two square green
    # eyes, rectangular mouth with parchment teeth, metallic ink body.
    # Bolt/rivet details on sides.
    # ------------------------------------------------------------------
    register(
        "robot",
        [
            # --- antenna ball ---
            (7, 0, _Gs),
            (8, 0, _Gs),
            (7, 1, _Gb),
            (8, 1, _Gh),
            # --- antenna stick ---
            (7, 2, _Is),
            (8, 2, _Ib),
            # --- head top outline ---
            (3, 3, _Id),
            (4, 3, _Id),
            (5, 3, _Id),
            (6, 3, _Id),
            (7, 3, _Id),
            (8, 3, _Id),
            (9, 3, _Id),
            (10, 3, _Id),
            (11, 3, _Id),
            (12, 3, _Id),
            # --- head row 1 ---
            (3, 4, _Id),
            (4, 4, _Ih),
            (5, 4, _Ih),
            (6, 4, _Ih),
            (7, 4, _Ib),
            (8, 4, _Ib),
            (9, 4, _Ib),
            (10, 4, _Is),
            (11, 4, _Is),
            (12, 4, _Id),
            # --- head row 2 (eyes top) ---
            (3, 5, _Id),
            (4, 5, _Ih),
            (5, 5, _Gd),
            (6, 5, _Gd),
            (7, 5, _Ib),
            (8, 5, _Ib),
            (9, 5, _Gd),
            (10, 5, _Gd),
            (11, 5, _Is),
            (12, 5, _Id),
            # --- head row 3 (eyes center — green glow) ---
            (2, 6, _Id),  # left bolt
            (3, 6, _Id),
            (4, 6, _Ih),
            (5, 6, _Gb),
            (6, 6, _Gh),
            (7, 6, _Ib),
            (8, 6, _Ib),
            (9, 6, _Gb),
            (10, 6, _Gh),
            (11, 6, _Is),
            (12, 6, _Id),
            (13, 6, _Id),  # right bolt
            # --- head row 4 (eyes bottom) ---
            (2, 7, _Is),  # left bolt
            (3, 7, _Id),
            (4, 7, _Ih),
            (5, 7, _Gd),
            (6, 7, _Gd),
            (7, 7, _Ib),
            (8, 7, _Ib),
            (9, 7, _Gd),
            (10, 7, _Gd),
            (11, 7, _Is),
            (12, 7, _Id),
            (13, 7, _Is),  # right bolt
            # --- head row 5 (between eyes and mouth) ---
            (3, 8, _Id),
            (4, 8, _Ih),
            (5, 8, _Ib),
            (6, 8, _Ib),
            (7, 8, _Ib),
            (8, 8, _Ib),
            (9, 8, _Ib),
            (10, 8, _Is),
            (11, 8, _Is),
            (12, 8, _Id),
            # --- mouth row 1 (teeth) ---
            (3, 9, _Id),
            (4, 9, _Ib),
            (5, 9, _Id),
            (6, 9, _Ph),
            (7, 9, _Id),
            (8, 9, _Ph),
            (9, 9, _Id),
            (10, 9, _Pb),
            (11, 9, _Id),
            (12, 9, _Id),
            # --- mouth row 2 (teeth lower) ---
            (3, 10, _Id),
            (4, 10, _Ib),
            (5, 10, _Id),
            (6, 10, _Pb),
            (7, 10, _Id),
            (8, 10, _Pb),
            (9, 10, _Id),
            (10, 10, _Ps),
            (11, 10, _Id),
            (12, 10, _Id),
            # --- head bottom outline ---
            (3, 11, _Id),
            (4, 11, _Id),
            (5, 11, _Id),
            (6, 11, _Id),
            (7, 11, _Id),
            (8, 11, _Id),
            (9, 11, _Id),
            (10, 11, _Id),
            (11, 11, _Id),
            (12, 11, _Id),
            # --- neck / jaw bolts ---
            (6, 12, _Id),
            (7, 12, _Is),
            (8, 12, _Is),
            (9, 12, _Id),
            # --- shoulder hint ---
            (4, 13, _ink_bg),
            (5, 13, _Id),
            (6, 13, _Is),
            (7, 13, _Ib),
            (8, 13, _Ib),
            (9, 13, _Is),
            (10, 13, _Id),
            (11, 13, _ink_bg),
        ],
    )

    # ------------------------------------------------------------------
    # gamepad — SNES/GBA-style controller seen from above
    #
    # Rounded rectangular body in ink, d-pad on left (cross with
    # highlight), two action buttons on right (green + flame), small
    # start/select in center, grip bumps on bottom.
    # ------------------------------------------------------------------
    register(
        "gamepad",
        [
            # --- top edge outline ---
            (3, 2, _Id),
            (4, 2, _Id),
            (5, 2, _Id),
            (6, 2, _Id),
            (7, 2, _Id),
            (8, 2, _Id),
            (9, 2, _Id),
            (10, 2, _Id),
            (11, 2, _Id),
            (12, 2, _Id),
            # --- AA corners top ---
            (2, 2, _ink_bg),
            (13, 2, _ink_bg),
            # --- row 1 ---
            (2, 3, _Id),
            (3, 3, _Ih),
            (4, 3, _Ih),
            (5, 3, _Ib),
            (6, 3, _Ib),
            (7, 3, _Ib),
            (8, 3, _Ib),
            (9, 3, _Ib),
            (10, 3, _Is),
            (11, 3, _Is),
            (12, 3, _Is),
            (13, 3, _Id),
            # --- row 2 (d-pad top + center buttons) ---
            (1, 4, _ink_bg),
            (2, 4, _Id),
            (3, 4, _Ih),
            (4, 4, _Ib),
            (5, 4, _Ih),  # d-pad up
            (6, 4, _Ib),
            (7, 4, _Ib),
            (8, 4, _Ib),
            (9, 4, _Ib),
            (10, 4, _Ib),
            (11, 4, _Is),
            (12, 4, _Is),
            (13, 4, _Id),
            (14, 4, _ink_bg),
            # --- row 3 (d-pad cross center + action buttons) ---
            (1, 5, _Id),
            (2, 5, _Ih),
            (3, 5, _Ih),
            (4, 5, _Ph),  # d-pad left
            (5, 5, _Pb),  # d-pad center
            (6, 5, _Ps),  # d-pad right
            (7, 5, _Ib),
            (8, 5, _Id),  # select
            (9, 5, _Id),  # start
            (10, 5, _Ib),
            (11, 5, _Gb),  # green button
            (12, 5, _Is),
            (13, 5, _Id),
            (14, 5, _ink_bg),
            # --- row 4 (d-pad bottom + action buttons row 2) ---
            (1, 6, _Id),
            (2, 6, _Ih),
            (3, 6, _Ib),
            (4, 6, _Ib),
            (5, 6, _Ps),  # d-pad down
            (6, 6, _Ib),
            (7, 6, _Ib),
            (8, 6, _Ib),
            (9, 6, _Ib),
            (10, 6, _Fb),  # flame button
            (11, 6, _Is),
            (12, 6, _Gb),  # green button lower
            (13, 6, _Id),
            (14, 6, _ink_bg),
            # --- row 5 (body) ---
            (1, 7, _Id),
            (2, 7, _Ib),
            (3, 7, _Ib),
            (4, 7, _Ib),
            (5, 7, _Ib),
            (6, 7, _Ib),
            (7, 7, _Is),
            (8, 7, _Is),
            (9, 7, _Is),
            (10, 7, _Is),
            (11, 7, _Is),
            (12, 7, _Is),
            (13, 7, _Id),
            (14, 7, _ink_bg),
            # --- row 6 (lower body) ---
            (1, 8, _Id),
            (2, 8, _Ib),
            (3, 8, _Ib),
            (4, 8, _Is),
            (5, 8, _Is),
            (6, 8, _Is),
            (7, 8, _Is),
            (8, 8, _Is),
            (9, 8, _Is),
            (10, 8, _Is),
            (11, 8, _Is),
            (12, 8, _Id),
            (13, 8, _Id),
            # --- row 7 (grip bumps) ---
            (1, 9, _ink_bg),
            (2, 9, _Id),
            (3, 9, _Is),
            (4, 9, _Is),
            (5, 9, _Id),
            (6, 9, _Id),
            (7, 9, _Id),
            (8, 9, _Id),
            (9, 9, _Id),
            (10, 9, _Id),
            (11, 9, _Id),
            (12, 9, _Id),
            (13, 9, _ink_bg),
            # --- bottom grip outline ---
            (2, 10, _ink_bg),
            (3, 10, _Id),
            (4, 10, _Id),
            (10, 10, _Id),
            (11, 10, _Id),
            (12, 10, _ink_bg),
        ],
    )

    # ------------------------------------------------------------------
    # play — right-pointing play triangle (bold, ~12x12)
    #
    # Green fill with 4-step shading.  Highlight on the top-left leading
    # edge, shadow on the trailing right point and bottom edge.  1px
    # deep-green outline around the entire shape.  Inner specular highlight
    # near the top-left and a subtle white glint for GBA-era polish.
    # ------------------------------------------------------------------
    register(
        "play",
        [
            # --- left column outline (vertical back edge) ---
            (3, 1, _green_bg),
            (3, 2, _Gd),
            (3, 3, _Gd),
            (3, 4, _Gd),
            (3, 5, _Gd),
            (3, 6, _Gd),
            (3, 7, _Gd),
            (3, 8, _Gd),
            (3, 9, _Gd),
            (3, 10, _Gd),
            (3, 11, _Gd),
            (3, 12, _Gd),
            (3, 13, _Gd),
            (3, 14, _green_bg),
            # --- row 0 (top tip + AA) ---
            (4, 1, _green_bg),
            (4, 2, _Gd),
            (5, 2, _green_bg),
            # --- row 1 ---
            (4, 3, _Gh),
            (5, 3, _Gd),
            (6, 3, _green_bg),
            # --- row 2 (specular glint) ---
            (4, 4, _Gh),
            (5, 4, WHITE),  # specular glint
            (6, 4, _Gh),
            (7, 4, _Gd),
            (8, 4, _green_bg),
            # --- row 3 (inner glow) ---
            (4, 5, _Gh),
            (5, 5, _green_glow),  # bright inner
            (6, 5, _Gb),
            (7, 5, _Gb),
            (8, 5, _Gd),
            (9, 5, _green_bg),
            # --- row 4 ---
            (4, 6, _Gh),
            (5, 6, _green_mid),  # mid-tone transition
            (6, 6, _Gb),
            (7, 6, _Gb),
            (8, 6, _Gs),
            (9, 6, _Gd),
            (10, 6, _green_bg),
            # --- row 5 (approaching widest) ---
            (4, 7, _Gh),
            (5, 7, _Gb),
            (6, 7, _green_glow),  # bright inner
            (7, 7, _Gb),
            (8, 7, _Gb),
            (9, 7, _green_edge),  # soft outer edge
            (10, 7, _Gd),
            (11, 7, _green_bg),
            # --- row 6 (maximum width — the point) ---
            (4, 8, _Gb),
            (5, 8, _green_mid),  # mid-tone
            (6, 8, _Gb),
            (7, 8, _Gb),
            (8, 8, _Gb),
            (9, 8, _Gs),
            (10, 8, _green_edge),  # soft outer
            (11, 8, _Gd),
            (12, 8, _green_bg),
            # --- row 7 (mirror of row 5) ---
            (4, 9, _Gb),
            (5, 9, _Gb),
            (6, 9, _Gb),
            (7, 9, _Gs),
            (8, 9, _green_edge),  # soft outer
            (9, 9, _Gs),
            (10, 9, _Gd),
            (11, 9, _green_bg),
            # --- row 8 ---
            (4, 10, _green_mid),  # mid-tone
            (5, 10, _Gs),
            (6, 10, _Gs),
            (7, 10, _Gs),
            (8, 10, _Gs),
            (9, 10, _Gd),
            (10, 10, _green_bg),
            # --- row 9 ---
            (4, 11, _Gs),
            (5, 11, _green_edge),  # soft outer
            (6, 11, _Gs),
            (7, 11, _Gd),
            (8, 11, _Gd),
            (9, 11, _green_bg),
            # --- row 10 ---
            (4, 12, _Gs),
            (5, 12, _Gd),
            (6, 12, _Gd),
            (7, 12, _green_bg),
            # --- row 11 (bottom tip + AA) ---
            (4, 13, _Gd),
            (5, 13, _green_bg),
        ],
    )

    # ------------------------------------------------------------------
    # checkmark — bold 3px wide check/tick mark
    #
    # Short stroke going down-right, then longer stroke going up-right.
    # Green with highlight on top edges, shadow on bottom, deep outline.
    # Fills roughly a 12x12 area centered in the 16x16 grid.  A white
    # specular glint sits near the top of the long stroke.
    # ------------------------------------------------------------------
    register(
        "checkmark",
        [
            # === long stroke (upper-right to vertex, going down-left) ===
            # tip at top-right
            (12, 1, _green_bg),
            (13, 1, _Gd),
            (14, 1, _green_bg),
            # row 2
            (12, 2, _Gd),
            (13, 2, _Gh),
            (14, 2, _Gd),
            # row 3 — specular highlight
            (11, 3, _Gd),
            (12, 3, _Gh),
            (13, 3, WHITE),  # specular glint
            (14, 3, _Gd),
            # row 4 (inner glow + edge)
            (10, 4, _Gd),
            (11, 4, _Gh),
            (12, 4, _green_glow),  # inner glow
            (13, 4, _green_edge),  # soft outer edge
            (14, 4, _Gd),
            # row 5
            (9, 5, _Gd),
            (10, 5, _Gh),
            (11, 5, _green_mid),  # mid-tone
            (12, 5, _Gb),
            (13, 5, _Gd),
            (14, 5, _green_bg),
            # row 6
            (8, 6, _Gd),
            (9, 6, _Gh),
            (10, 6, _Gb),
            (11, 6, _green_edge),  # soft outer
            (12, 6, _Gd),
            (13, 6, _green_bg),
            # row 7
            (7, 7, _Gd),
            (8, 7, _green_mid),  # mid-tone
            (9, 7, _Gb),
            (10, 7, _green_edge),  # soft outer
            (11, 7, _Gd),
            (12, 7, _green_bg),
            # row 8
            (6, 8, _Gd),
            (7, 8, _Gb),
            (8, 8, _green_mid),  # mid-tone
            (9, 8, _Gs),
            (10, 8, _Gd),
            (11, 8, _green_bg),
            # row 9
            (5, 9, _Gd),
            (6, 9, _Gb),
            (7, 9, _green_mid),  # mid-tone
            (8, 9, _Gs),
            (9, 9, _Gd),
            (10, 9, _green_bg),
            # === vertex (bottom of the V) ===
            (4, 10, _Gd),
            (5, 10, _Gb),
            (6, 10, _Gb),
            (7, 10, _Gs),
            (8, 10, _Gd),
            (9, 10, _green_bg),
            # vertex lower
            (4, 11, _Gd),
            (5, 11, _Gb),
            (6, 11, _Gs),
            (7, 11, _Gd),
            (8, 11, _green_bg),
            # vertex bottom shadow
            (4, 12, _green_bg),
            (5, 12, _Gd),
            (6, 12, _Gd),
            (7, 12, _green_bg),
            # === short stroke (going up-left from vertex) ===
            # row 10 (shares with vertex)
            (3, 10, _Gd),
            (3, 9, _Gd),
            (4, 9, _Gb),
            (5, 9, _Gd),
            # row 8
            (2, 8, _Gd),
            (3, 8, _Gh),
            (4, 8, _Gb),
            (5, 8, _Gd),
            # row 7
            (2, 7, _Gd),
            (3, 7, WHITE),  # specular glint on short stroke
            (4, 7, _Gb),
            (5, 7, _Gd),
            (6, 7, _green_bg),
            # row 6
            (1, 6, _green_bg),
            (2, 6, _Gd),
            (3, 6, _Gh),
            (4, 6, _Gd),
            (5, 6, _green_bg),
            # tip at top-left
            (1, 5, _green_bg),
            (2, 5, _Gd),
            (3, 5, _Gd),
            (4, 5, _green_bg),
        ],
    )
