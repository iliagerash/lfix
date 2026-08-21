"""CLI entry point for `lfix`."""

from __future__ import annotations

import typer

from llmfixture import __version__

app = typer.Typer(
    name="lfix",
    help=(
        "Catch deprecated model IDs, broken structured-output schemas, "
        "and fragile MCP tools."
    ),
    no_args_is_help=True,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    _: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """LLM Fixture CLI."""
