from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUI = ROOT / "src/keys_ng/tui/main.py"

def _source() -> str:
    return TUI.read_text(encoding="utf-8")

def test_tui_handles_textual_select_null_sentinel() -> None:
    source = _source()
    assert 'getattr(Select, "NULL", None)' in source
    assert 'event.value not in (None, Select.BLANK)' not in source
    assert 'value in (None, Select.BLANK)' not in source
    assert 'value not in (None, Select.BLANK)' not in source

def test_inbox_changed_handler_guards_before_integer_conversion() -> None:
    tree = ast.parse(_source())
    inbox = next(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == "InboxScreen")
    handler = next(node for node in inbox.body if isinstance(node, ast.FunctionDef) and node.name == "on_select_changed")
    rendered = ast.unparse(handler)
    assert "_select_value_is_blank(event.value)" in rendered
    assert "int(str(event.value))" in rendered
