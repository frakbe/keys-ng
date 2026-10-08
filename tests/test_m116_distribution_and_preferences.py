from __future__ import annotations

from pathlib import Path
import tomllib

from keys_ng import __version__


def test_m116_version_and_briefcase_match():
    assert __version__ == "0.1.25"
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["tool"]["briefcase"]["version"] == __version__


def test_flatpak_manifest_uses_pyside_baseapp_and_host_spawn_permission():
    text = Path("packaging/flatpak/org.keysng.KeysNG.yml").read_text(encoding="utf-8")
    assert "io.qt.PySide.BaseApp" in text
    assert "org.keysng.KeysNG" in text
    assert "--talk-name=org.freedesktop.Flatpak" in text


def test_native_distribution_workflow_contains_all_desktop_targets():
    text = Path(".github/workflows/distribution.yml").read_text(encoding="utf-8")
    assert "windows-msi:" in text
    assert "macos-dmg:" in text
    assert "linux-flatpak:" in text
    assert "briefcase package windows -a keys_ng -p msi" in text
    assert "briefcase package macOS -a keys_ng -p dmg" in text
    assert "flatpak build-bundle" in text


def test_gui_has_preferences_and_new_lock_shortcuts():
    text = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "class SettingsDialog(QDialog)" in text
    assert '_("Preferences…")' in text
    assert '("Ctrl+L", lambda: self.call_active("lock", False))' in text
    assert '("Ctrl+Shift+L", self.hard_lock_all)' in text
    assert '("Ctrl+P", lambda: self.call_active("unlock"))' in text


def test_tui_has_new_lock_shortcuts_and_unlock_action():
    text = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert 'Binding("ctrl+l", "lock_vault"' in text
    assert 'Binding("f9", "hard_lock_vault"' in text
    assert 'Binding("ctrl+p", "unlock_vault"' in text
    assert "def action_unlock_vault" in text


def test_macos_icon_is_real_icns():
    data = Path("src/keys_ng/resources/keys-icon.icns").read_bytes()
    assert data[:4] == b"icns"


def test_flatpak_host_adapter_uses_flatpak_spawn(monkeypatch):
    from keys_ng.platform import host
    monkeypatch.setenv("FLATPAK_ID", "org.keysng.KeysNG")
    monkeypatch.setattr(host.shutil, "which", lambda name: "/usr/bin/flatpak-spawn" if name == "flatpak-spawn" else None)
    assert host.host_argv(["gpg", "--version"]) == ["/usr/bin/flatpak-spawn", "--host", "gpg", "--version"]


def test_flatpak_disables_self_desktop_registration():
    text = Path("src/keys_ng/platform/desktop_integration.py").read_text(encoding="utf-8")
    assert "if in_flatpak():" in text
    assert "return None" in text


def test_tui_preferences_exposes_gui_settings():
    text = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    for label in (
        "pref-crypto",
        "pref-verify-gpg",
        "pref-notice-bg",
        "pref-notice-fg",
        "pref-notice-seconds",
        "pref-ssh-terminal",
        "pref-ssh-options",
        "pref-rdp-linux-client",
        "pref-rdp-linux-options",
        "pref-rdp-windows-client",
        "pref-rdp-windows-options",
        "pref-rdp-macos-client",
        "pref-rdp-macos-options",
    ):
        assert label in text


def test_launcher_settings_are_used_by_tui_and_gui():
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "settings=settings" in tui
    assert "settings=settings" in gui
    assert "pref-diagnostics" not in tui
    assert 'classes="prefs-options"' in tui
