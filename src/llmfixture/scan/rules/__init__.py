from llmfixture.models import Finding
from llmfixture.scan.rules import deprecated_model, risky_alias
from llmfixture.scan.types import ScanContext

_RULES = (deprecated_model.check, risky_alias.check)


def run_rules(context: ScanContext) -> list[Finding]:
    findings: list[Finding] = []
    for check in _RULES:
        findings.extend(check(context))
    return findings
