from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from keys_ng import __version__
from keys_ng.platform.desktop_integration import install_user_desktop_integration


def test_version_source_matches_expected_release():
    assert __version__ == "0.1.23"


def test_cli_version_command():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path("src").resolve())
    result = subprocess.run(
        [sys.executable, "-m", "keys_ng.cli.main", "version"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.stdout.strip() == f"Keys NG {__version__}"


def test_tui_version_works_without_loading_textual():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path("src").resolve())
    result = subprocess.run(
        [sys.executable, "-m", "keys_ng.tui.main", "version"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.stdout.strip() == f"Keys NG {__version__}"


def test_linux_launcher_has_no_tryexec(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    paths = install_user_desktop_integration()
    desktop = paths.desktop_file.read_text(encoding="utf-8")
    assert "TryExec=" not in desktop
    assert "Exec=" in desktop


def test_desktop_template_has_no_tryexec():
    desktop = Path("src/keys_ng/resources/org.keysng.KeysNG.desktop").read_text(encoding="utf-8")
    assert "TryExec=" not in desktop


def test_gui_license_displays_dynamic_version():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "Installed version:" in source
    assert "version=__version__" in source
