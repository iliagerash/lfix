"""Run a codebase scan and build a Report."""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

from llmfixture import __version__
from llmfixture.metadata import load_metadata
from llmfixture.models import Report, ReportKind
from llmfixture.scan.discover import discover
from llmfixture.scan.parse_js import parse_js
from llmfixture.scan.parse_python import parse_python
from llmfixture.scan.parse_text import parse_text
from llmfixture.scan.rules import run_rules
from llmfixture.scan.types import (
    CallSite,
    ClassifiedFile,
    FileKind,
    ScanContext,
    StringLiteral,
)

_JS_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}


def scan(paths: Sequence[Path], *, cwd: Path | None = None) -> Report:
    cwd = cwd or Path.cwd()
    started = time.perf_counter()
    files = discover(paths, cwd=cwd)
    literals: list[StringLiteral] = []
    calls: list[CallSite] = []
    for classified in files:
        parsed_literals, parsed_calls = _parse(classified)
        literals.extend(parsed_literals)
        calls.extend(parsed_calls)
    root = paths[0] if paths else cwd
    root = root if root.is_absolute() else cwd / root
    if root.is_file():
        root = root.parent
    context = ScanContext(
        root=root.resolve(),
        files=files,
        literals=literals,
        calls=calls,
        metadata=load_metadata(),
    )
    findings = tuple(run_rules(context))
    duration_ms = int((time.perf_counter() - started) * 1000)
    schema_files = sum(1 for item in files if item.kind is FileKind.schema)
    model_calls = sum(1 for call in calls if "model" in call.kwargs)
    return Report(
        kind=ReportKind.scan,
        title="AI Codebase Scan",
        cli_version=__version__,
        findings=findings,
        counts={
            "files": len(files),
            "model_calls": model_calls,
            "schema_files": schema_files,
        },
        metadata_version=context.metadata.version,
        duration_ms=duration_ms,
    )


def _parse(classified: ClassifiedFile) -> tuple[list[StringLiteral], list[CallSite]]:
    try:
        source = classified.path.read_text(encoding="utf-8")
    except OSError:
        return [], []
    if "\0" in source:
        return [], []
    suffix = classified.path.suffix.lower()
    if suffix == ".py":
        return parse_python(classified.path, source)
    if suffix in _JS_SUFFIXES:
        return parse_js(classified.path, source)
    return parse_text(classified.path, source)
