"""Stats and analytics CLI commands."""

from datetime import datetime, timedelta

import typer
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.cli.helpers import console, get_client, require_auth

app = typer.Typer(help="Stats and analytics (CLI exclusive).")


@app.command("summary")
def summary() -> None:
    """Show personal stats summary."""
    require_auth()

    with get_client() as client:
        xp_resp = client.get("/api/librarians/me/xp")
        badges_resp = client.get("/api/librarians/me/badges")
        streak_resp = client.get("/api/librarians/me/streak")

    if xp_resp.status_code != 200:
        console.print("[red]Failed to fetch stats. Re-login may be needed.[/red]")
        raise SystemExit(1)

    xp = xp_resp.json()
    badges = badges_resp.json() if badges_resp.status_code == 200 else {"badges": [], "total": 0}
    streak = streak_resp.json() if streak_resp.status_code == 200 else {"current_streak": 0, "longest_streak": 0}

    panel_content = Text()
    panel_content.append(f"Rank: ", style="dim")
    panel_content.append(f"{xp['rank']}\n", style="bold gold1")
    panel_content.append(f"XP: ", style="dim")
    panel_content.append(f"{xp['total_xp']} pages read\n", style="green")
    if xp.get("next_rank"):
        panel_content.append(f"Next: ", style="dim")
        panel_content.append(f"{xp['next_rank']} ({xp['xp_to_next_rank']} XP away)\n", style="yellow")
    panel_content.append(f"Streak: ", style="dim")
    panel_content.append(f"{streak['current_streak']}d", style="bold red")
    panel_content.append(f" (best: {streak['longest_streak']}d)\n", style="dim")
    panel_content.append(f"Badges: ", style="dim")
    panel_content.append(f"{badges['total']}", style="cyan")

    console.print(Panel(panel_content, title="[gold1]Your Library Stats[/gold1]", border_style="gold1"))

    if badges.get("badges"):
        console.print("\n[bold]Earned Badges:[/bold]")
        for b in badges["badges"]:
            tier_color = "magenta" if b.get("tier") == "Rare" else "cyan"
            console.print(f"  [{tier_color}]★[/{tier_color}] {b['name']} — {b['description']}")


@app.command("decay-forecast")
def decay_forecast(
    units: int = typer.Option(30, help="Number of decay units to forecast"),
) -> None:
    """Predict which volumes will go overdue soon (CLI exclusive).

    Decay units depend on config (default: 10 seconds each).
    """
    with get_client() as client:
        resp = client.get("/api/volumes/", params={"per_page": 100})

    if resp.status_code != 200:
        console.print("[red]Failed to fetch volumes.[/red]")
        raise SystemExit(1)

    data = resp.json()
    items = data.get("items", [])

    at_risk = []
    for vol in items:
        current = vol.get("dewey_score", 100)
        future = max(0, current - (3 * units))  # 3 points per decay unit
        if current > 25 and future <= 25:
            units_until = max(1, int((current - 25) / 3))
            at_risk.append({
                "id": vol["id"],
                "title": vol["title"],
                "current": round(current, 1),
                "future": round(future, 1),
                "units_until": units_until,
            })

    at_risk.sort(key=lambda x: x["units_until"])

    if not at_risk:
        console.print(f"[green]No volumes will go overdue in the next {units} decay units.[/green]")
        return

    table = Table(title=f"Decay Forecast ({units} units)")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Current", justify="right", style="yellow")
    table.add_column(f"In {units}u", justify="right", style="red")
    table.add_column("Goes Overdue In", justify="right", style="bold red")

    for item in at_risk:
        table.add_row(
            str(item["id"]),
            item["title"][:40],
            str(item["current"]),
            str(item["future"]),
            f"{item['units_until']}u",
        )

    console.print(table)
    console.print(f"\n[yellow]{len(at_risk)} volume(s) will need review soon.[/yellow]")


@app.command("heatmap")
def heatmap() -> None:
    """Show review activity heatmap (GitHub contribution graph style, CLI exclusive)."""
    require_auth()

    with get_client() as client:
        xp_resp = client.get("/api/librarians/me/xp")

    if xp_resp.status_code != 200:
        console.print("[red]Failed to fetch data.[/red]")
        raise SystemExit(1)

    data = xp_resp.json()
    recent = data.get("recent_awards", [])

    # Build a simple activity map for the last 4 weeks
    today = datetime.utcnow().date()
    activity: dict[str, int] = {}
    for award in recent:
        date_str = award["created_at"][:10]
        activity[date_str] = activity.get(date_str, 0) + award["amount"]

    console.print("[bold gold1]Review Activity (Last 4 weeks)[/bold gold1]\n")

    days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # Build 4 weeks of data
    lines = []
    for dow in range(7):
        row = f"[dim]{days_labels[dow]}[/dim] "
        for week in range(3, -1, -1):
            delta = timedelta(days=(today.weekday() - dow) % 7 + week * 7)
            day = today - delta
            day_str = day.isoformat()
            count = activity.get(day_str, 0)
            if count == 0:
                row += "[dim]░[/dim] "
            elif count < 10:
                row += "[green]▒[/green] "
            elif count < 25:
                row += "[bold green]▓[/bold green] "
            else:
                row += "[bold green on green]█[/bold green on green] "
        lines.append(row)

    for line in lines:
        console.print(line)

    console.print(f"\n[dim]░ = no activity  [green]▒[/green] = some  [bold green]▓[/bold green] = active  █ = very active[/dim]")
