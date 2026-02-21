"""Role-based permissions (the circulation desk)."""

from fastapi import Depends, HTTPException

from src.auth.library_card import verify_library_card
from src.config.defaults import RANKS


def get_rank_level(role: str) -> int:
    """Get the numeric level of a rank."""
    for i, (rank_name, _) in enumerate(RANKS):
        if rank_name == role:
            return i
    return 0


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
