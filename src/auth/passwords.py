"""Password hashing helpers for librarian credentials."""

from __future__ import annotations

import hashlib

import bcrypt

_BCRYPT_SHA256_PREFIX = "$overdue-sha256-bcrypt$"
_BCRYPT_PASSWORD_LIMIT = 72


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")


def _bcrypt_secret(password: str) -> bytes:
    return hashlib.sha256(_password_bytes(password)).hexdigest().encode("ascii")


def hash_password(password: str) -> str:
    """Hash a password without bcrypt's 72-byte input limit."""
    hashed = bcrypt.hashpw(_bcrypt_secret(password), bcrypt.gensalt()).decode("ascii")
    return f"{_BCRYPT_SHA256_PREFIX}{hashed}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify current hashes and legacy raw bcrypt hashes."""
    if hashed_password.startswith(_BCRYPT_SHA256_PREFIX):
        stored_hash = hashed_password.removeprefix(_BCRYPT_SHA256_PREFIX)
        return _check_bcrypt(_bcrypt_secret(password), stored_hash)

    password_bytes = _password_bytes(password)
    if _check_bcrypt(password_bytes, hashed_password):
        return True

    if len(password_bytes) > _BCRYPT_PASSWORD_LIMIT:
        return _check_bcrypt(password_bytes[:_BCRYPT_PASSWORD_LIMIT], hashed_password)

    return False


def _check_bcrypt(secret: bytes, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(secret, hashed_password.encode("ascii"))
    except ValueError:
        return False
