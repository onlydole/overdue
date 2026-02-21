"""Application settings loaded from environment variables."""

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
    cors_origins: list[str] = ["*"]
    host: str = "0.0.0.0"
    port: int = 8000
    webhook_secret: str = ""
    dewey_recalc_interval_minutes: int = 15
    search_min_score: float = 0.3


settings = Settings()
