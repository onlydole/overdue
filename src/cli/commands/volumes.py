"""Volume CLI commands."""

from pathlib import Path

import typer
from rich.table import Table

from src.cli.helpers import console, get_client, require_auth

app = typer.Typer(help="Volume management commands.")


@app.command("list")
def list_volumes(
    shelf_id: int | None = typer.Option(None, help="Filter by shelf ID"),
    sort: str = typer.Option("date", help="Sort by: dewey or date"),
    page: int = typer.Option(1, help="Page number"),
) -> None:
    """List volumes in the library."""
    params = {"page": page, "per_page": 20}
    if shelf_id:
        params["shelf_id"] = shelf_id

    with get_client() as client:
        resp = client.get("/api/volumes/", params=params)

    if resp.status_code != 200:
        console.print("[red]Failed to fetch volumes.[/red]")
        raise SystemExit(1)

    data = resp.json()
    items = data.get("items", [])

    if sort == "dewey":
        items.sort(key=lambda v: v.get("dewey_score", 0))

    table = Table(title=f"Volumes (Page {data.get('page', 1)}/{max(1, -(-data.get('total', 0) // 20))})")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Dewey", justify="right")
    table.add_column("Shelf", justify="right", style="dim")

    for vol in items:
        score = vol.get("dewey_score", 0)
        score_color = "green" if score >= 75 else "yellow" if score >= 50 else "red" if score >= 25 else "bold red"
        table.add_row(
            str(vol["id"]),
            vol["title"][:50],
            f"[{score_color}]{score}[/{score_color}]",
            str(vol.get("shelf_id", "")),
        )

    console.print(table)
    console.print(f"[dim]Total: {data.get('total', 0)} volumes[/dim]")


@app.command("create")
def create_volume(
    title: str = typer.Argument(help="Volume title"),
    shelf: int = typer.Option(..., "--shelf", help="Shelf ID"),
    content: str = typer.Option(None, "--content", help="Content text"),
    file: Path | None = typer.Option(None, "--file", help="Read content from file"),
    bookmarks: str = typer.Option("", help="Comma-separated bookmarks"),
) -> None:
    """Create a new volume. Use --file to read content from a file (CLI power feature)."""
    require_auth()

    if file:
        if not file.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise SystemExit(1)
        volume_content = file.read_text()
    elif content:
        volume_content = content
    else:
        console.print("[red]Provide --content or --file.[/red]")
        raise SystemExit(1)

    payload = {
        "title": title,
        "content": volume_content,
        "shelf_id": shelf,
        "bookmarks": [b.strip() for b in bookmarks.split(",") if b.strip()] if bookmarks else [],
    }

    with get_client() as client:
        resp = client.post("/api/volumes/", json=payload)

    if resp.status_code == 201:
        data = resp.json()
        console.print(f"[green]Volume '{data['title']}' shelved (ID: {data['id']}, Dewey: {data['dewey_score']}).[/green]")
    else:
        console.print(f"[red]Failed: {resp.json().get('detail', resp.text)}[/red]")
        raise SystemExit(1)


@app.command("review")
def review_volumes(
    ids: list[int] = typer.Argument(help="Volume ID(s) to review"),
) -> None:
    """Review one or more volumes (batch review is a CLI power feature)."""
    require_auth()

    with get_client() as client:
        for vol_id in ids:
            resp = client.post(f"/api/volumes/{vol_id}/review")
            if resp.status_code == 200:
                data = resp.json()
                console.print(f"[green]Reviewed '{data['title']}' — Dewey: {data['dewey_score']}[/green]")
            else:
                detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                console.print(f"[red]Volume {vol_id}: {detail}[/red]")


@app.command("import")
def import_volumes(
    shelf: int = typer.Option(..., "--shelf", help="Target shelf ID"),
    dir: Path = typer.Option(..., "--dir", help="Directory of .md files to import"),
) -> None:
    """Import all .md files from a directory as volumes (CLI exclusive)."""
    require_auth()

    if not dir.is_dir():
        console.print(f"[red]Not a directory: {dir}[/red]")
        raise SystemExit(1)

    md_files = sorted(dir.glob("*.md"))
    if not md_files:
        console.print("[yellow]No .md files found.[/yellow]")
        return

    console.print(f"[dim]Found {len(md_files)} markdown files...[/dim]")

    with get_client() as client:
        for f in md_files:
            title = f.stem.replace("-", " ").replace("_", " ").title()
            content = f.read_text()
            payload = {
                "title": title,
                "content": content,
                "shelf_id": shelf,
                "bookmarks": [],
            }
            resp = client.post("/api/volumes/", json=payload)
            if resp.status_code == 201:
                data = resp.json()
                console.print(f"  [green]+ {data['title']} (ID: {data['id']})[/green]")
            else:
                console.print(f"  [red]x {title}: {resp.text[:100]}[/red]")

    console.print("[green]Import complete.[/green]")


@app.command("overdue")
def list_overdue() -> None:
    """List all overdue volumes (Dewey <= 25)."""
    with get_client() as client:
        resp = client.get("/api/reading-room/overdue")

    if resp.status_code != 200:
        console.print("[red]Failed to fetch overdue report.[/red]")
        raise SystemExit(1)

    data = resp.json()
    overdue = data.get("overdue_items", [])
    attention = data.get("needs_attention_items", [])

    if not overdue and not attention:
        console.print("[green]No overdue volumes! Your stacks are pristine.[/green]")
        return

    if overdue:
        table = Table(title="Overdue Volumes (Dewey <= 25)")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold red")
        table.add_column("Dewey", justify="right", style="red")

        for item in overdue:
            table.add_row(str(item["id"]), item["title"][:50], str(round(item.get("dewey_score", 0), 1)))
        console.print(table)

    if attention:
        table = Table(title="Needs Attention (Dewey 25-50)")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold yellow")
        table.add_column("Dewey", justify="right", style="yellow")

        for item in attention:
            table.add_row(str(item["id"]), item["title"][:50], str(round(item.get("dewey_score", 0), 1)))
        console.print(table)
