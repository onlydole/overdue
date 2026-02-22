"""GBA-style 'Heroic Librarian' avatars.

Provides unique, hand-crafted pixel silhouettes for each librarian,
inspired by classic 32-bit RPG sprites.
"""

from __future__ import annotations

AVATAR_CATALOG: dict[str, dict] = {
    "avatar_01": {
        "name": "Sol",
        "role_title": "Venus Scribe",
        "description": "Determined and brave, guarding the core earth-scripts.",
        "material": "cloth",
        "primary": "#f0c543",
        "secondary": "#3d7ab3",
        "outline": "#11131a",
        "path": "M12 4h8v2h4v4h2v12h-2v4h-4v2h-12v-2h-4v-4h-2v-12h2v-4h4v-2z", # Spiky hair base
        "accents": "M13 14h6v2h2v4h-2v2h-6v-2h-2v-4h2z M15 7h2v2h-2z" # Scarf
    },
    "avatar_02": {
        "name": "Zephyr",
        "role_title": "Jupiter Librarian",
        "description": "A light-footed scholar of the high clouds.",
        "material": "spectral",
        "primary": "#b76ef0",
        "secondary": "#f0e6d3",
        "outline": "#11131a",
        "path": "M14 3h6v2h4v2h2v16h-2v4h-4v2h-10v-2h-4v-4h-2v-16h2v-2h4v-2z", # Tall cape base
        "accents": "M14 12h8v10h-8z M16 5h2v2h-2z" # Flowing robes
    },
    "avatar_03": {
        "name": "Pyre",
        "role_title": "Mars Warden",
        "description": "The fiery protector of the forbidden scrolls.",
        "material": "chitin",
        "primary": "#e8563e",
        "secondary": "#5a251d",
        "outline": "#11131a",
        "path": "M10 5h12v2h4v18h-4v4h-12v-4h-4v-18h4z", # Bulkier base
        "accents": "M11 10h10v12h-10z M12 6h8v2h-8z" # Armor plating
    },
    "avatar_04": {
        "name": "Tide",
        "role_title": "Mercury Scholar",
        "description": "A healer of brittle margins and water-damaged ink.",
        "material": "gelatin",
        "primary": "#7eb5e3",
        "secondary": "#ffffff",
        "outline": "#11131a",
        "path": "M14 4h6v2h4v18h-4v4h-10v-4h-4v-18h4z", # Hooded base
        "accents": "M14 6h6v16h-6z M15 5h4v1h-4z" # Long robes
    },
    "avatar_05": {
        "name": "Geo",
        "role_title": "Shadow Steward",
        "description": "A silent wanderer of the deep, forgotten stacks.",
        "material": "stone",
        "primary": "#8b7355",
        "secondary": "#232342",
        "outline": "#11131a",
        "path": "M12 3h10v2h4v4h2v16h-2v4h-14v-4h-2v-16h2z", # Cloaked base
        "accents": "M13 10h10v14h-10z M14 4h6v2h-6z" # Heavy cloak
    },
    "avatar_06": {
        "name": "Ash",
        "role_title": "Solar Annotator",
        "description": "Illuminates dark footnotes with bright ember-flare.",
        "material": "cloth",
        "primary": "#f07a3e",
        "secondary": "#f0c543",
        "outline": "#11131a",
        "path": "M14 4h6v2h4v4h2v14h-2v4h-10v-4h-4v-14h4v-4h2z", # Slender base
        "accents": "M14 12h8v8h-8z M16 6h4v4h-4z" # Vest and sash
    },
    "avatar_07": {
        "name": "Zen",
        "role_title": "Sutra Keeper",
        "description": "Master of physical shelves and mental archives.",
        "material": "stone",
        "primary": "#ffffff",
        "secondary": "#f0c543",
        "outline": "#11131a",
        "path": "M14 5h8v4h2v16h-2v4h-10v-4h-2v-16h4z", # Bald/shaved base
        "accents": "M15 14h6v10h-6z M16 10h4v2h-4z" # Simple prayer beads/vest
    },
    "avatar_08": {
        "name": "Thorn",
        "role_title": "Verdant Guard",
        "description": "Protects the living library of the great grove.",
        "material": "gelatin",
        "primary": "#5cdb5c",
        "secondary": "#3d9e3d",
        "outline": "#11131a",
        "path": "M12 4h8v2h4v4h2v14h-2v4h-12v-4h-4v-14h4v-4h2z", # Pointed ears base
        "accents": "M13 14h8v10h-8z M14 6h6v4h-6z" # Leaf-pattern tunic
    },
}

def _get_avatar_svg_content(avatar_id: str) -> str:
    meta = AVATAR_CATALOG.get(avatar_id, AVATAR_CATALOG["avatar_01"])
    
    # Heroic face and eyes are shared but positioned by class
    # Removed translate(8,8) to fill the 32x32 viewbox better
    return f"""
    <g class="avatar-root">
        <!-- Outline/Shadow -->
        <path d="{meta['path']}" fill="{meta['outline']}" opacity="0.4"/>
        <!-- Main Body Silhouette -->
        <path d="{meta['path']}" fill="{meta['secondary']}" transform="scale(0.9) translate(1, 1)"/>
        <!-- Primary Accents -->
        <path d="{meta['accents']}" fill="{meta['primary']}"/>
        <!-- Heroic Face -->
        <path d="M15 9h2v2h-2z M14 10h4v2h-4z" fill="#f8efd9"/>
        <!-- Eyes -->
        <path d="M15 10h1v1h-1z M18 10h1v1h-1z" fill="{meta['outline']}" class="eye-blink"/>
        <!-- Highlight -->
        <path d="M14 6h2v1h-2z M20 10h1v4h-1z" fill="white" opacity="0.2"/>
    </g>
    """

def render_avatar_svg(avatar_id: str, size: int = 32) -> str:
    content = _get_avatar_svg_content(avatar_id)
    animation = f"""
    <style>
        @keyframes avatar-idle {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(1px); }} }}
        @keyframes blink {{ 0%, 90%, 100% {{ opacity: 1; }} 95% {{ opacity: 0; }} }}
        .avatar-root {{ animation: avatar-idle 1s steps(2) infinite; }}
        .eye-blink {{ animation: blink 4s infinite; }}
    </style>
    """
    # Changed viewBox to 32 32 for better scaling
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"'
        f' width="{size}" height="{size}" class="pixel-icon" role="img" aria-hidden="true"'
        f' style="image-rendering: pixelated;">'
        f"{animation}{content}</svg>"
    )

def render_avatar_svg_bare(avatar_id: str) -> str | None:
    # Changed viewBox to 32 32
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{_get_avatar_svg_content(avatar_id)}</svg>'

def get_avatar_choices() -> list[dict[str, str]]:
    return [
        {
            "id": aid,
            "name": m["name"],
            "role_title": m["role_title"],
            "description": m["description"],
            "material": m["material"]
        }
        for aid, m in AVATAR_CATALOG.items()
    ]
