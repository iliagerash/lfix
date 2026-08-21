"""JSON report contract. Do not change keys without a schema_version bump."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from llmfixture.models import Finding, Report

SCHEMA_VERSION = 1


def render_json(report: Report) -> str:
    return json.dumps(report_dict(report), indent=2) + "\n"


def report_dict(report: Report) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": report.kind.value,
        "title": report.title,
        "cli_version": report.cli_version,
        "metadata_version": report.metadata_version,
        "duration_ms": report.duration_ms,
        "counts": dict(report.counts),
        "findings": [_finding_dict(finding) for finding in report.findings],
    }


def _finding_dict(finding: Finding) -> dict[str, Any]:
    location: Mapping[str, object] | None
    if finding.location is None:
        location = None
    else:
        location = {
            "path": finding.location.path,
            "line": finding.location.line,
            "column": finding.location.column,
            "snippet": finding.location.snippet,
        }
    return {
        "rule_id": finding.rule_id,
        "severity": finding.severity.value,
        "message": finding.message,
        "explanation": finding.explanation,
        "suggestion": finding.suggestion,
        "location": location,
        "extra": dict(finding.extra),
    }
