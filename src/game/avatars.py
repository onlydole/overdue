"""Pixel art librarian avatar system -- shoulders-up portraits.

Provides 12 diverse 16x16 pixel art librarian avatars rendered as inline SVG.
Each avatar is built programmatically as a shoulders-up portrait with detailed
facial features: skin tone, hair pattern, hair color, outfit color, and
optional glasses.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------
_GLASSES_FRAME = "#333333"
_GLASSES_LENS = "#87CEEB"


def _darken(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color by the given factor."""
    h = hex_color.lstrip("#")
    r = int(int(h[0:2], 16) * factor)
    g = int(int(h[2:4], 16) * factor)
    b = int(int(h[4:6], 16) * factor)
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"


# ---------------------------------------------------------------------------
# Avatar catalog
# ---------------------------------------------------------------------------
AVATAR_CATALOG: dict[str, dict] = {
    "avatar_01": {
        "name": "Sage",
        "description": "A silver-haired scholar in forest green, wise eyes behind glasses.",
        "skin_tone": "#F5D0A9",
        "hair_style": "short_cropped",
        "hair_color": "#C0C0C0",
        "glasses": True,
        "outfit_color": "#2E7D32",
    },
    "avatar_02": {
        "name": "Ember",
        "description": "An auburn-curled storyteller draped in deep purple.",
        "skin_tone": "#8D5524",
        "hair_style": "curly",
        "hair_color": "#A0522D",
        "glasses": False,
        "outfit_color": "#4A148C",
    },
    "avatar_03": {
        "name": "Atlas",
        "description": "A bespectacled navigator in crisp navy, head shining bright.",
        "skin_tone": "#C68642",
        "hair_style": "bald",
        "hair_color": None,
        "glasses": True,
        "outfit_color": "#1A237E",
    },
    "avatar_04": {
        "name": "Wren",
        "description": "Long blonde hair flowing over a burgundy coat.",
        "skin_tone": "#F5D0A9",
        "hair_style": "long_straight",
        "hair_color": "#F0E68C",
        "glasses": False,
        "outfit_color": "#7B1FA2",
    },
    "avatar_05": {
        "name": "Basil",
        "description": "A confident reader in teal with a neat afro.",
        "skin_tone": "#3C1F0A",
        "hair_style": "short_afro",
        "hair_color": "#1A1A1A",
        "glasses": False,
        "outfit_color": "#00695C",
    },
    "avatar_06": {
        "name": "Quinn",
        "description": "Blue-mohawked rebel librarian in bold red.",
        "skin_tone": "#E0AC69",
        "hair_style": "mohawk",
        "hair_color": "#1976D2",
        "glasses": False,
        "outfit_color": "#C62828",
    },
    "avatar_07": {
        "name": "Nova",
        "description": "Braided hair and golden outfit, always peering through glasses.",
        "skin_tone": "#6B4226",
        "hair_style": "braids",
        "hair_color": "#3E2723",
        "glasses": True,
        "outfit_color": "#F9A825",
    },
    "avatar_08": {
        "name": "Reed",
        "description": "Red ponytail bouncing above a cool slate jacket.",
        "skin_tone": "#F5D0A9",
        "hair_style": "ponytail",
        "hair_color": "#B22222",
        "glasses": False,
        "outfit_color": "#546E7A",
    },
    "avatar_09": {
        "name": "Indigo",
        "description": "Purple bob cut framing a face above olive green.",
        "skin_tone": "#C68642",
        "hair_style": "bob_cut",
        "hair_color": "#7B1FA2",
        "glasses": False,
        "outfit_color": "#558B2F",
    },
    "avatar_10": {
        "name": "Ash",
        "description": "Sharp undercut and glasses over a charcoal coat.",
        "skin_tone": "#8D5524",
        "hair_style": "undercut",
        "hair_color": "#1A1A1A",
        "glasses": True,
        "outfit_color": "#37474F",
    },
    "avatar_11": {
        "name": "Clover",
        "description": "Long locs cascading over an emerald tunic.",
        "skin_tone": "#3C1F0A",
        "hair_style": "locs",
        "hair_color": "#3E2723",
        "glasses": False,
        "outfit_color": "#1B5E20",
    },
    "avatar_12": {
        "name": "Pixel",
        "description": "Green spiky hair and a pink outfit -- the wildcard librarian.",
        "skin_tone": "#F5D0A9",
        "hair_style": "spiky",
        "hair_color": "#2E7D32",
        "glasses": False,
        "outfit_color": "#E91E63",
    },
}


# ---------------------------------------------------------------------------
# Hair pattern helpers -- each returns a list of (x, y, color) pixels
# Coordinates updated for the wider portrait face (cols 3-12).
# ---------------------------------------------------------------------------

def _hair_short_cropped(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Short cropped hair: covers top of head in two rows, tight to sides."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    pixels.append((3, 2, hair_color))
    pixels.append((12, 2, hair_color))
    return pixels


def _hair_curly(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Curly hair: puffy top with volume on the sides."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(2, 14):
        pixels.append((x, 1, hair_color))
    for x in range(3, 13):
        pixels.append((x, 2, hair_color))
    pixels.append((2, 2, hair_color))
    pixels.append((13, 2, hair_color))
    pixels.append((2, 3, hair_color))
    pixels.append((13, 3, hair_color))
    pixels.append((2, 4, hair_color))
    pixels.append((13, 4, hair_color))
    return pixels


def _hair_bald(hair_color: str | None, skin_tone: str) -> list[tuple[int, int, str]]:
    """Bald: no hair pixels, just a shiny highlight on the head."""
    return [(6, 0, "#FFFFFF")]


def _hair_long_straight(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Long straight hair flowing down past the shoulders."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    pixels.append((2, 2, hair_color))
    pixels.append((3, 2, hair_color))
    pixels.append((12, 2, hair_color))
    pixels.append((13, 2, hair_color))
    for y in range(3, 7):
        pixels.append((2, y, hair_color))
        pixels.append((13, y, hair_color))
    for y in range(7, 11):
        pixels.append((1, y, hair_color))
        pixels.append((14, y, hair_color))
    return pixels


def _hair_short_afro(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Short rounded afro sitting on top of the head."""
    pixels = []
    for x in range(3, 13):
        pixels.append((x, 0, hair_color))
    for x in range(2, 14):
        pixels.append((x, 1, hair_color))
    for x in range(3, 13):
        pixels.append((x, 2, hair_color))
    pixels.append((2, 2, hair_color))
    pixels.append((13, 2, hair_color))
    pixels.append((2, 3, hair_color))
    pixels.append((13, 3, hair_color))
    return pixels


def _hair_mohawk(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Tall mohawk: narrow strip standing up high."""
    pixels = []
    for x in range(6, 10):
        pixels.append((x, 0, hair_color))
    for x in range(5, 11):
        pixels.append((x, 1, hair_color))
    for x in range(5, 11):
        pixels.append((x, 2, hair_color))
    return pixels


def _hair_braids(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Braids: hair pulled up top with two braids hanging down."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    pixels.append((3, 2, hair_color))
    pixels.append((12, 2, hair_color))
    for y in range(3, 10):
        pixels.append((2, y, hair_color))
        pixels.append((13, y, hair_color))
    return pixels


def _hair_ponytail(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Ponytail pulled back: hair on top and a tail trailing behind."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    pixels.append((3, 2, hair_color))
    pixels.append((13, 1, hair_color))
    pixels.append((14, 2, hair_color))
    pixels.append((14, 3, hair_color))
    pixels.append((14, 4, hair_color))
    pixels.append((14, 5, hair_color))
    return pixels


def _hair_bob_cut(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Bob cut: neat hair that frames the face to chin level."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    for y in range(2, 5):
        pixels.append((2, y, hair_color))
        pixels.append((3, y, hair_color))
        pixels.append((12, y, hair_color))
        pixels.append((13, y, hair_color))
    pixels.append((1, 5, hair_color))
    pixels.append((2, 5, hair_color))
    pixels.append((13, 5, hair_color))
    pixels.append((14, 5, hair_color))
    return pixels


def _hair_undercut(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Undercut: longer hair on top swept to one side, shaved sides."""
    pixels = []
    for x in range(3, 11):
        pixels.append((x, 0, hair_color))
    for x in range(2, 12):
        pixels.append((x, 1, hair_color))
    pixels.append((2, 2, hair_color))
    pixels.append((3, 2, hair_color))
    return pixels


def _hair_locs(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Locs: thick strands gathered on top and hanging down."""
    pixels = []
    for x in range(4, 12):
        pixels.append((x, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    pixels.append((3, 2, hair_color))
    pixels.append((12, 2, hair_color))
    for y in range(3, 10):
        pixels.append((2, y, hair_color))
        pixels.append((13, y, hair_color))
    pixels.append((1, 4, hair_color))
    pixels.append((14, 4, hair_color))
    pixels.append((1, 6, hair_color))
    pixels.append((14, 6, hair_color))
    pixels.append((1, 8, hair_color))
    pixels.append((14, 8, hair_color))
    return pixels


def _hair_spiky(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Spiky hair: wild spikes pointing in multiple directions."""
    pixels = []
    pixels.append((4, 0, hair_color))
    pixels.append((7, 0, hair_color))
    pixels.append((10, 0, hair_color))
    for x in range(3, 13):
        pixels.append((x, 1, hair_color))
    pixels.append((2, 1, hair_color))
    pixels.append((13, 1, hair_color))
    for x in range(3, 13):
        pixels.append((x, 2, hair_color))
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
# Core pixel builder — shoulders-up portrait
# ---------------------------------------------------------------------------

def _build_avatar_pixels(avatar_def: dict) -> list[tuple[int, int, str]]:
    """Build the full list of (x, y, color) pixels for a portrait avatar.

    The portrait occupies the full 16x16 grid:
      Rows 0-3:  Hair (overlaps forehead skin)
      Row 4:     Eyebrows
      Row 5:     Eyes
      Row 6:     Cheeks
      Row 7:     Nose
      Row 8:     Mouth
      Row 9:     Chin
      Row 10:    Neck
      Rows 11-15: Collar, shoulders, upper outfit
    Face spans columns 3-12 (10px wide).
    """
    skin = avatar_def["skin_tone"]
    outfit = avatar_def["outfit_color"]
    hair_style = avatar_def["hair_style"]
    hair_color = avatar_def["hair_color"]
    has_glasses = avatar_def["glasses"]

    lip_color = _darken(skin, 0.75)
    nose_color = _darken(skin, 0.85)
    brow_color = hair_color or _darken(skin, 0.5)

    pixels: list[tuple[int, int, str]] = []

    # ------------------------------------------------------------------
    # Head skin base (rows 0-9)
    # Rows 0-3 will be overwritten by hair; we paint skin first.
    # ------------------------------------------------------------------
    for y in range(0, 4):
        for x in range(3, 13):
            pixels.append((x, y, skin))

    # Row 4: eyebrow row
    for x in range(3, 13):
        pixels.append((x, 4, skin))
    pixels.append((4, 4, brow_color))
    pixels.append((5, 4, brow_color))
    pixels.append((6, 4, brow_color))
    pixels.append((9, 4, brow_color))
    pixels.append((10, 4, brow_color))
    pixels.append((11, 4, brow_color))

    # Row 5: eyes
    for x in range(3, 13):
        pixels.append((x, 5, skin))
    pixels.append((5, 5, "#FFFFFF"))
    pixels.append((6, 5, "#1A1A1A"))
    pixels.append((9, 5, "#FFFFFF"))
    pixels.append((10, 5, "#1A1A1A"))

    # Row 6: cheeks
    for x in range(3, 13):
        pixels.append((x, 6, skin))

    # Row 7: nose
    for x in range(3, 13):
        pixels.append((x, 7, skin))
    pixels.append((7, 7, nose_color))
    pixels.append((8, 7, nose_color))

    # Row 8: mouth
    for x in range(3, 13):
        pixels.append((x, 8, skin))
    pixels.append((6, 8, lip_color))
    pixels.append((7, 8, lip_color))
    pixels.append((8, 8, lip_color))
    pixels.append((9, 8, lip_color))

    # Row 9: chin (slightly narrower)
    for x in range(4, 12):
        pixels.append((x, 9, skin))

    # ------------------------------------------------------------------
    # Neck (row 10) — 4px wide centered
    # ------------------------------------------------------------------
    for x in range(6, 10):
        pixels.append((x, 10, skin))

    # ------------------------------------------------------------------
    # Collar + shoulders (rows 11-15, widening)
    # ------------------------------------------------------------------
    for x in range(5, 11):
        pixels.append((x, 11, outfit))
    for x in range(3, 13):
        pixels.append((x, 12, outfit))
    for x in range(2, 14):
        pixels.append((x, 13, outfit))
    for x in range(1, 15):
        pixels.append((x, 14, outfit))
    for x in range(1, 15):
        pixels.append((x, 15, outfit))

    # ------------------------------------------------------------------
    # Glasses (on eye row = row 5, cols 4-11)
    # Two 2px lens areas with bridge between
    # ------------------------------------------------------------------
    if has_glasses:
        pixels.append((4, 5, _GLASSES_FRAME))
        pixels.append((5, 5, _GLASSES_LENS))
        pixels.append((6, 5, _GLASSES_LENS))
        pixels.append((7, 5, _GLASSES_FRAME))
        pixels.append((8, 5, _GLASSES_FRAME))
        pixels.append((9, 5, _GLASSES_LENS))
        pixels.append((10, 5, _GLASSES_LENS))
        pixels.append((11, 5, _GLASSES_FRAME))

    # ------------------------------------------------------------------
    # Hair layer (painted last so it overlaps skin/forehead)
    # ------------------------------------------------------------------
    builder = _HAIR_BUILDERS.get(hair_style)
    if builder:
        pixels.extend(builder(hair_color, skin))

    return pixels


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------

def render_avatar_svg(avatar_id: str, size: int = 32) -> str:
    """Return an inline SVG string for the given avatar.

    The SVG uses a 16x16 ``viewBox`` and renders at the specified *size*
    in device pixels.  The ``image-rendering: pixelated`` style keeps the
    pixel art crisp when scaled.
    """
    avatar_def = AVATAR_CATALOG.get(avatar_id)
    if avatar_def is None:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"'
            f' width="{size}" height="{size}"'
            f' style="image-rendering: pixelated;">'
            f'<rect width="16" height="16" fill="#ccc"/>'
            f'<text x="8" y="12" text-anchor="middle"'
            f' font-size="10" fill="#666">?</text>'
            f'</svg>'
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
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"'
        f' width="{size}" height="{size}"'
        f' style="image-rendering: pixelated;">\n'
        f'  {rect_block}\n'
        f'</svg>'
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
