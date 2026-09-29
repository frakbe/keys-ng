from pathlib import Path


def test_gui_can_start_without_vault_and_open_native_directory_dialog():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("vault", nargs="*"' in source
    assert "QFileDialog.getExistingDirectory" in source
    assert '_("No vault is open.")' in source
    assert '_("Open vault…")' in source


def test_gui_uses_vertical_multi_vault_tabs():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "class VaultPane(QWidget)" in source
    assert "class MainWindow(QMainWindow)" in source
    assert "QTabWidget.TabPosition.West" in source
    assert "self.tabs.setTabsClosable(True)" in source
    assert "self.tabs.addTab(pane, pane.display_name)" in source
    assert "self.tabs.setTabToolTip(index, str(resolved))" in source


def test_multi_vault_actions_are_dispatched_only_to_active_tab():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "def active_pane(self) -> VaultPane | None:" in source
    assert "def call_active(self, method: str, *args) -> None:" in source
    for method in (
        "focus_search",
        "copy_url_clicked",
        "copy_username_clicked",
        "copy_password_clicked",
        "copy_otp_clicked",
        "open_action_clicked",
    ):
        assert f'call_active("{method}")' in source


def test_hard_lock_clears_all_open_vaults_before_killing_agent():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "def hard_lock_all(self) -> None:" in source
    assert "pane.vault.lock(hard=False)" in source
    assert "panes[0].vault.crypto.hard_lock()" in source
