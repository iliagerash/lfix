"""Flag unversioned / rolling model aliases used as a model id."""

from __future__ import annotations

from pathlib import Path

from llmfixture.models import Finding, Location, Severity
from llmfixture.scan.types import ScanContext

RULE_ID = "model.risky_alias"


def check(context: ScanContext) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for call in context.calls:
        raw = call.kwargs.get("model")
        if not isinstance(raw, str):
            continue
        if context.metadata.is_retired(raw):
            continue
        if not context.metadata.is_risky_alias(raw):
            continue
        key = (str(call.path), call.line, raw)
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=Severity.medium,
                message=f'Model alias "{raw}" tracks provider updates silently.',
                suggestion="Pin to a versioned model ID for reproducible behavior.",
                location=Location(
                    path=_display_path(context.root, call.path),
                    line=call.line,
                    column=call.column,
                    snippet=raw,
                ),
            )
        )
    return findings


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
