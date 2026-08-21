"""Shared report formatting helpers."""

from __future__ import annotations

from collections.abc import Mapping

from llmfixture.models import Finding, Location, Report, Severity


def counts_summary(counts: Mapping[str, int]) -> str:
    parts = [
        f"{value} {key.replace('_', ' ')}" for key, value in counts.items()
    ]
    return ", ".join(parts)


def location_label(location: Location | None) -> str:
    if location is None:
        return ""
    return location.display()


def finding_body(finding: Finding) -> list[str]:
    lines: list[str] = [finding.message]
    if finding.explanation:
        lines.append(finding.explanation)
    if finding.suggestion:
        lines.append(finding.suggestion)
    return lines


def footer(report: Report) -> str:
    tallies = report.count_by_severity()
    return (
        f"{_plural(tallies[Severity.high], 'issue')} · "
        f"{_plural(tallies[Severity.medium], 'warning')} · "
        f"{_plural(tallies[Severity.low], 'suggestion')}"
    )


def _plural(count: int, noun: str) -> str:
    if count == 1:
        return f"1 {noun}"
    return f"{count} {noun}s"
