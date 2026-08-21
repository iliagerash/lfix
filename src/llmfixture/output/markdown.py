"""Markdown report for files and PR comments."""

from __future__ import annotations

from llmfixture.models import Report
from llmfixture.output._shared import (
    counts_summary,
    finding_body,
    footer,
    location_label,
)


def render_markdown(report: Report) -> str:
    lines = [
        f"# {report.title}",
        "",
        counts_summary(report.counts),
        "",
    ]
    if not report.findings:
        lines.append("No findings.")
        lines.append("")
        return "\n".join(lines)

    for finding in report.findings:
        loc = location_label(finding.location)
        heading = f"## {finding.severity.value.upper()}"
        if loc:
            heading = f"{heading} `{loc}`"
        lines.append(heading)
        lines.append("")
        for body in finding_body(finding):
            lines.append(body)
            lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(footer(report))
    lines.append("")
    return "\n".join(lines)
