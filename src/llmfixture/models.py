"""Core report types shared by every command."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"


class ReportKind(StrEnum):
    scan = "scan"
    mcp = "mcp"


@dataclass(frozen=True)
class Location:
    path: str
    line: int | None = None
    column: int | None = None
    snippet: str | None = None

    def display(self) -> str:
        if self.line is None:
            return self.path
        return f"{self.path}:{self.line}"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    explanation: str = ""
    suggestion: str = ""
    location: Location | None = None
    extra: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Report:
    kind: ReportKind
    title: str
    cli_version: str
    findings: tuple[Finding, ...]
    counts: Mapping[str, int]
    metadata_version: str | None = None
    duration_ms: int = 0

    def count_by_severity(self) -> dict[Severity, int]:
        tallies = {severity: 0 for severity in Severity}
        for finding in self.findings:
            tallies[finding.severity] += 1
        return tallies
