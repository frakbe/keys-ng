from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "src/keys_ng/gui/main.py"


def _direct_nodes(function: ast.FunctionDef | ast.AsyncFunctionDef):
    """Yield nodes in one function scope, without descending into nested scopes."""
    stack = list(function.body)
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        stack.extend(ast.iter_child_nodes(node))


def test_gui_functions_do_not_shadow_gettext_alias_with_discard_variable() -> None:
    """`_` is gettext in this module, so assigning to `_` makes it local and breaks `_()` calls."""
    tree = ast.parse(GUI.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for function in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
        nodes = list(_direct_nodes(function))
        calls_gettext = any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_"
            for node in nodes
        )
        binds_underscore = any(
            isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "_"
            for node in nodes
        )
        if calls_gettext and binds_underscore:
            offenders.append(function.name)
    assert not offenders, f"GUI functions shadow gettext alias `_`: {offenders}"
