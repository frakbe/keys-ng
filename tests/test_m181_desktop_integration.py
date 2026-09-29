from __future__ import annotations

from pathlib import Path

from keys_ng.platform.app_identity import APP_ID, DESKTOP_FILE_NAME, icon_bytes
from keys_ng.platform.desktop_integration import (
    desktop_integration_status,
    ensure_user_desktop_integration,
    install_user_desktop_integration,
    uninstall_user_desktop_integration,
    user_paths,
)


def test_desktop_identity_matches_desktop_filename():
    assert DESKTOP_FILE_NAME == APP_ID


def test_user_desktop_integration_install_and_remove(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    paths = install_user_desktop_integration()

    assert paths.desktop_file == tmp_path / "applications" / f"{APP_ID}.desktop"
    assert paths.icon_file == tmp_path / "icons" / "hicolor" / "64x64" / "apps" / f"{APP_ID}.png"
    assert paths.icon_file.read_bytes() == icon_bytes()

    desktop = paths.desktop_file.read_text(encoding="utf-8")
    assert f"Icon={APP_ID}" in desktop
    assert "Type=Application" in desktop
    assert "NoDisplay=false" in desktop
    assert "TryExec=" not in desktop

    ok, status_paths = desktop_integration_status()
    assert ok is True
    assert status_paths == paths

    uninstall_user_desktop_integration()
    ok, _ = desktop_integration_status()
    assert ok is False


def test_gui_ensures_desktop_integration_on_linux():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "ensure_user_desktop_integration()" in source
