"""Authentication CLI commands."""

import typer
from rich.prompt import Prompt

from src.cli.helpers import clear_token, console, get_client, load_token, save_token

app = typer.Typer(help="Authentication commands.")


@app.command()
def login(
    username: str = typer.Option(None, help="Username"),
    password: str = typer.Option(None, help="Password", hide_input=True),
) -> None:
    """Log in and store your library card."""
    if not username:
        username = Prompt.ask("Username")
    if not password:
        password = Prompt.ask("Password", password=True)

    with get_client() as client:
        resp = client.post("/api/librarians/login", json={"username": username, "password": password})

    if resp.status_code == 200:
        data = resp.json()
        save_token(data["access_token"])
        console.print(f"[green]Welcome back, {username}! Library card saved.[/green]")
    else:
        console.print(f"[red]Login failed: {resp.json().get('detail', 'Unknown error')}[/red]")
        raise SystemExit(1)


@app.command()
def logout() -> None:
    """Clear your stored library card."""
    clear_token()
    console.print("[yellow]Library card cleared. Goodbye![/yellow]")


@app.command()
def whoami() -> None:
    """Show current logged-in user."""
    from src.cli.helpers import require_auth
    require_auth()

    with get_client() as client:
        resp = client.get("/api/librarians/me/xp")

    if resp.status_code == 200:
        data = resp.json()
        console.print(f"[gold1]Rank:[/gold1] {data['rank']}")
        console.print(f"[green]XP:[/green] {data['total_xp']} pages read")
        if data.get("next_rank"):
            console.print(f"[dim]Next rank: {data['next_rank']} ({data['xp_to_next_rank']} XP to go)[/dim]")
    else:
        console.print("[red]Session expired. Run 'overdue login' again.[/red]")
