from __future__ import annotations

import sys
import time

from keys_ng.services.clipboard import (
    ClipboardUnavailable,
    clear_native_clipboard,
    read_native_clipboard,
    set_native_clipboard,
)


def _normalise(value: str) -> str:
    # Windows clipboard implementations may normalise line endings.
    return value.replace("\r\n", "\n")


def _native_worker(secret: str, timeout_seconds: int) -> None:
    backend = set_native_clipboard(secret)
    # Acknowledge as soon as the native setter succeeds. The parent TUI can
    # then render its temporary notification without waiting for the extra
    # clipboard read-back, which can take noticeable time on some desktops.
    sys.stdout.write(f"READY {backend}\n")
    sys.stdout.flush()
    try:
        read_native_clipboard(backend)
    except ClipboardUnavailable:
        pass
    time.sleep(timeout_seconds)
    try:
        if _normalise(read_native_clipboard(backend)) == _normalise(secret):
            clear_native_clipboard(backend)
    except ClipboardUnavailable:
        # Failure to clear after the TTL must not keep the helper alive forever.
        pass


def _qt_worker(secret: str, timeout_seconds: int) -> None:
    try:
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtCore import QTimer
    except ImportError as exc:
        raise ClipboardUnavailable("No native clipboard tool found and PySide6 is not installed") from exc
    from keys_ng.services.clipboard import copy_secret_qt

    app = QGuiApplication([])
    copy_secret_qt(secret, timeout_seconds * 1000)
    app.processEvents()
    # Report readiness immediately after Qt has processed the clipboard write;
    # a read-back still happens locally but no longer delays the caller UI.
    sys.stdout.write("READY qt\n")
    sys.stdout.flush()
    _ = app.clipboard().text()
    QTimer.singleShot(timeout_seconds * 1000 + 250, app.quit)
    app.exec()


def main() -> None:
    timeout = max(1, int(sys.argv[1]))
    secret = sys.stdin.buffer.read().decode("utf-8")
    try:
        _native_worker(secret, timeout)
        return
    except ClipboardUnavailable as native_error:
        try:
            _qt_worker(secret, timeout)
            return
        except ClipboardUnavailable as qt_error:
            print(f"{native_error}; {qt_error}", file=sys.stderr)
            raise SystemExit(2)


if __name__ == "__main__":
    main()
