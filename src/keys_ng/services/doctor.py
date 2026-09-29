from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import platform
import shutil
import sys

from keys_ng import __version__
from keys_ng.crypto.backend import CryptoBackend
from keys_ng.platform.desktop_integration import desktop_integration_status
from keys_ng.services.clipboard import available_native_clipboard_backend
from keys_ng.services.diagnostics import default_log_path
from keys_ng.storage.settings import AppSettings


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    name: str
    ok: bool
    detail: str
    optional: bool = False


def _module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def collect_doctor_checks(crypto: CryptoBackend, settings: AppSettings | None = None) -> list[DoctorCheck]:
    settings = settings or AppSettings.load()
    checks: list[DoctorCheck] = [
        DoctorCheck("Keys NG", True, __version__),
        DoctorCheck("Python", sys.version_info >= (3, 11), f"{platform.python_version()} ({sys.executable})"),
    ]
    for name, ok, detail in crypto.diagnose():
        checks.append(DoctorCheck(name, ok, detail))

    checks.extend(
        [
            DoctorCheck("GUI / PySide6", _module("PySide6"), "available" if _module("PySide6") else "not installed", optional=True),
            DoctorCheck("TUI / Textual", _module("textual"), "available" if _module("textual") else "not installed", optional=True),
            DoctorCheck("QR / zxing-cpp", _module("zxingcpp"), "available" if _module("zxingcpp") else "not installed", optional=True),
            DoctorCheck("QR / Pillow", _module("PIL"), "available" if _module("PIL") else "not installed", optional=True),
        ]
    )

    backend = available_native_clipboard_backend()
    checks.append(DoctorCheck("Clipboard", backend is not None or _module("PySide6"), backend or ("Qt" if _module("PySide6") else "no native/Qt backend"), optional=True))

    ssh = shutil.which("ssh")
    checks.append(DoctorCheck("SSH client", bool(ssh), ssh or "not found", optional=True))
    if sys.platform.startswith("linux"):
        terminal_candidates = ["xdg-terminal", "xdg-terminal-exec", "ptyxis", "gnome-terminal", "kgx", "konsole", "xterm", "alacritty"]
        found_terminal = settings.ssh_terminal if settings.ssh_terminal != "auto" else next((name for name in terminal_candidates if shutil.which(name)), None)
        checks.append(DoctorCheck("SSH terminal", bool(found_terminal), str(found_terminal or "not found"), optional=True))
        rdp = settings.rdp_linux_client if settings.rdp_linux_client != "auto" else next((name for name in ("xfreerdp3", "xfreerdp") if shutil.which(name)), None)
        checks.append(DoctorCheck("RDP client", bool(rdp), str(rdp or "not found"), optional=True))
    elif sys.platform == "win32":
        rdp = shutil.which(settings.rdp_windows_client or "mstsc")
        checks.append(DoctorCheck("RDP client", bool(rdp), rdp or "not found", optional=True))
    elif sys.platform == "darwin":
        rdp = shutil.which("open")
        checks.append(DoctorCheck("RDP launcher", bool(rdp), rdp or "not found", optional=True))

    try:
        installed, paths = desktop_integration_status()
        checks.append(DoctorCheck("Application menu", installed, str(paths.desktop_file), optional=True))
    except RuntimeError as exc:
        checks.append(DoctorCheck("Application menu", False, str(exc), optional=True))

    checks.append(DoctorCheck("Settings", True, str(AppSettings.default_path())))
    log_path = settings.diagnostics_log_file or str(default_log_path())
    checks.append(DoctorCheck("Diagnostics", True, f"{'enabled' if settings.diagnostics_enabled else 'disabled'}; {log_path}", optional=True))
    return checks
