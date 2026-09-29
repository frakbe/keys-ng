from pathlib import Path


def test_gui_uses_tree_and_folder_controls():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "QTreeWidget" in source
    assert "New folder" in source
    assert "move_folder" in source
    assert "move_entry" in source


def test_tui_entrypoint_and_tree_exist():
    source = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    project = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "Tree(" in source
    assert 'keys-ng-tui = "keys_ng.tui.main:main"' in project
    assert 'tui = ["textual' in project
