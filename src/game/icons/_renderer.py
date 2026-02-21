"""SVG renderer for 16x16 pixel art icons."""

from __future__ import annotations

from src.game.icons._palette import INK_BASE


def _build_rects(
    pixels: list[tuple[int, int, str]],
    color: str | None = None,
) -> str:
    """Deduplicate pixels and return a joined string of ``<rect>`` elements."""
    seen: dict[tuple[int, int], str] = {}
    for x, y, c in pixels:
        seen[(x, y)] = color if color else c
    parts: list[str] = []
    for (x, y), c in sorted(seen.items()):
        parts.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>')
    return "".join(parts)


def render_icon_svg(
    name: str,
    size: int = 16,
    color: str | None = None,
    *,
    _catalog: dict[str, list[tuple[int, int, str]]] | None = None,
) -> str:
    """Return an inline SVG string for the given icon.

    The SVG uses a 16x16 ``viewBox`` and renders at the specified *size*
    in device pixels.  The ``image-rendering: pixelated`` style keeps the
    pixel art crisp when scaled.

    If *color* is provided, all pixels are rendered in that color (monochrome
    tinting).  Otherwise, the icon's original palette is used.

    The *_catalog* parameter is injected by ``__init__.py`` to avoid circular
    imports.
    """
    if _catalog is None:
        _catalog = {}

    pixels = _catalog.get(name)

    if pixels is None:
        # Fallback: question mark placeholder at 16x16
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"'
            f' width="{size}" height="{size}"'
            f' class="pixel-icon" role="img" aria-hidden="true"'
            f' style="image-rendering: pixelated;">'
            f'<rect x="5" y="2" width="6" height="1" fill="{INK_BASE}"/>'
            f'<rect x="9" y="3" width="3" height="2" fill="{INK_BASE}"/>'
            f'<rect x="7" y="5" width="3" height="2" fill="{INK_BASE}"/>'
            f'<rect x="7" y="7" width="2" height="1" fill="{INK_BASE}"/>'
            f'<rect x="7" y="10" width="2" height="2" fill="{INK_BASE}"/>'
            f"</svg>"
        )

    rect_block = _build_rects(pixels, color)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"'
        f' width="{size}" height="{size}"'
        f' class="pixel-icon" role="img" aria-hidden="true"'
        f' style="image-rendering: pixelated;">'
        f"{rect_block}"
        f"</svg>"
    )


def render_icon_svg_bare(
    name: str,
    color: str | None = None,
    *,
    _catalog: dict[str, list[tuple[int, int, str]]] | None = None,
) -> str | None:
    """Return a bare SVG string (no width/height/class/style) for static files.

    Returns ``None`` if *name* is not in the catalog.
    """
    if _catalog is None:
        _catalog = {}

    pixels = _catalog.get(name)
    if pixels is None:
        return None

    rect_block = _build_rects(pixels, color)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        f"{rect_block}"
        f"</svg>"
    )
