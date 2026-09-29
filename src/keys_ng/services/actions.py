from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from urllib.parse import quote

from keys_ng.models import Action
from keys_ng.storage.settings import AppSettings
from keys_ng.platform.host import host_argv, in_flatpak


class ActionError(RuntimeError):
    pass


def _which(name: str) -> str | None:
    if not in_flatpak():
        return shutil.which(name)
    from keys_ng.platform.host import host_which
    return host_which(name)


def _resolve_executable(name: str) -> str | None:
    """Resolve a configured executable without invoking a shell."""
    if not name:
        return None
    if not in_flatpak() and (os.path.isabs(name) or os.sep in name or (os.altsep and os.altsep in name)):
        return name if os.path.isfile(name) and os.access(name, os.X_OK) else None
    return _which(name)


def _ssh_terminal(settings: AppSettings) -> tuple[str, list[str]]:
    requested = settings.ssh_terminal.strip()
    if requested.lower() != "auto":
        exe = _resolve_executable(requested)
        if not exe:
            raise ActionError(f"Configured SSH terminal not found: {requested}")
        if settings.ssh_terminal_options:
            return exe, list(settings.ssh_terminal_options)
        inferred = {
            "gnome-terminal": ["--"],
            "kgx": ["--"],
            "ptyxis": ["--"],
            "konsole": ["-e"],
            "xterm": ["-e"],
            "alacritty": ["-e"],
        }.get(os.path.basename(exe), [])
        return exe, inferred

    # Prefer the proposed XDG default-terminal launcher when installed.  It
    # accepts the command and argv directly, so no terminal-specific quoting is
    # necessary.  "xdg-terminal" is also accepted for distributions shipping
    # that spelling.
    candidates: tuple[tuple[str, list[str]], ...] = (
        ("xdg-terminal", []),
        ("xdg-terminal-exec", []),
        ("gnome-terminal", ["--"]),
        ("kgx", ["--"]),
        ("ptyxis", ["--"]),
        ("konsole", ["-e"]),
        ("xterm", ["-e"]),
        ("alacritty", ["-e"]),
    )
    for name, default_options in candidates:
        exe = _which(name)
        if exe:
            options = list(settings.ssh_terminal_options) if settings.ssh_terminal_options else default_options
            return exe, options
    raise ActionError("No supported terminal emulator found for SSH")


def _launch_ssh(action: Action, settings: AppSettings) -> None:
    ssh = _which("ssh")
    if not ssh:
        raise ActionError("ssh executable not found")
    target = f"{action.username}@{action.host}" if action.username else str(action.host)
    ssh_argv = [ssh]
    if action.ssh_x11_forwarding == "X":
        ssh_argv.append("-X")
    elif action.ssh_x11_forwarding == "Y":
        ssh_argv.append("-Y")
    ssh_argv.extend(action.ssh_options)
    if action.port:
        ssh_argv += ["-p", str(action.port)]
    ssh_argv.append(target)

    # On Windows there is no portable terminal-exec convention.  Let OpenSSH
    # inherit the current console; GUI callers can configure an explicit
    # terminal only on Unix-like desktops for now.
    if sys.platform == "win32":
        subprocess.Popen(host_argv(ssh_argv), shell=False)
        return

    terminal, terminal_options = _ssh_terminal(settings)
    subprocess.Popen(host_argv([terminal, *terminal_options, *ssh_argv]), shell=False)


def _linux_rdp(action: Action, settings: AppSettings) -> None:
    requested = settings.rdp_linux_client.strip()
    if requested.lower() == "auto":
        exe = next((_which(name) for name in ("xfreerdp3", "xfreerdp") if _which(name)), None)
        if not exe:
            raise ActionError("No supported RDP client found (xfreerdp3/xfreerdp)")
    else:
        exe = _resolve_executable(requested)
        if not exe:
            raise ActionError(f"Configured Linux RDP client not found: {requested}")
    target = str(action.host)
    if action.port:
        target += f":{action.port}"
    argv = [exe, *settings.rdp_linux_options, f"/v:{target}"]
    if action.username:
        argv.append(f"/u:{action.username}")
    subprocess.Popen(host_argv(argv), shell=False)


def _windows_rdp(action: Action, settings: AppSettings) -> None:
    requested = settings.rdp_windows_client.strip() or "mstsc"
    exe = _resolve_executable(requested)
    if not exe:
        raise ActionError(f"Configured Windows RDP client not found: {requested}")
    target = str(action.host)
    if action.port:
        target += f":{action.port}"
    subprocess.Popen(host_argv([exe, *settings.rdp_windows_options, f"/v:{target}"]), shell=False)


def _macos_rdp(action: Action, settings: AppSettings) -> None:
    # Microsoft Remote Desktop/Windows App on macOS supports the legacy rdp://
    # URI scheme.  The default uses `open`; options may select a specific app,
    # e.g. ["-a", "Windows App"].
    requested = settings.rdp_macos_client.strip()
    client = "open" if requested.lower() == "auto" else requested
    exe = _resolve_executable(client)
    if not exe:
        raise ActionError(f"Configured macOS RDP launcher not found: {client}")
    target = str(action.host)
    if action.port:
        target += f":{action.port}"
    attributes = [f"full%20address=s:{quote(target, safe=':.')}" ]
    if action.username:
        attributes.append(f"username=s:{quote(action.username, safe='@\\')}")
    uri = "rdp://" + "&".join(attributes)
    subprocess.Popen(host_argv([exe, *settings.rdp_macos_options, uri]), shell=False)


def launch_action(action: Action, settings: AppSettings | None = None) -> None:
    action.validate()
    settings = settings or AppSettings.load()
    if action.type == "url":
        if not webbrowser.open(action.url or ""):
            raise ActionError("Unable to open URL")
        return
    if action.type == "ssh":
        _launch_ssh(action, settings)
        return
    if action.type == "rdp":
        if sys.platform == "win32":
            _windows_rdp(action, settings)
        elif sys.platform == "darwin":
            _macos_rdp(action, settings)
        else:
            _linux_rdp(action, settings)
        return
    if action.type == "command":
        if not action.argv:
            raise ActionError("Empty command")
        subprocess.Popen(host_argv(action.argv), shell=False)
        return
    raise ActionError(f"Unsupported action type: {action.type}")
