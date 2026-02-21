"""Book-themed 16x16 pixel art icons (GBA-era fidelity).

Six icons for the Overdue library app: books, book-open, book-closed,
scroll, bookmark, clipboard.  Each uses 4-step shading ramps, 1px dark
outlines, and anti-aliased diagonal edges via ``blend_colors``.
"""

from __future__ import annotations

from src.game.icons._palette import (
    DARK,
    FLAME,
    GOLD,
    GREEN,
    INK,
    PARCHMENT,
    blend_colors,
)

# Convenience unpacking -------------------------------------------------
_fh, _fb, _fs, _fd = FLAME  # highlight, base, shadow, deep
_gh, _gb, _gs, _gd = GOLD
_nh, _nb, _ns, _nd = GREEN
_ph, _pb, _ps, _pd = PARCHMENT
_ih, _ib, _is, _id = INK

# Anti-alias blends used at diagonal transitions -----------------------
_flame_bg = blend_colors(_fd, DARK, 0.5)
_gold_bg = blend_colors(_gd, DARK, 0.5)
_green_bg = blend_colors(_nd, DARK, 0.5)
_parch_bg = blend_colors(_pd, DARK, 0.5)
_ink_bg = blend_colors(_id, DARK, 0.5)
_flame_gold = blend_colors(_fs, _gs, 0.5)
_parch_flame = blend_colors(_ps, _fs, 0.5)
_parch_gold = blend_colors(_ps, _gs, 0.5)
_gold_ink = blend_colors(_gs, _is, 0.5)


# ======================================================================
# Icon definitions
# ======================================================================


def _books() -> list[tuple[int, int, str]]:
    """Stack of 3 angled books -- bottom flame-red, middle green, top gold."""
    px: list[tuple[int, int, str]] = []

    # -- Bottom book (flame red, widest, rows 10-14) --------------------
    # Outline top edge
    px += [(x, 9, _fd) for x in range(2, 14)]
    # Anti-alias corners
    px += [(1, 10, _flame_bg), (14, 9, _flame_bg)]
    # Cover top surface (highlight)
    px += [(x, 10, _fh) for x in range(2, 14)]
    # Cover body
    px += [(x, 11, _fb) for x in range(2, 14)]
    px += [(x, 12, _fb) for x in range(2, 14)]
    # Page edges visible on right
    px += [(14, 10, _ph), (14, 11, _pb), (14, 12, _ps)]
    # Shadow bottom row of cover
    px += [(x, 13, _fs) for x in range(2, 14)]
    # Outline bottom
    px += [(x, 14, _fd) for x in range(2, 14)]
    # Spine highlight on left
    px += [(2, 10, _fh), (2, 11, _fh), (2, 12, _fb), (2, 13, _fs)]
    # Spine outline left edge
    px += [(1, y, _fd) for y in range(10, 15)]
    # Right outline
    px += [(14, 13, _fd), (14, 14, _fd)]
    # Pages strip
    px += [(15, 10, _pd), (15, 11, _pd), (15, 12, _pd)]

    # -- Middle book (green, rows 5-9) ----------------------------------
    px += [(x, 5, _nd) for x in range(3, 13)]
    px += [(2, 6, _green_bg)]
    px += [(x, 6, _nh) for x in range(3, 13)]
    px += [(x, 7, _nb) for x in range(3, 13)]
    px += [(x, 8, _ns) for x in range(3, 13)]
    px += [(x, 9, _nd) for x in range(3, 13)]
    # Spine left
    px += [(2, y, _nd) for y in range(6, 10)]
    px += [(3, 6, _nh), (3, 7, _nh), (3, 8, _nb), (3, 9, _ns)]
    # Page edges right
    px += [(13, 6, _ph), (13, 7, _pb), (13, 8, _ps)]
    px += [(13, 9, _nd)]
    # Anti-alias
    px += [(13, 5, _green_bg)]

    # -- Top book (gold, narrowest, rows 1-5) ---------------------------
    px += [(x, 1, _gd) for x in range(4, 12)]
    px += [(3, 2, _gold_bg)]
    px += [(x, 2, _gh) for x in range(4, 12)]
    px += [(x, 3, _gb) for x in range(4, 12)]
    px += [(x, 4, _gs) for x in range(4, 12)]
    px += [(x, 5, _gd) for x in range(4, 12)]
    # Gold leaf detail on cover
    px += [(6, 3, _gh), (7, 3, _gh), (8, 3, _gh), (9, 3, _gh)]
    # Spine left
    px += [(3, y, _gd) for y in range(2, 6)]
    px += [(4, 2, _gh), (4, 3, _gh), (4, 4, _gb), (4, 5, _gs)]
    # Page edge right
    px += [(12, 2, _ph), (12, 3, _pb), (12, 4, _ps)]
    px += [(12, 5, _gd)]
    px += [(12, 1, _gold_bg)]

    return px


def _book_open() -> list[tuple[int, int, str]]:
    """Open book viewed from above, spine vertical in center."""
    px: list[tuple[int, int, str]] = []

    # -- Spine (center column, x=7-8) ----------------------------------
    px += [(7, y, _gd) for y in range(2, 14)]
    px += [(8, y, _gd) for y in range(2, 14)]
    px += [(7, y, _gs) for y in range(3, 13)]
    px += [(8, y, _gs) for y in range(3, 13)]

    # -- Left cover outline ---------------------------------------------
    px += [(x, 1, _gd) for x in range(1, 8)]
    px += [(0, y, _gd) for y in range(2, 14)]
    px += [(x, 14, _gd) for x in range(1, 8)]
    # Left cover fill
    px += [(1, y, _gs) for y in range(2, 14)]
    # Anti-alias top-left and bottom-left
    px += [(0, 1, _gold_bg), (0, 14, _gold_bg)]

    # -- Left page area -------------------------------------------------
    for y in range(2, 14):
        for x in range(2, 7):
            if y == 2:
                px.append((x, y, _ph))
            elif y == 13:
                px.append((x, y, _ps))
            else:
                px.append((x, y, _pb))
    # Text lines on left page
    for y in (4, 6, 8, 10):
        px += [(x, y, _ib) for x in range(3, 6)]
    for y in (5, 7, 9, 11):
        px += [(x, y, _ih) for x in range(3, 5)]

    # -- Right cover outline --------------------------------------------
    px += [(x, 1, _gd) for x in range(8, 15)]
    px += [(15, y, _gd) for y in range(2, 14)]
    px += [(x, 14, _gd) for x in range(8, 15)]
    # Right cover fill
    px += [(14, y, _gs) for y in range(2, 14)]
    # Anti-alias top-right and bottom-right
    px += [(15, 1, _gold_bg), (15, 14, _gold_bg)]

    # -- Right page area ------------------------------------------------
    for y in range(2, 14):
        for x in range(9, 14):
            if y == 2:
                px.append((x, y, _ph))
            elif y == 13:
                px.append((x, y, _ps))
            else:
                px.append((x, y, _pb))
    # Text lines on right page
    for y in (4, 6, 8, 10):
        px += [(x, y, _ib) for x in range(10, 13)]
    for y in (5, 7, 9, 11):
        px += [(x, y, _ih) for x in range(10, 12)]

    # Spine highlight strip
    px += [(7, 2, _gb), (8, 2, _gb)]
    px += [(7, 13, _gb), (8, 13, _gb)]

    return px


def _book_closed() -> list[tuple[int, int, str]]:
    """Single closed book, front-facing with gold leaf detail."""
    px: list[tuple[int, int, str]] = []

    # -- Outline --------------------------------------------------------
    # Top edge
    px += [(x, 1, _fd) for x in range(3, 12)]
    # Bottom edge
    px += [(x, 14, _fd) for x in range(3, 13)]
    # Left edge (spine)
    px += [(2, y, _fd) for y in range(2, 15)]
    # Right edge
    px += [(12, y, _fd) for y in range(2, 15)]
    # Anti-alias corners
    px += [(2, 1, _flame_bg), (12, 1, _flame_bg)]
    px += [(2, 14, _flame_bg), (12, 14, _flame_bg)]

    # -- Spine (left strip, x=3-4) -------------------------------------
    px += [(3, y, _fh) for y in range(2, 14)]
    px += [(4, y, _fb) for y in range(2, 14)]

    # -- Cover body -----------------------------------------------------
    for y in range(2, 14):
        for x in range(5, 12):
            if y == 2:
                px.append((x, y, _fh))
            elif y in (3, 4, 5, 6):
                px.append((x, y, _fb))
            elif y in (7, 8, 9, 10):
                px.append((x, y, _fs))
            else:
                px.append((x, y, _fs))

    # Top highlight on cover surface
    px += [(x, 2, _fh) for x in range(5, 12)]

    # -- Gold leaf rectangle on cover (decorative detail) ---------------
    px += [(7, 5, _gd), (8, 5, _gd), (9, 5, _gd)]
    px += [(7, 6, _gd), (8, 6, _gb), (9, 6, _gd)]
    px += [(7, 7, _gd), (8, 7, _gb), (9, 7, _gd)]
    px += [(7, 8, _gd), (8, 8, _gd), (9, 8, _gd)]
    # Gold leaf center highlight
    px += [(8, 6, _gh), (8, 7, _gh)]

    # -- Page edges visible on right side (parchment strip) -------------
    px += [(13, y, _pd) for y in range(3, 14)]
    px += [(13, 3, _ph), (13, 4, _ph)]
    px += [(13, y, _pb) for y in range(5, 10)]
    px += [(13, y, _ps) for y in range(10, 13)]
    px += [(13, 13, _pd)]

    # -- Bottom shadow edge ---------------------------------------------
    px += [(x, 13, _fd) for x in range(5, 12)]

    return px


def _scroll() -> list[tuple[int, int, str]]:
    """Rolled parchment scroll with visible text lines."""
    px: list[tuple[int, int, str]] = []

    # -- Top roll (cylinder) --------------------------------------------
    # Outline
    px += [(x, 0, _gd) for x in range(3, 13)]
    px += [(2, 1, _gold_bg), (13, 1, _gold_bg)]
    # Roll surface -- 2 rows
    px += [(x, 1, _gh) for x in range(3, 13)]
    px += [(x, 2, _gb) for x in range(3, 13)]
    px += [(x, 3, _gs) for x in range(3, 13)]
    # Roll end caps
    px += [(2, y, _gd) for y in range(1, 4)]
    px += [(13, y, _gd) for y in range(1, 4)]
    # Highlight on top-left of roll
    px += [(4, 1, _gh), (5, 1, _gh)]
    # Shadow under roll
    px += [(x, 3, _gd) for x in range(4, 12)]
    # Dowel ends visible beyond roll
    px += [(1, 1, _gd), (1, 2, _gs), (14, 1, _gd), (14, 2, _gs)]

    # -- Parchment body (unrolled middle section) -----------------------
    # Left and right borders
    px += [(3, y, _pd) for y in range(4, 12)]
    px += [(12, y, _pd) for y in range(4, 12)]
    # Parchment fill
    for y in range(4, 12):
        for x in range(4, 12):
            if y == 4:
                px.append((x, y, _ph))
            elif y == 11:
                px.append((x, y, _ps))
            else:
                px.append((x, y, _pb))
    # Text lines (ink)
    for y in (5, 7, 9):
        px += [(x, y, _ib) for x in range(5, 11)]
    for y in (6, 8):
        px += [(x, y, _ih) for x in range(5, 9)]

    # -- Bottom roll (cylinder) -----------------------------------------
    px += [(x, 12, _gs) for x in range(3, 13)]
    px += [(x, 13, _gb) for x in range(3, 13)]
    px += [(x, 14, _gh) for x in range(3, 13)]
    px += [(x, 15, _gd) for x in range(3, 13)]
    # Roll end caps
    px += [(2, y, _gd) for y in range(12, 16)]
    px += [(13, y, _gd) for y in range(12, 16)]
    # Highlight on bottom roll
    px += [(5, 14, _gh), (6, 14, _gh)]
    # Shadow on top of bottom roll
    px += [(x, 12, _gd) for x in range(4, 12)]
    # Dowel ends
    px += [(1, 13, _gd), (1, 14, _gs), (14, 13, _gd), (14, 14, _gs)]
    # Anti-alias corners
    px += [(2, 12, _gold_bg), (13, 12, _gold_bg)]
    px += [(2, 15, _gold_bg), (13, 15, _gold_bg)]

    return px


def _bookmark() -> list[tuple[int, int, str]]:
    """Ribbon bookmark with V-split at bottom and star detail."""
    px: list[tuple[int, int, str]] = []

    # -- Outline (deep shadow) ------------------------------------------
    # Left edge
    px += [(4, y, _fd) for y in range(0, 12)]
    # Right edge
    px += [(11, y, _fd) for y in range(0, 12)]
    # Top edge
    px += [(x, 0, _fd) for x in range(5, 11)]

    # -- Ribbon body (6 pixels wide: x=5..10) ---------------------------
    # Top highlight row
    px += [(x, 1, _fh) for x in range(5, 11)]
    # Body fill
    for y in range(2, 10):
        px.append((5, y, _fh))  # left highlight edge
        for x in range(6, 10):
            px.append((x, y, _fb))  # base
        px.append((10, y, _fs))  # right shadow edge

    # -- V-split at bottom (rows 10-15) ---------------------------------
    # Row 10: full width, starting to taper
    px += [(5, 10, _fh), (6, 10, _fb), (7, 10, _fb)]
    px += [(8, 10, _fb), (9, 10, _fb), (10, 10, _fs)]
    # Row 11: notch begins
    px += [(5, 11, _fb), (6, 11, _fb)]
    px += [(9, 11, _fb), (10, 11, _fs)]
    px += [(4, 11, _fd)]
    px += [(11, 11, _fd)]
    # Row 12
    px += [(4, 12, _fd), (5, 12, _fb), (6, 12, _fs)]
    px += [(9, 12, _fb), (10, 12, _fs), (11, 12, _fd)]
    # Anti-alias inner V
    px += [(7, 11, _flame_bg), (8, 11, _flame_bg)]
    # Row 13
    px += [(4, 13, _fd), (5, 13, _fs)]
    px += [(10, 13, _fs), (11, 13, _fd)]
    # Anti-alias
    px += [(6, 13, _flame_bg), (9, 13, _flame_bg)]
    # Row 14: tips
    px += [(4, 14, _fd), (5, 14, _fd)]
    px += [(10, 14, _fd), (11, 14, _fd)]
    # Row 15: final points
    px += [(4, 15, _flame_bg)]
    px += [(11, 15, _flame_bg)]

    # -- Decorative star near top (small 3x3 star at center) ------------
    px += [(7, 3, _gh), (8, 3, _gh)]
    px += [(6, 4, _gb), (7, 4, _gh), (8, 4, _gh), (9, 4, _gb)]
    px += [(7, 5, _gb), (8, 5, _gb)]

    return px


def _clipboard() -> list[tuple[int, int, str]]:
    """Clipboard with metal clip and text lines on paper."""
    px: list[tuple[int, int, str]] = []

    # -- Metal clip at top (gold, rows 0-3) -----------------------------
    # Clip outline
    px += [(6, 0, _gd), (7, 0, _gd), (8, 0, _gd), (9, 0, _gd)]
    px += [(5, 1, _gd), (10, 1, _gd)]
    px += [(5, 2, _gd), (10, 2, _gd)]
    px += [(5, 3, _gd), (6, 3, _gd), (7, 3, _gd), (8, 3, _gd)]
    px += [(9, 3, _gd), (10, 3, _gd)]
    # Clip fill
    px += [(6, 1, _gh), (7, 1, _gh), (8, 1, _gb), (9, 1, _gb)]
    px += [(6, 2, _gb), (7, 2, _gb), (8, 2, _gs), (9, 2, _gs)]
    # Anti-alias clip corners
    px += [(5, 0, _gold_bg), (10, 0, _gold_bg)]

    # -- Board outline --------------------------------------------------
    # Left edge
    px += [(2, y, _pd) for y in range(3, 15)]
    # Right edge
    px += [(13, y, _pd) for y in range(3, 15)]
    # Top edge
    px += [(x, 2, _pd) for x in range(3, 13)]
    # Bottom edge
    px += [(x, 15, _pd) for x in range(2, 14)]
    # Anti-alias corners
    px += [(2, 2, _parch_bg), (13, 2, _parch_bg)]
    px += [(2, 15, _parch_bg), (13, 15, _parch_bg)]

    # -- Board fill (parchment body) ------------------------------------
    for y in range(3, 15):
        for x in range(3, 13):
            if y == 3:
                px.append((x, y, _ph))
            elif y == 14:
                px.append((x, y, _ps))
            else:
                px.append((x, y, _pb))

    # -- Paper area (slightly inset, lighter parchment) -----------------
    for y in range(5, 14):
        for x in range(4, 12):
            px.append((x, y, _ph))

    # -- Text lines (ink) -----------------------------------------------
    for y in (6, 8, 10, 12):
        px += [(x, y, _ib) for x in range(5, 11)]
    for y in (7, 9, 11):
        px += [(x, y, _ih) for x in range(5, 9)]

    # -- Board shadow on right and bottom edges -------------------------
    px += [(12, y, _ps) for y in range(4, 15)]
    px += [(x, 14, _ps) for x in range(4, 12)]

    return px


# ======================================================================
# Registration entry point
# ======================================================================


def register_icons(register) -> None:  # type: ignore[type-arg]
    """Register all book-themed 16x16 icons in the global catalog."""
    register("books", _books())
    register("book-open", _book_open())
    register("book-closed", _book_closed())
    register("scroll", _scroll())
    register("bookmark", _bookmark())
    register("clipboard", _clipboard())
