"""Plain-text terminal report."""

from __future__ import annotations

from llmfixture.models import Report
from llmfixture.output._shared import (
    counts_summary,
    finding_body,
    footer,
    location_label,
)

_INDENT = "        "


def render_terminal(report: Report) -> str:
    header = f"{report.title} — {counts_summary(report.counts)}"
    blocks = [header, ""]
    if not report.findings:
        blocks.append("No findings.")
        return "\n".join(blocks) + "\n"

    for finding in report.findings:
        loc = location_label(finding.location)
        label = finding.severity.value.upper()
        heading = f"{label:<8}{loc}".rstrip()
        lines = [heading, *(_INDENT + line for line in finding_body(finding))]
        blocks.append("\n".join(lines))
        blocks.append("")
    blocks.append(footer(report))
    return "\n".join(blocks) + "\n"
