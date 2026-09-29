from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUI = ROOT / "src/keys_ng/tui/main.py"


def _class_methods(class_name: str) -> set[str]:
    tree = ast.parse(TUI.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {child.name for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))}
    raise AssertionError(f"Class not found: {class_name}")


def test_modal_screens_do_not_override_textual_refresh() -> None:
    # Textual calls Widget.refresh() while mounting/styling a screen. An application
    # method with the same name can run before compose/on_mount has created child
    # widgets and crash with NoMatches. Keep application refresh operations named
    # explicitly instead of overriding the framework lifecycle method.
    for class_name in ("InboxScreen", "TrustedSignersScreen"):
        assert "refresh" not in _class_methods(class_name)


def test_inbox_and_trust_have_explicit_refresh_methods() -> None:
    assert "refresh_inbox" in _class_methods("InboxScreen")
    assert "refresh_signers" in _class_methods("TrustedSignersScreen")
