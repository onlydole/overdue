"""Custom exception classes for library incidents."""


class LibraryIncident(Exception):
    """Base exception for all library incidents."""

    def __init__(self, code: str, detail: str, status_code: int = 500):
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class VolumeNotFound(LibraryIncident):
    """TS-001: The requested volume is not on any shelf."""

    def __init__(self) -> None:
        super().__init__(
            code="TS-001",
            detail="That volume isn't on any of our shelves. Check the catalog and try again.",
            status_code=404,
        )


class ShelfNotFound(LibraryIncident):
    """TS-002: The requested shelf does not exist."""

    def __init__(self) -> None:
        super().__init__(
            code="TS-002",
            detail="That shelf isn't in our library. Check the catalog and try again.",
            status_code=404,
        )


class InvalidLibraryCard(LibraryIncident):
    """TS-003: The provided library card is invalid."""

    def __init__(self) -> None:
        super().__init__(
            code="TS-003",
            detail="You'll need a library card to access the stacks.",
            status_code=401,
        )


class ExpiredLibraryCard(LibraryIncident):
    """TS-004: The library card has expired."""

    def __init__(self) -> None:
        super().__init__(
            code="TS-004",
            detail="Your library card has expired. Renew at POST /librarians/login.",
            status_code=401,
        )


class InsufficientPermissions(LibraryIncident):
    """TS-005: The librarian lacks the required rank."""

    def __init__(self) -> None:
        super().__init__(
            code="TS-005",
            detail="Only the head librarian has access to the restricted section.",
            status_code=403,
        )


class DuplicateEntry(LibraryIncident):
    """TS-006: A conflicting entry already exists."""

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            code="TS-006",
            detail=detail or "A volume with that title is already shelved in this section.",
            status_code=409,
        )


class QuietHoursExceeded(LibraryIncident):
    """TS-007: Rate limit exceeded."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            code="TS-007",
            detail=f"The librarian says you're being too loud! Try again in {retry_after}s.",
            status_code=429,
        )


class ValidationIncident(LibraryIncident):
    """TS-008: Request validation failed."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            code="TS-008",
            detail=detail,
            status_code=422,
        )


class VolumeTooLarge(LibraryIncident):
    """TS-011: The volume content exceeds the maximum allowed size."""

    def __init__(self, max_size_kb: int) -> None:
        super().__init__(
            code="TS-011",
            detail=f"That volume is too thick for our shelves. Maximum: {max_size_kb}KB.",
            status_code=413,
        )


class DeprecatedFeature(LibraryIncident):
    """TS-012: A deprecated feature or config option was used."""

    def __init__(self, feature: str, alternative: str) -> None:
        super().__init__(
            code="TS-012",
            detail=f"'{feature}' is deprecated. Use '{alternative}' instead.",
            status_code=400,
        )
