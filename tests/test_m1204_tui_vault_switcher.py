from pathlib import Path

from keys_ng.services.vault_sessions import VaultSessionManager


class DummyVault:
    def __init__(self, path: Path, locked: bool = False) -> None:
        self.path = path.resolve()
        self.locked = locked
        self.lock_calls = 0

    def lock(self, hard: bool = False) -> None:
        self.locked = True
        self.lock_calls += 1


def test_session_manager_keeps_multiple_vaults_and_switches(tmp_path):
    a = DummyVault(tmp_path / "a")
    b = DummyVault(tmp_path / "b", locked=True)
    manager = VaultSessionManager(a)  # type: ignore[arg-type]
    manager.add(b)  # type: ignore[arg-type]

    assert len(manager) == 2
    assert manager.active is b
    assert manager.activate(a.path) is a
    assert manager.active is a
    assert b.locked is True


def test_session_manager_close_active_falls_back_to_an_open_vault(tmp_path):
    a = DummyVault(tmp_path / "a")
    b = DummyVault(tmp_path / "b")
    manager = VaultSessionManager(a)  # type: ignore[arg-type]
    manager.add(b)  # type: ignore[arg-type]

    replacement = manager.close(b.path)

    assert replacement is a
    assert manager.active is a
    assert b.lock_calls == 1


def test_session_manager_lock_all_preserves_sessions(tmp_path):
    a = DummyVault(tmp_path / "a")
    b = DummyVault(tmp_path / "b")
    manager = VaultSessionManager(a)  # type: ignore[arg-type]
    manager.add(b)  # type: ignore[arg-type]

    manager.lock_all()

    assert len(manager) == 2
    assert a.locked and b.locked


def test_tui_binds_ctrl_j_to_open_vault_switcher():
    root = Path(__file__).resolve().parents[1]
    text = (root / "src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert 'Binding("ctrl+j", "switch_vault"' in text
    assert "def action_switch_vault(self) -> None:" in text
    assert "VaultSwitcherScreen()" in text
    assert "sessions.add(Vault(candidate, crypto), activate=True)" in text


def test_switch_vault_message_is_temporary_banner():
    root = Path(__file__).resolve().parents[1]
    text = (root / "src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    block = text.split("def _display_active_vault", 1)[1].split("def _activate_opened_vault", 1)[0]
    assert 'self._show_clipboard_banner(message, "success")' in block
    assert 'self._status(message)' not in block
