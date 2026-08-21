"""Extract string values from .env, YAML, JSON, and prompt files."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from llmfixture.scan.types import CallSite, StringLiteral

_ENV = re.compile(
    r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<q>['\"]?)(?P<value>[^'\"\n]*)(?P=q)\s*$"
)


def parse_text(path: Path, source: str) -> tuple[list[StringLiteral], list[CallSite]]:
    suffix = path.suffix.lower()
    if path.name.startswith(".env"):
        return _from_env(path, source)
    if suffix in {".yml", ".yaml"}:
        return _from_yaml(path, source), []
    if suffix == ".json":
        return _from_json(path, source), []
    return _from_plain(path, source), []


def _from_env(path: Path, source: str) -> tuple[list[StringLiteral], list[CallSite]]:
    literals: list[StringLiteral] = []
    calls: list[CallSite] = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        match = _ENV.match(line.strip())
        if not match:
            continue
        key, value = match.group("key"), match.group("value")
        literals.append(
            StringLiteral(path=path, line=line_no, column=0, value=value)
        )
        if "model" in key.lower():
            calls.append(
                CallSite(
                    path=path,
                    line=line_no,
                    column=0,
                    callee="",
                    kwargs={"model": value},
                )
            )
    return literals, calls


def _from_yaml(path: Path, source: str) -> list[StringLiteral]:
    try:
        loaded = yaml.safe_load(source)
    except yaml.YAMLError:
        return _from_plain(path, source)
    values = _walk_strings(loaded)
    return _locate(path, source, values)


def _from_json(path: Path, source: str) -> list[StringLiteral]:
    try:
        loaded = json.loads(source)
    except json.JSONDecodeError:
        return _from_plain(path, source)
    values = _walk_strings(loaded)
    return _locate(path, source, values)


def _from_plain(path: Path, source: str) -> list[StringLiteral]:
    literals: list[StringLiteral] = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped:
            literals.append(
                StringLiteral(path=path, line=line_no, column=0, value=stripped)
            )
    return literals


def _walk_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        found: list[str] = []
        for item in value.values():
            found.extend(_walk_strings(item))
        return found
    if isinstance(value, list):
        found = []
        for item in value:
            found.extend(_walk_strings(item))
        return found
    return []


def _locate(path: Path, source: str, values: list[str]) -> list[StringLiteral]:
    literals: list[StringLiteral] = []
    used: set[tuple[int, str]] = set()
    lines = source.splitlines()
    for value in values:
        for line_no, line in enumerate(lines, start=1):
            if value in line and (line_no, value) not in used:
                used.add((line_no, value))
                literals.append(
                    StringLiteral(path=path, line=line_no, column=0, value=value)
                )
                break
    return literals
