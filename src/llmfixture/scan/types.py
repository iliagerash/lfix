"""Types produced by the scanner before rules run."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from llmfixture.metadata.loader import Metadata


class FileKind(StrEnum):
    source = "source"
    schema = "schema"
    prompt = "prompt"
    config = "config"


@dataclass(frozen=True)
class ClassifiedFile:
    path: Path
    kind: FileKind


@dataclass(frozen=True)
class StringLiteral:
    path: Path
    line: int
    column: int
    value: str


@dataclass(frozen=True)
class CallSite:
    path: Path
    line: int
    column: int
    callee: str
    kwargs: Mapping[str, object]


@dataclass(frozen=True)
class ScanContext:
    root: Path
    files: Sequence[ClassifiedFile]
    literals: Sequence[StringLiteral]
    calls: Sequence[CallSite]
    metadata: Metadata
