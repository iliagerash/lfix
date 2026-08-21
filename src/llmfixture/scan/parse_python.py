"""Extract string literals and call sites from Python via ast."""

from __future__ import annotations

import ast
from pathlib import Path

from llmfixture.scan.types import CallSite, StringLiteral


def parse_python(path: Path, source: str) -> tuple[list[StringLiteral], list[CallSite]]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], []
    visitor = _Visitor(path)
    visitor.visit(tree)
    return visitor.literals, visitor.calls


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.literals: list[StringLiteral] = []
        self.calls: list[CallSite] = []

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            self.literals.append(
                StringLiteral(
                    path=self.path,
                    line=node.lineno,
                    column=node.col_offset,
                    value=node.value,
                )
            )

    def visit_Call(self, node: ast.Call) -> None:
        kwargs: dict[str, object] = {}
        for keyword in node.keywords:
            if keyword.arg is None:
                continue
            value = keyword.value
            if isinstance(value, ast.Constant):
                kwargs[keyword.arg] = value.value
        self.calls.append(
            CallSite(
                path=self.path,
                line=node.lineno,
                column=node.col_offset,
                callee=_callee(node.func),
                kwargs=kwargs,
            )
        )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._model_binding(target, node.value, node.lineno, node.col_offset)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._model_binding(node.target, node.value, node.lineno, node.col_offset)
        self.generic_visit(node)

    def _model_binding(
        self, target: ast.expr, value: ast.expr, line: int, column: int
    ) -> None:
        if not isinstance(target, ast.Name):
            return
        if "model" not in target.id.lower():
            return
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            self.calls.append(
                CallSite(
                    path=self.path,
                    line=line,
                    column=column,
                    callee="",
                    kwargs={"model": value.value},
                )
            )


def _callee(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _callee(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""
