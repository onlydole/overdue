"""Shelf CLI commands."""

import typer
from rich.table import Table

from src.cli.helpers import console, get_client, require_auth

app = typer.Typer(help="Shelf management commands.")


@app.command("list")
def list_shelves() -> None:
    """List all shelves in the library."""
    with get_client() as client:
        resp = client.get("/api/shelves/")

    if resp.status_code != 200:
        console.print("[red]Failed to fetch shelves.[/red]")
        raise SystemExit(1)

    data = resp.json()
    table = Table(title="Library Shelves")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="gold1")
    table.add_column("Volumes", justify="right")
    table.add_column("Avg Dewey", justify="right")

    for shelf in data.get("items", []):
        score = shelf.get("average_dewey_score", 0)
        score_color = "green" if score >= 75 else "yellow" if score >= 50 else "red"
        table.add_row(
            str(shelf["id"]),
            shelf["name"],
            str(shelf.get("volume_count", 0)),
            f"[{score_color}]{score}[/{score_color}]",
        )

    console.print(table)


@app.command("create")
def create_shelf(
    name: str = typer.Argument(help="Shelf name"),
    description: str = typer.Option("", help="Shelf description"),
) -> None:
    """Create a new shelf."""
    require_auth()

    payload = {"name": name}
    if description:
        payload["description"] = description

    with get_client() as client:
        resp = client.post("/api/shelves/", json=payload)

    if resp.status_code == 201:
        data = resp.json()
        console.print(f"[green]Shelf '{data['name']}' created (ID: {data['id']}).[/green]")
    else:
        console.print(f"[red]Failed: {resp.json().get('detail', resp.text)}[/red]")
        raise SystemExit(1)
