from pathlib import Path


def test_gui_supports_compact_and_expanded_tree_startup():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert '"--tree-view"' in source
    assert '(args.tree_view or settings.tree_startup_view) == "expanded"' in source
    assert 'self.entries.collapseAll()' in source


def test_tui_supports_compact_and_expanded_tree_startup():
    source = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert '"--tree-view"' in source
    assert 'expand=(tree_startup_view == "expanded")' in source
