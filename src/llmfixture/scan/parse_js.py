"""Extract string literals and model= / model: sites from JS/TS via regex."""

from __future__ import annotations

import re
from pathlib import Path

from llmfixture.scan.types import CallSite, StringLiteral

_STRING = re.compile(r"""(?P<q>['"])(?P<body>(?:\\.|[^\\])*?)(?P=q)""")
_LINE_COMMENT = re.compile(r"//.*$")
_KWARG = re.compile(
    r"\b(?P<key>model|max_tokens|max_output_tokens|response_format)\s*[:=]\s*"
    r"(?P<q>['\"])(?P<body>(?:\\.|[^\\])*?)(?P=q)",
)


def parse_js(path: Path, source: str) -> tuple[list[StringLiteral], list[CallSite]]:
    literals: list[StringLiteral] = []
    calls: list[CallSite] = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        code = _LINE_COMMENT.sub("", line)
        for match in _STRING.finditer(code):
            literals.append(
                StringLiteral(
                    path=path,
                    line=line_no,
                    column=match.start("body"),
                    value=_unescape(match.group("body")),
                )
            )
        kwargs: dict[str, object] = {}
        for match in _KWARG.finditer(code):
            kwargs[match.group("key")] = _unescape(match.group("body"))
        if kwargs:
            calls.append(
                CallSite(
                    path=path,
                    line=line_no,
                    column=0,
                    callee="",
                    kwargs=kwargs,
                )
            )
    return literals, calls


def _unescape(value: str) -> str:
    return value.replace(r"\'", "'").replace(r"\"", '"').replace(r"\\", "\\")
