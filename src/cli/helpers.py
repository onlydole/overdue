"""Shared CLI utilities: API client, Rich console, formatting."""

import os
from pathlib import Path

import httpx
from rich.console import Console

console = Console()

TOKEN_DIR = Path.home() / ".overdue"
TOKEN_FILE = TOKEN_DIR / "token"


def get_base_url() -> str:
    return os.environ.get("OVERDUE_URL", "http://localhost:8000")


def save_token(token: str) -> None:
    # The token is a bearer credential: keep the directory and file private
    # so other local users can't read it and impersonate the librarian.
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_DIR.chmod(0o700)
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        # os.open's mode only applies at creation; tighten files that already
        # existed with wider permissions from earlier versions.
        os.fchmod(f.fileno(), 0o600)
        f.write(token)


def load_token() -> str | None:
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def clear_token() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_client() -> httpx.Client:
    token = load_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=get_base_url(), headers=headers, timeout=30.0)


def require_auth() -> str:
    token = load_token()
    if not token:
        console.print("[red]Not logged in. Run 'overdue login' first.[/red]")
        raise SystemExit(1)
    return token
