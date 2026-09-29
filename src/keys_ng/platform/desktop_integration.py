from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from keys_ng.platform.app_identity import APP_ID, APP_NAME
from keys_ng.platform.host import in_flatpak

DESKTOP_FILENAME = f"{APP_ID}.desktop"
ICON_FILENAME = f"{APP_ID}.png"
WINDOWS_SHORTCUT = f"{APP_NAME}.lnk"
MAC_APP_NAME = f"{APP_NAME}.app"


@dataclass(frozen=True, slots=True)
class DesktopIntegrationPaths:
    # Kept for backward compatibility with the Linux-specific M1.8 API. On
    # Windows/macOS desktop_file means the application-menu launcher path.
    desktop_file: Path
    icon_file: Path


def _xdg_data_home() -> Path:
    raw = os.environ.get("XDG_DATA_HOME")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".local" / "share"


def _gui_executable() -> str:
    found = shutil.which("keys-ng-gui")
    if found:
        return str(Path(found).resolve())
    # Source/venv fallback. The generated launcher is intentionally bound to the
    # Python environment that installed it.
    return str(Path(sys.executable).resolve())


def user_paths() -> DesktopIntegrationPaths:
    if sys.platform.startswith("linux"):
        base = _xdg_data_home()
        return DesktopIntegrationPaths(
            desktop_file=base / "applications" / DESKTOP_FILENAME,
            icon_file=base / "icons" / "hicolor" / "64x64" / "apps" / ICON_FILENAME,
        )
    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        shortcut = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / WINDOWS_SHORTCUT
        icon = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Keys NG" / "keys-icon.ico"
        return DesktopIntegrationPaths(shortcut, icon)
    if sys.platform == "darwin":
        app = Path.home() / "Applications" / MAC_APP_NAME
        return DesktopIntegrationPaths(app, app / "Contents" / "Resources" / "keys-icon.png")
    raise RuntimeError(f"Application-menu integration is not supported on {sys.platform}")


def _resource_bytes(name: str) -> bytes:
    return files("keys_ng").joinpath("resources", name).read_bytes()


def _desktop_exec_token(value: str) -> str:
    # Freedesktop Exec supports double-quoted arguments. Backslash and quote are
    # escaped explicitly so virtualenv/user paths containing spaces remain valid.
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _install_linux(paths: DesktopIntegrationPaths) -> None:
    paths.desktop_file.parent.mkdir(parents=True, exist_ok=True)
    paths.icon_file.parent.mkdir(parents=True, exist_ok=True)
    template = _resource_bytes(DESKTOP_FILENAME).decode("utf-8")
    gui = _gui_executable()
    if Path(gui).name.lower().startswith("python"):
        exec_line = f"Exec={_desktop_exec_token(gui)} -m keys_ng.gui.main"
    else:
        exec_line = f"Exec={_desktop_exec_token(gui)}"
    lines = []
    for line in template.splitlines():
        if line.startswith("Exec="):
            lines.append(exec_line)
        elif line.startswith("TryExec="):
            # TryExec is intentionally omitted. Some GIO/GNOME versions reject
            # otherwise valid per-user launchers when TryExec contains an
            # absolute path with characters that are legal in Unix home paths.
            continue
        else:
            lines.append(line)
    paths.desktop_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    paths.icon_file.write_bytes(_resource_bytes("keys-icon.png"))
    paths.desktop_file.chmod(0o644)
    paths.icon_file.chmod(0o644)


def _install_windows(paths: DesktopIntegrationPaths) -> None:
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        raise RuntimeError("PowerShell is required to create the Windows Start Menu shortcut")
    paths.desktop_file.parent.mkdir(parents=True, exist_ok=True)
    paths.icon_file.parent.mkdir(parents=True, exist_ok=True)
    paths.icon_file.write_bytes(_resource_bytes("keys-icon.ico"))
    exe = _gui_executable()
    # pip/venv installs normally expose keys-ng-gui.exe. If not, launch the
    # module through the current Python interpreter.
    if Path(exe).name.lower().startswith("python"):
        target = exe
        arguments = "-m keys_ng.gui.main"
    else:
        target = exe
        arguments = ""
    script = (
        "$w=New-Object -ComObject WScript.Shell;"
        f"$s=$w.CreateShortcut('{str(paths.desktop_file).replace("'", "''")}');"
        f"$s.TargetPath='{target.replace("'", "''")}';"
        f"$s.Arguments='{arguments.replace("'", "''")}';"
        f"$s.IconLocation='{str(paths.icon_file).replace("'", "''")},0';"
        f"$s.WorkingDirectory='{str(Path.home()).replace("'", "''")}';"
        "$s.Save()"
    )
    completed = subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-Command", script], check=False)
    if completed.returncode != 0 or not paths.desktop_file.exists():
        raise RuntimeError("Failed to create the Windows Start Menu shortcut")


def _install_macos(paths: DesktopIntegrationPaths) -> None:
    app = paths.desktop_file
    contents = app / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    macos.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)
    paths.icon_file.write_bytes(_resource_bytes("keys-icon.png"))
    gui = _gui_executable()
    if Path(gui).name.lower().startswith("python"):
        command = f'exec "{gui}" -m keys_ng.gui.main "$@"\n'
    else:
        command = f'exec "{gui}" "$@"\n'
    launcher = macos / "keys-ng-gui"
    launcher.write_text("#!/bin/sh\n" + command, encoding="utf-8")
    launcher.chmod(0o755)
    plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>{APP_NAME}</string>
<key>CFBundleDisplayName</key><string>{APP_NAME}</string>
<key>CFBundleIdentifier</key><string>{APP_ID}</string>
<key>CFBundleExecutable</key><string>keys-ng-gui</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleIconFile</key><string>keys-icon.png</string>
</dict></plist>
'''
    (contents / "Info.plist").write_text(plist, encoding="utf-8")


def install_user_desktop_integration() -> DesktopIntegrationPaths:
    """Install a per-user application-menu launcher on Linux, Windows or macOS."""
    paths = user_paths()
    if sys.platform.startswith("linux"):
        _install_linux(paths)
    elif sys.platform == "win32":
        _install_windows(paths)
    elif sys.platform == "darwin":
        _install_macos(paths)
    else:
        raise RuntimeError(f"Application-menu integration is not supported on {sys.platform}")
    return paths


def ensure_user_desktop_integration() -> DesktopIntegrationPaths | None:
    """Best-effort per-user application-menu integration used by the GUI."""
    if in_flatpak():
        # Flatpak installs its own exported .desktop file and icon. Writing a
        # second per-user launcher would create duplicates and stale Exec paths.
        return None
    try:
        paths = user_paths()
        if not desktop_integration_status()[0]:
            return install_user_desktop_integration()
        if sys.platform.startswith("linux"):
            # Recreate the launcher so its Exec line follows the currently active
            # installation/virtualenv, not a stale PATH-dependent command.
            return install_user_desktop_integration()
        return paths
    except (OSError, RuntimeError):
        return None


def uninstall_user_desktop_integration() -> DesktopIntegrationPaths:
    paths = user_paths()
    if sys.platform == "darwin":
        shutil.rmtree(paths.desktop_file, ignore_errors=True)
    else:
        for path in (paths.desktop_file, paths.icon_file):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
    return paths


def desktop_integration_status() -> tuple[bool, DesktopIntegrationPaths]:
    paths = user_paths()
    if sys.platform == "darwin":
        ok = (paths.desktop_file / "Contents" / "Info.plist").is_file() and paths.icon_file.is_file()
    else:
        ok = paths.desktop_file.is_file() and paths.icon_file.is_file()
    return ok, paths
