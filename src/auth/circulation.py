"""Role-based permissions (the circulation desk)."""

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException

from src.auth.library_card import verify_library_card
from src.config.defaults import RANKS
from src.errors.incidents import InsufficientPermissions

# Librarians at this rank or above may curate any volume/shelf in the library;
# everyone else may only manage what they personally created.
CURATOR_ROLE = "Head Librarian"


def get_rank_level(role: str) -> int:
    """Get the numeric level of a rank."""
    for i, (rank_name, _) in enumerate(RANKS):
        if rank_name == role:
            return i
    return 0


def is_curator(payload: dict[str, Any]) -> bool:
    """True if the actor holds the curator rank (library-wide management rights)."""
    return get_rank_level(payload.get("role", "Page")) >= get_rank_level(CURATOR_ROLE)


def can_manage_resource(payload: dict[str, Any], owner_id: int) -> bool:
    """Authorize a mutation: the actor must own the resource or be a curator.

    Prevents broken-object-level-authorization (IDOR): without this, any
    authenticated librarian could edit or delete volumes and shelves created
    by others.
    """
    try:
        actor_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return False
    return actor_id == owner_id or is_curator(payload)


def require_resource_owner(
    payload: dict[str, Any],
    owner_id: int,
    detail: str = "Only the keeper of this item or a head librarian may change it.",
) -> None:
    """Raise a 403 incident unless the actor may manage the owned resource.

    ``detail`` lets callers give a resource-specific message (volume vs shelf).
    """
    if not can_manage_resource(payload, owner_id):
        raise InsufficientPermissions(detail)


def require_role(minimum_role: str) -> Callable[..., dict[str, Any]]:
    """Create a dependency that requires a minimum librarian rank."""
    minimum_level = get_rank_level(minimum_role)

    def check_role(payload: dict[str, Any] = Depends(verify_library_card)) -> dict[str, Any]:
        user_role = payload.get("role", "Page")
        user_level = get_rank_level(user_role)

        if user_level < minimum_level:
            raise HTTPException(
                status_code=403,
                detail="Only the head librarian has access to the restricted section.",
            )
        return payload

    return check_role
