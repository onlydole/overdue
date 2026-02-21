"""Pixel art librarian avatar system.

Provides 12 diverse 16x16 pixel art librarian avatars rendered as inline SVG.
Each avatar is built programmatically from a shared base body template with
variations in skin tone, hair pattern, hair color, outfit color, accessories
(glasses), and a small book held in one hand.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------
_PANTS_COLOR = "#2C3E50"
_SHOE_COLOR = "#1A1A1A"
_BOOK_COVER = "#8B4513"
_BOOK_PAGES = "#F5F5DC"
_GLASSES_FRAME = "#333333"
_GLASSES_LENS = "#87CEEB"

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
# ---------------------------------------------------------------------------

def _hair_short_cropped(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Short cropped hair: covers top of head in two rows, tight to sides."""
    pixels = []
    # Row 1: top of hair
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: hair wraps around top of head
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: hair on sides only (face exposed in middle)
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    return pixels


def _hair_curly(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Curly hair: puffy top with volume on the sides."""
    pixels = []
    # Row 0: extra puff on top
    for x in range(6, 11):
        pixels.append((x, 0, hair_color))
    # Row 1: wide curly top
    for x in range(5, 12):
        pixels.append((x, 1, hair_color))
    # Row 2: full crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: sides puff outward
    pixels.append((4, 3, hair_color))
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    pixels.append((12, 3, hair_color))
    # Row 4: side puffs continue
    pixels.append((4, 4, hair_color))
    pixels.append((12, 4, hair_color))
    return pixels


def _hair_bald(hair_color: str | None, skin_tone: str) -> list[tuple[int, int, str]]:
    """Bald: no hair pixels, just a shiny highlight on the head."""
    pixels = []
    # Slight shine highlight on the top of the bare head
    pixels.append((7, 1, "#FFFFFF"))
    return pixels


def _hair_long_straight(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Long straight hair flowing down past the shoulders."""
    pixels = []
    # Row 1: top
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: full crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: sides frame face
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    # Row 4: sides continue
    pixels.append((5, 4, hair_color))
    pixels.append((11, 4, hair_color))
    # Row 5: sides continue
    pixels.append((5, 5, hair_color))
    pixels.append((11, 5, hair_color))
    # Row 6-7: hair flows down past neck/shoulders
    pixels.append((4, 6, hair_color))
    pixels.append((5, 6, hair_color))
    pixels.append((11, 6, hair_color))
    pixels.append((12, 6, hair_color))
    pixels.append((4, 7, hair_color))
    pixels.append((12, 7, hair_color))
    return pixels


def _hair_short_afro(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Short rounded afro sitting on top of the head."""
    pixels = []
    # Row 0: top of afro
    for x in range(6, 11):
        pixels.append((x, 0, hair_color))
    # Row 1: wide afro
    for x in range(5, 12):
        pixels.append((x, 1, hair_color))
    # Row 2: full round shape
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: sides
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    return pixels


def _hair_mohawk(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Tall mohawk: narrow strip standing up high."""
    pixels = []
    # Row 0: tip of mohawk
    pixels.append((8, 0, hair_color))
    # Row 0-1: mohawk strip
    for x in range(7, 10):
        pixels.append((x, 0, hair_color))
    for x in range(7, 10):
        pixels.append((x, 1, hair_color))
    # Row 2: mohawk base
    for x in range(6, 11):
        pixels.append((x, 2, hair_color))
    return pixels


def _hair_braids(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Braids: hair pulled up top with two braids hanging down."""
    pixels = []
    # Row 1: top gathered
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: sides begin braids
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    # Row 4-7: braids hang down on both sides
    for y in range(4, 9):
        pixels.append((4, y, hair_color))
        pixels.append((12, y, hair_color))
    return pixels


def _hair_ponytail(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Ponytail pulled back: hair on top and a tail trailing behind."""
    pixels = []
    # Row 1: top
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: side on left
    pixels.append((5, 3, hair_color))
    # Ponytail trailing to the right side
    pixels.append((12, 2, hair_color))
    pixels.append((13, 3, hair_color))
    pixels.append((13, 4, hair_color))
    pixels.append((13, 5, hair_color))
    pixels.append((13, 6, hair_color))
    return pixels


def _hair_bob_cut(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Bob cut: neat hair that frames the face to chin level."""
    pixels = []
    # Row 1: top
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Row 3: sides frame face
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    # Row 4: sides continue
    pixels.append((5, 4, hair_color))
    pixels.append((11, 4, hair_color))
    # Row 5: chin-length ends -- slight outward flare
    pixels.append((4, 5, hair_color))
    pixels.append((5, 5, hair_color))
    pixels.append((11, 5, hair_color))
    pixels.append((12, 5, hair_color))
    return pixels


def _hair_undercut(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Undercut: longer hair on top swept to one side, shaved sides."""
    pixels = []
    # Row 1: swept top -- offset to the left
    for x in range(5, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: swept crown, heavier on left
    for x in range(4, 11):
        pixels.append((x, 2, hair_color))
    # Left overhang
    pixels.append((4, 3, hair_color))
    pixels.append((5, 3, hair_color))
    return pixels


def _hair_locs(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Locs: thick strands gathered on top and hanging down."""
    pixels = []
    # Row 1: top
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    # Row 2: crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Sides and hanging locs
    pixels.append((5, 3, hair_color))
    pixels.append((11, 3, hair_color))
    # Locs hang down on both sides in alternating pattern
    for y in range(4, 10):
        pixels.append((4, y, hair_color))
        pixels.append((12, y, hair_color))
    # Extra loc strands
    pixels.append((3, 5, hair_color))
    pixels.append((13, 5, hair_color))
    pixels.append((3, 7, hair_color))
    pixels.append((13, 7, hair_color))
    return pixels


def _hair_spiky(hair_color: str, skin_tone: str) -> list[tuple[int, int, str]]:
    """Spiky hair: wild spikes pointing in multiple directions."""
    pixels = []
    # Row 0: spike tips
    pixels.append((6, 0, hair_color))
    pixels.append((8, 0, hair_color))
    pixels.append((10, 0, hair_color))
    # Row 1: spikes base + more tips
    pixels.append((5, 1, hair_color))
    for x in range(6, 11):
        pixels.append((x, 1, hair_color))
    pixels.append((11, 1, hair_color))
    # Row 2: crown
    for x in range(5, 12):
        pixels.append((x, 2, hair_color))
    # Side spikes
    pixels.append((4, 2, hair_color))
    pixels.append((12, 2, hair_color))
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
# Core pixel builder
# ---------------------------------------------------------------------------

def _build_avatar_pixels(avatar_def: dict) -> list[tuple[int, int, str]]:
    """Build the full list of (x, y, color) pixels for an avatar.

    The base character template occupies roughly columns 5-11 and rows 1-15
    on the 16x16 grid.  Hair, glasses, book, and other details are layered
    on top.
    """
    skin = avatar_def["skin_tone"]
    outfit = avatar_def["outfit_color"]
    hair_style = avatar_def["hair_style"]
    hair_color = avatar_def["hair_color"]
    has_glasses = avatar_def["glasses"]

    pixels: list[tuple[int, int, str]] = []

    # ------------------------------------------------------------------
    # Head / face  (rows 2-5, columns 6-10)
    # Row 2 is top of head (may be covered by hair)
    # ------------------------------------------------------------------
    # Row 2: top of head (skin -- hair overlaps this)
    for x in range(6, 11):
        pixels.append((x, 2, skin))

    # Row 3: face row 1 -- forehead
    for x in range(6, 11):
        pixels.append((x, 3, skin))

    # Row 4: face row 2 -- eyes row
    for x in range(6, 11):
        pixels.append((x, 4, skin))
    # Eyes
    pixels.append((7, 4, "#FFFFFF"))  # left eye white
    pixels.append((9, 4, "#FFFFFF"))  # right eye white

    # Row 5: face row 3 -- mouth area
    for x in range(6, 11):
        pixels.append((x, 5, skin))
    # Subtle smile
    pixels.append((7, 5, "#C0392B"))  # left corner of smile
    pixels.append((8, 5, "#C0392B"))  # center of smile
    pixels.append((9, 5, "#C0392B"))  # right corner of smile

    # ------------------------------------------------------------------
    # Glasses (on eye row = row 4)
    # ------------------------------------------------------------------
    if has_glasses:
        pixels.append((6, 4, _GLASSES_FRAME))
        pixels.append((7, 4, _GLASSES_LENS))
        pixels.append((8, 4, _GLASSES_FRAME))  # bridge
        pixels.append((9, 4, _GLASSES_LENS))
        pixels.append((10, 4, _GLASSES_FRAME))

    # ------------------------------------------------------------------
    # Neck (row 6)
    # ------------------------------------------------------------------
    pixels.append((7, 6, skin))
    pixels.append((8, 6, skin))
    pixels.append((9, 6, skin))

    # ------------------------------------------------------------------
    # Body / outfit (rows 7-10)
    # ------------------------------------------------------------------
    # Row 7: shoulders
    for x in range(5, 12):
        pixels.append((x, 7, outfit))

    # Row 8: upper torso + arms
    pixels.append((4, 8, skin))   # left hand
    for x in range(5, 12):
        pixels.append((x, 8, outfit))
    pixels.append((12, 8, skin))  # right hand

    # Row 9: mid torso + arms with book
    pixels.append((4, 9, skin))   # left hand
    for x in range(5, 12):
        pixels.append((x, 9, outfit))
    pixels.append((12, 9, skin))  # right hand

    # Book in right hand area (rows 8-9, columns 12-13)
    pixels.append((13, 8, _BOOK_COVER))
    pixels.append((14, 8, _BOOK_PAGES))
    pixels.append((13, 9, _BOOK_COVER))
    pixels.append((14, 9, _BOOK_PAGES))

    # Row 10: lower torso
    for x in range(5, 12):
        pixels.append((x, 10, outfit))

    # ------------------------------------------------------------------
    # Belt detail
    # ------------------------------------------------------------------
    pixels.append((6, 10, "#795548"))
    pixels.append((7, 10, "#795548"))
    pixels.append((8, 10, "#D4A017"))  # belt buckle
    pixels.append((9, 10, "#795548"))
    pixels.append((10, 10, "#795548"))

    # ------------------------------------------------------------------
    # Legs / pants (rows 11-13)
    # ------------------------------------------------------------------
    # Row 11: upper legs
    for x in range(6, 8):
        pixels.append((x, 11, _PANTS_COLOR))
    for x in range(9, 11):
        pixels.append((x, 11, _PANTS_COLOR))

    # Row 12: mid legs
    for x in range(6, 8):
        pixels.append((x, 12, _PANTS_COLOR))
    for x in range(9, 11):
        pixels.append((x, 12, _PANTS_COLOR))

    # Row 13: lower legs
    for x in range(6, 8):
        pixels.append((x, 13, _PANTS_COLOR))
    for x in range(9, 11):
        pixels.append((x, 13, _PANTS_COLOR))

    # ------------------------------------------------------------------
    # Shoes (rows 14-15)
    # ------------------------------------------------------------------
    # Row 14
    pixels.append((5, 14, _SHOE_COLOR))
    pixels.append((6, 14, _SHOE_COLOR))
    pixels.append((7, 14, _SHOE_COLOR))
    pixels.append((9, 14, _SHOE_COLOR))
    pixels.append((10, 14, _SHOE_COLOR))
    pixels.append((11, 14, _SHOE_COLOR))

    # Row 15: shoe soles
    pixels.append((5, 15, "#4E342E"))
    pixels.append((6, 15, "#4E342E"))
    pixels.append((7, 15, "#4E342E"))
    pixels.append((9, 15, "#4E342E"))
    pixels.append((10, 15, "#4E342E"))
    pixels.append((11, 15, "#4E342E"))

    # ------------------------------------------------------------------
    # Hair layer (painted on top of base so it overrides skin where needed)
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

    Parameters
    ----------
    avatar_id:
        One of the keys in :data:`AVATAR_CATALOG` (e.g. ``"avatar_01"``).
    size:
        Width and height of the rendered SVG element in pixels.

    Returns
    -------
    str
        A complete ``<svg>`` element suitable for inline embedding in HTML.
    """
    avatar_def = AVATAR_CATALOG.get(avatar_id)
    if avatar_def is None:
        # Fallback: render a simple question-mark placeholder
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

    # Build SVG rects
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
    """Return a list of avatar choices for a picker UI.

    Each entry contains:
    - ``id``: the avatar identifier (e.g. ``"avatar_01"``)
    - ``name``: the display name (e.g. ``"Sage"``)
    - ``description``: a short flavour description
    """
    return [
        {"id": avatar_id, "name": meta["name"], "description": meta["description"]}
        for avatar_id, meta in AVATAR_CATALOG.items()
    ]
