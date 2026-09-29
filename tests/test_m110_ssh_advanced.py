from __future__ import annotations

from pathlib import Path

import pytest

from keys_ng.models import Action, Entry
from keys_ng.services import actions as actions_service
from keys_ng.services.ssh_options import SSHOptionsError, format_ssh_options, parse_ssh_options
from keys_ng.storage.settings import AppSettings


def test_ssh_advanced_options_roundtrip_in_entry_json():
    entry = Entry.create(
        "Production",
        actions=[Action(
            type="ssh",
            host="server.example.org",
            port=22,
            username="mario",
            ssh_x11_forwarding="Y",
            ssh_options=["-J", "bastion.example.org", "-o", "ServerAliveInterval=30"],
        )],
    )
    loaded = Entry.from_bytes(entry.to_bytes())
    action = loaded.actions[0]
    assert action.ssh_x11_forwarding == "Y"
    assert action.ssh_options == ["-J", "bastion.example.org", "-o", "ServerAliveInterval=30"]


def test_linux_ssh_places_x11_and_advanced_options_before_destination(monkeypatch):
    commands = []
    found = {"ssh": "/usr/bin/ssh", "xdg-terminal-exec": "/usr/bin/xdg-terminal-exec"}
    monkeypatch.setattr(actions_service.shutil, "which", lambda name: found.get(name))
    monkeypatch.setattr(actions_service.subprocess, "Popen", lambda argv, shell=False: commands.append((argv, shell)))
    monkeypatch.setattr(actions_service.sys, "platform", "linux")

    actions_service.launch_action(
        Action(
            type="ssh",
            host="server.example.org",
            port=2222,
            username="mario",
            ssh_x11_forwarding="Y",
            ssh_options=["-J", "jump.example.org", "-o", "ServerAliveInterval=30"],
        ),
        AppSettings(ssh_terminal="auto"),
    )

    assert commands == [([
        "/usr/bin/xdg-terminal-exec",
        "/usr/bin/ssh",
        "-Y",
        "-J",
        "jump.example.org",
        "-o",
        "ServerAliveInterval=30",
        "-p",
        "2222",
        "mario@server.example.org",
    ], False)]


def test_parse_ssh_options_supports_jump_host_and_quoting():
    argv = parse_ssh_options('-J bastion.example.org -o "ProxyJump=jump user" -L 8080:localhost:80')
    assert argv == ["-J", "bastion.example.org", "-o", "ProxyJump=jump user", "-L", "8080:localhost:80"]
    assert parse_ssh_options(format_ssh_options(argv)) == argv


@pytest.mark.parametrize("text", ["-X", "-Y", "-x", "-p 2200", "-p2200", "-l root", "-lroot", "-o Port=2200", "-oUser=root", "-- foo"])
def test_ssh_advanced_options_cannot_override_managed_fields(text):
    with pytest.raises(SSHOptionsError):
        parse_ssh_options(text)


def test_gui_exposes_x11_and_advanced_ssh_controls():
    source = (Path(__file__).parents[1] / "src" / "keys_ng" / "gui" / "main.py").read_text(encoding="utf-8")
    assert 'self.ssh_x11_combo.addItem(_("X11 forwarding (-X)"), "X")' in source
    assert 'self.ssh_x11_combo.addItem(_("Trusted X11 forwarding (-Y)"), "Y")' in source
    assert 'form.addRow(self.ssh_options_label, self.ssh_options_edit)' in source
    service = (Path(__file__).parents[1] / 'src' / 'keys_ng' / 'services' / 'entry_editor.py').read_text(encoding='utf-8')
    assert 'parse_ssh_options(draft.ssh_options)' in service
    assert 'ssh_options=parse_ssh_options' in service
