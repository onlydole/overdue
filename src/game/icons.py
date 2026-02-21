"""Pixel art icon system -- 8x8 decorative icons rendered as inline SVG.

Provides 27 pixel art icons for use throughout the UI, replacing native emoji
with a cohesive retro aesthetic. Each icon is an 8x8 grid of colored pixels
rendered as SVG ``<rect>`` elements, following the same pattern as the avatar
system in ``avatars.py``.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Default palette -- warm library tones
# ---------------------------------------------------------------------------
_GOLD = "#f0c543"
_GOLD_DARK = "#c49b22"
_PARCHMENT = "#f0e6d3"
_FLAME = "#e8563e"
_FLAME_ORANGE = "#f07a3e"
_GREEN = "#5cdb5c"
_GREEN_DARK = "#2E7D32"
_BLUE = "#7eb5e3"
_PURPLE = "#b76ef0"
_INK = "#8b8b9e"
_WHITE = "#ffffff"
_DARK = "#1a1a2e"

# ---------------------------------------------------------------------------
# Icon catalog -- each icon is a list of (x, y, color) pixel tuples on 8x8
# ---------------------------------------------------------------------------
_ICON_CATALOG: dict[str, list[tuple[int, int, str]]] = {}


def _register(name: str, pixels: list[tuple[int, int, str]]) -> None:
    _ICON_CATALOG[name] = pixels


# --- books: stack of 3 books ---
_register("books", [
    # Bottom book (widest, red-ish)
    (1, 5, _FLAME), (2, 5, _FLAME), (3, 5, _FLAME), (4, 5, _FLAME), (5, 5, _FLAME), (6, 5, _FLAME),
    (1, 6, _FLAME), (2, 6, _PARCHMENT), (3, 6, _PARCHMENT), (4, 6, _PARCHMENT), (5, 6, _PARCHMENT), (6, 6, _FLAME),
    # Middle book (medium, green)
    (1, 3, _GREEN_DARK), (2, 3, _GREEN_DARK), (3, 3, _GREEN_DARK), (4, 3, _GREEN_DARK), (5, 3, _GREEN_DARK),
    (1, 4, _GREEN_DARK), (2, 4, _PARCHMENT), (3, 4, _PARCHMENT), (4, 4, _PARCHMENT), (5, 4, _GREEN_DARK),
    # Top book (narrow, gold)
    (2, 1, _GOLD), (3, 1, _GOLD), (4, 1, _GOLD), (5, 1, _GOLD),
    (2, 2, _GOLD), (3, 2, _PARCHMENT), (4, 2, _PARCHMENT), (5, 2, _GOLD),
])

# --- book-open: open book with pages ---
_register("book-open", [
    # Spine
    (3, 1, _GOLD_DARK), (4, 1, _GOLD_DARK),
    (3, 2, _GOLD_DARK), (4, 2, _GOLD_DARK),
    (3, 3, _GOLD_DARK), (4, 3, _GOLD_DARK),
    (3, 4, _GOLD_DARK), (4, 4, _GOLD_DARK),
    (3, 5, _GOLD_DARK), (4, 5, _GOLD_DARK),
    # Left pages
    (0, 2, _GOLD), (1, 1, _GOLD), (2, 1, _PARCHMENT),
    (0, 3, _PARCHMENT), (1, 3, _PARCHMENT), (2, 3, _PARCHMENT),
    (0, 4, _PARCHMENT), (1, 4, _PARCHMENT), (2, 4, _PARCHMENT),
    (1, 2, _PARCHMENT), (2, 2, _PARCHMENT),
    (0, 5, _GOLD), (1, 5, _GOLD), (2, 5, _GOLD),
    # Right pages
    (5, 1, _GOLD), (6, 1, _GOLD), (7, 2, _GOLD),
    (5, 2, _PARCHMENT), (6, 2, _PARCHMENT),
    (5, 3, _PARCHMENT), (6, 3, _PARCHMENT), (7, 3, _PARCHMENT),
    (5, 4, _PARCHMENT), (6, 4, _PARCHMENT), (7, 4, _PARCHMENT),
    (5, 5, _GOLD), (6, 5, _GOLD), (7, 5, _GOLD),
])

# --- book-closed: single closed book ---
_register("book-closed", [
    (2, 1, _FLAME), (3, 1, _FLAME), (4, 1, _FLAME), (5, 1, _FLAME),
    (2, 2, _FLAME), (3, 2, _PARCHMENT), (4, 2, _PARCHMENT), (5, 2, _FLAME),
    (2, 3, _FLAME), (3, 3, _PARCHMENT), (4, 3, _PARCHMENT), (5, 3, _FLAME),
    (2, 4, _FLAME), (3, 4, _PARCHMENT), (4, 4, _PARCHMENT), (5, 4, _FLAME),
    (2, 5, _FLAME), (3, 5, _PARCHMENT), (4, 5, _PARCHMENT), (5, 5, _FLAME),
    (2, 6, _FLAME), (3, 6, _FLAME), (4, 6, _FLAME), (5, 6, _FLAME),
])

# --- fire: flame ---
_register("fire", [
    (3, 0, _GOLD),
    (3, 1, _GOLD), (4, 1, _GOLD),
    (2, 2, _FLAME_ORANGE), (3, 2, _GOLD), (4, 2, _GOLD), (5, 2, _FLAME_ORANGE),
    (2, 3, _FLAME_ORANGE), (3, 3, _FLAME_ORANGE), (4, 3, _GOLD), (5, 3, _FLAME_ORANGE),
    (1, 4, _FLAME), (2, 4, _FLAME_ORANGE), (3, 4, _FLAME_ORANGE), (4, 4, _FLAME_ORANGE), (5, 4, _FLAME_ORANGE), (6, 4, _FLAME),
    (1, 5, _FLAME), (2, 5, _FLAME), (3, 5, _FLAME), (4, 5, _FLAME), (5, 5, _FLAME), (6, 5, _FLAME),
    (2, 6, _FLAME), (3, 6, _FLAME), (4, 6, _FLAME), (5, 6, _FLAME),
])

# --- trophy: trophy cup ---
_register("trophy", [
    (2, 0, _GOLD), (3, 0, _GOLD), (4, 0, _GOLD), (5, 0, _GOLD),
    (1, 1, _GOLD), (2, 1, _GOLD), (3, 1, _GOLD), (4, 1, _GOLD), (5, 1, _GOLD), (6, 1, _GOLD),
    (0, 2, _GOLD_DARK), (1, 2, _GOLD), (2, 2, _GOLD), (3, 2, _GOLD), (4, 2, _GOLD), (5, 2, _GOLD), (6, 2, _GOLD), (7, 2, _GOLD_DARK),
    (1, 3, _GOLD), (2, 3, _GOLD), (3, 3, _GOLD), (4, 3, _GOLD), (5, 3, _GOLD), (6, 3, _GOLD),
    (2, 4, _GOLD), (3, 4, _GOLD), (4, 4, _GOLD), (5, 4, _GOLD),
    (3, 5, _GOLD_DARK), (4, 5, _GOLD_DARK),
    (2, 6, _GOLD_DARK), (3, 6, _GOLD_DARK), (4, 6, _GOLD_DARK), (5, 6, _GOLD_DARK),
])

# --- star: 5-pointed star ---
_register("star", [
    (3, 0, _GOLD), (4, 0, _GOLD),
    (3, 1, _GOLD), (4, 1, _GOLD),
    (0, 2, _GOLD), (1, 2, _GOLD), (2, 2, _GOLD), (3, 2, _GOLD), (4, 2, _GOLD), (5, 2, _GOLD), (6, 2, _GOLD), (7, 2, _GOLD),
    (1, 3, _GOLD), (2, 3, _GOLD), (3, 3, _GOLD), (4, 3, _GOLD), (5, 3, _GOLD), (6, 3, _GOLD),
    (2, 4, _GOLD), (3, 4, _GOLD), (4, 4, _GOLD), (5, 4, _GOLD),
    (1, 5, _GOLD), (2, 5, _GOLD), (3, 5, _GOLD_DARK), (4, 5, _GOLD_DARK), (5, 5, _GOLD), (6, 5, _GOLD),
    (1, 6, _GOLD), (2, 6, _GOLD_DARK), (5, 6, _GOLD_DARK), (6, 6, _GOLD),
])

# --- sparkles: sparkle/shine ---
_register("sparkles", [
    (3, 0, _GOLD),
    (1, 1, _GOLD), (6, 1, _GOLD),
    (3, 2, _GOLD),
    (5, 3, _GOLD),
    (0, 4, _GOLD), (1, 4, _GOLD), (2, 4, _GOLD), (3, 4, _WHITE), (4, 4, _GOLD), (5, 4, _GOLD), (6, 4, _GOLD), (7, 4, _GOLD),
    (5, 5, _GOLD),
    (3, 6, _GOLD),
    (1, 7, _GOLD), (6, 7, _GOLD),
])

# --- library: building with columns ---
_register("library", [
    (2, 0, _GOLD), (3, 0, _GOLD), (4, 0, _GOLD), (5, 0, _GOLD),
    (1, 1, _GOLD), (2, 1, _GOLD), (3, 1, _GOLD), (4, 1, _GOLD), (5, 1, _GOLD), (6, 1, _GOLD),
    (1, 2, _PARCHMENT), (2, 2, _PARCHMENT), (3, 2, _PARCHMENT), (4, 2, _PARCHMENT), (5, 2, _PARCHMENT), (6, 2, _PARCHMENT),
    (1, 3, _PARCHMENT), (2, 3, _INK), (3, 3, _PARCHMENT), (4, 3, _PARCHMENT), (5, 3, _INK), (6, 3, _PARCHMENT),
    (1, 4, _PARCHMENT), (2, 4, _INK), (3, 4, _PARCHMENT), (4, 4, _PARCHMENT), (5, 4, _INK), (6, 4, _PARCHMENT),
    (1, 5, _PARCHMENT), (2, 5, _INK), (3, 5, _PARCHMENT), (4, 5, _PARCHMENT), (5, 5, _INK), (6, 5, _PARCHMENT),
    (0, 6, _GOLD_DARK), (1, 6, _GOLD_DARK), (2, 6, _GOLD_DARK), (3, 6, _GOLD_DARK), (4, 6, _GOLD_DARK), (5, 6, _GOLD_DARK), (6, 6, _GOLD_DARK), (7, 6, _GOLD_DARK),
])

# --- moon: crescent moon ---
_register("moon", [
    (3, 0, _GOLD), (4, 0, _GOLD), (5, 0, _GOLD),
    (2, 1, _GOLD), (3, 1, _GOLD),
    (1, 2, _GOLD), (2, 2, _GOLD),
    (1, 3, _GOLD), (2, 3, _GOLD),
    (1, 4, _GOLD), (2, 4, _GOLD),
    (2, 5, _GOLD), (3, 5, _GOLD),
    (3, 6, _GOLD), (4, 6, _GOLD), (5, 6, _GOLD),
])

# --- zap: lightning bolt ---
_register("zap", [
    (4, 0, _GOLD), (5, 0, _GOLD),
    (3, 1, _GOLD), (4, 1, _GOLD),
    (2, 2, _GOLD), (3, 2, _GOLD), (4, 2, _GOLD), (5, 2, _GOLD), (6, 2, _GOLD),
    (4, 3, _GOLD), (5, 3, _GOLD),
    (3, 4, _GOLD), (4, 4, _GOLD),
    (2, 5, _GOLD), (3, 5, _GOLD),
    (1, 6, _GOLD), (2, 6, _GOLD), (3, 6, _GOLD), (4, 6, _GOLD), (5, 6, _GOLD),
    (3, 7, _GOLD), (4, 7, _GOLD),
])

# --- award: medal/ribbon ---
_register("award", [
    (2, 0, _PURPLE), (5, 0, _PURPLE),
    (2, 1, _PURPLE), (3, 1, _PURPLE), (4, 1, _PURPLE), (5, 1, _PURPLE),
    (3, 2, _GOLD), (4, 2, _GOLD),
    (2, 3, _GOLD), (3, 3, _GOLD), (4, 3, _GOLD), (5, 3, _GOLD),
    (2, 4, _GOLD), (3, 4, _WHITE), (4, 4, _WHITE), (5, 4, _GOLD),
    (2, 5, _GOLD), (3, 5, _GOLD), (4, 5, _GOLD), (5, 5, _GOLD),
    (3, 6, _GOLD), (4, 6, _GOLD),
])

# --- robot: robot face ---
_register("robot", [
    (3, 0, _INK), (4, 0, _INK),
    (1, 1, _INK), (2, 1, _INK), (3, 1, _INK), (4, 1, _INK), (5, 1, _INK), (6, 1, _INK),
    (1, 2, _INK), (2, 2, _GREEN), (3, 2, _INK), (4, 2, _INK), (5, 2, _GREEN), (6, 2, _INK),
    (1, 3, _INK), (2, 3, _INK), (3, 3, _INK), (4, 3, _INK), (5, 3, _INK), (6, 3, _INK),
    (2, 4, _INK), (3, 4, _PARCHMENT), (4, 4, _PARCHMENT), (5, 4, _INK),
    (1, 5, _INK), (2, 5, _INK), (3, 5, _INK), (4, 5, _INK), (5, 5, _INK), (6, 5, _INK),
    (0, 3, _INK), (7, 3, _INK),
])

# --- gamepad: game controller ---
_register("gamepad", [
    (1, 1, _INK), (2, 1, _INK), (3, 1, _INK), (4, 1, _INK), (5, 1, _INK), (6, 1, _INK),
    (0, 2, _INK), (1, 2, _INK), (2, 2, _INK), (3, 2, _INK), (4, 2, _INK), (5, 2, _INK), (6, 2, _INK), (7, 2, _INK),
    (0, 3, _INK), (1, 3, _PARCHMENT), (2, 3, _INK), (3, 3, _INK), (4, 3, _INK), (5, 3, _GREEN), (6, 3, _INK), (7, 3, _INK),
    (0, 4, _INK), (1, 4, _INK), (2, 4, _INK), (3, 4, _INK), (4, 4, _INK), (5, 4, _INK), (6, 4, _FLAME), (7, 4, _INK),
    (1, 5, _INK), (2, 5, _INK), (5, 5, _INK), (6, 5, _INK),
])

# --- clock: clock face ---
_register("clock", [
    (2, 0, _INK), (3, 0, _INK), (4, 0, _INK), (5, 0, _INK),
    (1, 1, _INK), (2, 1, _PARCHMENT), (3, 1, _PARCHMENT), (4, 1, _PARCHMENT), (5, 1, _PARCHMENT), (6, 1, _INK),
    (1, 2, _PARCHMENT), (2, 2, _PARCHMENT), (3, 2, _PARCHMENT), (4, 2, _PARCHMENT), (5, 2, _PARCHMENT), (6, 2, _PARCHMENT),
    (1, 3, _PARCHMENT), (2, 3, _PARCHMENT), (3, 3, _PARCHMENT), (4, 3, _GOLD), (5, 3, _PARCHMENT), (6, 3, _PARCHMENT),
    (1, 4, _PARCHMENT), (2, 4, _PARCHMENT), (3, 4, _PARCHMENT), (4, 4, _GOLD), (5, 4, _PARCHMENT), (6, 4, _PARCHMENT),
    (1, 5, _PARCHMENT), (2, 5, _PARCHMENT), (3, 5, _PARCHMENT), (4, 5, _PARCHMENT), (5, 5, _PARCHMENT), (6, 5, _PARCHMENT),
    (2, 6, _INK), (3, 6, _INK), (4, 6, _INK), (5, 6, _INK),
])

# --- search: magnifying glass ---
_register("search", [
    (2, 0, _INK), (3, 0, _INK), (4, 0, _INK),
    (1, 1, _INK), (2, 1, _PARCHMENT), (3, 1, _PARCHMENT), (4, 1, _PARCHMENT), (5, 1, _INK),
    (1, 2, _PARCHMENT), (2, 2, _PARCHMENT), (3, 2, _PARCHMENT), (4, 2, _PARCHMENT), (5, 2, _PARCHMENT),
    (1, 3, _PARCHMENT), (2, 3, _PARCHMENT), (3, 3, _PARCHMENT), (4, 3, _PARCHMENT), (5, 3, _INK),
    (2, 4, _INK), (3, 4, _INK), (4, 4, _INK), (5, 4, _INK), (6, 4, _GOLD_DARK),
    (6, 5, _GOLD_DARK), (7, 5, _GOLD_DARK),
    (7, 6, _GOLD_DARK),
])

# --- chart: bar chart ---
_register("chart", [
    (1, 1, _GREEN), (2, 1, _GREEN),
    (1, 2, _GREEN), (2, 2, _GREEN), (4, 2, _GOLD), (5, 2, _GOLD),
    (1, 3, _GREEN), (2, 3, _GREEN), (4, 3, _GOLD), (5, 3, _GOLD),
    (1, 4, _GREEN), (2, 4, _GREEN), (4, 4, _GOLD), (5, 4, _GOLD), (6, 4, _FLAME), (7, 4, _FLAME),
    (1, 5, _GREEN), (2, 5, _GREEN), (4, 5, _GOLD), (5, 5, _GOLD), (6, 5, _FLAME), (7, 5, _FLAME),
    (0, 6, _INK), (1, 6, _INK), (2, 6, _INK), (3, 6, _INK), (4, 6, _INK), (5, 6, _INK), (6, 6, _INK), (7, 6, _INK),
])

# --- crown: crown ---
_register("crown", [
    (0, 1, _GOLD), (3, 1, _GOLD), (4, 1, _GOLD), (7, 1, _GOLD),
    (0, 2, _GOLD), (1, 2, _GOLD), (3, 2, _GOLD), (4, 2, _GOLD), (6, 2, _GOLD), (7, 2, _GOLD),
    (0, 3, _GOLD), (1, 3, _GOLD), (2, 3, _GOLD), (3, 3, _GOLD), (4, 3, _GOLD), (5, 3, _GOLD), (6, 3, _GOLD), (7, 3, _GOLD),
    (0, 4, _GOLD), (1, 4, _GOLD), (2, 4, _GOLD), (3, 4, _GOLD), (4, 4, _GOLD), (5, 4, _GOLD), (6, 4, _GOLD), (7, 4, _GOLD),
    (0, 5, _GOLD_DARK), (1, 5, _FLAME), (2, 5, _GOLD_DARK), (3, 5, _GOLD_DARK), (4, 5, _GOLD_DARK), (5, 5, _GOLD_DARK), (6, 5, _FLAME), (7, 5, _GOLD_DARK),
])

# --- clipboard: clipboard ---
_register("clipboard", [
    (2, 0, _GOLD_DARK), (3, 0, _GOLD_DARK), (4, 0, _GOLD_DARK), (5, 0, _GOLD_DARK),
    (1, 1, _PARCHMENT), (2, 1, _PARCHMENT), (3, 1, _PARCHMENT), (4, 1, _PARCHMENT), (5, 1, _PARCHMENT), (6, 1, _PARCHMENT),
    (1, 2, _PARCHMENT), (2, 2, _INK), (3, 2, _INK), (4, 2, _INK), (5, 2, _INK), (6, 2, _PARCHMENT),
    (1, 3, _PARCHMENT), (2, 3, _PARCHMENT), (3, 3, _PARCHMENT), (4, 3, _PARCHMENT), (5, 3, _PARCHMENT), (6, 3, _PARCHMENT),
    (1, 4, _PARCHMENT), (2, 4, _INK), (3, 4, _INK), (4, 4, _INK), (5, 4, _PARCHMENT), (6, 4, _PARCHMENT),
    (1, 5, _PARCHMENT), (2, 5, _PARCHMENT), (3, 5, _PARCHMENT), (4, 5, _PARCHMENT), (5, 5, _PARCHMENT), (6, 5, _PARCHMENT),
    (1, 6, _PARCHMENT), (2, 6, _INK), (3, 6, _INK), (4, 6, _INK), (5, 6, _INK), (6, 6, _PARCHMENT),
    (1, 7, _PARCHMENT), (2, 7, _PARCHMENT), (3, 7, _PARCHMENT), (4, 7, _PARCHMENT), (5, 7, _PARCHMENT), (6, 7, _PARCHMENT),
])

# --- bookmark: bookmark ribbon ---
_register("bookmark", [
    (2, 0, _FLAME), (3, 0, _FLAME), (4, 0, _FLAME), (5, 0, _FLAME),
    (2, 1, _FLAME), (3, 1, _FLAME), (4, 1, _FLAME), (5, 1, _FLAME),
    (2, 2, _FLAME), (3, 2, _FLAME), (4, 2, _FLAME), (5, 2, _FLAME),
    (2, 3, _FLAME), (3, 3, _FLAME), (4, 3, _FLAME), (5, 3, _FLAME),
    (2, 4, _FLAME), (3, 4, _FLAME), (4, 4, _FLAME), (5, 4, _FLAME),
    (2, 5, _FLAME), (5, 5, _FLAME),
    (2, 6, _FLAME), (5, 6, _FLAME),
    (3, 5, _FLAME_ORANGE), (4, 5, _FLAME_ORANGE),
])

# --- play: right-pointing triangle ---
_register("play", [
    (2, 1, _GREEN),
    (2, 2, _GREEN), (3, 2, _GREEN),
    (2, 3, _GREEN), (3, 3, _GREEN), (4, 3, _GREEN),
    (2, 4, _GREEN), (3, 4, _GREEN), (4, 4, _GREEN), (5, 4, _GREEN),
    (2, 5, _GREEN), (3, 5, _GREEN), (4, 5, _GREEN),
    (2, 6, _GREEN), (3, 6, _GREEN),
    (2, 7, _GREEN),
])

# --- checkmark: check/tick mark ---
_register("checkmark", [
    (6, 1, _GREEN),
    (5, 2, _GREEN), (6, 2, _GREEN),
    (4, 3, _GREEN), (5, 3, _GREEN),
    (1, 4, _GREEN), (3, 4, _GREEN), (4, 4, _GREEN),
    (2, 5, _GREEN), (3, 5, _GREEN),
    (2, 6, _GREEN),
])

# --- person: person silhouette ---
_register("person", [
    (3, 0, _INK), (4, 0, _INK),
    (2, 1, _INK), (3, 1, _INK), (4, 1, _INK), (5, 1, _INK),
    (3, 2, _INK), (4, 2, _INK),
    (3, 3, _INK), (4, 3, _INK),
    (1, 4, _INK), (2, 4, _INK), (3, 4, _INK), (4, 4, _INK), (5, 4, _INK), (6, 4, _INK),
    (0, 5, _INK), (1, 5, _INK), (2, 5, _INK), (3, 5, _INK), (4, 5, _INK), (5, 5, _INK), (6, 5, _INK), (7, 5, _INK),
    (0, 6, _INK), (1, 6, _INK), (2, 6, _INK), (5, 6, _INK), (6, 6, _INK), (7, 6, _INK),
])

# --- construction: warning/barricade ---
_register("construction", [
    (3, 0, _GOLD), (4, 0, _GOLD),
    (2, 1, _GOLD), (3, 1, _FLAME), (4, 1, _FLAME), (5, 1, _GOLD),
    (1, 2, _GOLD), (2, 2, _FLAME), (3, 2, _GOLD), (4, 2, _GOLD), (5, 2, _FLAME), (6, 2, _GOLD),
    (0, 3, _GOLD), (1, 3, _FLAME), (2, 3, _GOLD), (3, 3, _GOLD), (4, 3, _GOLD), (5, 3, _GOLD), (6, 3, _FLAME), (7, 3, _GOLD),
    (0, 4, _GOLD), (1, 4, _GOLD), (2, 4, _GOLD), (3, 4, _GOLD), (4, 4, _GOLD), (5, 4, _GOLD), (6, 4, _GOLD), (7, 4, _GOLD),
    (0, 5, _FLAME), (1, 5, _GOLD), (2, 5, _GOLD), (3, 5, _FLAME), (4, 5, _FLAME), (5, 5, _GOLD), (6, 5, _GOLD), (7, 5, _FLAME),
])

# --- house: house/building ---
_register("house", [
    (3, 0, _FLAME), (4, 0, _FLAME),
    (2, 1, _FLAME), (3, 1, _FLAME), (4, 1, _FLAME), (5, 1, _FLAME),
    (1, 2, _FLAME), (2, 2, _FLAME), (3, 2, _FLAME), (4, 2, _FLAME), (5, 2, _FLAME), (6, 2, _FLAME),
    (0, 3, _FLAME), (1, 3, _FLAME), (2, 3, _FLAME), (3, 3, _FLAME), (4, 3, _FLAME), (5, 3, _FLAME), (6, 3, _FLAME), (7, 3, _FLAME),
    (1, 4, _PARCHMENT), (2, 4, _PARCHMENT), (3, 4, _PARCHMENT), (4, 4, _PARCHMENT), (5, 4, _PARCHMENT), (6, 4, _PARCHMENT),
    (1, 5, _PARCHMENT), (2, 5, _BLUE), (3, 5, _PARCHMENT), (4, 5, _GOLD_DARK), (5, 5, _GOLD_DARK), (6, 5, _PARCHMENT),
    (1, 6, _PARCHMENT), (2, 6, _BLUE), (3, 6, _PARCHMENT), (4, 6, _GOLD_DARK), (5, 6, _GOLD_DARK), (6, 6, _PARCHMENT),
])

# --- key: key ---
_register("key", [
    (1, 1, _GOLD), (2, 1, _GOLD),
    (0, 2, _GOLD), (1, 2, _GOLD), (2, 2, _GOLD), (3, 2, _GOLD),
    (1, 3, _GOLD), (2, 3, _GOLD), (3, 3, _GOLD), (4, 3, _GOLD), (5, 3, _GOLD), (6, 3, _GOLD), (7, 3, _GOLD),
    (0, 4, _GOLD), (1, 4, _GOLD), (2, 4, _GOLD), (3, 4, _GOLD),
    (1, 5, _GOLD), (2, 5, _GOLD),
    (5, 4, _GOLD), (6, 4, _GOLD),
    (7, 4, _GOLD),
])

# --- hourglass: hourglass ---
_register("hourglass", [
    (1, 0, _GOLD_DARK), (2, 0, _GOLD_DARK), (3, 0, _GOLD_DARK), (4, 0, _GOLD_DARK), (5, 0, _GOLD_DARK), (6, 0, _GOLD_DARK),
    (2, 1, _PARCHMENT), (3, 1, _PARCHMENT), (4, 1, _PARCHMENT), (5, 1, _PARCHMENT),
    (3, 2, _PARCHMENT), (4, 2, _PARCHMENT),
    (3, 3, _GOLD), (4, 3, _GOLD),
    (3, 4, _GOLD), (4, 4, _GOLD),
    (3, 5, _PARCHMENT), (4, 5, _PARCHMENT),
    (2, 6, _PARCHMENT), (3, 6, _PARCHMENT), (4, 6, _PARCHMENT), (5, 6, _PARCHMENT),
    (1, 7, _GOLD_DARK), (2, 7, _GOLD_DARK), (3, 7, _GOLD_DARK), (4, 7, _GOLD_DARK), (5, 7, _GOLD_DARK), (6, 7, _GOLD_DARK),
])

# --- scroll: scroll/document ---
_register("scroll", [
    (2, 0, _GOLD_DARK), (3, 0, _GOLD_DARK), (4, 0, _GOLD_DARK), (5, 0, _GOLD_DARK), (6, 0, _GOLD_DARK),
    (1, 1, _PARCHMENT), (2, 1, _PARCHMENT), (3, 1, _PARCHMENT), (4, 1, _PARCHMENT), (5, 1, _PARCHMENT), (6, 1, _GOLD_DARK),
    (1, 2, _PARCHMENT), (2, 2, _INK), (3, 2, _INK), (4, 2, _INK), (5, 2, _PARCHMENT), (6, 2, _PARCHMENT),
    (1, 3, _PARCHMENT), (2, 3, _PARCHMENT), (3, 3, _PARCHMENT), (4, 3, _PARCHMENT), (5, 3, _PARCHMENT), (6, 3, _PARCHMENT),
    (1, 4, _PARCHMENT), (2, 4, _INK), (3, 4, _INK), (4, 4, _INK), (5, 4, _INK), (6, 4, _PARCHMENT),
    (1, 5, _PARCHMENT), (2, 5, _PARCHMENT), (3, 5, _PARCHMENT), (4, 5, _PARCHMENT), (5, 5, _PARCHMENT), (6, 5, _PARCHMENT),
    (1, 6, _GOLD_DARK), (2, 6, _GOLD_DARK), (3, 6, _GOLD_DARK), (4, 6, _GOLD_DARK), (5, 6, _GOLD_DARK), (6, 6, _GOLD_DARK),
])


# --- settings gear ---
_register("gear", [
    (3, 0, _INK), (4, 0, _INK),
    (1, 1, _INK), (2, 1, _INK), (3, 1, _INK), (4, 1, _INK), (5, 1, _INK), (6, 1, _INK),
    (0, 2, _INK), (1, 2, _INK), (2, 2, _PARCHMENT), (3, 2, _PARCHMENT), (4, 2, _PARCHMENT), (5, 2, _PARCHMENT), (6, 2, _INK), (7, 2, _INK),
    (0, 3, _INK), (2, 3, _PARCHMENT), (3, 3, _DARK), (4, 3, _DARK), (5, 3, _PARCHMENT), (7, 3, _INK),
    (0, 4, _INK), (2, 4, _PARCHMENT), (3, 4, _DARK), (4, 4, _DARK), (5, 4, _PARCHMENT), (7, 4, _INK),
    (0, 5, _INK), (1, 5, _INK), (2, 5, _PARCHMENT), (3, 5, _PARCHMENT), (4, 5, _PARCHMENT), (5, 5, _PARCHMENT), (6, 5, _INK), (7, 5, _INK),
    (1, 6, _INK), (2, 6, _INK), (3, 6, _INK), (4, 6, _INK), (5, 6, _INK), (6, 6, _INK),
    (3, 7, _INK), (4, 7, _INK),
])


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------

def render_icon_svg(name: str, size: int = 16, color: str | None = None) -> str:
    """Return an inline SVG string for the given icon.

    The SVG uses an 8x8 ``viewBox`` and renders at the specified *size*
    in device pixels.  The ``image-rendering: pixelated`` style keeps the
    pixel art crisp when scaled.

    If *color* is provided, all pixels are rendered in that color (monochrome
    tinting).  Otherwise, the icon's original palette is used.
    """
    pixels = _ICON_CATALOG.get(name)

    if pixels is None:
        # Fallback: question mark placeholder
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8"'
            f' width="{size}" height="{size}"'
            f' class="pixel-icon" role="img" aria-hidden="true"'
            f' style="image-rendering: pixelated;">'
            f'<rect x="2" y="1" width="4" height="1" fill="#8b8b9e"/>'
            f'<rect x="4" y="2" width="2" height="1" fill="#8b8b9e"/>'
            f'<rect x="3" y="3" width="2" height="1" fill="#8b8b9e"/>'
            f'<rect x="3" y="4" width="1" height="1" fill="#8b8b9e"/>'
            f'<rect x="3" y="6" width="1" height="1" fill="#8b8b9e"/>'
            f'</svg>'
        )

    # Build rect elements
    rects: list[str] = []
    seen: dict[tuple[int, int], str] = {}
    for x, y, c in pixels:
        seen[(x, y)] = color if color else c

    for (x, y), c in sorted(seen.items()):
        rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>')

    rect_block = "".join(rects)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8"'
        f' width="{size}" height="{size}"'
        f' class="pixel-icon" role="img" aria-hidden="true"'
        f' style="image-rendering: pixelated;">'
        f'{rect_block}'
        f'</svg>'
    )


def get_icon_names() -> list[str]:
    """Return a sorted list of all available icon names."""
    return sorted(_ICON_CATALOG.keys())
