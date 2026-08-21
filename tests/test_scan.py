from pathlib import Path

from llmfixture.models import Finding
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


def test_discover_classifies_source_schema_prompt() -> None:
    files = discover([FIXTURE], cwd=FIXTURE)
    kinds = {item.path.name: item.kind for item in files}
    assert kinds["resume_parser.py"] is FileKind.source
    assert kinds["match.schema.json"] is FileKind.schema
    assert kinds["hello.prompt.md"] is FileKind.prompt


def test_scan_reports_exact_lines() -> None:
    report = scan([FIXTURE], cwd=FIXTURE)
    by_rule: dict[str, list[Finding]] = {}
    for finding in report.findings:
        by_rule.setdefault(finding.rule_id, []).append(finding)
    deprecated = by_rule["model.deprecated"][0]
    aliases = by_rule["model.risky_alias"]
    assert deprecated.location is not None
    assert deprecated.location.path.endswith("resume_parser.py")
    assert deprecated.location.line == 3
    alias_paths = {item.location.path for item in aliases if item.location}
    alias_lines = {
        (item.location.path, item.location.line, item.location.snippet)
        for item in aliases
        if item.location
    }
    assert any(path.endswith("classifier.ts") for path in alias_paths)
    assert any(
        path.endswith("classifier.ts") and line == 3 and snippet == "latest"
        for path, line, snippet in alias_lines
    )
    assert any(
        path.endswith("pin.py") and snippet == "latest"
        for path, _line, snippet in alias_lines
    )
    assert report.counts["schema_files"] == 1


def test_scan_ignores_ci_runners_and_generic_strings() -> None:
    report = scan([FIXTURE], cwd=FIXTURE)
    snippets = [
        finding.location.snippet
        for finding in report.findings
        if finding.location is not None
    ]
    assert "ubuntu-latest" not in snippets
    assert "windows-latest" not in snippets
    messages = " ".join(finding.message for finding in report.findings)
    assert 'Model alias "default"' not in messages
    assert 'Model alias "phi"' not in messages


def test_clean_file_has_no_findings() -> None:
    report = scan([FIXTURE / "src" / "ai" / "clean.py"], cwd=FIXTURE)
    assert report.findings == ()


def test_discover_honors_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("/secret_deps\n*.generated.py\n")
    (tmp_path / "ok.py").write_text("x = 1\n")
    (tmp_path / "app.generated.py").write_text('MODEL = "latest"\n')
    hidden = tmp_path / "secret_deps" / "pkg"
    hidden.mkdir(parents=True)
    (hidden / "lib.py").write_text('MODEL = "latest"\n')
    names = {item.path.name for item in discover([tmp_path], cwd=tmp_path)}
    assert "ok.py" in names
    assert "lib.py" not in names
    assert "app.generated.py" not in names


def test_discover_scans_vendor_unless_gitignored(tmp_path: Path) -> None:
    vendor = tmp_path / "vendor" / "pkg"
    vendor.mkdir(parents=True)
    (vendor / "lib.py").write_text("x = 1\n")
    (tmp_path / "app.py").write_text("x = 1\n")
    names = {item.path.name for item in discover([tmp_path], cwd=tmp_path)}
    assert "lib.py" in names
    (tmp_path / ".gitignore").write_text("/vendor\n")
    names = {item.path.name for item in discover([tmp_path], cwd=tmp_path)}
    assert "lib.py" not in names
    assert "app.py" in names
