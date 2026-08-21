"""Flag string literals that match a retired model ID."""

from __future__ import annotations

from pathlib import Path

from llmfixture.models import Finding, Location, Severity
from llmfixture.scan.types import ScanContext

RULE_ID = "model.deprecated"


def check(context: ScanContext) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for literal in context.literals:
        record = context.metadata.get_model(literal.value)
        if record is None or not context.metadata.is_retired(literal.value):
            continue
        key = (str(literal.path), literal.line, literal.value)
        if key in seen:
            continue
        seen.add(key)
        bits = []
        extra: dict[str, object] = {}
        if record.eol:
            bits.append(f"EOL: {record.eol}.")
            extra["eol"] = record.eol
        if record.successor:
            bits.append(f"Successor: {record.successor}.")
            extra["successor"] = record.successor
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=Severity.high,
                message=f"Deprecated model: {literal.value}",
                explanation=" ".join(bits),
                suggestion=(
                    f"Pin to {record.successor}."
                    if record.successor
                    else "Pin to a current versioned model ID."
                ),
                location=Location(
                    path=_display_path(context.root, literal.path),
                    line=literal.line,
                    column=literal.column,
                    snippet=literal.value,
                ),
                extra=extra,
            )
        )
    return findings


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
