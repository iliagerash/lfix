"""Walk project paths and classify files."""

from __future__ import annotations

import fnmatch
import os
from collections.abc import Iterable
from pathlib import Path

from llmfixture.scan.types import ClassifiedFile, FileKind

DEFAULT_IGNORE_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".eggs",
        "*.egg-info",
    }
)

_SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
_CONFIG_NAMES = {".env", ".env.example", ".env.local"}
_CONFIG_SUFFIXES = {".yml", ".yaml", ".toml"}


def discover(paths: Iterable[Path], *, cwd: Path | None = None) -> list[ClassifiedFile]:
    cwd = cwd or Path.cwd()
    found: dict[Path, ClassifiedFile] = {}
    for raw in paths:
        root = raw if raw.is_absolute() else cwd / raw
        if not root.exists():
            continue
        gitignore = _load_gitignore(root if root.is_dir() else root.parent)
        if root.is_file():
            classified = _classify(root, root.parent)
            if classified is not None:
                found[root.resolve()] = classified
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            current = Path(dirpath)
            dirnames[:] = [
                name
                for name in dirnames
                if not _ignored(Path(name), gitignore, is_dir=True)
            ]
            for name in filenames:
                path = current / name
                rel = path.relative_to(root)
                if _ignored(rel, gitignore, is_dir=False):
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
    if path.name in _CONFIG_NAMES or suffix in _CONFIG_SUFFIXES:
        return ClassifiedFile(path=path, kind=FileKind.config)
    return None


def _load_gitignore(root: Path) -> tuple[str, ...]:
    path = root / ".gitignore"
    if not path.is_file():
        return ()
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        patterns.append(line)
    return tuple(patterns)


def _ignored(rel: Path, gitignore: tuple[str, ...], *, is_dir: bool) -> bool:
    name = rel.name
    if name in DEFAULT_IGNORE_DIRS or name.endswith(".egg-info"):
        return True
    posix = rel.as_posix()
    for pattern in gitignore:
        directory_only = pattern.endswith("/")
        pat = pattern.rstrip("/")
        if directory_only and not is_dir:
            if any(fnmatch.fnmatch(part, pat) for part in rel.parts[:-1]):
                return True
            continue
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(posix, pat):
            return True
        if any(fnmatch.fnmatch(part, pat) for part in rel.parts):
            return True
    return False
