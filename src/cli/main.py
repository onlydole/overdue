"""Overdue CLI entry point."""

import typer

app = typer.Typer(
    name="overdue",
    help="Don't let your knowledge expire. Manage your library from the command line.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Show the Overdue version."""
    typer.echo("overdue 0.1.0a1")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
) -> None:
    """Start the Overdue server."""
    import uvicorn

    uvicorn.run("src.main:app", host=host, port=port, reload=reload)
