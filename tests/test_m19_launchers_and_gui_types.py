from __future__ import annotations

from pathlib import Path

import pytest

from keys_ng.models import Action
from keys_ng.services import actions as actions_service
from keys_ng.storage.settings import AppSettings


def test_settings_roundtrip_launcher_options(tmp_path):
    path = tmp_path / "config.toml"
    settings = AppSettings(
        ssh_terminal="gnome-terminal",
        ssh_terminal_options=["--", "--wait"],
        rdp_linux_client="xfreerdp3",
        rdp_linux_options=["/dynamic-resolution", "+clipboard"],
        rdp_windows_client="mstsc",
        rdp_windows_options=["/f", "/multimon"],
        rdp_macos_client="open",
        rdp_macos_options=["-a", "Windows App"],
    )
    settings.save(path)
    assert AppSettings.load(path) == settings


def test_settings_reject_non_string_launcher_option(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[launchers.ssh]\nterminal_options = ["--", 1]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="terminal_options"):
        AppSettings.load(path)


def test_linux_ssh_uses_terminal_without_shell(monkeypatch):
    commands = []
    found = {
        "ssh": "/usr/bin/ssh",
        "xdg-terminal-exec": "/usr/bin/xdg-terminal-exec",
    }
    monkeypatch.setattr(actions_service.shutil, "which", lambda name: found.get(name))
    monkeypatch.setattr(actions_service.subprocess, "Popen", lambda argv, shell=False: commands.append((argv, shell)))
    monkeypatch.setattr(actions_service.sys, "platform", "linux")

    actions_service.launch_action(
        Action(type="ssh", host="server.example.org", port=2222, username="mario"),
        AppSettings(ssh_terminal="auto"),
    )

    assert commands == [([
        "/usr/bin/xdg-terminal-exec",
        "/usr/bin/ssh",
        "-p",
        "2222",
        "mario@server.example.org",
    ], False)]


def test_linux_rdp_adds_configured_options(monkeypatch):
    commands = []
    monkeypatch.setattr(actions_service.shutil, "which", lambda name: "/usr/bin/xfreerdp3" if name == "xfreerdp3" else None)
    monkeypatch.setattr(actions_service.subprocess, "Popen", lambda argv, shell=False: commands.append((argv, shell)))
    monkeypatch.setattr(actions_service.sys, "platform", "linux")

    actions_service.launch_action(
        Action(type="rdp", host="rdp.example.org", port=3390, username="DOMAIN\\mario"),
        AppSettings(rdp_linux_options=["/dynamic-resolution", "+clipboard"]),
    )

    assert commands == [([
        "/usr/bin/xfreerdp3",
        "/dynamic-resolution",
        "+clipboard",
        "/v:rdp.example.org:3390",
        "/u:DOMAIN\\mario",
    ], False)]


def test_linux_rdp_uses_domain_and_password_stdin(monkeypatch):
    commands = []

    class FakeStdin:
        def __init__(self):
            self.data = ""
            self.closed = False

        def write(self, value):
            self.data += value
            return len(value)

        def flush(self):
            pass

        def close(self):
            self.closed = True

    class FakeProcess:
        def __init__(self):
            self.stdin = FakeStdin()

    process = FakeProcess()

    def fake_popen(argv, shell=False, **kwargs):
        commands.append((argv, shell, kwargs))
        return process

    monkeypatch.setattr(actions_service.shutil, "which", lambda name: "/usr/bin/xfreerdp3" if name == "xfreerdp3" else None)
    monkeypatch.setattr(actions_service.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(actions_service.sys, "platform", "linux")

    actions_service.launch_action(
        Action(
            type="rdp",
            host="rdp.example.org",
            username="mario",
            rdp_domain="CONTOSO",
        ),
        AppSettings(rdp_linux_options=["/dynamic-resolution", "+clipboard"]),
        password="correct horse battery staple",
    )

    argv, shell, kwargs = commands[0]
    assert shell is False
    assert "/d:CONTOSO" in argv
    assert "/from-stdin:force" in argv
    assert not any(item.startswith("/p:") for item in argv)
    assert kwargs["stdin"] is actions_service.subprocess.PIPE
    assert kwargs["text"] is True
    assert process.stdin.data == "correct horse battery staple\n"
    assert process.stdin.closed is True


def test_linux_rdp_defaults_to_local_domain(monkeypatch):
    commands = []
    monkeypatch.setattr(actions_service.shutil, "which", lambda name: "/usr/bin/xfreerdp3" if name == "xfreerdp3" else None)
    monkeypatch.setattr(actions_service.subprocess, "Popen", lambda argv, shell=False: commands.append((argv, shell)))
    monkeypatch.setattr(actions_service.sys, "platform", "linux")

    actions_service.launch_action(
        Action(type="rdp", host="rdp.example.org", username="mario"),
        AppSettings(),
    )

    assert "/d:." in commands[0][0]


def test_linux_rdp_preserves_embedded_domain_username(monkeypatch):
    commands = []
    monkeypatch.setattr(actions_service.shutil, "which", lambda name: "/usr/bin/xfreerdp3" if name == "xfreerdp3" else None)
    monkeypatch.setattr(actions_service.subprocess, "Popen", lambda argv, shell=False: commands.append((argv, shell)))
    monkeypatch.setattr(actions_service.sys, "platform", "linux")

    actions_service.launch_action(
        Action(type="rdp", host="rdp.example.org", username="DOMAIN\\mario"),
        AppSettings(),
    )

    assert not any(item.startswith("/d:") for item in commands[0][0])


def test_gui_entry_dialog_has_web_ssh_rdp_selector():
    source = (Path(__file__).parents[1] / "src" / "keys_ng" / "gui" / "main.py").read_text(encoding="utf-8")
    assert 'self.action_type_combo.addItem(_("Web / URL"), "url")' in source
    assert 'self.action_type_combo.addItem(_("SSH connection"), "ssh")' in source
    assert 'self.action_type_combo.addItem(_("RDP connection"), "rdp")' in source
    assert 'form.addRow(_("Entry type"), self.action_type_combo)' in source
    service = (Path(__file__).parents[1] / 'src' / 'keys_ng' / 'services' / 'entry_editor.py').read_text(encoding='utf-8')
    assert 'type="ssh"' in service and 'host=host' in service and 'username=username or None' in service
    assert 'rdp_domain=draft.rdp_domain.strip() or None' in service
