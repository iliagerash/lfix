from pathlib import Path

from llmfixture.scan.discover import discover
from llmfixture.scan.engine import scan
from llmfixture.scan.parse_js import parse_js
from llmfixture.scan.parse_python import parse_python
from llmfixture.scan.types import FileKind

FIXTURE = Path(__file__).parent / "fixtures" / "scan_app"


def test_python_literal_line_number() -> None:
    path = FIXTURE / "src" / "ai" / "resume_parser.py"
    literals, _calls = parse_python(path, path.read_text(encoding="utf-8"))
    values = {item.value: item.line for item in literals}
    assert values["claude-sonnet-4-20250514"] == 3


def test_js_literal_line_number() -> None:
    path = FIXTURE / "src" / "ai" / "classifier.ts"
    literals, calls = parse_js(path, path.read_text(encoding="utf-8"))
    values = {item.value: item.line for item in literals}
    assert values["latest"] == 3
    assert any(call.kwargs.get("model") == "latest" for call in calls)


def test_discover_skips_node_modules() -> None:
    files = discover([FIXTURE], cwd=FIXTURE)
    paths = {item.path.name for item in files}
    assert "ignored.py" not in paths
    assert "resume_parser.py" in paths
    kinds = {item.path.name: item.kind for item in files}
    assert kinds["match.schema.json"] is FileKind.schema
    assert kinds["hello.prompt.md"] is FileKind.prompt


def test_scan_reports_exact_lines() -> None:
    report = scan([FIXTURE], cwd=FIXTURE)
    by_rule = {finding.rule_id: finding for finding in report.findings}
    deprecated = by_rule["model.deprecated"]
    alias = by_rule["model.risky_alias"]
    assert deprecated.location is not None
    assert deprecated.location.path.endswith("resume_parser.py")
    assert deprecated.location.line == 3
    assert alias.location is not None
    assert alias.location.path.endswith("classifier.ts")
    assert alias.location.line == 3
    assert "ignored.py" not in deprecated.location.path
    assert report.counts["schema_files"] == 1


def test_clean_file_has_no_findings() -> None:
    report = scan([FIXTURE / "src" / "ai" / "clean.py"], cwd=FIXTURE)
    assert report.findings == ()
