"""Small shared utilities."""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Current UTC time as a naive datetime.

    The database stores naive UTC timestamps, so this strips tzinfo to keep
    stored and computed datetimes directly comparable.
    """
    return datetime.now(UTC).replace(tzinfo=None)
