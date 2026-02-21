"""GBA-era color palette with 4-step shading ramps and blending helpers.

Each ramp provides (highlight, base, shadow, deep_shadow) for consistent
multi-step shading across all icons and avatars.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 4-step shading ramps: (highlight, base, shadow, deep_shadow)
# ---------------------------------------------------------------------------
GOLD = ("#ffe9a0", "#f0c543", "#c49b22", "#8a6b10")
FLAME = ("#ff9e6e", "#e8563e", "#b33a25", "#7a2214")
GREEN = ("#8aef8a", "#5cdb5c", "#3d9e3d", "#2a6e2a")
BLUE = ("#b0d8f0", "#7eb5e3", "#5a8bba", "#3d6490")
PURPLE = ("#d4a0f0", "#b76ef0", "#8a4cc4", "#5e308a")
PARCHMENT = ("#fffaf0", "#f0e6d3", "#d4c4a8", "#b0a080")
INK = ("#ababbe", "#8b8b9e", "#6a6a80", "#4a4a60")

# Standalone colors
WHITE = "#ffffff"
DARK = "#1a1a2e"
BLACK = "#0f0e17"

# Legacy aliases (match old flat palette names for easy migration)
GOLD_BASE = GOLD[1]
GOLD_DARK = GOLD[2]
FLAME_BASE = FLAME[1]
FLAME_ORANGE = FLAME[0]
GREEN_BASE = GREEN[1]
GREEN_DARK = GREEN[2]
BLUE_BASE = BLUE[1]
PURPLE_BASE = PURPLE[1]
PARCHMENT_BASE = PARCHMENT[1]
INK_BASE = INK[1]


# ---------------------------------------------------------------------------
# Color manipulation helpers
# ---------------------------------------------------------------------------


def darken(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color by the given factor (0.0 = black, 1.0 = unchanged)."""
    h = hex_color.lstrip("#")
    r = int(int(h[0:2], 16) * factor)
    g = int(int(h[2:4], 16) * factor)
    b = int(int(h[4:6], 16) * factor)
    return f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"


def lighten(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color by the given factor (0.0 = unchanged, 1.0 = white)."""
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    r = r + int((255 - r) * factor)
    g = g + int((255 - g) * factor)
    b = b + int((255 - b) * factor)
    return f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"


def blend_colors(c1: str, c2: str, ratio: float = 0.5) -> str:
    """Blend two hex colors. ratio=0.0 gives c1, ratio=1.0 gives c2."""
    h1 = c1.lstrip("#")
    h2 = c2.lstrip("#")
    r = int(int(h1[0:2], 16) * (1 - ratio) + int(h2[0:2], 16) * ratio)
    g = int(int(h1[2:4], 16) * (1 - ratio) + int(h2[2:4], 16) * ratio)
    b = int(int(h1[4:6], 16) * (1 - ratio) + int(h2[4:6], 16) * ratio)
    return f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"
