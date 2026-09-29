from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def in_flatpak() -> bool:
    return bool(os.environ.get("FLATPAK_ID")) or Path("/.flatpak-info").exists()


def host_prefix() -> list[str]:
    """Prefix argv so external desktop tools execute on the host from Flatpak."""
    if not in_flatpak():
        return []
    spawn = shutil.which("flatpak-spawn") or "/usr/bin/flatpak-spawn"
    return [spawn, "--host"]


def host_which(name: str) -> str | None:
    """Resolve an executable on the host without invoking a shell."""
    if not in_flatpak():
        if os.path.isabs(name) or os.sep in name or (os.altsep and os.altsep in name):
            return name if os.path.isfile(name) and os.access(name, os.X_OK) else None
        return shutil.which(name)
    prefix = host_prefix()
    if os.path.isabs(name):
        proc = subprocess.run([*prefix, "test", "-x", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return name if proc.returncode == 0 else None
    if os.sep in name or (os.altsep and os.altsep in name):
        return None
    proc = subprocess.run([*prefix, "which", name], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False, shell=False)
    if proc.returncode != 0:
        return None
    value = proc.stdout.decode("utf-8", "replace").strip().splitlines()
    return value[0] if value else None


def host_argv(argv: list[str]) -> list[str]:
    return [*host_prefix(), *argv]
