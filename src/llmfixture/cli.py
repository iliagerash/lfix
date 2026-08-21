"""CLI entry point for `lfix`."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from llmfixture import __version__
from llmfixture.exit_codes import USAGE_ERROR, for_report
from llmfixture.models import Severity
from llmfixture.output import render
from llmfixture.scan.engine import scan as run_scan

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


@app.command()
def scan(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Files or directories to scan.", show_default=False),
    ] = None,
    fmt: Annotated[
        str,
        typer.Option("--format", help="term, json, or md"),
    ] = "term",
    fail_on: Annotated[Severity, typer.Option("--fail-on")] = Severity.high,
) -> None:
    """Scan a codebase for deprecated model IDs and risky aliases."""
    targets = paths or [Path(".")]
    try:
        report = run_scan(targets)
        typer.echo(render(report, fmt), nl=False)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(USAGE_ERROR) from exc
    raise typer.Exit(for_report(report, fail_on))
