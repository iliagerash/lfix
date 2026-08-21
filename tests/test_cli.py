from pathlib import Path

from typer.testing import CliRunner

from llmfixture import __version__
from llmfixture.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "lfix" in result.stdout
    assert "scan" in result.stdout


def test_scan_command_flags_deprecated(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text('MODEL = "claude-sonnet-4-20250514"\n', encoding="utf-8")
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])
    assert result.exit_code == 1
    assert "claude-sonnet-4-20250514" in result.stdout
    assert '"rule_id": "model.deprecated"' in result.stdout
