"""Bundled provider/model metadata. Local files only — never fetched at runtime."""

from __future__ import annotations

import json
from collections.abc import Mapping
from enum import StrEnum
from functools import lru_cache
from importlib.resources import files
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ModelStatus(StrEnum):
    current = "current"
    deprecated = "deprecated"
    eol = "eol"


class ModelKind(StrEnum):
    api = "api"
    open_weights = "open_weights"


class ModelRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    provider: str
    status: ModelStatus
    kind: ModelKind = ModelKind.api
    source: str | None = None
    eol: str | None = None
    successor: str | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    structured_output: bool | None = None
    aliases: list[str] = Field(default_factory=list)

    @field_validator("eol")
    @classmethod
    def eol_is_iso_date(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parts = value.split("-")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise ValueError(f"eol must be YYYY-MM-DD, got {value!r}")
        return value

    @model_validator(mode="after")
    def high_rows_need_citation(self) -> Self:
        high = self.status in {ModelStatus.deprecated, ModelStatus.eol}
        if high and not self.source:
            raise ValueError(f"{self.id}: deprecated/eol rows require source")
        if high and not self.successor:
            raise ValueError(f"{self.id}: deprecated/eol rows require successor")
        if self.status is ModelStatus.eol and not self.eol:
            raise ValueError(f"{self.id}: eol rows require eol date")
        return self


class SdkDeprecation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sdk: str
    symbol: str
    replacement: str
    since: str | None = None


class AliasTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exact: list[str]
    suffixes: list[str] = Field(default_factory=list)


class Snapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    generated_at: str
    sources: list[str]


class Metadata(BaseModel):
    snapshot: Snapshot
    models: Mapping[str, ModelRecord]
    aliases: AliasTable
    sdks: tuple[SdkDeprecation, ...]

    @property
    def version(self) -> str:
        return self.snapshot.version

    def get_model(self, model_id: str) -> ModelRecord | None:
        return self.models.get(model_id)

    def is_retired(self, model_id: str) -> bool:
        record = self.get_model(model_id)
        return record is not None and record.status in {
            ModelStatus.deprecated,
            ModelStatus.eol,
        }

    def is_risky_alias(self, name: str) -> bool:
        if name in self.models:
            return False
        if name in self.aliases.exact:
            return True
        return any(name.endswith(suffix) for suffix in self.aliases.suffixes)


def _read_json(name: str) -> str:
    return files("llmfixture.metadata.data").joinpath(name).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def load_metadata() -> Metadata:
    snapshot = Snapshot.model_validate(json.loads(_read_json("snapshot.json")))
    allowed_providers = set(json.loads(_read_json("providers.json")))
    raw_models = json.loads(_read_json("models.json"))
    if not isinstance(raw_models, list):
        raise ValueError("models.json must be a JSON array")
    models = {}
    seen: set[str] = set()
    for item in raw_models:
        record = ModelRecord.model_validate(item)
        if record.provider not in allowed_providers:
            raise ValueError(f"{record.id}: unknown provider {record.provider!r}")
        names = [record.id, *record.aliases]
        for name in names:
            if name in seen:
                raise ValueError(f"duplicate model id or alias: {name}")
            seen.add(name)
            models[name] = record
    aliases = AliasTable.model_validate(json.loads(_read_json("aliases.json")))
    raw_sdks = json.loads(_read_json("sdks.json"))
    if not isinstance(raw_sdks, list):
        raise ValueError("sdks.json must be a JSON array")
    sdks = tuple(SdkDeprecation.model_validate(item) for item in raw_sdks)
    return Metadata(snapshot=snapshot, models=models, aliases=aliases, sdks=sdks)
