from pathlib import Path

from llmfixture.models import Finding, Location, Report, ReportKind, Severity
from llmfixture.output import render

SNAPSHOTS = Path(__file__).parent / "snapshots"

SCAN_REPORT = Report(
    kind=ReportKind.scan,
    title="AI Codebase Scan",
    cli_version="0.1.0",
    metadata_version="2026.08.1",
    duration_ms=0,
    counts={"files": 47, "model_calls": 12, "schema_files": 8},
    findings=(
        Finding(
            rule_id="model.deprecated",
            severity=Severity.high,
            message="Deprecated model: claude-sonnet-4-20250514",
            explanation="EOL: 2026-08-01. Successor: claude-sonnet-4-6.",
            suggestion="Pin to claude-sonnet-4-6.",
            location=Location(path="src/ai/resume-parser.ts", line=14),
            extra={
                "eol": "2026-08-01",
                "successor": "claude-sonnet-4-6",
            },
        ),
        Finding(
            rule_id="model.risky_alias",
            severity=Severity.medium,
            message='Model alias "latest" tracks provider updates silently.',
            suggestion="Pin to a versioned model ID for reproducible behavior.",
            location=Location(path="src/ai/classifier.ts", line=8),
        ),
    ),
)


def test_terminal_matches_brief_example() -> None:
    expected = (SNAPSHOTS / "scan.term.txt").read_text(encoding="utf-8")
    assert render(SCAN_REPORT, "term") == expected


def test_json_contract() -> None:
    expected = (SNAPSHOTS / "scan.json").read_text(encoding="utf-8")
    assert render(SCAN_REPORT, "json") == expected


def test_markdown_report() -> None:
    expected = (SNAPSHOTS / "scan.md").read_text(encoding="utf-8")
    assert render(SCAN_REPORT, "markdown") == expected


def test_empty_scan_has_no_findings_line() -> None:
    empty = SCAN_REPORT.__class__(
        kind=SCAN_REPORT.kind,
        title=SCAN_REPORT.title,
        cli_version=SCAN_REPORT.cli_version,
        findings=(),
        counts=SCAN_REPORT.counts,
        metadata_version=SCAN_REPORT.metadata_version,
        duration_ms=0,
    )
    text = render(empty, "term")
    assert "No findings." in text
    assert "issue" not in text
