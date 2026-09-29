from pathlib import Path


def test_tui_copy_bindings_are_priority_and_clipboard_reports_failures():
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    for key in ("ctrl+u", "ctrl+b", "ctrl+c", "ctrl+t"):
        assert f'Binding("{key}"' in tui
    assert tui.count("priority=True") >= 4
    assert "Clipboard error" in tui

    clipboard = Path("src/keys_ng/services/clipboard.py").read_text(encoding="utf-8")
    helper = Path("src/keys_ng/services/clipboard_helper.py").read_text(encoding="utf-8")
    assert 'acknowledgement.startswith("READY")' in clipboard
    assert 'sys.stdout.write(f"READY {backend}\\n")' in helper
    assert "read_native_clipboard" in helper
    assert "Clipboard verification failed" in helper


def test_gui_has_search_menu_and_embedded_help():
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert '"Ctrl+F"' in gui
    assert "setClearButtonEnabled(True)" in gui
    assert "build_menus" in gui
    assert 'addMenu(_("Entry"))' in gui
    assert 'addMenu("?")' in gui
    assert "QTextBrowser" in gui
    assert "setMarkdown" in gui
    assert '"README.md"' in gui
    assert '"SECURITY.md"' in gui
    assert '"LICENSE.md"' in gui
    for language in ("en", "it"):
        assert Path(f"src/keys_ng/help/{language}/README.md").exists()
        assert Path(f"src/keys_ng/help/{language}/SECURITY.md").exists()
        assert Path(f"src/keys_ng/help/{language}/LICENSE.md").exists()
