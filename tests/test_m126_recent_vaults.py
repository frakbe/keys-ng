from pathlib import Path

SOURCE = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")


def test_gui_start_page_lists_three_recent_vaults():
    assert "settings.recent_vaults[:3]" in SOURCE
    assert "self.recent_list = QListWidget()" in SOURCE
    assert "self.recent_list.itemClicked.connect(self.open_recent_vault)" in SOURCE
    assert 'QListWidgetItem(f"{path.name or str(path)}\\n{path}")' in SOURCE


def test_recent_vault_item_opens_the_stored_path():
    assert "item.data(Qt.ItemDataRole.UserRole)" in SOURCE
    assert "self.open_vault(str(path))" in SOURCE


def test_gui_global_hard_lock_captures_tree_state():
    assert "pane._capture_expanded_folders()" in SOURCE
    assert "pane.vault.lock(hard=False)" in SOURCE
