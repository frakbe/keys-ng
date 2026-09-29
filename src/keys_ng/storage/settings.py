from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import tomllib

from platformdirs import user_config_dir


def _string_list(value, name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{name} must be an array of strings")
    return list(value)


def _toml_string(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _toml_array(values: list[str]) -> str:
    return "[" + ", ".join(_toml_string(value) for value in values) + "]"


@dataclass(slots=True)
class AppSettings:
    language: str = "auto"
    clipboard_password_timeout: int = 20
    clipboard_totp_timeout: int = 10
    auto_lock_timeout: int = 300
    crypto_backend: str = "auto"
    gpg_executable: str = ""
    gpgconf_executable: str = ""
    tree_startup_view: str = "expanded"
    recent_vaults: list[str] = field(default_factory=list)
    tui_clipboard_notice_background: str = ""
    tui_clipboard_notice_foreground: str = ""
    tui_clipboard_notice_seconds: float = 2.5
    diagnostics_enabled: bool = False
    diagnostics_level: str = "DEBUG"
    diagnostics_log_file: str = ""
    diagnostics_max_bytes: int = 2_000_000
    diagnostics_backup_count: int = 3

    # Launcher settings intentionally use argv-style lists.  They are never
    # interpreted by a shell, so options containing spaces remain one argument
    # and secrets cannot accidentally become shell syntax.
    ssh_terminal: str = "auto"
    ssh_terminal_options: list[str] = field(default_factory=list)
    rdp_linux_client: str = "auto"
    rdp_linux_options: list[str] = field(default_factory=list)
    rdp_windows_client: str = "mstsc"
    rdp_windows_options: list[str] = field(default_factory=list)
    rdp_macos_client: str = "auto"
    rdp_macos_options: list[str] = field(default_factory=list)

    @classmethod
    def default_path(cls) -> Path:
        return Path(user_config_dir("keys-ng", "Keys NG")) / "config.toml"

    @classmethod
    def load(cls, path: Path | None = None) -> "AppSettings":
        path = path or cls.default_path()
        if not path.exists():
            return cls()
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        clipboard = data.get("clipboard", {})
        security = data.get("security", {})
        ui = data.get("ui", {})
        gnupg = data.get("gnupg", {})
        diagnostics = data.get("diagnostics", {})
        launchers = data.get("launchers", {})
        ssh = launchers.get("ssh", {})
        rdp = launchers.get("rdp", {})
        rdp_linux = rdp.get("linux", {})
        rdp_windows = rdp.get("windows", {})
        rdp_macos = rdp.get("macos", {})

        tree_startup_view = str(ui.get("tree_startup_view", "expanded")).strip().lower()
        tui = ui.get("tui", {})
        if tree_startup_view not in {"expanded", "compact"}:
            raise ValueError("ui.tree_startup_view must be 'expanded' or 'compact'")

        return cls(
            language=str(data.get("language", "auto")),
            clipboard_password_timeout=int(clipboard.get("password_timeout", 20)),
            clipboard_totp_timeout=int(clipboard.get("totp_timeout", 10)),
            auto_lock_timeout=int(security.get("auto_lock_timeout", 300)),
            crypto_backend=str(security.get("crypto_backend", "auto")),
            gpg_executable=str(gnupg.get("gpg", "")).strip(),
            gpgconf_executable=str(gnupg.get("gpgconf", "")).strip(),
            tree_startup_view=tree_startup_view,
            recent_vaults=_string_list(ui.get("recent_vaults", []), "ui.recent_vaults")[:5],
            tui_clipboard_notice_background=str(tui.get("clipboard_notice_background", "")).strip(),
            tui_clipboard_notice_foreground=str(tui.get("clipboard_notice_foreground", "")).strip(),
            tui_clipboard_notice_seconds=max(0.5, min(10.0, float(tui.get("clipboard_notice_seconds", 2.5)))),
            diagnostics_enabled=bool(diagnostics.get("enabled", False)),
            diagnostics_level=str(diagnostics.get("level", "DEBUG")).strip().upper(),
            diagnostics_log_file=str(diagnostics.get("log_file", "")).strip(),
            diagnostics_max_bytes=max(65536, int(diagnostics.get("max_bytes", 2_000_000))),
            diagnostics_backup_count=max(1, min(20, int(diagnostics.get("backup_count", 3)))),
            ssh_terminal=str(ssh.get("terminal", "auto")).strip() or "auto",
            ssh_terminal_options=_string_list(ssh.get("terminal_options", []), "launchers.ssh.terminal_options"),
            rdp_linux_client=str(rdp_linux.get("client", "auto")).strip() or "auto",
            rdp_linux_options=_string_list(rdp_linux.get("options", []), "launchers.rdp.linux.options"),
            rdp_windows_client=str(rdp_windows.get("client", "mstsc")).strip() or "mstsc",
            rdp_windows_options=_string_list(rdp_windows.get("options", []), "launchers.rdp.windows.options"),
            rdp_macos_client=str(rdp_macos.get("client", "auto")).strip() or "auto",
            rdp_macos_options=_string_list(rdp_macos.get("options", []), "launchers.rdp.macos.options"),
        )


    def remember_vault(self, path: str | Path) -> None:
        resolved = str(Path(path).expanduser().resolve())
        current = [item for item in self.recent_vaults if item != resolved]
        self.recent_vaults = [resolved, *current][:5]

    def save(self, path: Path | None = None) -> Path:
        path = path or self.default_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        text = (
            f"language = {_toml_string(self.language)}\n\n"
            "[clipboard]\n"
            f"password_timeout = {self.clipboard_password_timeout}\n"
            f"totp_timeout = {self.clipboard_totp_timeout}\n\n"
            "[security]\n"
            f"auto_lock_timeout = {self.auto_lock_timeout}\n"
            f"crypto_backend = {_toml_string(self.crypto_backend)}\n\n"
            "[gnupg]\n"
            f"gpg = {_toml_string(self.gpg_executable)}\n"
            f"gpgconf = {_toml_string(self.gpgconf_executable)}\n\n"
            "[ui]\n"
            f"tree_startup_view = {_toml_string(self.tree_startup_view)}\n"
            f"recent_vaults = {_toml_array(self.recent_vaults[:5])}\n\n"
            "[ui.tui]\n"
            f"clipboard_notice_background = {_toml_string(self.tui_clipboard_notice_background)}\n"
            f"clipboard_notice_foreground = {_toml_string(self.tui_clipboard_notice_foreground)}\n"
            f"clipboard_notice_seconds = {self.tui_clipboard_notice_seconds:g}\n\n"
            "[diagnostics]\n"
            f"enabled = {str(self.diagnostics_enabled).lower()}\n"
            f"level = {_toml_string(self.diagnostics_level)}\n"
            f"log_file = {_toml_string(self.diagnostics_log_file)}\n"
            f"max_bytes = {self.diagnostics_max_bytes}\n"
            f"backup_count = {self.diagnostics_backup_count}\n\n"
            "[launchers.ssh]\n"
            f"terminal = {_toml_string(self.ssh_terminal)}\n"
            f"terminal_options = {_toml_array(self.ssh_terminal_options)}\n\n"
            "[launchers.rdp.linux]\n"
            f"client = {_toml_string(self.rdp_linux_client)}\n"
            f"options = {_toml_array(self.rdp_linux_options)}\n\n"
            "[launchers.rdp.windows]\n"
            f"client = {_toml_string(self.rdp_windows_client)}\n"
            f"options = {_toml_array(self.rdp_windows_options)}\n\n"
            "[launchers.rdp.macos]\n"
            f"client = {_toml_string(self.rdp_macos_client)}\n"
            f"options = {_toml_array(self.rdp_macos_options)}\n"
        )
        path.write_text(text, encoding="utf-8")
        if os.name != "nt":
            os.chmod(path, 0o600)
        return path
