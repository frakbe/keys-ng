from __future__ import annotations

import hashlib
from pathlib import Path

from keys_ng.platform.app_identity import APP_ID, APP_NAME, DESKTOP_FILE_NAME, icon_bytes


LEGACY_ICON_SHA256 = "d31d8e46d40f914355633cf65da86120d550406a190e1c086754511da173b58b"


def test_bundled_icon_is_exact_legacy_icon():
    digest = hashlib.sha256(icon_bytes()).hexdigest()
    assert digest == LEGACY_ICON_SHA256
    assert len(icon_bytes()) == 1339


def test_gui_applies_application_icon_and_identity():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "configure_process_identity()" in source
    assert "apply_qt_identity(app)" in source
    assert "window.setWindowIcon(application_icon)" in source
    assert APP_NAME == "Keys NG"
    assert APP_ID == "org.keysng.KeysNG"
    assert DESKTOP_FILE_NAME == APP_ID


def test_tui_sets_terminal_identity_best_effort():
    source = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert "set_textual_terminal_title(self)" in source


def test_icon_is_declared_as_package_data():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert '"resources/*.png"' in pyproject
    assert '"resources/*.desktop"' in pyproject


def test_icon_attribution_is_documented():
    assert "keys-icon.png" in Path("LICENSE").read_text(encoding="utf-8")
    assert "Franco 'frakbe' Bersani" in Path("LICENSE").read_text(encoding="utf-8")
