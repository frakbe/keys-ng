from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUI = (ROOT / "src/keys_ng/tui/main.py").read_text(encoding="utf-8")


def test_locked_tree_selection_is_guarded_before_vault_reads():
    marker = "def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:"
    block = TUI.split(marker, 1)[1].split("def _status", 1)[0]
    assert "if vault.locked:" in block
    assert block.index("if vault.locked:") < block.index("vault.get_entry")
    assert block.index("if vault.locked:") < block.index("vault.get_folder")


def test_single_entry_export_requires_confirmation():
    marker = "def action_export_entry(self) -> None:"
    block = TUI.split(marker, 1)[1].split("def action_lock_vault", 1)[0]
    assert "ConfirmScreen(" in block
    assert "_finish_export_entry" in block
    assert "plaintext KeePassXC XML" in block


def test_password_generator_can_copy_before_use():
    assert 'Button(_("Copy generated password"), id="gen-copy")' in TUI
    assert "def _copy_generated(self)" in TUI
    assert "copy_secret_cli(value, settings.clipboard_password_timeout)" in TUI


def test_no_shift_modifier_in_main_keys_app_bindings():
    start = TUI.index("class KeysApp(App):")
    end = TUI.index("def __init__(self) -> None:", start)
    bindings = TUI[start:end]
    assert "shift+" not in bindings.lower()
