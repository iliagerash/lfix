"""Load and validate `lfix.yml`."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from llmfixture.models import Severity


class ConfigError(Exception):
    """Invalid or missing fixture config."""


class IgnoreRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str
    paths: list[str] = Field(default_factory=list)


class McpAssert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_total_tokens: int | None = None
    no_overlapping_tools: bool | None = None
    examples_required_for_complex_tools: bool | None = None


class Fixture(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str
    type: Literal["scan", "mcp"]
    paths: list[str] = Field(default_factory=list)
    fail_on: Severity | None = None
    ignore: list[IgnoreRule] = Field(default_factory=list)
    config: str | None = None
    assertions: McpAssert | None = Field(default=None, alias="assert")

    @model_validator(mode="after")
    def require_type_fields(self) -> Fixture:
        if self.type == "scan" and not self.paths:
            raise ValueError("scan fixtures require paths")
        if self.type == "mcp" and not self.config:
            raise ValueError("mcp fixtures require config")
        return self


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project: str | None = None
    fail_on: Severity = Severity.high
    fixtures: list[Fixture] = Field(default_factory=list)


def load_config(path: Path) -> Config:
    if not path.is_file():
        raise ConfigError(f"config not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError(f"config must be a mapping: {path}")
    try:
        return Config.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"invalid config {path}: {exc}") from exc
