"""Application settings loaded from environment variables."""

import warnings

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Overdue application configuration.

    All settings can be overridden via environment variables prefixed with ``OVERDUE_``.
    """

    model_config = {"env_prefix": "OVERDUE_"}

    app_name: str = "Overdue"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./overdue.db"
    secret_key: str = "change-me-in-production"
    token_expiry_minutes: int = 60  # 1 hour
    token_refresh_window_minutes: int = 15  # refresh allowed in last 15 min
    cors_origins: list[str] = ["*"]  # deprecated -- use allowed_origins
    allowed_origins: list[str] = ["*"]
    host: str = "0.0.0.0"
    port: int = 8000
    webhook_secret: str = ""
    dewey_recalc_interval_minutes: int = 15
    dewey_decay_rate: int = 3  # points lost per decay unit
    dewey_decay_seconds: int = 10  # seconds per decay unit (10 = fast demo, 86400 = realistic daily)
    streak_cooldown_seconds: int = 5  # seconds between reviews for streak (5 = fast demo, 86400 = daily)
    search_min_score: float = 0.3
    max_volume_size_kb: int = 512  # max content size in KB

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


settings = Settings()
