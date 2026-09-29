from pathlib import Path

from keys_ng.services.ui_capabilities import (
    GUI_CAPABILITIES,
    INTERACTIVE_CAPABILITIES,
    TUI_CAPABILITIES,
    missing_interactive_capabilities,
)

ROOT = Path(__file__).resolve().parents[1]


def test_gui_tui_interactive_capability_contract_is_equal():
    assert GUI_CAPABILITIES == INTERACTIVE_CAPABILITIES
    assert TUI_CAPABILITIES == INTERACTIVE_CAPABILITIES
    assert not missing_interactive_capabilities("gui")
    assert not missing_interactive_capabilities("tui")


def test_gui_and_tui_expose_m120_user_workflows():
    gui = (ROOT / "src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    tui = (ROOT / "src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    for token in (
        "import_keepassxc",
        "export_vault_xml",
        "generate_password",
        "copy_notes",
    ):
        assert token in gui
        assert token in tui
    assert "KeePassXCImportDialog" in gui
    assert "KeePassXCImportScreen" in tui
    assert "PasswordGeneratorDialog" in gui
    assert "PasswordGeneratorScreen" in tui


def test_tui_ctrl_c_is_not_priority_global_binding():
    source = (ROOT / "src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert 'Binding("ctrl+c", "copy_password", _("Copy password"))' in source
    assert 'Binding("ctrl+c", "copy_password", _("Copy password"), priority=True)' not in source
