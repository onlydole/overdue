"""Seed data CLI command."""

import asyncio

import typer

app = typer.Typer(help="Database seeding commands.")


@app.command()
def seed(
    reset: bool = typer.Option(False, "--reset", help="Drop and recreate all tables before seeding"),
) -> None:
    """Seed the database with demo data."""
    from rich.console import Console
    console = Console()

    async def _seed() -> None:
        from src.db.engine import async_session, engine
        from src.db.tables import Base

        if reset:
            console.print("[yellow]Resetting database...[/yellow]")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            console.print("[green]Tables recreated.[/green]")
        else:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        from src.db.seed import is_db_empty, seed_demo_data, _get_demo_password

        async with async_session() as session:
            if not await is_db_empty(session):
                console.print("[yellow]Database already has data. Use --reset to clear first.[/yellow]")
                return
            demo_pw = _get_demo_password()
            await seed_demo_data(session)
            console.print("[green]Demo data seeded successfully![/green]")
            console.print(f"[dim]Demo accounts: archie, paige, dewey[/dim]")
            console.print(f"[dim]Set OVERDUE_DEMO_PASSWORD env var to control the demo password.[/dim]")
            console.print(f"[dim]Current demo password: {demo_pw}[/dim]")

    asyncio.run(_seed())
