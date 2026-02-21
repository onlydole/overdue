"""Bot management CLI commands."""

import asyncio

import typer

app = typer.Typer(help="Manage AI bot players on the leaderboard.")


@app.command("add")
def add_bot(
    difficulty: str = typer.Argument(
        ..., help="Bot difficulty: casual, diligent, or obsessive"
    ),
    name: str = typer.Option(None, "--name", help="Custom bot username"),
    count: int = typer.Option(1, "--count", "-n", help="Number of bots to create"),
) -> None:
    """Add AI bot player(s) to the leaderboard."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if difficulty not in ("casual", "diligent", "obsessive"):
        console.print(f"[red]Invalid difficulty '{difficulty}'. Choose: casual, diligent, obsessive[/red]")
        raise typer.Exit(1)

    if name and count > 1:
        console.print("[red]Cannot use --name with --count > 1 (names must be unique).[/red]")
        raise typer.Exit(1)

    async def _add() -> None:
        from src.db.engine import async_session, engine
        from src.db.tables import Base
        from src.game.bots import create_bot

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        created = []
        async with async_session() as session:
            for _ in range(count):
                bot = await create_bot(session, difficulty, name=name)
                await session.commit()
                created.append(bot)

        table = Table(title=f"Created {len(created)} bot(s)")
        table.add_column("Username", style="cyan")
        table.add_column("Difficulty", style="yellow")
        table.add_column("XP", justify="right", style="green")
        table.add_column("Rank", style="magenta")
        table.add_column("Avatar", style="dim")

        for bot in created:
            table.add_row(
                bot.username,
                bot.bot_difficulty,
                str(bot.total_xp),
                bot.role,
                bot.avatar_id,
            )
        console.print(table)

    asyncio.run(_add())


@app.command("remove")
def remove_bot(
    name: str = typer.Argument(None, help="Bot username to remove"),
    all_bots: bool = typer.Option(False, "--all", help="Remove all bots"),
) -> None:
    """Remove bot player(s) from the leaderboard."""
    from rich.console import Console

    console = Console()

    if not name and not all_bots:
        console.print("[red]Provide a bot name or use --all to remove all bots.[/red]")
        raise typer.Exit(1)

    async def _remove() -> None:
        from src.db.engine import async_session, engine
        from src.db.tables import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            if all_bots:
                from src.game.bots import remove_all_bots
                count = await remove_all_bots(session)
                await session.commit()
                if count:
                    console.print(f"[green]Removed {count} bot(s).[/green]")
                else:
                    console.print("[yellow]No bots found to remove.[/yellow]")
            else:
                from src.game.bots import remove_bot as rm_bot
                removed = await rm_bot(session, name)
                await session.commit()
                if removed:
                    console.print(f"[green]Removed bot '{name}' and all related data.[/green]")
                else:
                    console.print(f"[yellow]No bot found with username '{name}'.[/yellow]")

    asyncio.run(_remove())


@app.command("list")
def list_bots() -> None:
    """List all AI bot players."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    async def _list() -> None:
        from src.db.engine import async_session, engine
        from src.db.tables import Base
        from src.game.bots import list_bots as get_bots

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            bots = await get_bots(session)

        if not bots:
            console.print("[yellow]No bots found. Use 'overdue bots add <difficulty>' to create some.[/yellow]")
            return

        table = Table(title=f"Bot Players ({len(bots)})")
        table.add_column("ID", justify="right", style="dim")
        table.add_column("Username", style="cyan")
        table.add_column("Difficulty", style="yellow")
        table.add_column("XP", justify="right", style="green")
        table.add_column("Rank", style="magenta")
        table.add_column("Avatar", style="dim")

        for bot in bots:
            table.add_row(
                str(bot["id"]),
                bot["username"],
                bot["difficulty"],
                str(bot["total_xp"]),
                bot["role"],
                bot["avatar_id"],
            )
        console.print(table)

    asyncio.run(_list())


@app.command("simulate")
def simulate(
    name: str = typer.Option(None, "--name", help="Simulate a specific bot"),
) -> None:
    """Simulate bot activity (advance XP, reviews, streaks)."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    async def _simulate() -> None:
        from src.db.engine import async_session, engine
        from src.db.tables import Base
        from src.game.bots import simulate_bot_activity

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            results = await simulate_bot_activity(session, bot_username=name)
            await session.commit()

        if not results:
            console.print("[yellow]No bots to simulate.[/yellow]")
            return

        table = Table(title="Simulation Results")
        table.add_column("Username", style="cyan")
        table.add_column("XP Gained", justify="right", style="green")
        table.add_column("New Total XP", justify="right", style="bold green")
        table.add_column("Rank", style="magenta")

        for r in results:
            table.add_row(
                r["username"],
                f"+{r['xp_gained']}",
                str(r["new_total_xp"]),
                r["new_rank"],
            )
        console.print(table)

    asyncio.run(_simulate())
