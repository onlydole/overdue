"""Pydantic models for librarians."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LibrarianCreate(BaseModel):
    """Request body for librarian registration."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class LibrarianLogin(BaseModel):
    """Request body for librarian login."""

    username: str
    password: str


class LibrarianResponse(BaseModel):
    """Public librarian profile."""

    id: int
    username: str
    email: str
    role: str
    total_xp: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LibraryCard(BaseModel):
    """JWT token response (library card)."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
