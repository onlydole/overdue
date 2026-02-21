"""JWT token (library card) generation and validation."""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.config.settings import settings

ALGORITHM = "HS256"
security = HTTPBearer()


def create_library_card(librarian_id: int, username: str, role: str) -> str:
    """Issue a new library card (JWT token)."""
    expire = datetime.utcnow() + timedelta(minutes=settings.token_expiry_minutes)
    payload = {
        "sub": str(librarian_id),
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_library_card(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate a library card and return the decoded payload."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=401,
                detail="You'll need a library card to access the stacks.",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Your library card has expired. Renew at POST /librarians/login.",
        )
