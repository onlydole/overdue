"""Golden Sun: The Lost Age style pixel art librarian avatar system.

Provides 12 diverse 32x32 pixel art librarian avatars rendered as inline SVG.
Each avatar is a tight close-up portrait matching Golden Sun GBA portrait
proportions: 6-row expressive eyes (9px wide) with 2px catchlights as the
centerpiece, volumetric hair covering rows 0-10, oval face filling ~80% of
the canvas, 5-tone skin shading, and minimal outfit (rows 27-31 only).
"""

from __future__ import annotations

from src.game.icons._palette import blend_colors, darken, lighten

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------
_GLASSES_FRAME = "#333333"
_GLASSES_LENS = "#87CEEB"
_GLASSES_LENS_HIGHLIGHT = "#c8e8f8"

# Iris colors for eye variety
_IRIS_COLORS = [
    "#5a3a1a",  # warm brown
    "#2e6b30",  # green
    "#3a5a8c",  # blue-grey
    "#6b4226",  # dark brown
    "#4a7a4a",  # hazel-green
]


def _iris_for_skin(skin: str) -> str:
    """Pick an iris color based on the skin tone hash for deterministic variety."""
    idx = sum(ord(c) for c in skin) % len(_IRIS_COLORS)
    return _IRIS_COLORS[idx]


# ---------------------------------------------------------------------------
# Shading ramp helpers
# ---------------------------------------------------------------------------


def _skin_ramp(skin: str) -> dict[str, str]:
    return {
        "highlight": lighten(skin, 0.20),
        "base": skin,
        "warm": blend_colors(skin, "#e88b8b", 0.15),
        "shadow": darken(skin, 0.10),
        "deep_shadow": darken(skin, 0.20),
    }


def _iris_ramp(iris_color: str) -> dict[str, str]:
    return {
        "catchlight": "#FFFFFF",
        "highlight": lighten(iris_color, 0.35),
        "base": iris_color,
        "shadow": darken(iris_color, 0.30),
    }


def _hair_ramp(hair_color: str) -> dict[str, str]:
    return {
        "highlight": lighten(hair_color, 0.40),
        "light": lighten(hair_color, 0.20),
        "base": hair_color,
        "shadow": darken(hair_color, 0.25),
        "deep_shadow": darken(hair_color, 0.45),
    }


# ---------------------------------------------------------------------------
# Avatar catalog
# ---------------------------------------------------------------------------
AVATAR_CATALOG: dict[str, dict] = {
    "avatar_01": {
        "name": "Paige",
        "description": (
            "A silver-haired archivist in forest green, peering through"
            " reading glasses with knowing eyes."
        ),
        "skin_tone": "#F5D0A9",
        "hair_style": "short_cropped",
        "hair_color": "#C0C0C0",
        "glasses": True,
        "outfit_color": "#2E7D32",
    },
    "avatar_02": {
        "name": "Follio",
        "description": (
            "An auburn-curled storyteller draped in deep purple, always midway through a tale."
        ),
        "skin_tone": "#8D5524",
        "hair_style": "curly",
        "hair_color": "#A0522D",
        "glasses": False,
        "outfit_color": "#4A148C",
    },
    "avatar_03": {
        "name": "Dewey",
        "description": (
            "A bespectacled navigator in crisp navy, head shining bright beneath the stacks."
        ),
        "skin_tone": "#C68642",
        "hair_style": "bald",
        "hair_color": None,
        "glasses": True,
        "outfit_color": "#1A237E",
    },
    "avatar_04": {
        "name": "Margot",
        "description": ("Long golden hair flowing over a burgundy coat, a quiet corner reader."),
        "skin_tone": "#F5D0A9",
        "hair_style": "long_straight",
        "hair_color": "#F0E68C",
        "glasses": False,
        "outfit_color": "#7B1FA2",
    },
    "avatar_05": {
        "name": "Coda",
        "description": ("A confident reader in teal with a neat afro, always finishing strong."),
        "skin_tone": "#3C1F0A",
        "hair_style": "short_afro",
        "hair_color": "#1A1A1A",
        "glasses": False,
        "outfit_color": "#00695C",
    },
    "avatar_06": {
        "name": "Verso",
        "description": ("Blue-mohawked rebel librarian in bold red, always turning the page."),
        "skin_tone": "#E0AC69",
        "hair_style": "mohawk",
        "hair_color": "#1976D2",
        "glasses": False,
        "outfit_color": "#C62828",
    },
    "avatar_07": {
        "name": "Octavia",
        "description": (
            "Braided hair and golden outfit, always peering through glasses at the fine print."
        ),
        "skin_tone": "#6B4226",
        "hair_style": "braids",
        "hair_color": "#3E2723",
        "glasses": True,
        "outfit_color": "#F9A825",
    },
    "avatar_08": {
        "name": "Fern",
        "description": (
            "Red ponytail bouncing above a cool slate jacket, the reference desk regular."
        ),
        "skin_tone": "#F5D0A9",
        "hair_style": "ponytail",
        "hair_color": "#B22222",
        "glasses": False,
        "outfit_color": "#546E7A",
    },
    "avatar_09": {
        "name": "Lyra",
        "description": (
            "Purple bob cut framing a curious face above olive green, drawn to poetry."
        ),
        "skin_tone": "#C68642",
        "hair_style": "bob_cut",
        "hair_color": "#7B1FA2",
        "glasses": False,
        "outfit_color": "#558B2F",
    },
    "avatar_10": {
        "name": "Quill",
        "description": (
            "Sharp undercut and glasses over a charcoal coat, the meticulous note-taker."
        ),
        "skin_tone": "#8D5524",
        "hair_style": "undercut",
        "hair_color": "#1A1A1A",
        "glasses": True,
        "outfit_color": "#37474F",
    },
    "avatar_11": {
        "name": "Sable",
        "description": ("Long locs cascading over an emerald tunic, keeper of rare volumes."),
        "skin_tone": "#3C1F0A",
        "hair_style": "locs",
        "hair_color": "#3E2723",
        "glasses": False,
        "outfit_color": "#1B5E20",
    },
    "avatar_12": {
        "name": "Bindery",
        "description": ("Green spiky hair and a pink outfit, the wildcard cataloger."),
        "skin_tone": "#F5D0A9",
        "hair_style": "spiky",
        "hair_color": "#2E7D32",
        "glasses": False,
        "outfit_color": "#E91E63",
    },
}


# ---------------------------------------------------------------------------
# Hair pattern helpers -- each returns a list of (x, y, color) pixels
# Coordinates for 32x32 canvas.  Face spans nearly full width at eye level.
# Hair zone is rows 0-10 with hairline shadow at row 11.
# Wide hairstyles must fill cols 0-31 at widest rows -- NO transparent gaps.
# All non-bald builders use 5-tone ramp from _hair_ramp().
# ---------------------------------------------------------------------------


def _hair_short_cropped(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Short cropped hair: graduated tone rows 0-10, wide coverage cols 2-29."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    row_tones = [
        r["highlight"],
        r["highlight"],
        r["light"],
        r["light"],
        r["base"],
        r["base"],
        r["base"],
        r["shadow"],
        r["shadow"],
        r["deep_shadow"],
        r["deep_shadow"],
    ]

    # Row widths: gradually widen from top
    row_ranges = [
        (6, 25),
        (4, 27),
        (3, 28),
        (2, 29),
        (2, 29),
        (2, 29),
        (2, 29),
        (2, 29),
        (3, 28),
        (4, 27),
        (5, 26),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        tone = row_tones[row_idx]
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, tone))
        # Edge shadows
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        # Scattered highlights
        for hx in range(lo + 3, hi, 4):
            pixels.append((hx, row_idx, r["highlight"] if row_idx < 6 else r["base"]))

    # Hairline shadow at row 11
    for x in range(5, 27):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_curly(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Curly hair: 2x2 curl clusters with massive volume, rows 0-10 + side puffs."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row 0: crown puff (cols 4-27)
    for x in range(4, 28):
        pixels.append((x, 0, r["base"]))
    for cx in (6, 10, 14, 18, 22, 26):
        pixels.append((cx, 0, r["highlight"]))
    pixels.append((4, 0, r["deep_shadow"]))
    pixels.append((27, 0, r["deep_shadow"]))

    # Row 1: wider puff (cols 2-29)
    for x in range(2, 30):
        pixels.append((x, 1, r["base"]))
    for cx in (4, 8, 12, 16, 20, 24, 28):
        pixels.append((cx, 1, r["highlight"]))
    pixels.append((2, 1, r["deep_shadow"]))
    pixels.append((29, 1, r["deep_shadow"]))

    # Rows 2-5: full volume cols 0-31 with curl clusters
    for y in range(2, 6):
        for x in range(0, 32):
            pixels.append((x, y, r["base"]))
        pixels.append((0, y, r["deep_shadow"]))
        pixels.append((31, y, r["deep_shadow"]))
        if y % 2 == 0:
            for cx in range(2, 30, 4):
                pixels.append((cx, y, r["highlight"]))
                if cx + 1 < 31:
                    pixels.append((cx + 1, y, r["light"]))
        else:
            for cx in range(2, 30, 4):
                pixels.append((cx, y, r["shadow"]))
                if cx + 1 < 31:
                    pixels.append((cx + 1, y, r["deep_shadow"]))

    # Rows 6-7: narrowing slightly (cols 0-31)
    for y in range(6, 8):
        for x in range(0, 32):
            pixels.append((x, y, r["base"] if y == 6 else r["shadow"]))
        pixels.append((0, y, r["deep_shadow"]))
        pixels.append((31, y, r["deep_shadow"]))
        for cx in range(3, 29, 4):
            pixels.append((cx, y, r["highlight"] if y == 6 else r["base"]))

    # Rows 8-10: transition to hairline
    for y in range(8, 11):
        lo = y - 6  # 2, 3, 4
        hi = 31 - lo
        for x in range(lo, hi + 1):
            pixels.append((x, y, r["shadow"] if y < 10 else r["deep_shadow"]))
        for cx in range(lo + 3, hi, 5):
            pixels.append((cx, y, r["base"] if y < 10 else r["shadow"]))

    # Side volume puffs rows 6-15 (cols 0-2 and 29-31)
    for y in range(6, 16):
        for dx in (0, 1, 2):
            pixels.append((dx, y, r["base"] if y < 11 else r["shadow"]))
        for dx in (29, 30, 31):
            pixels.append((dx, y, r["base"] if y < 11 else r["shadow"]))
        pixels.append((0, y, r["deep_shadow"]))
        pixels.append((31, y, r["deep_shadow"]))
        if y % 2 == 0:
            pixels.append((1, y, r["highlight"]))
            pixels.append((30, y, r["highlight"]))
        else:
            pixels.append((1, y, r["shadow"]))
            pixels.append((30, y, r["shadow"]))

    # Hairline shadow at row 11
    for x in range(3, 29):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_bald(hair_color: str | None, skin_tone: str) -> list[tuple[int, int, str]]:
    """Bald: wide specular highlight arc at crown rows 0-5."""
    pixels: list[tuple[int, int, str]] = []
    near_white = lighten(skin_tone, 0.40)
    bright = lighten(skin_tone, 0.25)
    subtle = lighten(skin_tone, 0.15)
    very_subtle = lighten(skin_tone, 0.08)

    # Row 0: wide crown highlight (cols 8-23)
    for x in range(8, 24):
        pixels.append((x, 0, near_white))
    for x in range(12, 20):
        pixels.append((x, 0, "#FFFFFF"))

    # Row 1: wider bright arc (cols 6-25)
    for x in range(6, 26):
        pixels.append((x, 1, bright))
    for x in range(10, 22):
        pixels.append((x, 1, near_white))
    for x in range(13, 19):
        pixels.append((x, 1, "#FFFFFF"))

    # Row 2: bright glow (cols 4-27)
    for x in range(4, 28):
        pixels.append((x, 2, bright))
    for x in range(10, 22):
        pixels.append((x, 2, near_white))

    # Row 3: subtle glow (cols 3-28)
    for x in range(3, 29):
        pixels.append((x, 3, subtle))
    for x in range(12, 20):
        pixels.append((x, 3, bright))

    # Row 4: wider subtle (cols 3-28)
    for x in range(3, 29):
        pixels.append((x, 4, subtle))
    for x in range(13, 19):
        pixels.append((x, 4, bright))

    # Rows 5-8: very subtle scalp sheen (cols 3-28)
    for y in range(5, 9):
        for x in range(3, 29):
            pixels.append((x, y, very_subtle))

    return pixels


def _hair_long_straight(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Long straight hair: rows 0-10 top full width, side curtains cols 0-2/29-31."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Rows 0-10: wide top coverage
    row_ranges = [
        (4, 27),
        (2, 29),
        (1, 30),
        (0, 31),
        (0, 31),
        (0, 31),
        (0, 31),
        (0, 31),
        (1, 30),
        (2, 29),
        (3, 28),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        tone = r["base"] if row_idx < 7 else r["shadow"]
        if row_idx >= 9:
            tone = r["deep_shadow"]
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, tone))
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        # Strand highlights every 3 cols
        for sx in range(lo + 2, hi, 3):
            hl = r["highlight"] if row_idx < 5 else r["light"]
            if row_idx >= 7:
                hl = r["base"]
            pixels.append((sx, row_idx, hl))
        # Strand shadows alternating
        for sx in range(lo + 3, hi, 3):
            pixels.append((sx, row_idx, r["shadow"] if row_idx < 7 else r["deep_shadow"]))

    # Side curtains cols 0-2 and 29-31 flowing to row 26
    for y in range(4, 27):
        for dx in (0, 1, 2):
            pixels.append((dx, y, r["base"]))
        for dx in (29, 30, 31):
            pixels.append((dx, y, r["base"]))
        if y % 3 == 0:
            pixels.append((0, y, r["highlight"]))
            pixels.append((31, y, r["highlight"]))
        elif y % 3 == 1:
            pixels.append((1, y, r["shadow"]))
            pixels.append((30, y, r["shadow"]))
        else:
            pixels.append((2, y, r["light"]))
            pixels.append((29, y, r["light"]))
        pixels.append((0, y, r["deep_shadow"] if y > 18 else r["shadow"]))
        pixels.append((31, y, r["deep_shadow"] if y > 18 else r["shadow"]))

    # Hairline shadow at row 11
    for x in range(3, 29):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_short_afro(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Short afro: dense texture rows 0-10 full width with side volume."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row ranges for round afro shape -- fills canvas
    row_ranges = [
        (4, 27),
        (2, 29),
        (1, 30),
        (0, 31),
        (0, 31),
        (0, 31),
        (0, 31),
        (0, 31),
        (1, 30),
        (2, 29),
        (3, 28),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, r["base"]))
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        # Dense afro texture: alternating highlight/shadow dots
        if row_idx % 2 == 0:
            for tx in range(lo + 2, hi, 3):
                pixels.append((tx, row_idx, r["highlight"]))
            for tx in range(lo + 3, hi, 3):
                pixels.append((tx, row_idx, r["light"]))
        else:
            for tx in range(lo + 1, hi, 3):
                pixels.append((tx, row_idx, r["highlight"]))
            for tx in range(lo + 2, hi, 3):
                pixels.append((tx, row_idx, r["shadow"]))

    # Side volume rows 5-14 (cols 0-1 and 30-31)
    for y in range(5, 15):
        pixels.append((0, y, r["deep_shadow"]))
        pixels.append((1, y, r["shadow"] if y < 11 else r["deep_shadow"]))
        pixels.append((30, y, r["shadow"] if y < 11 else r["deep_shadow"]))
        pixels.append((31, y, r["deep_shadow"]))
        if y % 2 == 0:
            pixels.append((1, y, r["highlight"]))
            pixels.append((30, y, r["highlight"]))

    # Hairline shadow at row 11
    for x in range(3, 29):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_mohawk(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Tall dramatic mohawk: wider spikes cols 8-23, rows 0-10."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row 0: spike tips (highlight)
    for sx in (9, 12, 15, 18, 21):
        pixels.append((sx, 0, r["highlight"]))

    # Row 1: spike upper bodies (cols 8-23)
    for x in range(8, 24):
        pixels.append((x, 1, r["highlight"]))
    for gx in (10, 13, 16, 19, 22):
        pixels.append((gx, 1, r["deep_shadow"]))

    # Row 2: widening (cols 7-24)
    for x in range(7, 25):
        pixels.append((x, 2, r["highlight"]))
    for gx in (10, 13, 16, 19, 22):
        pixels.append((gx, 2, r["light"]))

    # Row 3: transition (cols 7-24)
    for x in range(7, 25):
        pixels.append((x, 3, r["light"]))
    for hx in (9, 13, 17, 21):
        pixels.append((hx, 3, r["highlight"]))
    pixels.append((7, 3, r["shadow"]))
    pixels.append((24, 3, r["shadow"]))

    # Row 4: base (cols 7-24)
    for x in range(7, 25):
        pixels.append((x, 4, r["base"]))
    for hx in (10, 14, 18, 22):
        pixels.append((hx, 4, r["light"]))
    pixels.append((7, 4, r["deep_shadow"]))
    pixels.append((24, 4, r["deep_shadow"]))

    # Row 5: base (cols 8-23)
    for x in range(8, 24):
        pixels.append((x, 5, r["base"]))
    pixels.append((11, 5, r["light"]))
    pixels.append((17, 5, r["light"]))
    pixels.append((8, 5, r["deep_shadow"]))
    pixels.append((23, 5, r["deep_shadow"]))

    # Row 6: base -> shadow (cols 8-23)
    for x in range(8, 24):
        pixels.append((x, 6, r["base"]))
    pixels.append((12, 6, r["shadow"]))
    pixels.append((18, 6, r["shadow"]))

    # Row 7: shadow (cols 9-22)
    for x in range(9, 23):
        pixels.append((x, 7, r["shadow"]))
    pixels.append((13, 7, r["base"]))
    pixels.append((17, 7, r["base"]))

    # Row 8: deeper shadow (cols 9-22)
    for x in range(9, 23):
        pixels.append((x, 8, r["shadow"]))
    pixels.append((14, 8, r["base"]))
    pixels.append((18, 8, r["base"]))

    # Row 9: deep shadow (cols 10-21)
    for x in range(10, 22):
        pixels.append((x, 9, r["deep_shadow"]))
    pixels.append((14, 9, r["shadow"]))
    pixels.append((18, 9, r["shadow"]))

    # Row 10: bottom fringe (cols 10-21)
    for x in range(10, 22):
        pixels.append((x, 10, r["deep_shadow"]))
    pixels.append((15, 10, r["shadow"]))
    pixels.append((17, 10, r["shadow"]))

    # Hairline shadow at row 11
    for x in range(10, 22):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_braids(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Braids: full-width top rows 0-10, braid strips cols 0-2 and 29-31 to row 26."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-10 -- wide
    row_ranges = [
        (5, 26),
        (3, 28),
        (2, 29),
        (1, 30),
        (1, 30),
        (1, 30),
        (1, 30),
        (2, 29),
        (3, 28),
        (4, 27),
        (5, 26),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        tone = r["base"] if row_idx < 6 else r["shadow"]
        if row_idx >= 9:
            tone = r["deep_shadow"]
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, tone))
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        for hx in range(lo + 3, hi, 5):
            pixels.append((hx, row_idx, r["highlight"] if row_idx < 5 else r["base"]))

    # Braid strips cols 0-2 and 29-31 with interlocking texture
    for y in range(4, 27):
        for dx in (0, 1, 2):
            pixels.append((dx, y, r["base"]))
        for dx in (29, 30, 31):
            pixels.append((dx, y, r["base"]))
        band = y % 4
        if band == 0:
            pixels.append((0, y, r["highlight"]))
            pixels.append((1, y, r["light"]))
            pixels.append((30, y, r["light"]))
            pixels.append((31, y, r["highlight"]))
        elif band == 1:
            pixels.append((1, y, r["shadow"]))
            pixels.append((2, y, r["highlight"]))
            pixels.append((29, y, r["highlight"]))
            pixels.append((30, y, r["shadow"]))
        elif band == 2:
            pixels.append((0, y, r["shadow"]))
            pixels.append((2, y, r["light"]))
            pixels.append((29, y, r["light"]))
            pixels.append((31, y, r["shadow"]))
        else:
            pixels.append((1, y, r["deep_shadow"]))
            pixels.append((30, y, r["deep_shadow"]))

    # Braid tie accessories at tips (row 26)
    tie_color = lighten(hair_color, 0.50)
    for dx in (0, 1, 2):
        pixels.append((dx, 26, tie_color))
    for dx in (29, 30, 31):
        pixels.append((dx, 26, tie_color))

    # Hairline shadow at row 11
    for x in range(5, 27):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_ponytail(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Ponytail: wide top rows 0-10, ponytail trailing right cols 29-31 rows 5-20."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-10 -- wide
    row_ranges = [
        (5, 26),
        (3, 28),
        (2, 29),
        (1, 30),
        (1, 30),
        (1, 30),
        (1, 30),
        (2, 29),
        (3, 28),
        (4, 27),
        (5, 26),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        tone = r["base"] if row_idx < 6 else r["shadow"]
        if row_idx >= 9:
            tone = r["deep_shadow"]
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, tone))
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        for hx in range(lo + 3, hi, 4):
            pixels.append((hx, row_idx, r["highlight"] if row_idx < 5 else r["base"]))

    # Ponytail trailing right: cols 29-31, rows 5-20
    tie_color = darken(hair_color, 0.40)
    for y in range(5, 21):
        for dx in (29, 30, 31):
            pixels.append((dx, y, r["base"]))
        if y % 3 == 0:
            pixels.append((30, y, r["highlight"]))
        elif y % 3 == 1:
            pixels.append((29, y, r["shadow"]))
        if y > 14:
            pixels.append((31, y, r["shadow"]))

    # Hair tie detail at row 6
    for dx in (29, 30, 31):
        pixels.append((dx, 6, tie_color))

    # Taper at bottom
    for dx in (29, 30, 31):
        pixels.append((dx, 19, r["deep_shadow"]))
        pixels.append((dx, 20, r["deep_shadow"]))

    # Hairline shadow at row 11
    for x in range(5, 27):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_bob_cut(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Bob cut: full-width top rows 0-10, side panels cols 0-2/29-31 rows 6-22."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-10 -- wide
    row_ranges = [
        (4, 27),
        (2, 29),
        (1, 30),
        (0, 31),
        (0, 31),
        (0, 31),
        (0, 31),
        (1, 30),
        (2, 29),
        (3, 28),
        (4, 27),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        tone = r["base"] if row_idx < 6 else r["shadow"]
        if row_idx >= 9:
            tone = r["deep_shadow"]
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, tone))
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        for hx in range(lo + 3, hi, 5):
            pixels.append((hx, row_idx, r["highlight"] if row_idx < 5 else r["base"]))

    # Side panels (cols 0-2 and 29-31) rows 6-22
    for y in range(6, 23):
        pixels.append((0, y, r["shadow"]))
        pixels.append((1, y, r["base"]))
        pixels.append((2, y, r["light"]))
        pixels.append((29, y, r["light"]))
        pixels.append((30, y, r["base"]))
        pixels.append((31, y, r["shadow"]))
        if y % 3 == 0:
            pixels.append((2, y, r["highlight"]))
            pixels.append((29, y, r["highlight"]))
        if y > 16:
            pixels.append((0, y, r["deep_shadow"]))
            pixels.append((31, y, r["deep_shadow"]))

    # Inward curl at tips (rows 21-22)
    pixels.append((1, 21, r["deep_shadow"]))
    pixels.append((2, 21, r["shadow"]))
    pixels.append((3, 21, r["base"]))
    pixels.append((4, 21, r["light"]))
    pixels.append((28, 21, r["light"]))
    pixels.append((29, 21, r["base"]))
    pixels.append((30, 21, r["shadow"]))
    pixels.append((31, 21, r["deep_shadow"]))
    pixels.append((2, 22, r["deep_shadow"]))
    pixels.append((3, 22, r["shadow"]))
    pixels.append((4, 22, r["base"]))
    pixels.append((28, 22, r["base"]))
    pixels.append((29, 22, r["shadow"]))
    pixels.append((30, 22, r["deep_shadow"]))

    # Hairline shadow at row 11
    for x in range(4, 28):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_undercut(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Undercut: wide swept top rows 0-8, shaved sides 8-11."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Dramatic swept top rows 0-8 -- wider
    row_ranges = [
        (5, 26),
        (3, 28),
        (2, 29),
        (2, 29),
        (2, 29),
        (2, 29),
        (3, 28),
        (4, 27),
        (5, 26),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, r["base"]))
        pixels.append((lo, row_idx, r["shadow"]))
        pixels.append((hi, row_idx, r["shadow"]))
        # Bold sweep highlights
        for hx in range(lo + 2, hi, 4):
            pixels.append((hx, row_idx, r["highlight"]))
        for hx in range(lo + 3, hi, 4):
            pixels.append((hx, row_idx, r["light"]))

    # Rows 9-10: deep shadow fringe
    for y in range(9, 11):
        for x in range(6, 26):
            pixels.append((x, y, r["deep_shadow"]))
        for hx in range(8, 24, 4):
            pixels.append((hx, y, r["shadow"]))

    # Shaved sides rows 8-11: stubble dots
    for y in range(8, 12):
        for x in (1, 2, 3):
            pixels.append((x, y, r["deep_shadow"]))
        for x in (28, 29, 30):
            pixels.append((x, y, r["deep_shadow"]))
        if y % 2 == 0:
            pixels.append((1, y, darken(hair_color, 0.60)))
            pixels.append((3, y, darken(hair_color, 0.60)))
            pixels.append((28, y, darken(hair_color, 0.60)))
            pixels.append((30, y, darken(hair_color, 0.60)))
        else:
            pixels.append((2, y, darken(hair_color, 0.60)))
            pixels.append((29, y, darken(hair_color, 0.60)))

    # Hairline shadow at row 11
    for x in range(5, 27):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_locs(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Locs: full-width top rows 0-10, loc strands cols 0-2 and 29-31 rows 6-26."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-10 -- wide
    row_ranges = [
        (5, 26),
        (3, 28),
        (2, 29),
        (1, 30),
        (1, 30),
        (1, 30),
        (1, 30),
        (2, 29),
        (3, 28),
        (4, 27),
        (5, 26),
    ]

    for row_idx, (lo, hi) in enumerate(row_ranges):
        tone = r["base"] if row_idx < 6 else r["shadow"]
        if row_idx >= 9:
            tone = r["deep_shadow"]
        for x in range(lo, hi + 1):
            pixels.append((x, row_idx, tone))
        pixels.append((lo, row_idx, r["deep_shadow"]))
        pixels.append((hi, row_idx, r["deep_shadow"]))
        for hx in range(lo + 3, hi, 5):
            pixels.append((hx, row_idx, r["highlight"] if row_idx < 5 else r["base"]))

    # Individual loc strands on sides, rows 6-26
    for y in range(6, 27):
        # Left side locs: cols 0-2
        pixels.append((0, y, r["base"]))
        pixels.append((1, y, r["base"]))
        pixels.append((2, y, r["base"]))
        band = y % 3
        if band == 0:
            pixels.append((0, y, r["highlight"]))
            pixels.append((1, y, r["light"]))
        elif band == 1:
            pixels.append((1, y, r["shadow"]))
            pixels.append((2, y, r["light"]))
        else:
            pixels.append((0, y, r["shadow"]))
            pixels.append((2, y, r["deep_shadow"]))
        if y % 4 == 0:
            pixels.append((0, y, r["deep_shadow"]))

        # Right side locs: cols 29-31
        pixels.append((29, y, r["base"]))
        pixels.append((30, y, r["base"]))
        pixels.append((31, y, r["base"]))
        if band == 0:
            pixels.append((30, y, r["light"]))
            pixels.append((31, y, r["highlight"]))
        elif band == 1:
            pixels.append((29, y, r["light"]))
            pixels.append((30, y, r["shadow"]))
        else:
            pixels.append((29, y, r["deep_shadow"]))
            pixels.append((31, y, r["shadow"]))
        if y % 4 == 2:
            pixels.append((31, y, r["deep_shadow"]))

    # Loc tips at row 26
    for dx in (0, 1, 2):
        pixels.append((dx, 26, r["deep_shadow"]))
    for dx in (29, 30, 31):
        pixels.append((dx, 26, r["deep_shadow"]))

    # Hairline shadow at row 11
    for x in range(5, 27):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


def _hair_spiky(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Spiky hair: wide triangular spikes cols 0-31, rows 0-10."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Spike tips at row 0 (highlight) -- full spread
    spike_tips = [3, 8, 13, 18, 23, 28]
    for x in spike_tips:
        pixels.append((x, 0, r["highlight"]))

    # Row 1: spike bodies + gaps
    for x in spike_tips:
        pixels.append((x, 1, r["highlight"]))
        if x - 1 >= 0:
            pixels.append((x - 1, 1, r["light"]))
        if x + 1 <= 31:
            pixels.append((x + 1, 1, r["light"]))
    for gx in (5, 10, 15, 20, 25):
        pixels.append((gx, 1, r["deep_shadow"]))

    # Row 2: wide base (cols 1-30)
    for x in range(1, 31):
        pixels.append((x, 2, r["base"]))
    for sx in spike_tips:
        pixels.append((sx, 2, r["highlight"]))
    for gx in (5, 10, 15, 20, 25):
        pixels.append((gx, 2, r["shadow"]))
    pixels.append((1, 2, r["deep_shadow"]))
    pixels.append((30, 2, r["deep_shadow"]))

    # Row 3: full width (cols 0-31)
    for x in range(0, 32):
        pixels.append((x, 3, r["base"]))
    for hx in range(2, 30, 4):
        pixels.append((hx, 3, r["light"]))
    pixels.append((0, 3, r["deep_shadow"]))
    pixels.append((31, 3, r["deep_shadow"]))

    # Rows 4-6: full width base
    for y in range(4, 7):
        for x in range(0, 32):
            pixels.append((x, y, r["base"]))
        pixels.append((0, y, r["shadow"]))
        pixels.append((31, y, r["shadow"]))
        for hx in range(3, 29, 4):
            pixels.append((hx, y, r["light"]))

    # Rows 7-8: shadow transition
    for y in range(7, 9):
        lo = y - 5  # 2, 3
        hi = 31 - lo
        for x in range(lo, hi + 1):
            pixels.append((x, y, r["shadow"]))
        for hx in range(lo + 3, hi, 5):
            pixels.append((hx, y, r["base"]))

    # Row 9-10: deep shadow fringe
    for y in range(9, 11):
        lo = y - 5  # 4, 5
        hi = 31 - lo
        for x in range(lo, hi + 1):
            pixels.append((x, y, r["deep_shadow"]))
        for hx in range(lo + 3, hi, 5):
            pixels.append((hx, y, r["shadow"]))

    # Hairline shadow at row 11
    for x in range(5, 27):
        pixels.append((x, 11, darken(skin_tone, 0.08)))

    return pixels


_HAIR_BUILDERS: dict[str, callable] = {
    "short_cropped": _hair_short_cropped,
    "curly": _hair_curly,
    "bald": _hair_bald,
    "long_straight": _hair_long_straight,
    "short_afro": _hair_short_afro,
    "mohawk": _hair_mohawk,
    "braids": _hair_braids,
    "ponytail": _hair_ponytail,
    "bob_cut": _hair_bob_cut,
    "undercut": _hair_undercut,
    "locs": _hair_locs,
    "spiky": _hair_spiky,
}


# ---------------------------------------------------------------------------
# Core pixel builder -- shoulders-up portrait at 32x32
# ---------------------------------------------------------------------------


def _build_avatar_pixels(avatar_def: dict) -> list[tuple[int, int, str]]:
    """Build the full list of (x, y, color) pixels for a portrait avatar.

    Golden Sun: The Lost Age style close-up portrait filling the ENTIRE 32x32
    canvas edge-to-edge.  Oval head contour nearly full-width at eye level,
    6-row expressive eyes (9px wide) with 2px catchlights, 5-tone skin shading,
    volumetric hair filling rows 0-10, and outfit filling full width at bottom.

    The portrait occupies the full 32x32 grid:
      Rows 0-10:  Hair zone (volumetric, overlaps skull, fills canvas width)
      Row 11:     Hairline / hair-skin transition
      Rows 12-13: Forehead (28px wide)
      Rows 14-19: EYES (6 rows, 9px wide -- the centerpiece, face 30px wide)
      Row 20:     Cheeks / blush + nose shadow
      Row 21:     Nose (tiny, 2px shadow)
      Rows 22-23: Mouth (5px)
      Rows 24-25: Chin / jaw (tapered)
      Row 26:     Neck
      Row 27:     Collar (20px)
      Rows 28-31: Outfit (fills to full 32px width)
    """
    skin = avatar_def["skin_tone"]
    outfit = avatar_def["outfit_color"]
    hair_style = avatar_def["hair_style"]
    hair_color = avatar_def["hair_color"]
    has_glasses = avatar_def["glasses"]

    # Derived skin shading via ramp
    sr = _skin_ramp(skin)
    skin_hi = sr["highlight"]
    skin_base = sr["base"]
    skin_warm = sr["warm"]
    skin_shadow = sr["shadow"]
    skin_deep = sr["deep_shadow"]

    # Face outline color (strong edge for oval contour)
    face_outline = darken(skin, 0.30)

    ear_color = darken(skin, 0.15)
    ear_fold = darken(ear_color, 0.15)
    lip_color = darken(skin, 0.25)
    lip_hi = blend_colors(lip_color, "#e88b8b", 0.3)
    brow_color = hair_color or darken(skin, 0.5)

    # Eye detail
    iris_color = _iris_for_skin(skin)
    ir = _iris_ramp(iris_color)
    sclera = "#FFFFFF"
    sclera_shadow = "#e8e0d0"
    eyelash = "#1a1a1a"
    pupil = "#0a0a0a"

    # Outfit shading
    outfit_shadow = darken(outfit, 0.3)
    outfit_hi = lighten(outfit, 0.15)

    # Directional lighting helpers: 3/4 perspective, lit from upper-left
    skin_left_lit = blend_colors(skin_base, skin_hi, 0.45)
    skin_right_shade = blend_colors(skin_base, skin_shadow, 0.4)

    pixels: list[tuple[int, int, str]] = []

    # ------------------------------------------------------------------
    # Face oval: row -> (left_col, right_col) inclusive
    # Face fills nearly 100% of canvas. Widest at eye level (rows 14-18).
    # Rows 0-11 are under hair, drawn for skull but overwritten by hair.
    # ------------------------------------------------------------------
    _face_oval: dict[int, tuple[int, int]] = {
        0: (6, 25),  # top skull (under hair) -- 20px
        1: (5, 26),  # 22px
        2: (4, 27),  # 24px
        3: (3, 28),  # 26px
        4: (3, 28),  # 26px
        5: (3, 28),  # 26px
        6: (3, 28),  # 26px
        7: (3, 28),  # 26px
        8: (3, 28),  # hairline area
        9: (3, 28),  # 26px
        10: (3, 28),  # 26px
        11: (2, 29),  # forehead wider -- 28px
        12: (2, 29),  # forehead -- 28px
        13: (2, 29),  # 28px
        14: (1, 30),  # eyes start -- 30px (nearly full width!)
        15: (1, 30),  # 30px
        16: (1, 30),  # 30px
        17: (1, 30),  # 30px
        18: (1, 30),  # eyes end -- 30px
        19: (2, 29),  # under-eye -- 28px
        20: (2, 29),  # cheeks -- 28px
        21: (3, 28),  # nose -- 26px
        22: (4, 27),  # mouth -- 24px
        23: (4, 27),  # 24px
        24: (5, 26),  # chin -- 22px
        25: (6, 25),  # chin tip -- 20px
    }

    # ------------------------------------------------------------------
    # Draw oval head with 3D shading (rows 0-25)
    # ------------------------------------------------------------------
    for y in range(0, 26):
        left, right = _face_oval[y]
        for x in range(left, right + 1):
            # Determine base skin tone for this region
            if y <= 13:
                # Forehead: highlighted (catches overhead light)
                base_tone = skin_hi
            elif y in (24, 25):
                # Chin: shadowed
                base_tone = skin_shadow
            else:
                base_tone = skin_base

            # --- Edge pixels: face outline ---
            if x == left or x == right:
                pixels.append((x, y, face_outline))
                continue

            # --- Next pixel inward: edge shadow for 3D roundness ---
            if x == left + 1 or x == right - 1:
                pixels.append((x, y, skin_shadow))
                continue

            # --- Directional lighting (upper-left light, 3/4 perspective) ---
            if x <= left + 3:
                tone = skin_left_lit if y <= 22 else base_tone
            elif x >= right - 2:
                tone = skin_right_shade if y <= 22 else skin_shadow
            elif x >= right - 4:
                tone = blend_colors(base_tone, skin_shadow, 0.2) if y <= 22 else base_tone
            else:
                tone = base_tone

            # --- Per-region overrides ---
            # Forehead shine (rows 12-13, shifted left for 3/4 lighting)
            if y in (12, 13) and 8 <= x <= 14:
                tone = lighten(skin, 0.25)
            # Cheek blush/warm (row 20) -- asymmetric: wider on left
            elif y == 20 and (left + 2 <= x <= left + 8 or right - 6 <= x <= right - 2):
                tone = skin_warm
            # Chin deep shadow at edges (rows 24-25)
            elif y == 24 and (x <= left + 3 or x >= right - 3):
                tone = skin_deep
            elif y == 25 and (x <= left + 3 or x >= right - 3):
                tone = skin_deep

            pixels.append((x, y, tone))

    # ------------------------------------------------------------------
    # Eyebrows (row 13): 6px tapered, adjusted for wider face
    # ------------------------------------------------------------------
    # Left brow: cols 4-9
    pixels.append((4, 13, darken(brow_color, 0.15)))
    for x in range(5, 10):
        pixels.append((x, 13, brow_color))
    pixels.append((10, 13, darken(brow_color, 0.15)))
    # Right brow: cols 22-27
    pixels.append((22, 13, darken(brow_color, 0.15)))
    for x in range(23, 28):
        pixels.append((x, 13, brow_color))
    pixels.append((28, 13, darken(brow_color, 0.15)))

    # ------------------------------------------------------------------
    # Eyes (rows 14-19) -- 6 rows tall, 9px wide per eye
    # Left eye cols 3-11, Right eye cols 20-28
    # Gap between eyes: cols 12-19 (8px nose bridge)
    # ------------------------------------------------------------------

    # --- Row 14: thick dark upper eyelid, full 9px width ---
    for x in range(3, 12):
        pixels.append((x, 14, eyelash))
    for x in range(20, 29):
        pixels.append((x, 14, eyelash))

    # --- Row 15: upper eye -- sclera, 2px catchlight, iris highlight ---
    # Left eye: cols 3-11
    pixels.append((3, 15, sclera))
    pixels.append((4, 15, ir["catchlight"]))  # 2px catchlight
    pixels.append((5, 15, ir["catchlight"]))  # 2px catchlight
    pixels.append((6, 15, ir["highlight"]))
    pixels.append((7, 15, ir["highlight"]))
    pixels.append((8, 15, ir["highlight"]))
    pixels.append((9, 15, sclera))
    pixels.append((10, 15, sclera))
    pixels.append((11, 15, skin_base))
    # Right eye: cols 20-28 (catchlight at cols 26-27)
    pixels.append((20, 15, skin_base))
    pixels.append((21, 15, sclera))
    pixels.append((22, 15, sclera))
    pixels.append((23, 15, ir["highlight"]))
    pixels.append((24, 15, ir["highlight"]))
    pixels.append((25, 15, ir["highlight"]))
    pixels.append((26, 15, ir["catchlight"]))  # 2px catchlight
    pixels.append((27, 15, ir["catchlight"]))  # 2px catchlight
    pixels.append((28, 15, sclera))

    # --- Row 16: mid eye -- sclera, iris highlight, iris base, pupil ---
    # Left eye
    pixels.append((3, 16, sclera))
    pixels.append((4, 16, ir["highlight"]))
    pixels.append((5, 16, ir["base"]))
    pixels.append((6, 16, ir["base"]))
    pixels.append((7, 16, pupil))
    pixels.append((8, 16, ir["base"]))
    pixels.append((9, 16, ir["base"]))
    pixels.append((10, 16, sclera))
    pixels.append((11, 16, skin_base))
    # Right eye
    pixels.append((20, 16, skin_base))
    pixels.append((21, 16, sclera))
    pixels.append((22, 16, ir["base"]))
    pixels.append((23, 16, ir["base"]))
    pixels.append((24, 16, pupil))
    pixels.append((25, 16, ir["base"]))
    pixels.append((26, 16, ir["base"]))
    pixels.append((27, 16, ir["highlight"]))
    pixels.append((28, 16, sclera))

    # --- Row 17: pupil center (big! 3px wide) ---
    # Left eye
    pixels.append((3, 17, sclera))
    pixels.append((4, 17, ir["base"]))
    pixels.append((5, 17, ir["base"]))
    pixels.append((6, 17, pupil))
    pixels.append((7, 17, pupil))
    pixels.append((8, 17, pupil))
    pixels.append((9, 17, ir["base"]))
    pixels.append((10, 17, sclera))
    pixels.append((11, 17, skin_base))
    # Right eye
    pixels.append((20, 17, skin_base))
    pixels.append((21, 17, sclera))
    pixels.append((22, 17, ir["base"]))
    pixels.append((23, 17, pupil))
    pixels.append((24, 17, pupil))
    pixels.append((25, 17, pupil))
    pixels.append((26, 17, ir["base"]))
    pixels.append((27, 17, ir["base"]))
    pixels.append((28, 17, sclera))

    # --- Row 18: lower eye narrows -- sclera shadow, iris shadow ---
    # Left eye
    pixels.append((3, 18, skin_base))
    pixels.append((4, 18, sclera_shadow))
    pixels.append((5, 18, ir["shadow"]))
    pixels.append((6, 18, ir["shadow"]))
    pixels.append((7, 18, ir["shadow"]))
    pixels.append((8, 18, ir["shadow"]))
    pixels.append((9, 18, sclera_shadow))
    pixels.append((10, 18, skin_base))
    pixels.append((11, 18, skin_base))
    # Right eye
    pixels.append((20, 18, skin_base))
    pixels.append((21, 18, skin_base))
    pixels.append((22, 18, sclera_shadow))
    pixels.append((23, 18, ir["shadow"]))
    pixels.append((24, 18, ir["shadow"]))
    pixels.append((25, 18, ir["shadow"]))
    pixels.append((26, 18, ir["shadow"]))
    pixels.append((27, 18, sclera_shadow))
    pixels.append((28, 18, skin_base))

    # --- Row 19: under-eye shadow (thin) ---
    # Left eye
    pixels.append((4, 19, skin_base))
    pixels.append((5, 19, skin_shadow))
    pixels.append((6, 19, skin_shadow))
    pixels.append((7, 19, skin_shadow))
    pixels.append((8, 19, skin_shadow))
    pixels.append((9, 19, skin_base))
    pixels.append((10, 19, skin_base))
    # Right eye
    pixels.append((21, 19, skin_base))
    pixels.append((22, 19, skin_base))
    pixels.append((23, 19, skin_shadow))
    pixels.append((24, 19, skin_shadow))
    pixels.append((25, 19, skin_shadow))
    pixels.append((26, 19, skin_shadow))
    pixels.append((27, 19, skin_base))

    # ------------------------------------------------------------------
    # Ears -- asymmetric for 3/4 perspective, adjusted for wider face
    # Left ear: cols 0-1, rows 16-18 (minimal, near side)
    # Right ear: cols 30-31, rows 15-19 (more visible, far side)
    # ------------------------------------------------------------------
    # Left ear: minimal
    pixels.append((1, 16, ear_color))
    pixels.append((1, 17, ear_color))
    pixels.append((1, 18, ear_color))
    pixels.append((0, 17, ear_fold))

    # Right ear: more visible (far side)
    pixels.append((30, 15, ear_color))
    pixels.append((30, 16, ear_color))
    pixels.append((30, 17, ear_color))
    pixels.append((30, 18, ear_color))
    pixels.append((30, 19, ear_color))
    pixels.append((31, 16, ear_color))
    pixels.append((31, 17, ear_color))
    pixels.append((31, 18, ear_color))
    # Inner fold shadow
    pixels.append((30, 17, ear_fold))
    pixels.append((30, 18, ear_fold))

    # ------------------------------------------------------------------
    # Nose (row 21): tiny shadow, shifted right for 3/4 perspective
    # ------------------------------------------------------------------
    pixels.append((17, 21, skin_shadow))
    pixels.append((18, 21, skin_deep))

    # ------------------------------------------------------------------
    # Mouth (rows 22-23): shifted right for 3/4 perspective
    # ------------------------------------------------------------------
    # Upper lip (row 22): 5px wide, cols 15-19
    for x in range(15, 20):
        pixels.append((x, 22, lip_color))

    # Lower lip (row 23): 4px wide with center highlight, cols 15-18
    for x in range(15, 19):
        pixels.append((x, 23, lip_color))
    pixels.append((16, 23, lip_hi))
    pixels.append((17, 23, lip_hi))

    # ------------------------------------------------------------------
    # Neck (row 26) -- 6px wide centered (cols 13-18)
    # ------------------------------------------------------------------
    for x in range(13, 19):
        pixels.append((x, 26, skin_base))
    pixels.append((13, 26, skin_shadow))
    pixels.append((18, 26, skin_shadow))

    # ------------------------------------------------------------------
    # Collar (row 27): 20px centered (cols 6-25)
    # ------------------------------------------------------------------
    for x in range(6, 26):
        pixels.append((x, 27, outfit))
    pixels.append((15, 27, outfit_shadow))
    pixels.append((16, 27, outfit_shadow))
    # V-neckline opening
    pixels.append((14, 27, skin_shadow))
    pixels.append((17, 27, skin_shadow))

    # ------------------------------------------------------------------
    # Outfit (rows 28-31) -- widening to fill full canvas
    # ------------------------------------------------------------------
    # Row 28: 26px (cols 3-28)
    for x in range(3, 29):
        pixels.append((x, 28, outfit))
    pixels.append((3, 28, outfit_hi))
    pixels.append((28, 28, outfit_shadow))
    pixels.append((15, 28, outfit_shadow))
    pixels.append((16, 28, outfit_shadow))

    # Row 29: 30px (cols 1-30)
    for x in range(1, 31):
        pixels.append((x, 29, outfit))
    pixels.append((1, 29, outfit_hi))
    pixels.append((30, 29, outfit_shadow))
    # Fabric fold shadow
    pixels.append((12, 29, outfit_shadow))
    pixels.append((19, 29, outfit_shadow))

    # Row 30: full width (cols 0-31)
    for x in range(0, 32):
        pixels.append((x, 30, outfit))
    pixels.append((0, 30, outfit_hi))
    pixels.append((31, 30, outfit_shadow))

    # Row 31: full width (cols 0-31)
    for x in range(0, 32):
        pixels.append((x, 31, outfit))
    pixels.append((0, 31, outfit_hi))
    pixels.append((31, 31, outfit_shadow))
    # Fabric fold shadow
    pixels.append((10, 31, outfit_shadow))
    pixels.append((21, 31, outfit_shadow))

    # ------------------------------------------------------------------
    # Glasses overlay (on eye rows 14-19, 6 rows matching new eye zone)
    # Left lens frame: cols 2-12, Right lens frame: cols 19-29
    # Bridge at rows 15-16 cols 12-19
    # ------------------------------------------------------------------
    if has_glasses:
        # Row 14: full frame top
        for x in range(2, 13):
            pixels.append((x, 14, _GLASSES_FRAME))
        for x in range(19, 30):
            pixels.append((x, 14, _GLASSES_FRAME))

        # Rows 15-18: frame sides + lens fill inside
        for y in range(15, 19):
            # Left lens
            pixels.append((2, y, _GLASSES_FRAME))
            pixels.append((12, y, _GLASSES_FRAME))
            # Right lens
            pixels.append((19, y, _GLASSES_FRAME))
            pixels.append((29, y, _GLASSES_FRAME))

        # Row 19: full frame bottom
        for x in range(2, 13):
            pixels.append((x, 19, _GLASSES_FRAME))
        for x in range(19, 30):
            pixels.append((x, 19, _GLASSES_FRAME))

        # Bridge: cols 12-19, rows 15-16
        for y in (15, 16):
            for x in range(12, 20):
                pixels.append((x, y, _GLASSES_FRAME))

        # Lens tint: blend eye pixels inside frame with lens color
        # Left lens interior: cols 3-11, rows 15-18
        for y in range(15, 19):
            for x in range(3, 12):
                pixels.append(
                    (
                        x,
                        y,
                        blend_colors(_get_last_color(pixels, x, y), _GLASSES_LENS, 0.3),
                    )
                )
        # Right lens interior: cols 20-28, rows 15-18
        for y in range(15, 19):
            for x in range(20, 29):
                pixels.append(
                    (
                        x,
                        y,
                        blend_colors(_get_last_color(pixels, x, y), _GLASSES_LENS, 0.3),
                    )
                )

        # Re-draw the core eye details through the tinted lens
        # Left eye key features (tinted)
        pixels.append((4, 15, blend_colors(ir["catchlight"], _GLASSES_LENS, 0.3)))
        pixels.append((5, 15, blend_colors(ir["catchlight"], _GLASSES_LENS, 0.3)))
        pixels.append((6, 15, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((7, 15, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((6, 17, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        pixels.append((7, 17, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        pixels.append((8, 17, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        # Right eye key features (tinted)
        pixels.append((26, 15, blend_colors(ir["catchlight"], _GLASSES_LENS, 0.3)))
        pixels.append((27, 15, blend_colors(ir["catchlight"], _GLASSES_LENS, 0.3)))
        pixels.append((24, 15, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((25, 15, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((23, 17, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        pixels.append((24, 17, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        pixels.append((25, 17, blend_colors(pupil, _GLASSES_LENS, 0.3)))

        # Lens highlight: 1px at upper-left of each lens
        pixels.append((3, 15, _GLASSES_LENS_HIGHLIGHT))
        pixels.append((20, 15, _GLASSES_LENS_HIGHLIGHT))

    # ------------------------------------------------------------------
    # Hair layer (painted last so it overlaps skin/forehead)
    # ------------------------------------------------------------------
    builder = _HAIR_BUILDERS.get(hair_style)
    if builder:
        pixels.extend(builder(hair_color, skin))

    return pixels


def _get_last_color(pixels: list[tuple[int, int, str]], x: int, y: int) -> str:
    """Find the last color set for a given coordinate in the pixel list."""
    for px, py, color in reversed(pixels):
        if px == x and py == y:
            return color
    return "#000000"


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------


def _build_rects(pixels: list[tuple[int, int, str]]) -> str:
    """De-duplicate pixels (later wins) and return a joined string of ``<rect>`` elements."""
    seen: dict[tuple[int, int], str] = {}
    for x, y, c in pixels:
        seen[(x, y)] = c
    parts: list[str] = []
    for (x, y), c in sorted(seen.items()):
        parts.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>')
    return "".join(parts)


def render_avatar_svg(avatar_id: str, size: int = 32) -> str:
    """Return an inline SVG string for the given avatar.

    The SVG uses a 32x32 ``viewBox`` and renders at the specified *size*
    in device pixels.  The ``image-rendering: pixelated`` style keeps the
    pixel art crisp when scaled.
    """
    avatar_def = AVATAR_CATALOG.get(avatar_id)
    if avatar_def is None:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"'
            f' width="{size}" height="{size}"'
            f' style="image-rendering: pixelated;">'
            f'<rect width="32" height="32" fill="#ccc"/>'
            f'<text x="16" y="24" text-anchor="middle"'
            f' font-size="18" fill="#666">?</text>'
            f"</svg>"
        )

    rect_block = _build_rects(_build_avatar_pixels(avatar_def))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"'
        f' width="{size}" height="{size}"'
        f' class="pixel-icon" role="img" aria-hidden="true"'
        f' style="image-rendering: pixelated;">'
        f"{rect_block}"
        f"</svg>"
    )


def render_avatar_svg_bare(avatar_id: str) -> str | None:
    """Return a bare SVG string (no width/height/class/style) for static files.

    Returns ``None`` if *avatar_id* is not in the catalog.
    """
    avatar_def = AVATAR_CATALOG.get(avatar_id)
    if avatar_def is None:
        return None

    rect_block = _build_rects(_build_avatar_pixels(avatar_def))

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{rect_block}</svg>'


# ---------------------------------------------------------------------------
# Avatar picker helpers
# ---------------------------------------------------------------------------


def get_avatar_choices() -> list[dict[str, str]]:
    """Return a list of avatar choices for a picker UI."""
    return [
        {"id": avatar_id, "name": meta["name"], "description": meta["description"]}
        for avatar_id, meta in AVATAR_CATALOG.items()
    ]
