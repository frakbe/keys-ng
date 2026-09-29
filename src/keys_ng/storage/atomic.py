from __future__ import annotations

from pathlib import Path
import os
import secrets


def atomic_write_ciphertext(path: Path, data: bytes) -> None:
    """Atomically replace a ciphertext file. The temporary file contains ciphertext only."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(tmp, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        if os.name != "nt":
            dir_fd = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def remove_stale_ciphertext_temps(directory: Path) -> int:
    """Remove abandoned atomic-write temp files. They contain ciphertext only."""
    if not directory.exists():
        return 0
    removed = 0
    for path in directory.glob(".*.*.tmp"):
        try:
            path.unlink()
            removed += 1
        except OSError:
            pass
    return removed
