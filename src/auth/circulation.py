"""Role-based permissions (the circulation desk)."""

from typing import Any

from fastapi import Depends, HTTPException

from src.auth.library_card import verify_library_card
from src.config.defaults import RANKS

# Librarians at this rank or above may curate any volume/shelf in the library;
# everyone else may only manage what they personally created.
CURATOR_ROLE = "Head Librarian"


def get_rank_level(role: str) -> int:
    """Get the numeric level of a rank."""
    for i, (rank_name, _) in enumerate(RANKS):
        if rank_name == role:
            return i
    return 0


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
    if actor_id == owner_id:
        return True
    return get_rank_level(payload.get("role", "Page")) >= get_rank_level(CURATOR_ROLE)


def require_resource_owner(payload: dict[str, Any], owner_id: int) -> None:
    """Raise 403 unless the actor may manage the owned resource."""
    if not can_manage_resource(payload, owner_id):
        raise HTTPException(
            status_code=403,
            detail="Only the volume's keeper or a head librarian may change it.",
        )


def require_role(minimum_role: str):
    """Create a dependency that requires a minimum librarian rank."""
    minimum_level = get_rank_level(minimum_role)

    def check_role(payload: dict = Depends(verify_library_card)) -> dict:
        user_role = payload.get("role", "Page")
        user_level = get_rank_level(user_role)

        if user_level < minimum_level:
            raise HTTPException(
                status_code=403,
                detail="Only the head librarian has access to the restricted section.",
            )
        return payload

    return check_role
