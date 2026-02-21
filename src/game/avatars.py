"""Golden Sun: The Lost Age style pixel art librarian avatar system.

Provides 12 custom 32x32 pixel art librarian avatars rendered as inline SVG.
Each avatar is built programmatically as a shoulders-up portrait with GBA-era
fidelity: 5-row expressive eyes with catchlights, 5-tone skin shading, strand-
level hair detail using full color ramps, and contoured outfit rendering.
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
            "An auburn-curled storyteller draped in deep purple,"
            " always midway through a tale."
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
            "A bespectacled navigator in crisp navy, head shining"
            " bright beneath the stacks."
        ),
        "skin_tone": "#C68642",
        "hair_style": "bald",
        "hair_color": None,
        "glasses": True,
        "outfit_color": "#1A237E",
    },
    "avatar_04": {
        "name": "Margot",
        "description": (
            "Long golden hair flowing over a burgundy coat,"
            " a quiet corner reader."
        ),
        "skin_tone": "#F5D0A9",
        "hair_style": "long_straight",
        "hair_color": "#F0E68C",
        "glasses": False,
        "outfit_color": "#7B1FA2",
    },
    "avatar_05": {
        "name": "Coda",
        "description": (
            "A confident reader in teal with a neat afro,"
            " always finishing strong."
        ),
        "skin_tone": "#3C1F0A",
        "hair_style": "short_afro",
        "hair_color": "#1A1A1A",
        "glasses": False,
        "outfit_color": "#00695C",
    },
    "avatar_06": {
        "name": "Verso",
        "description": (
            "Blue-mohawked rebel librarian in bold red,"
            " always turning the page."
        ),
        "skin_tone": "#E0AC69",
        "hair_style": "mohawk",
        "hair_color": "#1976D2",
        "glasses": False,
        "outfit_color": "#C62828",
    },
    "avatar_07": {
        "name": "Octavia",
        "description": (
            "Braided hair and golden outfit, always peering through"
            " glasses at the fine print."
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
            "Red ponytail bouncing above a cool slate jacket,"
            " the reference desk regular."
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
            "Purple bob cut framing a curious face above olive green,"
            " drawn to poetry."
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
            "Sharp undercut and glasses over a charcoal coat,"
            " the meticulous note-taker."
        ),
        "skin_tone": "#8D5524",
        "hair_style": "undercut",
        "hair_color": "#1A1A1A",
        "glasses": True,
        "outfit_color": "#37474F",
    },
    "avatar_11": {
        "name": "Sable",
        "description": (
            "Long locs cascading over an emerald tunic,"
            " keeper of rare volumes."
        ),
        "skin_tone": "#3C1F0A",
        "hair_style": "locs",
        "hair_color": "#3E2723",
        "glasses": False,
        "outfit_color": "#1B5E20",
    },
    "avatar_12": {
        "name": "Bindery",
        "description": (
            "Green spiky hair and a pink outfit,"
            " the wildcard cataloger."
        ),
        "skin_tone": "#F5D0A9",
        "hair_style": "spiky",
        "hair_color": "#2E7D32",
        "glasses": False,
        "outfit_color": "#E91E63",
    },
}


# ---------------------------------------------------------------------------
# Hair pattern helpers -- each returns a list of (x, y, color) pixels
# Coordinates for 32x32 canvas.  Face spans columns 6-25.
# Hair zone is rows 0-6 with hairline shadow at row 6-7 boundary.
# All non-bald builders use 5-tone ramp from _hair_ramp().
# ---------------------------------------------------------------------------


def _hair_short_cropped(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Short cropped hair: graduated tone rows 0-6, cols 7-25."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Map each row to a dominant tone for graduated shading
    row_tones = [
        r["highlight"],
        r["light"],
        r["light"],
        r["base"],
        r["base"],
        r["shadow"],
        r["deep_shadow"],
    ]

    # Row 0: narrow top
    for x in range(9, 23):
        pixels.append((x, 0, row_tones[0]))
    # Highlight accents
    pixels.append((12, 0, r["highlight"]))
    pixels.append((18, 0, r["highlight"]))

    # Row 1: wider
    for x in range(7, 25):
        pixels.append((x, 1, row_tones[1]))
    pixels.append((10, 1, r["highlight"]))
    pixels.append((15, 1, r["highlight"]))
    pixels.append((20, 1, r["highlight"]))

    # Row 2: full coverage
    for x in range(7, 25):
        pixels.append((x, 2, row_tones[2]))
    pixels.append((9, 2, r["highlight"]))
    pixels.append((14, 2, r["highlight"]))
    pixels.append((19, 2, r["highlight"]))
    pixels.append((7, 2, r["shadow"]))
    pixels.append((24, 2, r["shadow"]))

    # Row 3: full coverage
    for x in range(7, 25):
        pixels.append((x, 3, row_tones[3]))
    pixels.append((11, 3, r["light"]))
    pixels.append((16, 3, r["light"]))
    pixels.append((21, 3, r["light"]))
    pixels.append((7, 3, r["shadow"]))
    pixels.append((24, 3, r["shadow"]))

    # Row 4
    for x in range(7, 25):
        pixels.append((x, 4, row_tones[4]))
    pixels.append((10, 4, r["light"]))
    pixels.append((17, 4, r["light"]))
    pixels.append((7, 4, r["shadow"]))
    pixels.append((24, 4, r["shadow"]))

    # Row 5
    for x in range(7, 25):
        pixels.append((x, 5, row_tones[5]))
    pixels.append((12, 5, r["base"]))
    pixels.append((19, 5, r["base"]))

    # Row 6: deep shadow fringe
    for x in range(8, 24):
        pixels.append((x, 6, row_tones[6]))
    pixels.append((13, 6, r["shadow"]))
    pixels.append((18, 6, r["shadow"]))

    # Hairline shadow at row 7
    for x in range(9, 23):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_curly(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Curly hair: 2x2 curl clusters with volume, rows 0-6 + side puffs."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row 0: puff top
    for x in range(8, 24):
        pixels.append((x, 0, r["base"]))
    # Curl highlights in 2x2 blocks
    for cx in (10, 14, 18, 22):
        pixels.append((cx, 0, r["highlight"]))

    # Row 1: wider puff
    for x in range(5, 27):
        pixels.append((x, 1, r["base"]))
    for cx in (7, 11, 15, 19, 23):
        pixels.append((cx, 1, r["highlight"]))
    pixels.append((5, 1, r["deep_shadow"]))
    pixels.append((26, 1, r["deep_shadow"]))

    # Row 2: full volume
    for x in range(4, 28):
        pixels.append((x, 2, r["base"]))
    # 2x2 curl clusters: upper-left = highlight, lower-right = shadow
    for cx in (6, 10, 14, 18, 22, 26):
        pixels.append((cx, 2, r["highlight"]))
        if cx + 1 < 28:
            pixels.append((cx + 1, 2, r["light"]))
    pixels.append((4, 2, r["deep_shadow"]))
    pixels.append((27, 2, r["deep_shadow"]))

    # Row 3: full volume with shadow clusters
    for x in range(4, 28):
        pixels.append((x, 3, r["base"]))
    for cx in (6, 10, 14, 18, 22, 26):
        pixels.append((cx, 3, r["shadow"]))
        if cx + 1 < 28:
            pixels.append((cx + 1, 3, r["deep_shadow"]))
    pixels.append((4, 3, r["deep_shadow"]))
    pixels.append((27, 3, r["deep_shadow"]))

    # Row 4: still wide
    for x in range(5, 27):
        pixels.append((x, 4, r["base"]))
    for cx in (7, 11, 15, 19, 23):
        pixels.append((cx, 4, r["highlight"]))
        if cx + 1 < 27:
            pixels.append((cx + 1, 4, r["light"]))
    pixels.append((5, 4, r["shadow"]))
    pixels.append((26, 4, r["shadow"]))

    # Row 5: narrowing
    for x in range(5, 27):
        pixels.append((x, 5, r["shadow"]))
    for cx in (8, 12, 16, 20, 24):
        pixels.append((cx, 5, r["base"]))

    # Row 6: bottom fringe
    for x in range(6, 26):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((10, 6, r["shadow"]))
    pixels.append((16, 6, r["shadow"]))
    pixels.append((22, 6, r["shadow"]))

    # Side volume puffs rows 5-8
    for y in range(5, 9):
        for dx in (3, 4, 5):
            pixels.append((dx, y, r["base"] if y < 7 else r["shadow"]))
        for dx in (26, 27, 28):
            pixels.append((dx, y, r["base"] if y < 7 else r["shadow"]))
        # Outer edge = deep_shadow
        pixels.append((3, y, r["deep_shadow"]))
        pixels.append((28, y, r["deep_shadow"]))
        # Curl texture
        if y % 2 == 0:
            pixels.append((4, y, r["highlight"]))
            pixels.append((27, y, r["highlight"]))

    # Hairline shadow
    for x in range(7, 25):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_bald(
    hair_color: str | None, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Bald: specular highlight arc at crown rows 0-2."""
    pixels: list[tuple[int, int, str]] = []
    near_white = lighten(skin_tone, 0.40)
    bright = lighten(skin_tone, 0.25)
    subtle = lighten(skin_tone, 0.15)

    # Row 0: narrow crown highlight
    for x in range(13, 19):
        pixels.append((x, 0, near_white))
    # Row 1: wider bright arc
    for x in range(12, 20):
        pixels.append((x, 1, bright))
    pixels.append((14, 1, "#FFFFFF"))
    pixels.append((15, 1, "#FFFFFF"))
    pixels.append((16, 1, "#FFFFFF"))
    pixels.append((17, 1, "#FFFFFF"))
    # Row 2: subtle glow
    for x in range(11, 21):
        pixels.append((x, 2, subtle))
    pixels.append((14, 2, bright))
    pixels.append((15, 2, bright))
    pixels.append((16, 2, bright))
    pixels.append((17, 2, bright))

    return pixels


def _hair_long_straight(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Long straight hair with strand lines, rows 0-6 top + side curtains."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row 0: narrow top
    for x in range(9, 23):
        pixels.append((x, 0, r["base"]))
    # Strand highlights every 3rd col
    for x in range(9, 23, 3):
        pixels.append((x, 0, r["highlight"]))

    # Row 1: wider
    for x in range(7, 25):
        pixels.append((x, 1, r["base"]))
    for x in range(7, 25, 3):
        pixels.append((x, 1, r["highlight"]))
    for x in range(8, 25, 3):
        pixels.append((x, 1, r["shadow"]))

    # Row 2: full
    for x in range(6, 26):
        pixels.append((x, 2, r["base"]))
    for x in range(6, 26, 3):
        pixels.append((x, 2, r["highlight"]))
    for x in range(7, 26, 3):
        pixels.append((x, 2, r["shadow"]))

    # Row 3: full
    for x in range(5, 27):
        pixels.append((x, 3, r["base"]))
    for x in range(5, 27, 3):
        pixels.append((x, 3, r["light"]))
    pixels.append((5, 3, r["deep_shadow"]))
    pixels.append((26, 3, r["deep_shadow"]))

    # Row 4
    for x in range(5, 27):
        pixels.append((x, 4, r["base"]))
    for x in range(5, 27, 3):
        pixels.append((x, 4, r["highlight"]))
    pixels.append((5, 4, r["shadow"]))
    pixels.append((26, 4, r["shadow"]))

    # Row 5
    for x in range(5, 27):
        pixels.append((x, 5, r["shadow"]))
    for x in range(6, 26, 3):
        pixels.append((x, 5, r["base"]))

    # Row 6: deep fringe
    for x in range(6, 26):
        pixels.append((x, 6, r["deep_shadow"]))
    for x in range(7, 25, 3):
        pixels.append((x, 6, r["shadow"]))

    # Side curtains cols 3-5 and 26-28 flowing to row 20
    for y in range(4, 21):
        for dx in (3, 4, 5):
            pixels.append((dx, y, r["base"]))
        for dx in (26, 27, 28):
            pixels.append((dx, y, r["base"]))
        # Strand lines: every 3rd row alternates
        if y % 3 == 0:
            pixels.append((3, y, r["highlight"]))
            pixels.append((28, y, r["highlight"]))
        elif y % 3 == 1:
            pixels.append((4, y, r["shadow"]))
            pixels.append((27, y, r["shadow"]))
        else:
            pixels.append((5, y, r["light"]))
            pixels.append((26, y, r["light"]))
        # Deep shadow on outer edges
        pixels.append((3, y, r["deep_shadow"] if y > 15 else r["shadow"]))
        pixels.append((28, y, r["deep_shadow"] if y > 15 else r["shadow"]))

    # Hairline shadow
    for x in range(7, 25):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_short_afro(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Short afro: dense texture with scattered highlight dots."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row 0: narrow top
    for x in range(9, 23):
        pixels.append((x, 0, r["base"]))
    # Scattered highlights 2-3px apart
    for x in (10, 13, 16, 19, 22):
        pixels.append((x, 0, r["highlight"]))

    # Row 1: wider
    for x in range(6, 26):
        pixels.append((x, 1, r["base"]))
    for x in (8, 11, 14, 17, 20, 23):
        pixels.append((x, 1, r["highlight"]))
    pixels.append((6, 1, r["deep_shadow"]))
    pixels.append((25, 1, r["deep_shadow"]))

    # Row 2: full round
    for x in range(5, 27):
        pixels.append((x, 2, r["base"]))
    for x in (7, 10, 13, 16, 19, 22, 25):
        pixels.append((x, 2, r["highlight"]))
    for x in (8, 12, 15, 18, 21, 24):
        pixels.append((x, 2, r["light"]))
    pixels.append((5, 2, r["deep_shadow"]))
    pixels.append((26, 2, r["deep_shadow"]))

    # Row 3: full round, dense texture
    for x in range(5, 27):
        pixels.append((x, 3, r["base"]))
    for x in (6, 9, 12, 15, 18, 21, 24):
        pixels.append((x, 3, r["highlight"]))
    for x in (7, 11, 14, 17, 20, 23):
        pixels.append((x, 3, r["shadow"]))
    pixels.append((5, 3, r["deep_shadow"]))
    pixels.append((26, 3, r["deep_shadow"]))

    # Row 4: still full
    for x in range(5, 27):
        pixels.append((x, 4, r["base"]))
    for x in (8, 11, 14, 17, 20, 23):
        pixels.append((x, 4, r["highlight"]))
    for x in (9, 13, 16, 19, 22):
        pixels.append((x, 4, r["light"]))

    # Row 5: bottom curve
    for x in range(6, 26):
        pixels.append((x, 5, r["shadow"]))
    for x in (8, 12, 16, 20, 24):
        pixels.append((x, 5, r["base"]))

    # Row 6: deep shadow fringe
    for x in range(7, 25):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((10, 6, r["shadow"]))
    pixels.append((16, 6, r["shadow"]))
    pixels.append((22, 6, r["shadow"]))

    # Side volume rows 5-8
    for y in range(5, 9):
        pixels.append((4, y, r["shadow"] if y < 7 else r["deep_shadow"]))
        pixels.append((5, y, r["base"] if y < 7 else r["shadow"]))
        pixels.append((26, y, r["base"] if y < 7 else r["shadow"]))
        pixels.append((27, y, r["shadow"] if y < 7 else r["deep_shadow"]))
        # Texture dots
        if y % 2 == 0:
            pixels.append((4, y, r["highlight"]))
            pixels.append((27, y, r["highlight"]))

    # Hairline shadow
    for x in range(8, 24):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_mohawk(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Tall mohawk with dramatic spikes, cols 10-21, rows 0-6."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Row 0: spike tips (highlight)
    pixels.append((12, 0, r["highlight"]))
    pixels.append((14, 0, r["highlight"]))
    pixels.append((16, 0, r["highlight"]))
    pixels.append((18, 0, r["highlight"]))
    pixels.append((20, 0, r["highlight"]))

    # Row 1: spike upper bodies (highlight -> light)
    for x in range(11, 21):
        pixels.append((x, 1, r["highlight"]))
    pixels.append((13, 1, r["light"]))
    pixels.append((15, 1, r["light"]))
    pixels.append((17, 1, r["light"]))
    pixels.append((19, 1, r["light"]))

    # Row 2: widening, base tone
    for x in range(10, 22):
        pixels.append((x, 2, r["light"]))
    pixels.append((12, 2, r["highlight"]))
    pixels.append((16, 2, r["highlight"]))
    pixels.append((20, 2, r["highlight"]))

    # Row 3: full strip, base
    for x in range(10, 22):
        pixels.append((x, 3, r["base"]))
    pixels.append((10, 3, r["shadow"]))
    pixels.append((21, 3, r["shadow"]))
    pixels.append((14, 3, r["light"]))
    pixels.append((18, 3, r["light"]))

    # Row 4: base -> shadow transition
    for x in range(10, 22):
        pixels.append((x, 4, r["base"]))
    pixels.append((10, 4, r["deep_shadow"]))
    pixels.append((21, 4, r["deep_shadow"]))
    pixels.append((13, 4, r["shadow"]))
    pixels.append((17, 4, r["shadow"]))

    # Row 5: shadow roots
    for x in range(11, 21):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((13, 5, r["base"]))
    pixels.append((17, 5, r["base"]))

    # Row 6: deep shadow base
    for x in range(11, 21):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((14, 6, r["shadow"]))
    pixels.append((18, 6, r["shadow"]))

    # Hairline shadow
    for x in range(12, 20):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_braids(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Braids: top coverage rows 0-6, two braid strips with interlocking texture."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-6
    for x in range(9, 23):
        pixels.append((x, 0, r["base"]))
    pixels.append((12, 0, r["highlight"]))
    pixels.append((18, 0, r["highlight"]))

    for x in range(7, 25):
        pixels.append((x, 1, r["base"]))
    pixels.append((9, 1, r["highlight"]))
    pixels.append((15, 1, r["highlight"]))
    pixels.append((21, 1, r["highlight"]))

    for x in range(6, 26):
        pixels.append((x, 2, r["base"]))
    pixels.append((8, 2, r["highlight"]))
    pixels.append((14, 2, r["light"]))
    pixels.append((20, 2, r["highlight"]))
    pixels.append((6, 2, r["shadow"]))
    pixels.append((25, 2, r["shadow"]))

    for x in range(6, 26):
        pixels.append((x, 3, r["base"]))
    pixels.append((10, 3, r["light"]))
    pixels.append((16, 3, r["light"]))
    pixels.append((22, 3, r["light"]))
    pixels.append((6, 3, r["deep_shadow"]))
    pixels.append((25, 3, r["deep_shadow"]))

    for x in range(6, 26):
        pixels.append((x, 4, r["shadow"]))
    pixels.append((9, 4, r["base"]))
    pixels.append((15, 4, r["base"]))
    pixels.append((21, 4, r["base"]))

    for x in range(7, 25):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((11, 5, r["base"]))
    pixels.append((17, 5, r["base"]))

    for x in range(8, 24):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((12, 6, r["shadow"]))
    pixels.append((18, 6, r["shadow"]))

    # Braid strips cols 3-5 and 26-28 with interlocking 2px braid texture
    for y in range(5, 26):
        # Left braid
        pixels.append((3, y, r["base"]))
        pixels.append((4, y, r["base"]))
        pixels.append((5, y, r["base"]))
        # Right braid
        pixels.append((26, y, r["base"]))
        pixels.append((27, y, r["base"]))
        pixels.append((28, y, r["base"]))
        # Interlocking braid texture: alternating 2px bands
        band = y % 4
        if band == 0:
            pixels.append((3, y, r["highlight"]))
            pixels.append((4, y, r["light"]))
            pixels.append((27, y, r["light"]))
            pixels.append((28, y, r["highlight"]))
        elif band == 1:
            pixels.append((4, y, r["shadow"]))
            pixels.append((5, y, r["highlight"]))
            pixels.append((26, y, r["highlight"]))
            pixels.append((27, y, r["shadow"]))
        elif band == 2:
            pixels.append((3, y, r["shadow"]))
            pixels.append((5, y, r["light"]))
            pixels.append((26, y, r["light"]))
            pixels.append((28, y, r["shadow"]))
        else:
            pixels.append((4, y, r["deep_shadow"]))
            pixels.append((27, y, r["deep_shadow"]))

    # Braid tie accessories at tips
    tie_color = lighten(hair_color, 0.50)
    pixels.append((3, 26, tie_color))
    pixels.append((4, 26, tie_color))
    pixels.append((5, 26, tie_color))
    pixels.append((26, 26, tie_color))
    pixels.append((27, 26, tie_color))
    pixels.append((28, 26, tie_color))

    # Hairline shadow
    for x in range(8, 24):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_ponytail(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Ponytail: top coverage rows 0-6 + ponytail trailing right."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-6
    for x in range(9, 23):
        pixels.append((x, 0, r["base"]))
    pixels.append((12, 0, r["highlight"]))
    pixels.append((19, 0, r["highlight"]))

    for x in range(7, 25):
        pixels.append((x, 1, r["base"]))
    pixels.append((10, 1, r["highlight"]))
    pixels.append((16, 1, r["highlight"]))
    pixels.append((22, 1, r["highlight"]))

    for x in range(6, 26):
        pixels.append((x, 2, r["base"]))
    pixels.append((8, 2, r["highlight"]))
    pixels.append((15, 2, r["light"]))
    pixels.append((21, 2, r["highlight"]))

    for x in range(6, 26):
        pixels.append((x, 3, r["base"]))
    pixels.append((6, 3, r["deep_shadow"]))
    pixels.append((25, 3, r["deep_shadow"]))
    pixels.append((10, 3, r["light"]))
    pixels.append((17, 3, r["light"]))

    for x in range(6, 26):
        pixels.append((x, 4, r["shadow"]))
    pixels.append((9, 4, r["base"]))
    pixels.append((14, 4, r["base"]))

    for x in range(7, 25):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((11, 5, r["base"]))
    pixels.append((18, 5, r["base"]))

    for x in range(8, 24):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((12, 6, r["shadow"]))
    pixels.append((19, 6, r["shadow"]))

    # Ponytail trailing right: cols 27-30, rows 3-13
    # Hair tie at row 4
    tie_color = darken(hair_color, 0.40)
    for y in range(3, 14):
        for dx in (27, 28, 29):
            if dx <= 31:
                pixels.append((dx, y, r["base"]))
        if y < 31:
            pixels.append((30, y, r["base"]))
        # Curvature shading
        if y % 3 == 0:
            pixels.append((28, y, r["highlight"]))
        elif y % 3 == 1:
            pixels.append((27, y, r["shadow"]))
        if y > 9:
            pixels.append((30, y, r["shadow"]))

    # Hair tie detail at row 4
    pixels.append((27, 4, tie_color))
    pixels.append((28, 4, tie_color))
    pixels.append((29, 4, tie_color))
    pixels.append((30, 4, tie_color))

    # Taper at bottom
    pixels.append((28, 13, r["deep_shadow"]))
    pixels.append((29, 13, r["deep_shadow"]))

    # Hairline shadow
    for x in range(8, 24):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_bob_cut(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Bob cut: top coverage rows 0-6 + side panels with inward curl at tips."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-6
    for x in range(9, 23):
        pixels.append((x, 0, r["base"]))
    pixels.append((12, 0, r["highlight"]))
    pixels.append((18, 0, r["highlight"]))

    for x in range(7, 25):
        pixels.append((x, 1, r["base"]))
    pixels.append((9, 1, r["highlight"]))
    pixels.append((15, 1, r["highlight"]))
    pixels.append((21, 1, r["highlight"]))

    for x in range(6, 26):
        pixels.append((x, 2, r["base"]))
    pixels.append((8, 2, r["highlight"]))
    pixels.append((14, 2, r["light"]))
    pixels.append((20, 2, r["highlight"]))

    for x in range(5, 27):
        pixels.append((x, 3, r["base"]))
    pixels.append((5, 3, r["deep_shadow"]))
    pixels.append((26, 3, r["deep_shadow"]))

    for x in range(5, 27):
        pixels.append((x, 4, r["shadow"]))
    pixels.append((9, 4, r["base"]))
    pixels.append((15, 4, r["base"]))
    pixels.append((21, 4, r["base"]))

    for x in range(6, 26):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((10, 5, r["base"]))
    pixels.append((17, 5, r["base"]))

    for x in range(6, 26):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((12, 6, r["shadow"]))
    pixels.append((19, 6, r["shadow"]))

    # Side panels (cols 3-6, 25-28) rows 4-18 with graduated shading
    for y in range(4, 19):
        # Left panel: inner=shadow, outer=highlight
        pixels.append((3, y, r["shadow"]))
        pixels.append((4, y, r["base"]))
        pixels.append((5, y, r["light"]))
        pixels.append((6, y, r["highlight"] if y % 3 == 0 else r["light"]))
        # Right panel: mirrored
        pixels.append((25, y, r["highlight"] if y % 3 == 0 else r["light"]))
        pixels.append((26, y, r["light"]))
        pixels.append((27, y, r["base"]))
        pixels.append((28, y, r["shadow"]))
        # Deeper shadow at outer edges as panels go lower
        if y > 12:
            pixels.append((3, y, r["deep_shadow"]))
            pixels.append((28, y, r["deep_shadow"]))

    # Inward curl at tips (row 18-19)
    pixels.append((4, 18, r["deep_shadow"]))
    pixels.append((5, 18, r["shadow"]))
    pixels.append((6, 18, r["base"]))
    pixels.append((7, 18, r["light"]))
    pixels.append((25, 18, r["light"]))
    pixels.append((26, 18, r["base"]))
    pixels.append((27, 18, r["shadow"]))
    pixels.append((28, 18, r["deep_shadow"]))
    # Row 19: inner curl tips
    pixels.append((5, 19, r["deep_shadow"]))
    pixels.append((6, 19, r["shadow"]))
    pixels.append((7, 19, r["base"]))
    pixels.append((25, 19, r["base"]))
    pixels.append((26, 19, r["shadow"]))
    pixels.append((27, 19, r["deep_shadow"]))

    # Hairline shadow
    for x in range(7, 25):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_undercut(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Undercut: dramatic swept top rows 0-5 with bold highlights, shaved sides."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Dramatic swept top rows 0-5
    for x in range(7, 23):
        pixels.append((x, 0, r["base"]))
    pixels.append((10, 0, r["highlight"]))
    pixels.append((14, 0, r["highlight"]))
    pixels.append((18, 0, r["highlight"]))

    for x in range(6, 25):
        pixels.append((x, 1, r["base"]))
    pixels.append((8, 1, r["highlight"]))
    pixels.append((12, 1, r["highlight"]))
    pixels.append((16, 1, r["highlight"]))
    pixels.append((20, 1, r["highlight"]))
    pixels.append((24, 1, r["light"]))

    for x in range(5, 26):
        pixels.append((x, 2, r["base"]))
    pixels.append((7, 2, r["highlight"]))
    pixels.append((11, 2, r["highlight"]))
    pixels.append((15, 2, r["highlight"]))
    pixels.append((19, 2, r["highlight"]))
    pixels.append((23, 2, r["light"]))

    for x in range(5, 27):
        pixels.append((x, 3, r["base"]))
    pixels.append((6, 3, r["highlight"]))
    pixels.append((10, 3, r["highlight"]))
    pixels.append((14, 3, r["highlight"]))
    pixels.append((18, 3, r["highlight"]))
    pixels.append((22, 3, r["light"]))
    pixels.append((26, 3, r["shadow"]))

    for x in range(6, 27):
        pixels.append((x, 4, r["base"]))
    pixels.append((8, 4, r["highlight"]))
    pixels.append((12, 4, r["highlight"]))
    pixels.append((16, 4, r["highlight"]))
    pixels.append((20, 4, r["light"]))
    pixels.append((24, 4, r["light"]))

    for x in range(7, 25):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((10, 5, r["base"]))
    pixels.append((15, 5, r["base"]))
    pixels.append((20, 5, r["base"]))

    # Shaved sides rows 5-7: deep_shadow stubble dots
    for y in range(5, 8):
        for x in (5, 6):
            pixels.append((x, y, r["deep_shadow"]))
        for x in (26, 27):
            pixels.append((x, y, r["deep_shadow"]))
        # Stubble texture dots (alternate)
        if y % 2 == 0:
            pixels.append((5, y, darken(hair_color, 0.60)))
            pixels.append((27, y, darken(hair_color, 0.60)))
        else:
            pixels.append((6, y, darken(hair_color, 0.60)))
            pixels.append((26, y, darken(hair_color, 0.60)))

    # Hairline shadow
    for x in range(8, 24):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_locs(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Locs: top coverage rows 0-6, individual 2px strands on sides."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Top coverage rows 0-6
    for x in range(9, 23):
        pixels.append((x, 0, r["base"]))
    pixels.append((12, 0, r["highlight"]))
    pixels.append((18, 0, r["highlight"]))

    for x in range(7, 25):
        pixels.append((x, 1, r["base"]))
    pixels.append((9, 1, r["highlight"]))
    pixels.append((15, 1, r["highlight"]))
    pixels.append((21, 1, r["highlight"]))

    for x in range(6, 26):
        pixels.append((x, 2, r["base"]))
    pixels.append((8, 2, r["highlight"]))
    pixels.append((14, 2, r["light"]))
    pixels.append((20, 2, r["highlight"]))
    pixels.append((6, 2, r["shadow"]))
    pixels.append((25, 2, r["shadow"]))

    for x in range(6, 26):
        pixels.append((x, 3, r["base"]))
    pixels.append((10, 3, r["light"]))
    pixels.append((16, 3, r["light"]))
    pixels.append((22, 3, r["light"]))
    pixels.append((6, 3, r["deep_shadow"]))
    pixels.append((25, 3, r["deep_shadow"]))

    for x in range(6, 26):
        pixels.append((x, 4, r["shadow"]))
    pixels.append((9, 4, r["base"]))
    pixels.append((15, 4, r["base"]))
    pixels.append((21, 4, r["base"]))

    for x in range(7, 25):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((11, 5, r["base"]))
    pixels.append((17, 5, r["base"]))

    for x in range(8, 24):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((12, 6, r["shadow"]))
    pixels.append((18, 6, r["shadow"]))

    # Individual 2px-wide loc strands on sides, rows 5-22
    # Left side locs: cols 3-5
    for y in range(5, 23):
        pixels.append((3, y, r["base"]))
        pixels.append((4, y, r["base"]))
        pixels.append((5, y, r["base"]))
        # Alternating tone bands for loc texture
        band = y % 3
        if band == 0:
            pixels.append((3, y, r["highlight"]))
            pixels.append((4, y, r["light"]))
        elif band == 1:
            pixels.append((4, y, r["shadow"]))
            pixels.append((5, y, r["light"]))
        else:
            pixels.append((3, y, r["shadow"]))
            pixels.append((5, y, r["deep_shadow"]))
        # Overlap shadow between strands
        if y % 4 == 0:
            pixels.append((3, y, r["deep_shadow"]))

    # Right side locs: cols 26-28
    for y in range(5, 23):
        pixels.append((26, y, r["base"]))
        pixels.append((27, y, r["base"]))
        pixels.append((28, y, r["base"]))
        band = y % 3
        if band == 0:
            pixels.append((27, y, r["light"]))
            pixels.append((28, y, r["highlight"]))
        elif band == 1:
            pixels.append((26, y, r["light"]))
            pixels.append((27, y, r["shadow"]))
        else:
            pixels.append((26, y, r["deep_shadow"]))
            pixels.append((28, y, r["shadow"]))
        if y % 4 == 2:
            pixels.append((28, y, r["deep_shadow"]))

    # Loc tips
    pixels.append((3, 22, r["deep_shadow"]))
    pixels.append((4, 22, r["deep_shadow"]))
    pixels.append((5, 22, r["deep_shadow"]))
    pixels.append((26, 22, r["deep_shadow"]))
    pixels.append((27, 22, r["deep_shadow"]))
    pixels.append((28, 22, r["deep_shadow"]))

    # Hairline shadow
    for x in range(8, 24):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

    return pixels


def _hair_spiky(
    hair_color: str, skin_tone: str
) -> list[tuple[int, int, str]]:
    """Spiky hair: defined triangular spikes with dark gaps between."""
    pixels: list[tuple[int, int, str]] = []
    r = _hair_ramp(hair_color)

    # Spike tips at row 0 (highlight)
    spike_tips = [7, 11, 15, 19, 23, 27]
    for x in spike_tips:
        if x <= 31:
            pixels.append((x, 0, r["highlight"]))

    # Row 1: spike upper bodies + gaps
    for x in range(5, 28):
        pixels.append((x, 1, r["base"]))
    # Spike tips still bright
    for sx in spike_tips:
        if sx <= 27:
            pixels.append((sx, 1, r["highlight"]))
            if sx - 1 >= 5:
                pixels.append((sx - 1, 1, r["light"]))
            if sx + 1 <= 27:
                pixels.append((sx + 1, 1, r["light"]))
    # Dark gaps between spikes
    for gx in (9, 13, 17, 21, 25):
        pixels.append((gx, 1, r["deep_shadow"]))

    # Row 2: wider base
    for x in range(5, 28):
        pixels.append((x, 2, r["base"]))
    for sx in (7, 11, 15, 19, 23):
        pixels.append((sx, 2, r["highlight"]))
    for gx in (9, 13, 17, 21, 25):
        pixels.append((gx, 2, r["shadow"]))
    pixels.append((5, 2, r["deep_shadow"]))
    pixels.append((27, 2, r["deep_shadow"]))

    # Row 3: solid base
    for x in range(5, 28):
        pixels.append((x, 3, r["base"]))
    pixels.append((8, 3, r["light"]))
    pixels.append((12, 3, r["light"]))
    pixels.append((16, 3, r["light"]))
    pixels.append((20, 3, r["light"]))
    pixels.append((24, 3, r["light"]))
    pixels.append((5, 3, r["deep_shadow"]))
    pixels.append((27, 3, r["deep_shadow"]))

    # Row 4: base with shadow edges
    for x in range(6, 27):
        pixels.append((x, 4, r["base"]))
    pixels.append((9, 4, r["light"]))
    pixels.append((15, 4, r["light"]))
    pixels.append((21, 4, r["light"]))
    pixels.append((6, 4, r["shadow"]))
    pixels.append((26, 4, r["shadow"]))

    # Row 5: shadow layer
    for x in range(7, 26):
        pixels.append((x, 5, r["shadow"]))
    pixels.append((10, 5, r["base"]))
    pixels.append((16, 5, r["base"]))
    pixels.append((22, 5, r["base"]))

    # Row 6: deep shadow fringe
    for x in range(8, 25):
        pixels.append((x, 6, r["deep_shadow"]))
    pixels.append((12, 6, r["shadow"]))
    pixels.append((18, 6, r["shadow"]))

    # Hairline shadow
    for x in range(9, 23):
        pixels.append((x, 7, darken(skin_tone, 0.08)))

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

    Golden Sun: The Lost Age style with 5-row expressive eyes, 5-tone skin
    shading, and detailed outfit rendering.

    The portrait occupies the full 32x32 grid:
      Rows 0-6:   Hair zone (skin base, overwritten by hair)
      Row 7:      Forehead / hair-skin transition (skin_highlight)
      Row 8:      Eyebrows (5px tapered, thinner)
      Rows 9-13:  Eyes (5 rows tall -- the centerpiece)
      Row 14:     Cheeks / blush
      Row 15:     Nose (1 row, 2px subtle shadow dot)
      Rows 16-17: Mouth (6px upper lip, 4px lower lip w/ center highlight)
      Rows 18-19: Chin/jaw (contoured taper with 5-tone shading)
      Rows 20-21: Neck
      Rows 22-23: Collar / neckline detail
      Rows 24-31: Shoulders + outfit (8 rows)
    Face spans columns 6-25 (20px wide).
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
    pupil = "#1A1A1A"

    # Outfit shading
    outfit_shadow = darken(outfit, 0.3)
    outfit_hi = lighten(outfit, 0.15)

    pixels: list[tuple[int, int, str]] = []

    # ------------------------------------------------------------------
    # Head skin base (rows 0-19)
    # Rows 0-6 will mostly be overwritten by hair.
    # ------------------------------------------------------------------

    # Rows 0-6: skin base under hair zone
    for y in range(0, 7):
        for x in range(6, 26):
            pixels.append((x, y, skin_base))

    # Row 7: forehead / hair-skin transition
    for x in range(6, 26):
        pixels.append((x, 7, skin_hi))

    # Row 8: eyebrow row -- skin base
    for x in range(6, 26):
        pixels.append((x, 8, skin_base))

    # Eyebrows: 5px tapered
    # Left brow: cols 8-12 (tapered: thin at outer edges)
    pixels.append((8, 8, darken(brow_color, 0.15)))
    for x in range(9, 13):
        pixels.append((x, 8, brow_color))
    # Right brow: cols 19-23
    for x in range(19, 23):
        pixels.append((x, 8, brow_color))
    pixels.append((23, 8, darken(brow_color, 0.15)))

    # ------------------------------------------------------------------
    # Eyes (rows 9-13) -- 5 rows tall, 7px wide per eye
    # Left eye cols 7-13, Right eye cols 18-24
    # ------------------------------------------------------------------

    # Skin base for eye rows
    for y in range(9, 14):
        for x in range(6, 26):
            pixels.append((x, y, skin_base))

    # --- Row 9: thick dark upper lid (eyelash line) ---
    for x in range(7, 14):
        pixels.append((x, 9, eyelash))
    for x in range(18, 25):
        pixels.append((x, 9, eyelash))

    # --- Row 10: sclera + iris highlight + catchlight ---
    # Left eye: cols 7-13
    pixels.append((7, 10, sclera))
    pixels.append((8, 10, sclera))
    pixels.append((9, 10, ir["catchlight"]))  # catchlight
    pixels.append((10, 10, ir["highlight"]))
    pixels.append((11, 10, ir["highlight"]))
    pixels.append((12, 10, sclera))
    pixels.append((13, 10, sclera))
    # Right eye: cols 18-24 (mirrored, catchlight at col 20)
    pixels.append((18, 10, sclera))
    pixels.append((19, 10, sclera))
    pixels.append((20, 10, ir["catchlight"]))  # catchlight
    pixels.append((21, 10, ir["highlight"]))
    pixels.append((22, 10, ir["highlight"]))
    pixels.append((23, 10, sclera))
    pixels.append((24, 10, sclera))

    # --- Row 11: sclera + iris base + pupil ---
    # Left eye
    pixels.append((7, 11, sclera))
    pixels.append((8, 11, sclera))
    pixels.append((9, 11, ir["base"]))
    pixels.append((10, 11, pupil))
    pixels.append((11, 11, ir["base"]))
    pixels.append((12, 11, sclera))
    pixels.append((13, 11, sclera))
    # Right eye
    pixels.append((18, 11, sclera))
    pixels.append((19, 11, sclera))
    pixels.append((20, 11, ir["base"]))
    pixels.append((21, 11, pupil))
    pixels.append((22, 11, ir["base"]))
    pixels.append((23, 11, sclera))
    pixels.append((24, 11, sclera))

    # --- Row 12: lower eye with iris shadow + sclera shadow ---
    # Left eye
    pixels.append((7, 12, skin_base))
    pixels.append((8, 12, sclera_shadow))
    pixels.append((9, 12, ir["shadow"]))
    pixels.append((10, 12, ir["shadow"]))
    pixels.append((11, 12, ir["shadow"]))
    pixels.append((12, 12, sclera_shadow))
    pixels.append((13, 12, skin_base))
    # Right eye
    pixels.append((18, 12, skin_base))
    pixels.append((19, 12, sclera_shadow))
    pixels.append((20, 12, ir["shadow"]))
    pixels.append((21, 12, ir["shadow"]))
    pixels.append((22, 12, ir["shadow"]))
    pixels.append((23, 12, sclera_shadow))
    pixels.append((24, 12, skin_base))

    # --- Row 13: under-eye shadow ---
    # Left eye
    pixels.append((7, 13, skin_base))
    pixels.append((8, 13, skin_shadow))
    pixels.append((9, 13, skin_shadow))
    pixels.append((10, 13, skin_shadow))
    pixels.append((11, 13, skin_shadow))
    pixels.append((12, 13, skin_shadow))
    pixels.append((13, 13, skin_base))
    # Right eye
    pixels.append((18, 13, skin_base))
    pixels.append((19, 13, skin_shadow))
    pixels.append((20, 13, skin_shadow))
    pixels.append((21, 13, skin_shadow))
    pixels.append((22, 13, skin_shadow))
    pixels.append((23, 13, skin_shadow))
    pixels.append((24, 13, skin_base))

    # ------------------------------------------------------------------
    # Ears (rows 9-13) -- shifted to match new eye zone
    # ------------------------------------------------------------------
    # Left ear: col 5 rows 9-13, col 4 rows 10-12
    pixels.append((5, 9, ear_color))
    pixels.append((5, 10, ear_color))
    pixels.append((5, 11, ear_color))
    pixels.append((5, 12, ear_color))
    pixels.append((5, 13, ear_color))
    pixels.append((4, 10, ear_color))
    pixels.append((4, 11, ear_color))
    pixels.append((4, 12, ear_color))
    # Inner fold shadow
    pixels.append((5, 10, ear_fold))
    pixels.append((5, 11, ear_fold))

    # Right ear: col 26 rows 9-13, col 27 rows 10-12
    pixels.append((26, 9, ear_color))
    pixels.append((26, 10, ear_color))
    pixels.append((26, 11, ear_color))
    pixels.append((26, 12, ear_color))
    pixels.append((26, 13, ear_color))
    pixels.append((27, 10, ear_color))
    pixels.append((27, 11, ear_color))
    pixels.append((27, 12, ear_color))
    # Inner fold shadow
    pixels.append((26, 10, ear_fold))
    pixels.append((26, 11, ear_fold))

    # ------------------------------------------------------------------
    # Row 14: Cheeks / blush
    # ------------------------------------------------------------------
    for x in range(6, 26):
        pixels.append((x, 14, skin_base))
    # Blush on cheeks
    for x in range(7, 12):
        pixels.append((x, 14, skin_warm))
    for x in range(20, 25):
        pixels.append((x, 14, skin_warm))

    # ------------------------------------------------------------------
    # Row 15: Nose (1 row only, 2px subtle shadow dot)
    # ------------------------------------------------------------------
    for x in range(6, 26):
        pixels.append((x, 15, skin_base))
    pixels.append((15, 15, skin_shadow))
    pixels.append((16, 15, skin_shadow))

    # ------------------------------------------------------------------
    # Mouth (rows 16-17)
    # ------------------------------------------------------------------
    for x in range(6, 26):
        pixels.append((x, 16, skin_base))
    for x in range(6, 26):
        pixels.append((x, 17, skin_base))

    # Upper lip (row 16): 6px wide
    for x in range(13, 19):
        pixels.append((x, 16, lip_color))

    # Lower lip (row 17): 4px wide with center highlight
    for x in range(14, 18):
        pixels.append((x, 17, lip_color))
    pixels.append((15, 17, lip_hi))
    pixels.append((16, 17, lip_hi))

    # ------------------------------------------------------------------
    # Chin / jaw (rows 18-19) -- contoured taper with 5-tone shading
    # ------------------------------------------------------------------
    for x in range(7, 25):
        pixels.append((x, 18, skin_base))
    # Jaw contour: 5 tones from center to edges
    pixels.append((7, 18, skin_deep))
    pixels.append((8, 18, skin_shadow))
    pixels.append((9, 18, skin_base))
    pixels.append((23, 18, skin_base))
    pixels.append((24, 18, skin_shadow))
    # Row 19: narrower jaw
    for x in range(8, 24):
        pixels.append((x, 19, skin_base))
    pixels.append((8, 19, skin_deep))
    pixels.append((9, 19, skin_shadow))
    pixels.append((22, 19, skin_shadow))
    pixels.append((23, 19, skin_deep))
    # Warm tones at chin center
    pixels.append((15, 19, skin_warm))
    pixels.append((16, 19, skin_warm))

    # ------------------------------------------------------------------
    # Neck (rows 20-21) -- 6px wide centered (cols 13-18)
    # ------------------------------------------------------------------
    for x in range(13, 19):
        pixels.append((x, 20, skin_base))
        pixels.append((x, 21, skin_base))
    pixels.append((13, 20, skin_shadow))
    pixels.append((18, 20, skin_shadow))
    pixels.append((13, 21, skin_shadow))
    pixels.append((18, 21, skin_shadow))

    # ------------------------------------------------------------------
    # Collar / neckline detail (rows 22-23)
    # ------------------------------------------------------------------
    # Row 22: collar with V-neckline (12px centered, cols 10-21)
    for x in range(10, 22):
        pixels.append((x, 22, outfit))
    pixels.append((15, 22, outfit_shadow))
    pixels.append((16, 22, outfit_shadow))
    # V-neckline opening
    pixels.append((14, 22, skin_shadow))
    pixels.append((17, 22, skin_shadow))

    # Row 23: collar widens (cols 8-23)
    for x in range(8, 24):
        pixels.append((x, 23, outfit))
    pixels.append((15, 23, outfit_shadow))
    pixels.append((16, 23, outfit_shadow))
    pixels.append((8, 23, outfit_hi))
    pixels.append((23, 23, outfit_hi))

    # ------------------------------------------------------------------
    # Shoulders + outfit (rows 24-31) -- widening from 14px to 28px
    # ------------------------------------------------------------------

    # Row 24: 14px (cols 9-22)
    for x in range(9, 23):
        pixels.append((x, 24, outfit))
    pixels.append((9, 24, outfit_hi))
    pixels.append((22, 24, outfit_shadow))
    pixels.append((15, 24, outfit_shadow))

    # Row 25: 18px (cols 7-24)
    for x in range(7, 25):
        pixels.append((x, 25, outfit))
    pixels.append((7, 25, outfit_hi))
    pixels.append((24, 25, outfit_shadow))
    # Fabric fold shadow
    pixels.append((12, 25, outfit_shadow))
    pixels.append((19, 25, outfit_shadow))

    # Row 26: 22px (cols 5-26)
    for x in range(5, 27):
        pixels.append((x, 26, outfit))
    pixels.append((5, 26, outfit_hi))
    pixels.append((26, 26, outfit_shadow))

    # Row 27: 24px (cols 4-27)
    for x in range(4, 28):
        pixels.append((x, 27, outfit))
    pixels.append((4, 27, outfit_hi))
    pixels.append((27, 27, outfit_shadow))
    # Fabric fold shadow
    pixels.append((11, 27, outfit_shadow))
    pixels.append((20, 27, outfit_shadow))

    # Row 28: 26px (cols 3-28)
    for x in range(3, 29):
        pixels.append((x, 28, outfit))
    pixels.append((3, 28, outfit_hi))
    pixels.append((28, 28, outfit_shadow))

    # Row 29: 28px (cols 2-29)
    for x in range(2, 30):
        pixels.append((x, 29, outfit))
    pixels.append((2, 29, outfit_hi))
    pixels.append((29, 29, outfit_shadow))
    # Fabric fold shadow
    pixels.append((10, 29, outfit_shadow))
    pixels.append((21, 29, outfit_shadow))

    # Row 30: 28px (cols 2-29)
    for x in range(2, 30):
        pixels.append((x, 30, outfit))
    pixels.append((2, 30, outfit_hi))
    pixels.append((29, 30, outfit_shadow))

    # Row 31: 28px (cols 2-29)
    for x in range(2, 30):
        pixels.append((x, 31, outfit))
    pixels.append((2, 31, outfit_hi))
    pixels.append((29, 31, outfit_shadow))
    # Fabric fold shadow
    pixels.append((9, 31, outfit_shadow))
    pixels.append((22, 31, outfit_shadow))

    # ------------------------------------------------------------------
    # Glasses overlay (on eye rows 9-13, 5 rows matching new eye zone)
    # ------------------------------------------------------------------
    if has_glasses:
        # Left lens frame: cols 6-14, rows 9-13
        # Right lens frame: cols 17-25, rows 9-13

        # Row 9: full frame top
        for x in range(6, 15):
            pixels.append((x, 9, _GLASSES_FRAME))
        for x in range(17, 26):
            pixels.append((x, 9, _GLASSES_FRAME))

        # Rows 10-12: frame sides + lens fill inside
        for y in range(10, 13):
            # Left lens
            pixels.append((6, y, _GLASSES_FRAME))
            pixels.append((14, y, _GLASSES_FRAME))
            # Right lens
            pixels.append((17, y, _GLASSES_FRAME))
            pixels.append((25, y, _GLASSES_FRAME))

        # Row 13: full frame bottom
        for x in range(6, 15):
            pixels.append((x, 13, _GLASSES_FRAME))
        for x in range(17, 26):
            pixels.append((x, 13, _GLASSES_FRAME))

        # Bridge: cols 14-17, row 10
        pixels.append((14, 10, _GLASSES_FRAME))
        pixels.append((15, 10, _GLASSES_FRAME))
        pixels.append((16, 10, _GLASSES_FRAME))
        pixels.append((17, 10, _GLASSES_FRAME))

        # Lens tint: blend eye pixels inside frame with lens color
        # Left lens interior: cols 7-13, rows 10-12
        for y in range(10, 13):
            for x in range(7, 14):
                # Get what was already drawn at this coordinate
                # We apply a lens tint by appending a blended pixel
                pixels.append(
                    (x, y, blend_colors(_get_last_color(pixels, x, y), _GLASSES_LENS, 0.3))
                )
        # Right lens interior: cols 18-24, rows 10-12
        for y in range(10, 13):
            for x in range(18, 25):
                pixels.append(
                    (x, y, blend_colors(_get_last_color(pixels, x, y), _GLASSES_LENS, 0.3))
                )

        # Re-draw the core eye details through the tinted lens
        # so iris/pupil/catchlight remain visible
        # Left eye: catchlight, iris, pupil (tinted)
        pixels.append((9, 10, blend_colors(ir["catchlight"], _GLASSES_LENS, 0.3)))
        pixels.append((10, 10, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((11, 10, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((9, 11, blend_colors(ir["base"], _GLASSES_LENS, 0.3)))
        pixels.append((10, 11, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        pixels.append((11, 11, blend_colors(ir["base"], _GLASSES_LENS, 0.3)))
        # Right eye
        pixels.append((20, 10, blend_colors(ir["catchlight"], _GLASSES_LENS, 0.3)))
        pixels.append((21, 10, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((22, 10, blend_colors(ir["highlight"], _GLASSES_LENS, 0.3)))
        pixels.append((20, 11, blend_colors(ir["base"], _GLASSES_LENS, 0.3)))
        pixels.append((21, 11, blend_colors(pupil, _GLASSES_LENS, 0.3)))
        pixels.append((22, 11, blend_colors(ir["base"], _GLASSES_LENS, 0.3)))

        # Lens highlight: 1px at upper-left of each lens
        pixels.append((7, 10, _GLASSES_LENS_HIGHLIGHT))
        pixels.append((18, 10, _GLASSES_LENS_HIGHLIGHT))

    # ------------------------------------------------------------------
    # Hair layer (painted last so it overlaps skin/forehead)
    # ------------------------------------------------------------------
    builder = _HAIR_BUILDERS.get(hair_style)
    if builder:
        pixels.extend(builder(hair_color, skin))

    return pixels


def _get_last_color(
    pixels: list[tuple[int, int, str]], x: int, y: int
) -> str:
    """Find the last color set for a given coordinate in the pixel list."""
    for px, py, color in reversed(pixels):
        if px == x and py == y:
            return color
    return "#000000"


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------


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

    pixels = _build_avatar_pixels(avatar_def)

    # De-duplicate: later entries win (hair overlaps skin, glasses overlay)
    pixel_map: dict[tuple[int, int], str] = {}
    for x, y, color in pixels:
        pixel_map[(x, y)] = color

    rects: list[str] = []
    for (x, y), color in sorted(pixel_map.items()):
        rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{color}"/>')

    rect_block = "\n  ".join(rects)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"'
        f' width="{size}" height="{size}"'
        f' style="image-rendering: pixelated;">\n'
        f"  {rect_block}\n"
        f"</svg>"
    )


# ---------------------------------------------------------------------------
# Avatar picker helpers
# ---------------------------------------------------------------------------


def get_avatar_choices() -> list[dict[str, str]]:
    """Return a list of avatar choices for a picker UI."""
    return [
        {"id": avatar_id, "name": meta["name"], "description": meta["description"]}
        for avatar_id, meta in AVATAR_CATALOG.items()
    ]
