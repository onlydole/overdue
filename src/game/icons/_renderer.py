"""SVG renderer for pixel art icons (supporting paths and rects)."""

from __future__ import annotations


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
    size: int = 24,
    color: str | None = None,
    *,
    _catalog: dict[str, str | list[tuple[int, int, str]]] | None = None,
) -> str:
    """Return an inline SVG string for the given icon.

    Supports both legacy pixel-lists (rendered as rects) and modern SVG paths.
    Default viewBox is 24x24 for high-fidelity icons.
    """
    if _catalog is None:
        _catalog = {}

    data = _catalog.get(name)

    if data is None:
        # Fallback: question mark
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
            f' width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2">'
            f'<path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />'
            f"</svg>"
        )

    # Handle legacy pixel lists (16x16)
    if isinstance(data, list):
        rect_block = _build_rects(data, color)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"'
            f' width="{size}" height="{size}"'
            f' class="pixel-icon" role="img" aria-hidden="true"'
            f' style="image-rendering: pixelated;">'
            f"{rect_block}"
            f"</svg>"
        )

    # Handle new path data (assumed 24x24 viewBox)
    # If color is provided, we use it for fill/stroke. 
    # The data string should contain the inner SVG elements (paths, etc).
    # We can inject the fill color into the parent SVG or the paths if they use "currentColor".
    style = f'style="color: {color};"' if color else ""
    
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
        f' width="{size}" height="{size}"'
        f' class="pixel-icon" role="img" aria-hidden="true"'
        f' {style}>'
        f"{data}"
        f"</svg>"
    )


def render_icon_svg_bare(
    name: str,
    color: str | None = None,
    *,
    _catalog: dict[str, str | list[tuple[int, int, str]]] | None = None,
) -> str | None:
    """Return a bare SVG string for static files."""
    if _catalog is None:
        _catalog = {}

    data = _catalog.get(name)
    if data is None:
        return None

    if isinstance(data, list):
        rect_block = _build_rects(data, color)
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">{rect_block}</svg>'

    style = f'style="color: {color};"' if color else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {style}>{data}</svg>'
