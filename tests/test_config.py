from pathlib import Path

import pytest

from llmfixture.config import ConfigError, load_config
from llmfixture.models import Severity

VALID_YAML = """
project: hiring-assistant
fail_on: high
fixtures:
  - name: codebase_scan
    type: scan
    paths:
      - ./src
      - ./prompts
      - ./schemas
    fail_on: high
    ignore:
      - rule: model.risky_alias
        paths: [./scripts/**]
  - name: mcp_tools
    type: mcp
    config: ./mcp-server/tools.json
    assert:
      max_total_tokens: 15000
      no_overlapping_tools: true
      examples_required_for_complex_tools: true
"""


def test_load_phase1_config(tmp_path: Path) -> None:
    path = tmp_path / "lfix.yml"
    path.write_text(VALID_YAML, encoding="utf-8")
    config = load_config(path)
    assert config.project == "hiring-assistant"
    assert config.fail_on is Severity.high
    assert [fixture.name for fixture in config.fixtures] == [
        "codebase_scan",
        "mcp_tools",
    ]
    scan, mcp = config.fixtures
    assert scan.type == "scan"
    assert scan.paths == ["./src", "./prompts", "./schemas"]
    assert scan.ignore[0].rule == "model.risky_alias"
    assert mcp.config == "./mcp-server/tools.json"
    assert mcp.assertions is not None
    assert mcp.assertions.max_total_tokens == 15000


def test_missing_file_is_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "missing.yml")


def test_scan_fixture_requires_paths(tmp_path: Path) -> None:
    path = tmp_path / "lfix.yml"
    path.write_text(
        "fixtures:\n  - name: scan\n    type: scan\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="paths"):
        load_config(path)


def test_mcp_fixture_requires_config(tmp_path: Path) -> None:
    path = tmp_path / "lfix.yml"
    path.write_text(
        "fixtures:\n  - name: tools\n    type: mcp\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="config"):
        load_config(path)


def test_unknown_keys_rejected(tmp_path: Path) -> None:
    path = tmp_path / "lfix.yml"
    path.write_text("project: x\nunknown: true\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid config"):
        load_config(path)
