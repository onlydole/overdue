"""Application settings loaded from environment variables."""

import hashlib
import warnings
from functools import cached_property

from pydantic_settings import BaseSettings

_SECRET_KEY_MIN_BYTES = 32

# Known placeholder secrets shipped in source/compose defaults. Deploying with
# any of these means the JWT signing key and session secret are public, which
# lets anyone forge a library card and impersonate any librarian (including a
# Head Librarian). Startup warns loudly when one of these is in effect.
_INSECURE_DEFAULT_SECRETS = frozenset(
    {
        "change-me-in-production-please-set-a-strong-secret-key",
        "change-me-in-production",
    }
)


class Settings(BaseSettings):
    """Overdue application configuration.

    All settings can be overridden via environment variables prefixed with ``OVERDUE_``.
    """

    model_config = {"env_prefix": "OVERDUE_"}

    app_name: str = "Overdue"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./overdue.db"
    secret_key: str = "change-me-in-production-please-set-a-strong-secret-key"
    token_expiry_minutes: int = 60  # 1 hour
    token_refresh_window_minutes: int = 15  # refresh allowed in last 15 min
    cors_origins: list[str] = ["*"]  # deprecated -- use allowed_origins
    allowed_origins: list[str] = ["*"]
    host: str = "0.0.0.0"
    port: int = 8000
    # Set true behind HTTPS so the session cookie carrying the library card is
    # only sent over TLS (Secure flag). Defaults false so the http://localhost
    # demo keeps working; turn on for any real deployment.
    session_https_only: bool = False
    webhook_secret: str = ""
    dewey_recalc_interval_minutes: int = 15
    dewey_decay_rate: int = 3  # points lost per decay unit
    dewey_decay_seconds: int = 10  # seconds per decay unit (10 = fast demo, 86400 = realistic daily)
    streak_cooldown_seconds: int = 5  # seconds between reviews for streak (5 = fast demo, 86400 = daily)
    search_min_score: float = 0.3
    max_volume_size_kb: int = 512  # max content size in KB

    @cached_property
    def signing_secret_key(self) -> str:
        """Return an HMAC-safe signing key (>=32 bytes for HS256)."""
        raw = (self.secret_key or "").encode("utf-8")
        if len(raw) >= _SECRET_KEY_MIN_BYTES:
            return self.secret_key
        return hashlib.sha256(raw).hexdigest()

    def is_using_insecure_secret(self) -> bool:
        """True when the signing secret is a known public placeholder."""
        return (self.secret_key or "") in _INSECURE_DEFAULT_SECRETS

    def get_origins(self) -> list[str]:
        """Return the effective CORS origins, preferring allowed_origins."""
        if self.cors_origins != ["*"]:
            warnings.warn(
                "OVERDUE_CORS_ORIGINS is deprecated. Use OVERDUE_ALLOWED_ORIGINS instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return self.cors_origins
        return self.allowed_origins

    def cors_allow_credentials(self) -> bool:
        """Whether to allow credentialed CORS.

        A wildcard origin combined with credentials is forbidden by the CORS
        spec and unsafe (Starlette would reflect the caller's Origin), so
        credentials are only enabled for an explicit origin allowlist.
        """
        return "*" not in self.get_origins()


settings = Settings()
