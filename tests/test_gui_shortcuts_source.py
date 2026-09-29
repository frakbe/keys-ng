from pathlib import Path


def test_gui_exposes_requested_copy_shortcuts_and_manual_totp_secret():
    source = (Path(__file__).parents[1] / "src" / "keys_ng" / "gui" / "main.py").read_text(encoding="utf-8")
    for shortcut in ("Ctrl+U", "Ctrl+B", "Ctrl+C", "Ctrl+T"):
        assert shortcut in source
    assert '_("TOTP secret")' in source
    service = (Path(__file__).parents[1] / "src" / "keys_ng" / "services" / "entry_editor.py").read_text(encoding="utf-8")
    assert "totp_from_secret" in service
    assert "build_entry_from_draft" in source
    assert "def copy_url_clicked" in source
