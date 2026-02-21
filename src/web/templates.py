"""Shared Jinja2 templates instance with avatar and icon rendering globals."""

from fastapi.templating import Jinja2Templates
from markupsafe import Markup

from src.game.avatars import render_avatar_svg
from src.game.icons import render_icon_svg

templates = Jinja2Templates(directory="templates")


def _render_avatar(avatar_id: str, size: int = 32) -> Markup:
    """Render an avatar SVG, safe for use in templates."""
    return Markup(render_avatar_svg(avatar_id or "avatar_01", size=size))


def _render_icon(name: str, size: int = 16, color: str | None = None) -> Markup:
    """Render a pixel art icon as an <img> tag pointing to a static SVG file."""
    if color == "#5cdb5c":
        variant = f"{name}--green"
    elif color == "#f0c543":
        variant = f"{name}--gold"
    elif color:
        # Uncommon tint — fall back to inline SVG
        return Markup(render_icon_svg(name, size=size, color=color))
    else:
        variant = name
    return Markup(
        f'<img src="/static/icons/{variant}.svg" '
        f'width="{size}" height="{size}" '
        f'class="pixel-icon" role="img" aria-hidden="true" alt="">'
    )


templates.env.globals["render_avatar"] = _render_avatar
templates.env.globals["render_icon"] = _render_icon


def _title_hash(title: str) -> int:
    """Derive a stable integer from a title string."""
    return sum(ord(c) for c in title)


templates.env.filters["title_hash"] = _title_hash
