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
    token_expiry_minutes: int = 1440  # 24 hours
    cors_origins: list[str] = ["*"]
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
