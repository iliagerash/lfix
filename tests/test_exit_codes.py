from llmfixture.exit_codes import SUCCESS, THRESHOLD_FAILED, for_report
from llmfixture.models import Finding, Report, ReportKind, Severity


def _report(*severities: Severity) -> Report:
    findings = tuple(
        Finding(
            rule_id="test.rule",
            severity=severity,
            message="x",
        )
        for severity in severities
    )
    return Report(
        kind=ReportKind.scan,
        title="t",
        cli_version="0.1.0",
        findings=findings,
        counts={},
    )


def test_no_findings_is_success() -> None:
    assert for_report(_report(), Severity.high) == SUCCESS


def test_fail_on_high_ignores_medium() -> None:
    assert for_report(_report(Severity.medium), Severity.high) == SUCCESS
    assert for_report(_report(Severity.high), Severity.high) == THRESHOLD_FAILED


def test_fail_on_medium_includes_high() -> None:
    assert for_report(_report(Severity.low), Severity.medium) == SUCCESS
    assert for_report(_report(Severity.medium), Severity.medium) == THRESHOLD_FAILED
    assert for_report(_report(Severity.high), Severity.medium) == THRESHOLD_FAILED
