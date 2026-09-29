from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys
import time

from platformdirs import user_log_dir

_LOGGER_NAME = "keys_ng"
_CONFIGURED = False
_LOG_PATH: Path | None = None


def default_log_path() -> Path:
    """Return the per-user diagnostics log path without creating it."""
    return Path(user_log_dir("keys-ng", "Keys NG")) / "keys-ng.log"


def diagnostics_log_path() -> Path | None:
    """Return the active diagnostics log path, if diagnostics are configured."""
    return _LOG_PATH


def configure_diagnostics(settings, component: str) -> Path | None:
    """Configure rotating file diagnostics from AppSettings.

    Diagnostics are opt-in. Callers must never include credentials, decrypted
    record fields, TOTP seeds/codes, clipboard contents, or plaintext exports.
    """
    global _CONFIGURED, _LOG_PATH
    if not getattr(settings, "diagnostics_enabled", False):
        return None
    if _CONFIGURED:
        return _LOG_PATH

    configured = str(getattr(settings, "diagnostics_log_file", "") or "").strip()
    path = Path(configured).expanduser() if configured else default_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        try:
            os.chmod(path.parent, 0o700)
        except OSError:
            pass

    level_name = str(getattr(settings, "diagnostics_level", "DEBUG") or "DEBUG").upper()
    level = getattr(logging, level_name, logging.DEBUG)
    max_bytes = max(65536, int(getattr(settings, "diagnostics_max_bytes", 2_000_000)))
    backup_count = max(1, min(20, int(getattr(settings, "diagnostics_backup_count", 3))))

    handler = RotatingFileHandler(
        path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s pid=%(process)d "
        "thread=%(threadName)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger = logging.getLogger(_LOGGER_NAME)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    _CONFIGURED = True
    _LOG_PATH = path.resolve()
    logger.info(
        "diagnostics.start component=%s platform=%s python=%s",
        component, sys.platform, sys.version.split()[0],
    )
    return _LOG_PATH


def get_logger(name: str) -> logging.Logger:
    """Return a child logger in the Keys NG diagnostics namespace."""
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")


def elapsed_ms(start: float) -> float:
    """Convert a perf_counter start value to elapsed milliseconds."""
    return (time.perf_counter() - start) * 1000.0


def safe_operation_args(args) -> str:
    """Return a non-secret summary of a GnuPG argv sequence.

    Only operation flags are exposed. Values following options are deliberately
    omitted so fingerprints, file names, UIDs, paths, and other arguments do not
    leak into diagnostic logs.
    """
    operation_flags = {
        "--decrypt": "decrypt",
        "--encrypt": "encrypt",
        "--list-keys": "list-keys",
        "--list-secret-keys": "list-secret-keys",
        "--import": "import",
        "--version": "version",
        "--kill": "kill",
    }
    found = [label for arg, label in operation_flags.items() if arg in args]
    return ",".join(found) if found else "gpg-operation"
