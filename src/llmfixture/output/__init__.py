"""Render a Report to terminal, JSON, or Markdown."""

from __future__ import annotations

from llmfixture.models import Report
from llmfixture.output.json import render_json
from llmfixture.output.markdown import render_markdown
from llmfixture.output.terminal import render_terminal

__all__ = ["render", "render_json", "render_markdown", "render_terminal"]


def render(report: Report, fmt: str) -> str:
    if fmt in {"term", "terminal"}:
        return render_terminal(report)
    if fmt == "json":
        return render_json(report)
    if fmt in {"md", "markdown"}:
        return render_markdown(report)
    raise ValueError(f"unknown output format: {fmt}")
