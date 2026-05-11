"""Password hashing behavior."""

import bcrypt

from src.auth.passwords import hash_password, verify_password


def test_hash_password_verifies_password() -> None:
    password = "LibraryCard1!"

    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password("WrongLibraryCard1!", hashed)


def test_hash_password_handles_long_passwords() -> None:
    password = f"{'A' * 80}library1!"

    hashed = hash_password(password)

    assert verify_password(password, hashed)


def test_verify_password_accepts_legacy_bcrypt_hashes() -> None:
    password = "LibraryCard1!"
    legacy_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

    assert verify_password(password, legacy_hash)
    assert not verify_password("WrongLibraryCard1!", legacy_hash)


def test_verify_password_accepts_legacy_truncated_long_passwords() -> None:
    password = f"{'A' * 80}library1!"
    password_bytes = password.encode("utf-8")
    legacy_hash = bcrypt.hashpw(password_bytes[:72], bcrypt.gensalt()).decode("ascii")

    assert verify_password(password, legacy_hash)


def test_verify_password_rejects_invalid_hashes() -> None:
    assert not verify_password("LibraryCard1!", "not-a-bcrypt-hash")
