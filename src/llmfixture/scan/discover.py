"""Walk project paths and classify files."""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from pathspec import GitIgnoreSpec

from llmfixture.scan.types import ClassifiedFile, FileKind

_SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
_CONFIG_NAMES = {".env", ".env.example", ".env.local"}


def discover(paths: Iterable[Path], *, cwd: Path | None = None) -> list[ClassifiedFile]:
    cwd = cwd or Path.cwd()
    found: dict[Path, ClassifiedFile] = {}
    for raw in paths:
        root = raw if raw.is_absolute() else cwd / raw
        if not root.exists():
            continue
        walk_root = root if root.is_dir() else root.parent
        base, spec = _ignore_spec(walk_root)
        if root.is_file():
            classified = _classify(root, walk_root)
            if classified is not None:
                found[root.resolve()] = classified
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            current = Path(dirpath)
            dirnames[:] = [
                name
                for name in dirnames
                if name != ".git"
                and not _ignored(spec, base, current / name, is_dir=True)
            ]
            for name in filenames:
                path = current / name
                if _ignored(spec, base, path, is_dir=False):
                    continue
                classified = _classify(path, root)
                if classified is not None:
                    found[path.resolve()] = classified
    return sorted(found.values(), key=lambda item: str(item.path))


def _classify(path: Path, root: Path) -> ClassifiedFile | None:
    suffix = path.suffix.lower()
    try:
        rel_parts = path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        rel_parts = path.parts
    if path.name.endswith(".d.ts") or ".min." in path.name:
        return None
    if suffix in _SOURCE_SUFFIXES:
        return ClassifiedFile(path=path, kind=FileKind.source)
    if path.name.endswith(".schema.json") or (
        "schemas" in rel_parts and suffix == ".json"
    ):
        return ClassifiedFile(path=path, kind=FileKind.schema)
    if (
        "prompts" in rel_parts
        or path.name.endswith(".prompt.md")
        or ("prompts" in rel_parts and suffix == ".txt")
    ):
        return ClassifiedFile(path=path, kind=FileKind.prompt)
    if path.name in _CONFIG_NAMES:
        return ClassifiedFile(path=path, kind=FileKind.config)
    return None


def _ignore_spec(start: Path) -> tuple[Path, GitIgnoreSpec]:
    base = _git_root(start) or start.resolve()
    gitignore = base / ".gitignore"
    if not gitignore.is_file():
        return base, GitIgnoreSpec.from_lines([])
    text = gitignore.read_text(encoding="utf-8", errors="replace")
    return base, GitIgnoreSpec.from_lines(text.splitlines())


def _git_root(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for path in (current, *current.parents):
        if (path / ".git").exists():
            return path
    return None


def _ignored(spec: GitIgnoreSpec, base: Path, path: Path, *, is_dir: bool) -> bool:
    try:
        posix = path.resolve().relative_to(base).as_posix()
    except ValueError:
        return False
    if spec.match_file(posix):
        return True
    return is_dir and spec.match_file(f"{posix}/")
