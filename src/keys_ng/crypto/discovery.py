from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys

from keys_ng.platform.host import host_which


@dataclass(slots=True, frozen=True)
class ExecutableDiscovery:
    """Resolved external executable and the method used to find it."""

    path: str | None
    method: str


def _candidate_is_executable(path: str | Path | None) -> str | None:
    if not path:
        return None
    candidate = Path(path).expanduser()
    try:
        if candidate.is_file():
            return str(candidate.resolve())
    except OSError:
        return None
    return None


def _windows_registry_roots() -> list[Path]:
    """Return GnuPG/Gpg4win installation roots advertised by the Windows registry."""
    if sys.platform != "win32":
        return []
    try:
        import winreg
    except ImportError:
        return []

    roots: list[Path] = []
    keys = (
        r"SOFTWARE\GnuPG",
        r"SOFTWARE\WOW6432Node\GnuPG",
        r"SOFTWARE\Gpg4win",
        r"SOFTWARE\WOW6432Node\Gpg4win",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Gpg4win",
    )
    values = ("Install Directory", "InstallDir", "InstallLocation", "Path")
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for key_name in keys:
            try:
                with winreg.OpenKey(hive, key_name) as key:
                    for value_name in values:
                        try:
                            value, _kind = winreg.QueryValueEx(key, value_name)
                        except OSError:
                            continue
                        if isinstance(value, str) and value.strip():
                            roots.append(Path(os.path.expandvars(value.strip())))
            except OSError:
                continue
    return roots


def _windows_standard_roots() -> list[Path]:
    if sys.platform != "win32":
        return []
    roots: list[Path] = []
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "ProgramW6432"):
        base = os.environ.get(variable)
        if base:
            roots.extend((Path(base) / "GnuPG", Path(base) / "Gpg4win"))
    # Deduplicate while preserving precedence.
    result: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root).casefold()
        if key not in seen:
            seen.add(key)
            result.append(root)
    return result


def discover_gnupg_executable(name: str, configured: str = "") -> ExecutableDiscovery:
    """Resolve a GnuPG executable without a shell.

    Precedence is: explicit user configuration, PATH/Flatpak host PATH,
    Windows registry installation roots, then conventional Windows locations.
    """
    configured = configured.strip()
    if configured:
        resolved = _candidate_is_executable(configured)
        if resolved:
            return ExecutableDiscovery(resolved, "configured")
        # A configured basename may intentionally rely on PATH.
        on_path = host_which(configured)
        if on_path:
            return ExecutableDiscovery(on_path, "configured/PATH")
        return ExecutableDiscovery(None, "configured path not found")

    on_path = host_which(name)
    if on_path:
        return ExecutableDiscovery(on_path, "PATH")
    if name == "gpg":
        on_path = host_which("gpg2")
        if on_path:
            return ExecutableDiscovery(on_path, "PATH (gpg2)")

    if sys.platform == "win32":
        relative_candidates = (
            Path("bin") / f"{name}.exe",
            Path(f"{name}.exe"),
        )
        for root in _windows_registry_roots():
            for relative in relative_candidates:
                resolved = _candidate_is_executable(root / relative)
                if resolved:
                    return ExecutableDiscovery(resolved, "Windows registry")
        for root in _windows_standard_roots():
            for relative in relative_candidates:
                resolved = _candidate_is_executable(root / relative)
                if resolved:
                    return ExecutableDiscovery(resolved, "standard Windows location")

    return ExecutableDiscovery(None, "not found")
