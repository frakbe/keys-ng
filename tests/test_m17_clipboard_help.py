from pathlib import Path

from keys_ng.i18n import configure_language, current_language
from keys_ng.services import clipboard


def test_native_clipboard_prefers_wayland(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda name: f"/usr/bin/{name}" if name in {"wl-copy", "wl-paste", "xclip", "xsel"} else None)
    assert clipboard.available_native_clipboard_backend() == "wayland"


def test_native_clipboard_never_places_secret_in_argv(monkeypatch):
    calls = []

    def fake_run(argv, *, input_bytes=None, timeout=3.0):
        calls.append((argv, input_bytes))
        return b""

    monkeypatch.setattr(clipboard, "_run_clipboard_command", fake_run)
    secret = "s3cret value with spaces"
    assert clipboard.set_native_clipboard(secret, "xclip") == "xclip"
    argv, input_bytes = calls[0]
    assert secret not in " ".join(argv)
    assert input_bytes == secret.encode("utf-8")


def test_gui_open_shortcut_and_localized_help_sources():
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert '("Ctrl+O", lambda: self.call_active("open_action_clicked"))' in gui
    assert 'self._menu_action(entry_menu, _("Open"), lambda: self.call_active("open_action_clicked"), "Ctrl+O")' in gui
    assert "current_language()" in gui
    assert 'joinpath(language, resource_name)' in gui
    assert 'joinpath("en", resource_name)' in gui


def test_explicit_italian_language_is_exposed_for_help_selection():
    configure_language("it_IT")
    assert current_language() == "it"


def test_license_names_original_author():
    for path in (Path("LICENSE"), Path("LICENSE.it.md"), Path("src/keys_ng/help/en/LICENSE.md"), Path("src/keys_ng/help/it/LICENSE.md")):
        text = path.read_text(encoding="utf-8")
        assert "Franco 'frakbe' Bersani" in text


def test_tui_uses_textual_clipboard_as_last_resort():
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert "self.copy_to_clipboard(value)" in tui
    assert "automatic clearing could not be verified" in tui
