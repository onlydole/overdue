"""Rate limiting configuration -- quiet hours in the library."""

from dataclasses import dataclass

from src.config.defaults import QUIET_HOURS_BURST, QUIET_HOURS_REQUESTS_PER_MINUTE


@dataclass(frozen=True)
class QuietHoursPolicy:
    """Defines rate-limiting behaviour for API consumers."""

    requests_per_minute: int = QUIET_HOURS_REQUESTS_PER_MINUTE
    burst: int = QUIET_HOURS_BURST
