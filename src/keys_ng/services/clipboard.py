from __future__ import annotations

import queue
import secrets
import shutil
import subprocess
import sys
import threading


class ClipboardUnavailable(RuntimeError):
    pass


def copy_secret_qt(secret: str, timeout_ms: int = 15000) -> None:
    """Copy a secret using Qt and clear it only if Keys NG still owns the token."""
    try:
        from PySide6.QtCore import QByteArray, QMimeData, QTimer
        from PySide6.QtGui import QGuiApplication
    except ImportError as exc:
        raise ClipboardUnavailable("PySide6 is required for the Qt clipboard backend") from exc

    app = QGuiApplication.instance()
    if app is None:
        raise ClipboardUnavailable("A Qt application instance is required")
    clipboard = app.clipboard()
    token = secrets.token_bytes(24)
    mime = QMimeData()
    mime.setText(secret)
    mime.setData("application/x-keys-ng-token", QByteArray(token))
    # Common desktop hint used by some clipboard managers to avoid history.
    mime.setData("x-kde-passwordManagerHint", QByteArray(b"secret"))
    clipboard.setMimeData(mime)

    def clear_if_owned() -> None:
        current = clipboard.mimeData()
        if current and bytes(current.data("application/x-keys-ng-token")) == token:
            clipboard.clear()

    QTimer.singleShot(timeout_ms, clear_if_owned)


def _run_clipboard_command(
    argv: list[str], *, input_bytes: bytes | None = None, timeout: float = 3.0
) -> bytes:
    try:
        completed = subprocess.run(
            argv,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ClipboardUnavailable(f"Clipboard command failed: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ClipboardUnavailable(detail or f"Clipboard command exited with {completed.returncode}")
    return completed.stdout


def available_native_clipboard_backend() -> str | None:
    """Return the best terminal-friendly clipboard backend for this platform."""
    if sys.platform == "darwin" and shutil.which("pbcopy") and shutil.which("pbpaste"):
        return "pbcopy"
    if sys.platform == "win32":
        if shutil.which("pwsh"):
            return "pwsh"
        if shutil.which("powershell"):
            return "powershell"
        return None

    # Prefer Wayland tools in a Wayland session, then X11 implementations.
    import os

    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy") and shutil.which("wl-paste"):
        return "wayland"
    if shutil.which("xclip"):
        return "xclip"
    if shutil.which("xsel"):
        return "xsel"
    # wl-copy can also work in sessions where WAYLAND_DISPLAY is inherited in a
    # non-standard way, so keep it as a final Unix-native candidate.
    if shutil.which("wl-copy") and shutil.which("wl-paste"):
        return "wayland"
    return None


def set_native_clipboard(secret: str, backend: str | None = None) -> str:
    """Write text to a platform clipboard without putting the secret in argv/env."""
    backend = backend or available_native_clipboard_backend()
    if backend is None:
        raise ClipboardUnavailable("No native clipboard backend is available")
    data = secret.encode("utf-8")
    if backend == "wayland":
        _run_clipboard_command(["wl-copy"], input_bytes=data)
    elif backend == "xclip":
        _run_clipboard_command(["xclip", "-selection", "clipboard", "-in"], input_bytes=data)
    elif backend == "xsel":
        _run_clipboard_command(["xsel", "--clipboard", "--input"], input_bytes=data)
    elif backend == "pbcopy":
        _run_clipboard_command(["pbcopy"], input_bytes=data)
    elif backend in {"pwsh", "powershell"}:
        _run_clipboard_command(
            [backend, "-NoProfile", "-NonInteractive", "-Command", "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
            input_bytes=data,
        )
    else:  # pragma: no cover - defensive programmer error
        raise ClipboardUnavailable(f"Unsupported clipboard backend: {backend}")
    return backend


def read_native_clipboard(backend: str) -> str:
    if backend == "wayland":
        data = _run_clipboard_command(["wl-paste", "--no-newline"])
    elif backend == "xclip":
        data = _run_clipboard_command(["xclip", "-selection", "clipboard", "-out"])
    elif backend == "xsel":
        data = _run_clipboard_command(["xsel", "--clipboard", "--output"])
    elif backend == "pbcopy":
        data = _run_clipboard_command(["pbpaste"])
    elif backend in {"pwsh", "powershell"}:
        data = _run_clipboard_command(
            [backend, "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard -Raw"]
        )
    else:  # pragma: no cover
        raise ClipboardUnavailable(f"Unsupported clipboard backend: {backend}")
    return data.decode("utf-8", errors="strict")


def clear_native_clipboard(backend: str) -> None:
    if backend == "wayland":
        # `wl-copy --clear` is supported by wl-clipboard. Supplying empty stdin
        # is kept as a fallback for older installations.
        try:
            _run_clipboard_command(["wl-copy", "--clear"])
        except ClipboardUnavailable:
            _run_clipboard_command(["wl-copy"], input_bytes=b"")
    elif backend == "xclip":
        _run_clipboard_command(["xclip", "-selection", "clipboard", "-in"], input_bytes=b"")
    elif backend == "xsel":
        try:
            _run_clipboard_command(["xsel", "--clipboard", "--clear"])
        except ClipboardUnavailable:
            _run_clipboard_command(["xsel", "--clipboard", "--input"], input_bytes=b"")
    elif backend == "pbcopy":
        _run_clipboard_command(["pbcopy"], input_bytes=b"")
    elif backend in {"pwsh", "powershell"}:
        _run_clipboard_command(
            [backend, "-NoProfile", "-NonInteractive", "-Command", "Set-Clipboard -Value ''"]
        )
    else:  # pragma: no cover
        raise ClipboardUnavailable(f"Unsupported clipboard backend: {backend}")


def copy_secret_cli(secret: str, timeout_seconds: int = 15) -> None:
    """Start a detached helper that owns/copies and later clears the clipboard.

    The helper prefers native terminal clipboard implementations. Qt is used only
    as a fallback, so the TUI no longer requires the GUI optional dependency.
    """
    argv = [sys.executable, "-m", "keys_ng.services.clipboard_helper", str(timeout_seconds)]
    creationflags = 0
    kwargs = {}
    if sys.platform == "win32":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    else:
        kwargs["start_new_session"] = True
    try:
        proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            creationflags=creationflags,
            **kwargs,
        )
        if proc.stdin is None or proc.stdout is None:
            raise ClipboardUnavailable("Unable to establish clipboard helper pipes")
        proc.stdin.write(secret.encode("utf-8"))
        proc.stdin.close()
        acknowledgements: queue.Queue[bytes | BaseException] = queue.Queue(maxsize=1)

        def read_acknowledgement() -> None:
            try:
                acknowledgements.put(proc.stdout.readline())
            except BaseException as exc:  # pragma: no cover
                acknowledgements.put(exc)

        threading.Thread(target=read_acknowledgement, daemon=True).start()
        try:
            raw_ack = acknowledgements.get(timeout=4.0)
        except queue.Empty as exc:
            proc.terminate()
            raise ClipboardUnavailable("Clipboard helper startup timed out") from exc
        if isinstance(raw_ack, BaseException):
            proc.terminate()
            raise ClipboardUnavailable(f"Clipboard helper failed: {raw_ack}")
        acknowledgement = raw_ack.decode("utf-8", errors="replace").strip()
        proc.stdout.close()
        if not acknowledgement.startswith("READY"):
            detail = ""
            if proc.stderr is not None:
                try:
                    detail = proc.stderr.read(2048).decode("utf-8", errors="replace").strip()
                except Exception:
                    detail = ""
            proc.terminate()
            raise ClipboardUnavailable(detail or "Clipboard helper did not initialise successfully")
    except (OSError, AttributeError, BrokenPipeError) as exc:
        raise ClipboardUnavailable(f"Unable to start clipboard helper: {exc}") from exc
