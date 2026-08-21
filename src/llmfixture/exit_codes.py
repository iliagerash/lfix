"""Process exit codes for `lfix`."""

from __future__ import annotations

from llmfixture.models import Report, Severity

SUCCESS = 0
THRESHOLD_FAILED = 1
USAGE_ERROR = 2
INTERNAL_ERROR = 3

_RANK = {
    Severity.low: 1,
    Severity.medium: 2,
    Severity.high: 3,
}


def for_report(report: Report, fail_on: Severity) -> int:
    """Return 1 when any finding meets or exceeds `fail_on`, else 0."""
    threshold = _RANK[fail_on]
    if any(_RANK[finding.severity] >= threshold for finding in report.findings):
        return THRESHOLD_FAILED
    return SUCCESS
