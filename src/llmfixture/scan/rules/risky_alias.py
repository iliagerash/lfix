"""Flag unversioned / rolling model aliases."""

from __future__ import annotations

from pathlib import Path

from llmfixture.models import Finding, Location, Severity
from llmfixture.scan.types import ScanContext

RULE_ID = "model.risky_alias"


def check(context: ScanContext) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for literal in context.literals:
        if context.metadata.is_retired(literal.value):
            continue
        if not context.metadata.is_risky_alias(literal.value):
            continue
        key = (str(literal.path), literal.line, literal.value)
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=Severity.medium,
                message=(
                    f'Model alias "{literal.value}" tracks provider updates silently.'
                ),
                suggestion="Pin to a versioned model ID for reproducible behavior.",
                location=Location(
                    path=_display_path(context.root, literal.path),
                    line=literal.line,
                    column=literal.column,
                    snippet=literal.value,
                ),
            )
        )
    return findings


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
