"""Shared Jinja2 templates instance with avatar rendering global."""

from fastapi.templating import Jinja2Templates
from markupsafe import Markup

from src.game.avatars import render_avatar_svg

templates = Jinja2Templates(directory="templates")


def _render_avatar(avatar_id: str, size: int = 32) -> Markup:
    """Render an avatar SVG, safe for use in templates."""
    return Markup(render_avatar_svg(avatar_id or "avatar_01", size=size))


templates.env.globals["render_avatar"] = _render_avatar
