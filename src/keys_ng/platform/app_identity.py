from __future__ import annotations

import sys
from importlib.resources import files

APP_NAME = "Keys NG"
APP_ID = "org.keysng.KeysNG"
DESKTOP_FILE_NAME = APP_ID


def icon_bytes() -> bytes:
    """Return the bundled legacy Keys application icon as PNG bytes."""
    return files("keys_ng").joinpath("resources", "keys-icon.png").read_bytes()


def configure_process_identity() -> None:
    """Set platform process identity before the GUI toolkit starts.

    On Windows this helps the taskbar group Keys NG separately from the Python
    interpreter when running from source. It is intentionally best-effort.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        # Identity must never prevent the password manager from starting.
        pass


def apply_qt_identity(app) -> object | None:
    """Apply application name, desktop identity and bundled icon to Qt.

    Returns the QIcon so callers can also set it explicitly on top-level
    windows if desired. Importing PySide6 is deferred to keep CLI/TUI free of
    a GUI dependency.
    """
    try:
        from PySide6.QtGui import QIcon, QPixmap
    except ImportError:
        return None

    app.setApplicationName(APP_NAME)
    if hasattr(app, "setApplicationDisplayName"):
        app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName("Keys NG")
    if hasattr(app, "setDesktopFileName"):
        app.setDesktopFileName(DESKTOP_FILE_NAME)

    pixmap = QPixmap()
    if not pixmap.loadFromData(icon_bytes(), "PNG"):
        return None
    icon = QIcon(pixmap)
    app.setWindowIcon(icon)
    return icon


def set_textual_terminal_title(app) -> None:
    """Best-effort TUI identity.

    A terminal application does not own the desktop window; the terminal
    emulator does. We can therefore set the terminal/window title where the
    host supports it, but cannot portably replace the terminal emulator's
    graphical taskbar icon from Textual.
    """
    try:
        app.title = APP_NAME
    except Exception:
        pass
    try:
        app.console.set_window_title(APP_NAME)
    except Exception:
        pass
