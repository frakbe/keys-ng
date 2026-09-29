from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
TUI = (ROOT / "src/keys_ng/tui/main.py").read_text(encoding="utf-8")


def _keys_app_binding_keys() -> list[str]:
    tree = ast.parse(TUI)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "KeysApp":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BINDINGS" for t in stmt.targets):
                    keys = []
                    if isinstance(stmt.value, ast.List):
                        for item in stmt.value.elts:
                            if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "Binding" and item.args:
                                if isinstance(item.args[0], ast.Constant) and isinstance(item.args[0].value, str):
                                    keys.append(item.args[0].value)
                    return keys
    raise AssertionError("KeysApp.BINDINGS not found")


def test_preferences_binding_is_terminal_portable():
    assert 'Binding("f2", "preferences"' in TUI
    assert 'Binding("ctrl+shift+p", "preferences"' not in TUI
    assert 'Binding("ctrl+,", "preferences"' not in TUI


def test_main_tui_has_no_ctrl_shift_letter_bindings():
    keys = _keys_app_binding_keys()
    assert not [key for key in keys if key.startswith("ctrl+shift+")], keys


def test_terminal_ambiguous_ctrl_i_is_not_used_for_trusted_signers():
    assert 'Binding("ctrl+i", "trusted_signers"' not in TUI
    assert 'Binding("f3", "trusted_signers"' in TUI


def test_question_mark_opens_inline_command_guide():
    assert 'Binding("question_mark", "shortcut_help"' in TUI
    assert 'HelpScreen("TUI_SHORTCUTS.md")' in TUI


def test_no_binding_key_ends_with_literal_comma():
    tree = ast.parse(TUI)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Binding" and node.args:
            key = node.args[0]
            if isinstance(key, ast.Constant) and isinstance(key.value, str) and key.value.endswith(","):
                bad.append(key.value)
    assert not bad, f"Textual binding keys ending in a literal comma are parsed as an empty alternate binding: {bad}"
