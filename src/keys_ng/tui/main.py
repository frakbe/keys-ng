from __future__ import annotations

import argparse
from pathlib import Path
import sys

from keys_ng import __version__
from keys_ng.crypto.factory import create_crypto_backend
from keys_ng.i18n import _, configure_language, current_language
from keys_ng.migration.keepassxc import format_import_report, import_keepassxc
from keys_ng.migration.keepassxc_export import export_entry_xml, export_vault_xml, write_export
from keys_ng.platform.app_identity import set_textual_terminal_title
from keys_ng.services.actions import launch_action
from keys_ng.services.clipboard import copy_secret_cli
from keys_ng.services.entry_editor import EntryDraft, build_entry_from_draft
from keys_ng.services.diagnostics import configure_diagnostics, get_logger
from keys_ng.services.qr import parse_totp_qr_file
from keys_ng.services.passwords import generate_password
from keys_ng.services.totp import build_otpauth_uri
from keys_ng.services.totp import generate_totp
from keys_ng.services.vault_init import VaultInitRequest, available_vault_keys, create_vault
from keys_ng.services.vault_sessions import VaultSessionManager
from keys_ng.services.trusted_signers import add_trusted_signer, eligible_signing_keys, list_trusted_signers, remove_trusted_signer
from keys_ng.storage.inbox import delete_inbox_item, import_inbox_item, inspect_inbox, pending_inbox_paths
from keys_ng.storage.settings import AppSettings
from keys_ng.storage.vault import Vault


ROOT_VALUE = "__keys_ng_root__"


def main() -> None:
    # Keep `keys-ng-tui version` available even when the optional Textual
    # dependency is not installed. This is useful for package diagnostics.
    if len(sys.argv) == 2 and sys.argv[1] in {"version", "--version"}:
        print(f"Keys NG {__version__}")
        return

    try:
        from textual.app import App, ComposeResult
        from textual.binding import Binding
        from textual.containers import Horizontal, Vertical, VerticalScroll
        from textual.screen import ModalScreen
        from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Select, Static, TextArea, Tree

        def _select_value_is_blank(value) -> bool:
            """Return True for all Textual empty-selection sentinels."""
            if value is None or value is Select.BLANK:
                return True
            null_sentinel = getattr(Select, "NULL", None)
            return null_sentinel is not None and value is null_sentinel

    except ImportError:
        print("keys-ng-tui requires Textual. Install with: pip install 'keys-ng[tui]'", file=sys.stderr)
        raise SystemExit(2)

    parser = argparse.ArgumentParser(prog="keys-ng-tui")
    parser.add_argument("--version", action="version", version=f"Keys NG {__version__}")
    parser.add_argument("vault", nargs="?", help="Vault directory; omit to start the new-vault wizard")
    parser.add_argument("--language", default=None)
    parser.add_argument("--tree-view", choices=("expanded", "compact"), default=None, help="Initial folder tree view")
    args = parser.parse_args()
    settings = AppSettings.load()
    configure_diagnostics(settings, "tui")
    get_logger("tui").info("tui.start")
    configure_language(args.language or settings.language)
    crypto = create_crypto_backend(settings.crypto_backend, settings.gpg_executable, settings.gpgconf_executable)
    tree_startup_view = args.tree_view or settings.tree_startup_view

    class VaultCreationApp(App[str | None]):
        """Standalone keyboard-first onboarding wizard used when no vault is supplied."""

        CSS = """
        Screen { align: center middle; }
        #wizard { width: 86%; height: auto; max-height: 90%; border: round $accent; padding: 1 2; background: $surface; }
        #wizard-title { text-style: bold; margin-bottom: 1; }
        .wizard-label { margin-top: 1; }
        #wizard-error { color: $error; min-height: 1; margin-top: 1; }
        #wizard-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """

        BINDINGS = [Binding("escape", "cancel", _("Cancel"))]

        def compose(self) -> ComposeResult:
            choices = available_vault_keys(crypto)
            recipient_options = [(key.label, key.fingerprint) for key in choices.recipients]
            signer_options = [(key.label, key.fingerprint) for key in choices.signers]
            with Vertical(id="wizard"):
                yield Static(_("Create a new vault"), id="wizard-title")
                yield Static(_("Keys NG will use your existing OpenPGP keys. It does not generate or manage key pairs."))
                yield Label(_("Vault directory"), classes="wizard-label")
                yield Input(str(Path.home() / "KeysNG-Vault"), id="vault-path")
                yield Label(_("Encryption recipient — full fingerprint shown"), classes="wizard-label")
                yield Select(recipient_options or [(_("No usable encryption keys"), "")], value=recipient_options[0][1] if recipient_options else "", id="recipient", allow_blank=False)
                yield Label(_("Signing key — secret key required"), classes="wizard-label")
                yield Select(signer_options or [(_("No usable signing keys"), "")], value=signer_options[0][1] if signer_options else "", id="signer", allow_blank=False)
                yield Checkbox(_("Require valid signatures"), value=True, id="require-signature")
                yield Label(_("Catalog privacy"), classes="wizard-label")
                yield Select([(_("Minimal"), "minimal"), (_("Standard"), "standard"), (_("Full"), "full")], value="standard", id="privacy", allow_blank=False)
                yield Static(_("A GnuPG encrypt/decrypt self-test runs before any vault files are written."))
                yield Static("", id="wizard-error")
                with Horizontal(id="wizard-buttons"):
                    yield Button(_("Cancel"), id="cancel")
                    yield Button(_("Create vault"), id="create", variant="primary")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "cancel":
                self.exit(None)
                return
            if event.button.id != "create":
                return
            try:
                recipient = self.query_one("#recipient", Select).value
                signer = self.query_one("#signer", Select).value
                require_signature = self.query_one("#require-signature", Checkbox).value
                if not recipient:
                    raise ValueError(_("No usable OpenPGP encryption key is available."))
                if require_signature and not signer:
                    raise ValueError(_("No usable OpenPGP secret signing key is available."))
                request = VaultInitRequest(
                    path=self.query_one("#vault-path", Input).value.strip(),
                    recipients=(str(recipient),),
                    signer=str(signer) if signer else None,
                    require_signature=bool(require_signature),
                    catalog_privacy=str(self.query_one("#privacy", Select).value),
                )
                created = create_vault(request, crypto)
                self.exit(str(created.path))
            except Exception as exc:
                self.query_one("#wizard-error", Static).update(f"{_('Error')}: {exc}")

        def action_cancel(self) -> None:
            self.exit(None)

    class VaultStartApp(App[str | None]):
        """Start screen for opening, creating, or selecting a recent vault."""
        CSS = """
        Screen { align: center middle; }
        #start { width: 82%; height: auto; border: round $accent; padding: 1 2; background: $surface; }
        #start-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        def compose(self) -> ComposeResult:
            recent = [(path, path) for path in settings.recent_vaults if Path(path).exists()]
            with Vertical(id="start"):
                yield Static(_("Keys NG — open or create a vault"))
                yield Label(_("Vault directory"))
                yield Input(str(Path.home()), id="start-path")
                yield Label(_("Recent vaults"))
                yield Select(recent, id="start-recent", allow_blank=True)
                with Horizontal(id="start-buttons"):
                    yield Button(_("Open"), id="start-open", variant="primary")
                    yield Button(_("Create new…"), id="start-create")
                    yield Button(_("Quit"), id="start-quit")
        def on_select_changed(self, event: Select.Changed) -> None:
            if event.select.id == "start-recent" and not _select_value_is_blank(event.value):
                self.query_one("#start-path", Input).value = str(event.value)
        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "start-quit": self.exit(None)
            elif event.button.id == "start-create": self.exit("__create__")
            elif event.button.id == "start-open": self.exit(self.query_one("#start-path", Input).value.strip() or None)

    def choose_vault(path: str | None = None) -> str | None:
        choice = path
        if not choice:
            while True:
                choice = VaultStartApp().run()
                if choice is None:
                    return None
                if choice == "__create__":
                    choice = VaultCreationApp().run()
                    if choice is None:
                        continue
                if choice:
                    break
        resolved = str(Path(choice).expanduser().resolve())
        settings.remember_vault(resolved)
        try: settings.save()
        except OSError: pass
        return resolved

    vault_path = choose_vault(args.vault)
    if not vault_path:
        return
    vault = Vault(vault_path, crypto)
    sessions = VaultSessionManager(vault)

    def folder_options(exclude_id: str | None = None) -> list[tuple[str, str]]:
        options: list[tuple[str, str]] = [(_("(Root)"), ROOT_VALUE)]
        for folder in vault.list_folders():
            if folder.id != exclude_id:
                options.append((vault.folder_path(folder.id), folder.id))
        return options

    class PasswordGeneratorScreen(ModalScreen[str | None]):
        CSS = """
        PasswordGeneratorScreen { align: center middle; }
        #generator { width: 68%; height: auto; border: round $accent; padding: 1 2; background: $surface; }
        #generator-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "cancel", _("Cancel"))]
        def compose(self) -> ComposeResult:
            with Vertical(id="generator"):
                yield Static(_("Generate password"))
                yield Label(_("Length")); yield Input("24", id="gen-length", type="integer")
                yield Checkbox(_("Uppercase"), value=True, id="gen-upper")
                yield Checkbox(_("Lowercase"), value=True, id="gen-lower")
                yield Checkbox(_("Digits"), value=True, id="gen-digits")
                yield Checkbox(_("Symbols"), value=True, id="gen-symbols")
                yield Checkbox(_("Allow ambiguous characters"), value=False, id="gen-ambiguous")
                yield Input("", id="gen-preview", password=False)
                yield Static("", id="gen-status")
                with Horizontal(id="generator-buttons"):
                    yield Button(_("Generate"), id="gen-refresh")
                    yield Button(_("Copy generated password"), id="gen-copy")
                    yield Button(_("Use password"), id="gen-use", variant="primary")
                    yield Button(_("Cancel"), id="gen-cancel")
        def on_mount(self) -> None: self._generate()
        def _generate(self) -> None:
            try:
                value = generate_password(
                    int(self.query_one("#gen-length", Input).value or "24"),
                    uppercase=self.query_one("#gen-upper", Checkbox).value,
                    lowercase=self.query_one("#gen-lower", Checkbox).value,
                    digits=self.query_one("#gen-digits", Checkbox).value,
                    symbols=self.query_one("#gen-symbols", Checkbox).value,
                    ambiguous=self.query_one("#gen-ambiguous", Checkbox).value,
                )
                self.query_one("#gen-preview", Input).value = value
            except Exception as exc:
                self.query_one("#gen-preview", Input).value = f"{_('Error')}: {exc}"
        def _copy_generated(self) -> None:
            value = self.query_one("#gen-preview", Input).value
            if not value or value.startswith(f"{_('Error')}:"):
                return
            status = self.query_one("#gen-status", Static)
            try:
                copy_secret_cli(value, settings.clipboard_password_timeout)
                status.update(_("Generated password copied to clipboard; it will be cleared automatically."))
            except Exception as exc:
                try:
                    self.app.copy_to_clipboard(value)
                    status.update(_("Generated password copied to clipboard."))
                except Exception:
                    status.update(f"{_('Clipboard error')}: {type(exc).__name__}")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "gen-refresh": self._generate()
            elif event.button.id == "gen-copy": self._copy_generated()
            elif event.button.id == "gen-use": self.dismiss(self.query_one("#gen-preview", Input).value)
            else: self.dismiss(None)
        def action_cancel(self) -> None: self.dismiss(None)

    class KeePassXCImportScreen(ModalScreen[bool]):
        CSS = """
        KeePassXCImportScreen { align: center middle; }
        #kp-panel { width: 90%; height: 90%; border: round $accent; padding: 1 2; background: $surface; }
        #kp-report { height: 1fr; }
        #kp-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "close", _("Close"))]
        def compose(self) -> ComposeResult:
            with Vertical(id="kp-panel"):
                yield Static(_("Import KeePassXC database / XML"))
                yield Label(_("Source .kdbx or .xml")); yield Input("", id="kp-source")
                yield Label(_("Key file (optional)")); yield Input("", id="kp-key-file")
                yield Label(_("Database password (optional; memory only)")); yield Input("", password=True, id="kp-password")
                yield Checkbox(_("KDBX has no password component"), value=False, id="kp-no-password")
                yield Label(_("YubiKey slot[:serial] (optional)")); yield Input("", id="kp-yubikey")
                yield TextArea(_("Use Preview to validate without writing to the vault."), id="kp-report", read_only=True)
                with Horizontal(id="kp-buttons"):
                    yield Button(_("Preview / dry run"), id="kp-preview")
                    yield Button(_("Import"), id="kp-import", variant="primary")
                    yield Button(_("Close"), id="kp-close")
        def _run(self, dry_run: bool):
            source = self.query_one("#kp-source", Input).value.strip()
            if not source: raise ValueError(_("Enter a KeePassXC KDBX or XML path."))
            return import_keepassxc(
                source, vault, source_format="auto",
                key_file=self.query_one("#kp-key-file", Input).value.strip() or None,
                no_password=self.query_one("#kp-no-password", Checkbox).value,
                yubikey=self.query_one("#kp-yubikey", Input).value.strip() or None,
                dry_run=dry_run, password=self.query_one("#kp-password", Input).value or None,
            )
        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "kp-close": self.dismiss(False); return
            try:
                report = self._run(event.button.id == "kp-preview")
                self.query_one("#kp-report", TextArea).load_text(format_import_report(report))
                if event.button.id == "kp-import": self.dismiss(True)
            except Exception as exc:
                self.query_one("#kp-report", TextArea).load_text(f"{_('Error')}: {exc}")
        def action_close(self) -> None: self.dismiss(False)

    class ExportVaultScreen(ModalScreen[str | None]):
        CSS = """ExportVaultScreen { align: center middle; } #export-panel { width: 72%; height: auto; border: round $accent; padding: 1 2; background: $surface; } #export-buttons { height: 3; align-horizontal: right; }"""
        def compose(self) -> ComposeResult:
            default = Path.cwd() / f"{vault.path.name or 'keys-ng-vault'}.xml"
            with Vertical(id="export-panel"):
                yield Static(_("Export complete vault as KeePassXC XML"))
                yield Static(_("WARNING: the XML contains plaintext credentials."))
                yield Input(str(default), id="export-path")
                with Horizontal(id="export-buttons"):
                    yield Button(_("Export"), id="export-ok", variant="primary")
                    yield Button(_("Cancel"), id="export-cancel")
        def on_button_pressed(self, event: Button.Pressed) -> None:
            self.dismiss(self.query_one("#export-path", Input).value.strip() if event.button.id == "export-ok" else None)

    class PreferencesScreen(ModalScreen[bool]):
        CSS = """PreferencesScreen { align: center middle; } #prefs { width: 82%; height: 88%; border: round $accent; padding: 1 2; background: $surface; } #prefs-buttons { height: 3; align-horizontal: right; }"""
        def compose(self) -> ComposeResult:
            with Vertical(id="prefs"):
                yield Static(_("Preferences"))
                with VerticalScroll():
                    yield Label(_("Language")); yield Input(settings.language, id="pref-language")
                    yield Label(_("Tree startup view")); yield Select([(_("Expanded"), "expanded"), (_("Compact"), "compact")], value=settings.tree_startup_view, id="pref-tree", allow_blank=False)
                    yield Label(_("Clipboard timeout (password/notes)")); yield Input(str(settings.clipboard_password_timeout), id="pref-clip", type="integer")
                    yield Label(_("Clipboard timeout (TOTP)")); yield Input(str(settings.clipboard_totp_timeout), id="pref-totp", type="integer")
                    yield Label(_("Auto-lock seconds")); yield Input(str(settings.auto_lock_timeout), id="pref-lock", type="integer")
                    yield Label("gpg"); yield Input(settings.gpg_executable, id="pref-gpg")
                    yield Label("gpgconf"); yield Input(settings.gpgconf_executable, id="pref-gpgconf")
                    yield Checkbox(_("Enable diagnostic logging"), value=settings.diagnostics_enabled, id="pref-diagnostics")
                with Horizontal(id="prefs-buttons"):
                    yield Button(_("Save"), id="prefs-save", variant="primary"); yield Button(_("Cancel"), id="prefs-cancel")
        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id != "prefs-save": self.dismiss(False); return
            try:
                settings.language = self.query_one("#pref-language", Input).value.strip() or "auto"
                settings.tree_startup_view = str(self.query_one("#pref-tree", Select).value)
                settings.clipboard_password_timeout = int(self.query_one("#pref-clip", Input).value)
                settings.clipboard_totp_timeout = int(self.query_one("#pref-totp", Input).value)
                settings.auto_lock_timeout = int(self.query_one("#pref-lock", Input).value)
                settings.gpg_executable = self.query_one("#pref-gpg", Input).value.strip()
                settings.gpgconf_executable = self.query_one("#pref-gpgconf", Input).value.strip()
                settings.diagnostics_enabled = self.query_one("#pref-diagnostics", Checkbox).value
                settings.save(); self.dismiss(True)
            except Exception: self.dismiss(False)

    class HelpScreen(ModalScreen[None]):
        CSS = """HelpScreen { align: center middle; } #help-panel { width: 92%; height: 92%; border: round $accent; padding: 1 2; background: $surface; } #help-text { height: 1fr; }"""
        def __init__(self, resource_name: str = "README.md") -> None:
            super().__init__(); self.resource_name = resource_name
        def _text(self) -> str:
            try:
                from importlib.resources import files
                root = files("keys_ng").joinpath("help")
                resource = root.joinpath(current_language(), self.resource_name)
                if not resource.is_file(): resource = root.joinpath("en", self.resource_name)
                text = resource.read_text(encoding="utf-8")
                if self.resource_name == "LICENSE.md": text = f"Keys NG {__version__}\n\n" + text
                return text
            except Exception as exc: return f"{_('Unable to load help document.')}: {exc}"
        def compose(self) -> ComposeResult:
            with Vertical(id="help-panel"):
                yield TextArea(self._text(), id="help-text", read_only=True)
                yield Button(_("Close"), id="help-close")
        def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(None)

    class EntryEditorScreen(ModalScreen[EntryDraft | None]):
        """Keyboard-first full editor shared semantically with the GUI editor."""

        CSS = """
        EntryEditorScreen { align: center middle; }
        #editor-panel { width: 88%; height: 92%; border: round $accent; padding: 1 2; background: $surface; }
        #editor-title { text-style: bold; margin-bottom: 1; }
        .editor-row { height: auto; margin-bottom: 1; }
        .editor-label { width: 22; padding-top: 1; }
        .editor-field { width: 1fr; }
        #notes { height: 8; }
        #editor-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        #editor-error { color: $error; height: auto; min-height: 1; }
        """

        BINDINGS = [
            Binding("escape", "cancel", _("Cancel")),
            Binding("ctrl+s", "save", _("Save"), priority=True),
        ]

        def __init__(self, draft: EntryDraft, title: str) -> None:
            super().__init__()
            self.draft = draft
            self.dialog_title = title

        def compose(self) -> ComposeResult:
            with Vertical(id="editor-panel"):
                yield Static(self.dialog_title, id="editor-title")
                with VerticalScroll():
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Title"), classes="editor-label")
                        yield Input(self.draft.title, id="title", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Folder"), classes="editor-label")
                        yield Select(folder_options(), value=self.draft.folder_id or ROOT_VALUE, id="folder", classes="editor-field", allow_blank=False)
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Entry type"), classes="editor-label")
                        yield Select(
                            [
                                (_("Generic credential"), "generic"),
                                (_("Web / URL"), "url"),
                                (_("SSH connection"), "ssh"),
                                (_("RDP connection"), "rdp"),
                            ],
                            value=self.draft.action_type,
                            id="action-type",
                            classes="editor-field",
                            allow_blank=False,
                        )
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Username"), classes="editor-label")
                        yield Input(self.draft.username, placeholder="{REF:U@I:<UUID>}", id="username", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Password"), classes="editor-label")
                        yield Input(self.draft.password, password=True, placeholder="{REF:P@I:<UUID>}", id="password", classes="editor-field")
                        yield Button(_("Generate…"), id="generate-password")
                        yield Button(_("Show"), id="toggle-password")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("URL"), classes="editor-label")
                        yield Input(self.draft.url, id="url", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Host"), classes="editor-label")
                        yield Input(self.draft.host, id="host", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Port"), classes="editor-label")
                        yield Input(self.draft.port, id="port", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Domain"), classes="editor-label")
                        yield Input(self.draft.rdp_domain, placeholder=".", id="rdp-domain", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("X11 forwarding"), classes="editor-label")
                        yield Select(
                            [(_("Disabled"), "off"), (_("X11 forwarding (-X)"), "X"), (_("Trusted X11 forwarding (-Y)"), "Y")],
                            value=self.draft.ssh_x11_forwarding,
                            id="x11",
                            classes="editor-field",
                            allow_blank=False,
                        )
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Advanced SSH options"), classes="editor-label")
                        yield Input(self.draft.ssh_options, placeholder="-J bastion.example.org -o ServerAliveInterval=30", id="ssh-options", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("Tags"), classes="editor-label")
                        yield Input(self.draft.tags, placeholder=_("comma separated"), id="tags", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("TOTP URI"), classes="editor-label")
                        yield Input(self.draft.totp_uri, id="totp-uri", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("TOTP secret"), classes="editor-label")
                        yield Input(self.draft.totp_secret, password=True, id="totp-secret", classes="editor-field")
                    with Horizontal(classes="editor-row"):
                        yield Label(_("TOTP QR image"), classes="editor-label")
                        yield Input("", placeholder=_("image file path"), id="totp-qr-path", classes="editor-field")
                        yield Button(_("Load QR"), id="load-qr")
                    yield Label(_("Notes"))
                    yield TextArea(self.draft.notes, id="notes")
                    yield Static(_("Fields not used by the selected entry type are ignored when saving."))
                    yield Static("", id="editor-error")
                with Horizontal(id="editor-buttons"):
                    yield Button(_("Save"), id="save", variant="primary")
                    yield Button(_("Cancel"), id="cancel")

        def _collect(self) -> EntryDraft:
            folder_value = self.query_one("#folder", Select).value
            return EntryDraft(
                title=self.query_one("#title", Input).value,
                folder_id=None if folder_value == ROOT_VALUE else str(folder_value),
                action_type=str(self.query_one("#action-type", Select).value),
                username=self.query_one("#username", Input).value,
                password=self.query_one("#password", Input).value,
                url=self.query_one("#url", Input).value,
                host=self.query_one("#host", Input).value,
                port=self.query_one("#port", Input).value,
                rdp_domain=self.query_one("#rdp-domain", Input).value,
                ssh_x11_forwarding=str(self.query_one("#x11", Select).value),
                ssh_options=self.query_one("#ssh-options", Input).value,
                tags=self.query_one("#tags", Input).value,
                totp_uri=self.query_one("#totp-uri", Input).value,
                totp_secret=self.query_one("#totp-secret", Input).value,
                notes=self.query_one("#notes", TextArea).text,
            )

        def action_save(self) -> None:
            self.dismiss(self._collect())

        def action_cancel(self) -> None:
            self.dismiss(None)

        def _finish_generated_password(self, value: str | None) -> None:
            if value:
                self.query_one("#password", Input).value = value

        def _toggle_password_visibility(self) -> None:
            password_input = self.query_one("#password", Input)
            password_input.password = not password_input.password
            toggle = self.query_one("#toggle-password", Button)
            toggle.label = _("Show") if password_input.password else _("Hide")

        def _load_qr(self) -> None:
            path = self.query_one("#totp-qr-path", Input).value.strip()
            if not path:
                self.query_one("#editor-error", Static).update(_("Enter a QR image file path."))
                return
            try:
                token = parse_totp_qr_file(path)
                self.query_one("#totp-uri", Input).value = build_otpauth_uri(token)
                self.query_one("#totp-secret", Input).value = token.secret
                self.query_one("#editor-error", Static).update(_("TOTP QR loaded."))
            except Exception as exc:
                self.query_one("#editor-error", Static).update(f"{_('Error')}: {exc}")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "save":
                self.action_save()
            elif event.button.id == "load-qr":
                self._load_qr()
            elif event.button.id == "generate-password":
                self.app.push_screen(PasswordGeneratorScreen(), self._finish_generated_password)
            elif event.button.id == "toggle-password":
                self._toggle_password_visibility()
            elif event.button.id == "cancel":
                self.action_cancel()

    class NameScreen(ModalScreen[str | None]):
        """Small modal used for folder creation and rename."""

        CSS = """
        NameScreen { align: center middle; }
        #name-panel { width: 60%; height: auto; border: round $accent; padding: 1 2; background: $surface; }
        #name-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "cancel", _("Cancel")), Binding("ctrl+s", "save", _("Save"), priority=True)]

        def __init__(self, title: str, value: str = "") -> None:
            super().__init__()
            self.dialog_title = title
            self.value = value

        def compose(self) -> ComposeResult:
            with Vertical(id="name-panel"):
                yield Static(self.dialog_title)
                yield Input(self.value, id="name")
                with Horizontal(id="name-buttons"):
                    yield Button(_("Save"), id="save", variant="primary")
                    yield Button(_("Cancel"), id="cancel")

        def action_save(self) -> None:
            value = self.query_one("#name", Input).value.strip()
            self.dismiss(value or None)

        def action_cancel(self) -> None:
            self.dismiss(None)

        def on_button_pressed(self, event: Button.Pressed) -> None:
            self.action_save() if event.button.id == "save" else self.action_cancel()

    class MoveScreen(ModalScreen[str | None | bool]):
        """Choose a destination folder. False means cancelled; None means root."""

        CSS = """
        MoveScreen { align: center middle; }
        #move-panel { width: 72%; height: auto; border: round $accent; padding: 1 2; background: $surface; }
        #move-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "cancel", _("Cancel")), Binding("ctrl+s", "save", _("Move"), priority=True)]

        def __init__(self, title: str, selected: str | None, exclude_id: str | None = None) -> None:
            super().__init__()
            self.dialog_title = title
            self.selected = selected
            self.exclude_id = exclude_id

        def compose(self) -> ComposeResult:
            with Vertical(id="move-panel"):
                yield Static(self.dialog_title)
                yield Select(folder_options(self.exclude_id), value=self.selected or ROOT_VALUE, id="destination", allow_blank=False)
                with Horizontal(id="move-buttons"):
                    yield Button(_("Move"), id="save", variant="primary")
                    yield Button(_("Cancel"), id="cancel")

        def action_save(self) -> None:
            value = self.query_one("#destination", Select).value
            self.dismiss(None if value == ROOT_VALUE else str(value))

        def action_cancel(self) -> None:
            self.dismiss(False)

        def on_button_pressed(self, event: Button.Pressed) -> None:
            self.action_save() if event.button.id == "save" else self.action_cancel()

    class ConfirmScreen(ModalScreen[bool]):
        """Explicit confirmation screen for destructive and sensitive actions."""

        CSS = """
        ConfirmScreen { align: center middle; }
        #confirm-panel { width: 64%; height: auto; border: round $warning; padding: 1 2; background: $surface; }
        #confirm-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "no", _("Cancel"))]

        def __init__(self, message: str, confirm_label: str | None = None, *, destructive: bool = False) -> None:
            super().__init__()
            self.message = message
            self.confirm_label = confirm_label or _("Confirm")
            self.destructive = destructive

        def compose(self) -> ComposeResult:
            with Vertical(id="confirm-panel"):
                yield Static(self.message)
                with Horizontal(id="confirm-buttons"):
                    yield Button(self.confirm_label, id="yes", variant="error" if self.destructive else "primary")
                    yield Button(_("Cancel"), id="no")

        def action_no(self) -> None:
            self.dismiss(False)

        def on_button_pressed(self, event: Button.Pressed) -> None:
            self.dismiss(event.button.id == "yes")

    class TrustedSignersScreen(ModalScreen[None]):
        CSS = """
        TrustedSignersScreen { align: center middle; }
        #trust-panel { width: 88%; height: auto; max-height: 85%; border: round $accent; padding: 1 2; background: $surface; }
        #trust-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "close", _("Close"))]

        def compose(self) -> ComposeResult:
            with Vertical(id="trust-panel"):
                yield Static(_("Trusted Inbox signers"))
                yield Static(_("GnuPG ownertrust is separate from this vault authorization."))
                yield Select([], id="trusted-select", allow_blank=True)
                yield Static("", id="trust-detail")
                with Horizontal(id="trust-buttons"):
                    yield Button(_("Add…"), id="trust-add")
                    yield Button(_("Remove"), id="trust-remove")
                    yield Button(_("Close"), id="trust-close")

        def on_mount(self) -> None:
            self.refresh_signers()

        def refresh_signers(self) -> None:
            select = self.query_one("#trusted-select", Select)
            signers = list_trusted_signers(vault)
            select.set_options([(s.label, s.fingerprint) for s in signers])
            if signers:
                select.value = signers[0].fingerprint
                self.query_one("#trust-detail", Static).update(signers[0].fingerprint)
            else:
                self.query_one("#trust-detail", Static).update(_("No trusted signers."))

        def action_close(self) -> None:
            self.dismiss(None)

        def on_select_changed(self, event: Select.Changed) -> None:
            if event.select.id == "trusted-select" and not _select_value_is_blank(event.value):
                self.query_one("#trust-detail", Static).update(str(event.value))

        def _finish_add(self, value) -> None:
            if not value or value is False:
                return
            try:
                add_trusted_signer(vault, str(value)); self.refresh_signers()
            except Exception as exc:
                self.query_one("#trust-detail", Static).update(f"{_('Error')}: {exc}")

        def _finish_remove(self, confirmed: bool) -> None:
            if not confirmed: return
            value = self.query_one("#trusted-select", Select).value
            if _select_value_is_blank(value): return
            try:
                remove_trusted_signer(vault, str(value)); self.refresh_signers()
            except Exception as exc:
                self.query_one("#trust-detail", Static).update(f"{_('Error')}: {exc}")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "trust-close": self.action_close(); return
            if event.button.id == "trust-add":
                trusted = {x.fingerprint for x in list_trusted_signers(vault)}
                keys = [k for k in eligible_signing_keys(vault) if k.fingerprint not in trusted]
                if not keys:
                    self.query_one("#trust-detail", Static).update(_("No additional eligible signing keys are available.")); return
                self.app.push_screen(ChoiceScreen(_("Authorize signer"), [(k.label, k.fingerprint) for k in keys]), self._finish_add)
            elif event.button.id == "trust-remove":
                value = self.query_one("#trusted-select", Select).value
                if not _select_value_is_blank(value):
                    self.app.push_screen(ConfirmScreen(_("Remove the selected signer from this vault's authorization list?"), _("Remove"), destructive=True), self._finish_remove)


    class ChoiceScreen(ModalScreen[str | bool]):
        CSS = """
        ChoiceScreen { align: center middle; }
        #choice-panel { width: 82%; height: auto; border: round $accent; padding: 1 2; background: $surface; }
        #choice-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        def __init__(self, title: str, options) -> None:
            super().__init__(); self.title_text = title; self.options = options
        def compose(self) -> ComposeResult:
            with Vertical(id="choice-panel"):
                yield Static(self.title_text)
                yield Select(self.options, id="choice", allow_blank=False)
                with Horizontal(id="choice-buttons"):
                    yield Button(_("Select"), id="choice-ok", variant="primary")
                    yield Button(_("Cancel"), id="choice-cancel")
        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "choice-cancel": self.dismiss(False)
            else: self.dismiss(str(self.query_one("#choice", Select).value))


    class InboxScreen(ModalScreen[None]):
        CSS = """
        InboxScreen { align: center middle; }
        #inbox-panel { width: 92%; height: 88%; border: round $accent; padding: 1 2; background: $surface; }
        #inbox-detail { height: 1fr; border: solid $panel; padding: 1; }
        #inbox-buttons { height: auto; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "close", _("Close"))]
        def __init__(self) -> None:
            super().__init__(); self.items = []
        def compose(self) -> ComposeResult:
            with Vertical(id="inbox-panel"):
                yield Static(_("Inbox — inspect, authorize and import pending encrypted records"))
                yield Select([], id="inbox-select", allow_blank=True)
                yield Static("", id="inbox-detail")
                with Horizontal(id="inbox-buttons"):
                    yield Button(_("Import"), id="inbox-import", variant="primary")
                    yield Button(_("Import all trusted"), id="inbox-import-all")
                    yield Button(_("Authorize signer"), id="inbox-authorize")
                    yield Button(_("Delete"), id="inbox-delete", variant="error")
                    yield Button(_("Refresh"), id="inbox-refresh")
                    yield Button(_("Close"), id="inbox-close")
        def on_mount(self) -> None: self.refresh_inbox()
        def action_close(self) -> None: self.dismiss(None)
        def _status(self, item) -> str:
            return {"trusted": _("VALID / TRUSTED"), "untrusted-signer": _("VALID SIGNATURE / NOT AUTHORIZED"), "unsigned": _("UNSIGNED"), "invalid-signature": _("INVALID SIGNATURE"), "cannot-decrypt": _("CANNOT DECRYPT"), "malformed": _("MALFORMED ENTRY")}.get(item.status, item.status)
        def refresh_inbox(self) -> None:
            self.items = inspect_inbox(vault)
            select = self.query_one("#inbox-select", Select)
            options = []
            for idx, item in enumerate(self.items):
                title = item.entry.title if item.entry else item.path.name
                options.append((f"{title} — {self._status(item)}", str(idx)))
            select.set_options(options)
            if self.items:
                select.value = "0"; self.show_item(0)
            else:
                self.query_one("#inbox-detail", Static).update(_("Inbox is empty."))
        def show_item(self, idx: int) -> None:
            item = self.items[idx]; entry = item.entry
            title = entry.title if entry else item.path.name
            username = entry.usernames[0] if entry and entry.usernames else "—"
            signer = item.signer_fingerprint or _("none")
            self.query_one("#inbox-detail", Static).update(f"{_('Title')}: {title}\n{_('Username')}: {username}\n{_('Status')}: {self._status(item)}\n{_('Signer')}: {signer}")
        def selected(self):
            value = self.query_one("#inbox-select", Select).value
            if _select_value_is_blank(value): return None
            idx = int(str(value)); return self.items[idx] if 0 <= idx < len(self.items) else None
        def on_select_changed(self, event: Select.Changed) -> None:
            if event.select.id == "inbox-select" and not _select_value_is_blank(event.value): self.show_item(int(str(event.value)))
        def _finish_unsigned(self, confirmed: bool) -> None:
            if not confirmed: return
            item = self.selected()
            if item:
                try: import_inbox_item(vault, item, accept_unsigned=True); self.refresh_inbox()
                except Exception as exc: self.query_one("#inbox-detail", Static).update(f"{_('Error')}: {exc}")
        def _finish_delete(self, confirmed: bool) -> None:
            if not confirmed: return
            item = self.selected()
            if item:
                try: delete_inbox_item(vault, item.path); self.refresh_inbox()
                except Exception as exc: self.query_one("#inbox-detail", Static).update(f"{_('Error')}: {exc}")
        def on_button_pressed(self, event: Button.Pressed) -> None:
            bid = event.button.id
            if bid == "inbox-close": self.action_close(); return
            if bid == "inbox-refresh": self.refresh_inbox(); return
            item = self.selected()
            if item is None: return
            if bid == "inbox-authorize":
                if item.status != "untrusted-signer" or not item.signer_fingerprint:
                    self.query_one("#inbox-detail", Static).update(_("The selected item does not have a valid untrusted signer.")); return
                try: add_trusted_signer(vault, item.signer_fingerprint); self.refresh_inbox()
                except Exception as exc: self.query_one("#inbox-detail", Static).update(f"{_('Error')}: {exc}")
            elif bid == "inbox-import":
                if item.status == "unsigned":
                    self.app.push_screen(ConfirmScreen(_("This item is unsigned; its sender cannot be authenticated. Import it anyway?"), _("Import unsigned")), self._finish_unsigned); return
                try: import_inbox_item(vault, item); self.refresh_inbox()
                except Exception as exc: self.query_one("#inbox-detail", Static).update(f"{_('Error')}: {exc}")
            elif bid == "inbox-import-all":
                for candidate in list(self.items):
                    if candidate.importable:
                        try: import_inbox_item(vault, candidate)
                        except Exception: pass
                self.refresh_inbox()
            elif bid == "inbox-delete":
                self.app.push_screen(ConfirmScreen(_("Delete this Inbox file without importing it?"), _("Delete"), destructive=True), self._finish_delete)

    class VaultSwitcherScreen(ModalScreen[tuple[str, str | None] | None]):
        """Select, activate, or close one of the vaults already open in the TUI."""

        CSS = """
        VaultSwitcherScreen { align: center middle; }
        #vault-switcher-panel { width: 86%; height: auto; max-height: 86%; border: round $accent; padding: 1 2; background: $surface; }
        #vault-switcher-buttons { height: 3; align-horizontal: right; margin-top: 1; }
        """
        BINDINGS = [Binding("escape", "cancel", _("Cancel"))]

        def compose(self) -> ComposeResult:
            options = []
            for opened in sessions.opened():
                state = _("locked") if opened.locked else _("unlocked")
                label = f"{opened.path.name or opened.path} [{state}] — {opened.path}"
                options.append((label, str(opened.path)))
            with Vertical(id="vault-switcher-panel"):
                yield Static(_("Open vaults"))
                yield Static(_("Choose which open vault should become active. Each vault keeps its own lock state."))
                yield Select(options, value=str(vault.path), id="vault-switcher-select", allow_blank=False)
                with Horizontal(id="vault-switcher-buttons"):
                    yield Button(_("Activate"), id="vault-switcher-activate", variant="primary")
                    yield Button(_("Close selected"), id="vault-switcher-close")
                    yield Button(_("Cancel"), id="vault-switcher-cancel")

        def action_cancel(self) -> None:
            self.dismiss(None)

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "vault-switcher-cancel":
                self.dismiss(None)
                return
            value = self.query_one("#vault-switcher-select", Select).value
            if _select_value_is_blank(value):
                return
            if event.button.id == "vault-switcher-activate":
                self.dismiss(("activate", str(value)))
            elif event.button.id == "vault-switcher-close":
                self.dismiss(("close", str(value)))

    class KeysApp(App):
        TITLE = "Keys NG"
        CSS = """
        #body { height: 1fr; }
        #tree { width: 40%; border: solid $accent; }
        #detail { width: 60%; border: solid $accent; padding: 1 2; }
        #search { dock: top; }
        #clipboard-banner { display: none; dock: bottom; height: 3; content-align: center middle; text-style: bold; padding: 0 2; }
        #clipboard-banner.visible { display: block; }
        #clipboard-banner.success { background: $success; color: $text; }
        #clipboard-banner.warning { background: $warning; color: $text; }
        #clipboard-banner.error { background: $error; color: $text; }
        #command-hints { dock: bottom; height: auto; min-height: 1; padding: 0 1; background: $panel; }
        #status { height: auto; min-height: 1; }
        """
        BINDINGS = [
            Binding("ctrl+q", "quit", _("Quit")),
            Binding("ctrl+f", "focus_search", _("Search")),
            Binding("n", "new_entry", _("New entry"), priority=True),
            Binding("ctrl+d", "new_folder", _("New folder"), priority=True),
            Binding("e", "edit_selected", _("Edit"), priority=True),
            Binding("m", "move_selected", _("Move"), priority=True),
            Binding("delete", "delete_selected", _("Delete"), priority=True),
            Binding("ctrl+u", "copy_url", _("Copy URL"), priority=True),
            Binding("f4", "copy_uuid", _("Copy UUID"), priority=True),
            Binding("ctrl+b", "copy_username", _("Copy username"), priority=True),
            Binding("ctrl+c", "copy_password", _("Copy password")),
            Binding("ctrl+t", "copy_totp", _("Copy TOTP"), priority=True),
            Binding("ctrl+n", "copy_notes", _("Copy notes"), priority=True),
            Binding("ctrl+o", "open_action", _("Open"), priority=True),
            Binding("x", "export_entry", _("Export entry XML"), priority=True),
            Binding("f8", "export_vault", _("Export vault XML"), priority=True),
            Binding("f7", "import_keepassxc", _("Import KeePassXC"), priority=True),
            Binding("f5", "open_vault", _("Open vault"), priority=True),
            Binding("f6", "recent_vault", _("Recent vault"), priority=True),
            Binding("ctrl+j", "switch_vault", _("Switch vault"), priority=True),
            Binding("ctrl+w", "close_vault", _("Close vault"), priority=True),
            Binding("f2", "preferences", _("Preferences"), priority=True),
            Binding("f1", "help", _("Help"), priority=True),
            Binding("question_mark", "shortcut_help", _("Commands"), key_display="?", priority=True),
            Binding("f3", "trusted_signers", _("Trusted signers"), priority=True),
            Binding("ctrl+l", "lock_vault", _("Lock"), priority=True),
            Binding("f9", "hard_lock_vault", _("Hard lock"), priority=True),
            Binding("ctrl+p", "unlock_vault", _("Unlock"), priority=True),
            Binding("r", "reload_tree", _("Reload")),
            Binding("i", "inbox", _("Inbox"), priority=True),
        ]

        def __init__(self) -> None:
            super().__init__()
            self.current_entry = None
            self.current_kind: str | None = None
            self.current_id: str | None = None
            self.current_folder_id: str | None = None
            self._banner_timer = None
            self._inbox_notice_shown = False

        def compose(self) -> ComposeResult:
            yield Header()
            yield Input(placeholder=_("Search…"), id="search")
            with Horizontal(id="body"):
                yield Tree(_("Vault"), id="tree")
                with Vertical(id="detail"):
                    yield Static(_("Select an entry or folder."), id="entry-detail")
                    yield Static("", id="status", markup=False)
            yield Static("", id="clipboard-banner", markup=False)
            yield Static("", id="command-hints", markup=False)
            yield Footer()

        def on_mount(self) -> None:
            set_textual_terminal_title(self)
            self.rebuild_tree()
            self.query_one("#tree", Tree).focus()
            self._update_command_hints()
            pending = len(pending_inbox_paths(vault))
            if pending:
                self._status(_("Inbox: {count} pending item(s). Press I to review.").format(count=pending))
                self._inbox_notice_shown = True

        def rebuild_tree(self, query: str = "") -> None:
            tree = self.query_one("#tree", Tree)
            tree.clear()
            if vault.locked:
                tree.root.set_label(f"{vault.path.name or vault.path} [{_('locked')}]")
                tree.root.expand()
                return
            tree.root.set_label(vault.path.name or _("Vault"))
            if query:
                paths = vault.folder_paths(catalog_snapshot=True)
                for item in vault.search(query):
                    path = paths.get(item.folder_id, _("Root")) if item.folder_id else _("Root")
                    tree.root.add_leaf(f"{item.title}  —  {path}", data=("entry", item.id))
                tree.root.expand()
                return
            folder_nodes = {}
            remaining = list(vault.list_folders())
            while remaining:
                progress = False
                for folder in list(remaining):
                    if folder.parent_id is None or folder.parent_id in folder_nodes:
                        parent = folder_nodes.get(folder.parent_id, tree.root)
                        folder_nodes[folder.id] = parent.add(
                            folder.name, data=("folder", folder.id), expand=(tree_startup_view == "expanded")
                        )
                        remaining.remove(folder)
                        progress = True
                if not progress:
                    break
            for item in vault.list_items():
                parent = folder_nodes.get(item.folder_id, tree.root)
                parent.add_leaf(item.title, data=("entry", item.id))
            tree.root.expand()

        def _reset_selection(self) -> None:
            self.current_entry = None
            self.current_kind = None
            self.current_id = None
            self.current_folder_id = None
            self.query_one("#entry-detail", Static).update(_("Select an entry or folder."))
            self._update_command_hints()

        def _refresh_after_mutation(self, message: str) -> None:
            self.rebuild_tree(self.query_one("#search", Input).value.strip())
            self._reset_selection()
            self._status(message)
            self.query_one("#tree", Tree).focus()

        def on_input_changed(self, event: Input.Changed) -> None:
            # Input.Changed bubbles from modal editor/name screens as well as
            # from the search box.  Treat only the main search Input as a
            # search event; otherwise opening/editing a modal would silently
            # filter the vault tree and clear the selected entry.
            if event.input.id != "search":
                return
            if vault.locked:
                return
            self.rebuild_tree(event.value.strip())
            self._reset_selection()

        def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
            data = event.node.data
            self.current_entry = None
            self.current_kind = data[0] if data else None
            self.current_id = data[1] if data else None
            if vault.locked:
                self.current_kind = None
                self.current_id = None
                self.current_folder_id = None
                self.query_one("#entry-detail", Static).update(_("Vault locked. Press Ctrl+P to unlock before opening entries."))
                self._status(_("Vault is locked."))
                self._update_command_hints()
                return
            if self.current_kind == "folder" and self.current_id:
                self.current_folder_id = self.current_id
                folder = vault.get_folder(self.current_id)
                path = vault.folder_path(folder.id)
                self.query_one("#entry-detail", Static).update(
                    f"[b]{folder.name}[/b]\n\n{_('Folder')}: {path}\n{_('UUID')}: {folder.id}"
                )
            elif self.current_kind == "entry" and self.current_id:
                self.current_entry = vault.get_entry(self.current_id)
                entry = self.current_entry
                self.current_folder_id = entry.folder_id
                folder = vault.folder_path(entry.folder_id) if entry.folder_id else _("Root")
                try:
                    username = vault.resolved_username(entry) or "—"
                    raw_username = entry.usernames[0] if entry.usernames else None
                    if raw_username and raw_username != username:
                        username = f"{username} ({_('reference')})"
                except Exception as exc:
                    username = f"{_('Broken reference')}: {exc}"
                otp_text = _("yes") if entry.totp else _("no")
                actions = ", ".join(action.type for action in entry.actions) or "—"
                self.query_one("#entry-detail", Static).update(
                    f"[b]{entry.title}[/b]\n\n{_('UUID')}: {entry.id}\n{_('Folder')}: {folder}\n{_('Username')}: {username}\n"
                    f"{_('Password')}: {'••••••••' if entry.password is not None else '—'}\nTOTP: {otp_text}\n"
                    f"{_('Actions')}: {actions}\n\n{entry.notes}"
                )
            else:
                self.current_folder_id = None
                self.query_one("#entry-detail", Static).update(_("Vault root"))
            self._update_command_hints()

        def _status(self, text: str) -> None:
            self.query_one("#status", Static).update(text)

        def _show_clipboard_banner(self, text: str, level: str = "success") -> None:
            banner = self.query_one("#clipboard-banner", Static)
            banner.update(text)
            banner.remove_class("success", "warning", "error")
            banner.add_class(level, "visible")
            if settings.tui_clipboard_notice_background:
                try:
                    banner.styles.background = settings.tui_clipboard_notice_background
                except Exception:
                    pass
            if settings.tui_clipboard_notice_foreground:
                try:
                    banner.styles.color = settings.tui_clipboard_notice_foreground
                except Exception:
                    pass
            if self._banner_timer is not None:
                self._banner_timer.stop()
            self._banner_timer = self.set_timer(settings.tui_clipboard_notice_seconds, self._hide_clipboard_banner)

        def _hide_clipboard_banner(self) -> None:
            banner = self.query_one("#clipboard-banner", Static)
            banner.remove_class("visible")

        def _update_command_hints(self) -> None:
            common = _("[N] New entry  [Ctrl+D] New folder  [Ctrl+J] Switch vault  [I] Inbox  [F3] Trusted signers  [?] Commands")
            if self.current_kind == "entry":
                extra = _("[E] Edit  [M] Move  [Del] Delete  [Ctrl+B] Username  [Ctrl+C] Password  [Ctrl+T] TOTP  [Ctrl+O] Open")
            elif self.current_kind == "folder":
                extra = _("[E] Rename  [M] Move  [Del] Delete")
            else:
                extra = _("[Ctrl+F] Search  [R] Reload")
            self.query_one("#command-hints", Static).update(f"{common}   {extra}")

        def action_focus_search(self) -> None:
            self.query_one("#search", Input).focus()

        def action_reload_tree(self) -> None:
            self.rebuild_tree(self.query_one("#search", Input).value.strip())
            pending = len(pending_inbox_paths(vault))
            if pending:
                self._status(_("Inbox: {count} pending item(s). Press I to review.").format(count=pending))

        def action_import_keepassxc(self) -> None:
            if vault.locked:
                self._status(_("Unlock the vault before importing.")); return
            self.push_screen(KeePassXCImportScreen(), lambda imported: self._refresh_after_mutation(_("KeePassXC import completed.")) if imported else None)

        def action_export_vault(self) -> None:
            if vault.locked: return
            self.push_screen(ExportVaultScreen(), self._finish_export_vault)

        def _finish_export_vault(self, destination: str | None) -> None:
            if not destination: return
            try:
                write_export(destination, export_vault_xml(vault))
                self._status(_("Exported plaintext XML to {path}. Delete it securely after use.").format(path=destination))
            except Exception as exc: self._status(f"{_('Error')}: {exc}")

        def _display_active_vault(self, message: str | None = None) -> None:
            """Refresh the main widgets after the active vault changes."""
            self.query_one("#search", Input).value = ""
            self._reset_selection()
            tree = self.query_one("#tree", Tree)
            if vault.locked:
                tree.clear()
                tree.root.set_label(f"{vault.path.name or vault.path} [{_('locked')}]")
                tree.root.expand()
                self.query_one("#entry-detail", Static).update(_("Vault locked. Press Ctrl+P to unlock before opening entries."))
            else:
                self.rebuild_tree()
            self.title = f"Keys NG — {vault.path.name or vault.path}"
            self.query_one("#tree", Tree).focus()
            if message:
                self._show_clipboard_banner(message, "success")
                self.query_one("#status", Static).update("")
            else:
                state = _("locked") if vault.locked else _("unlocked")
                self._status(_("Active vault: {path} ({state})").format(path=vault.path, state=state))
            self._update_command_hints()

        def _activate_opened_vault(self, path: str) -> None:
            nonlocal vault
            try:
                vault = sessions.activate(path)
                self._display_active_vault(_("Switched to vault: {path}").format(path=vault.path))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_open_vault(self) -> None:
            self.push_screen(NameScreen(_("Open vault directory"), str(Path.home())), self._finish_open_vault)

        def _finish_open_vault(self, path: str | None) -> None:
            nonlocal vault
            if not path:
                return
            try:
                candidate = str(Path(path).expanduser().resolve())
                if sessions.contains(candidate):
                    vault = sessions.activate(candidate)
                else:
                    vault = sessions.add(Vault(candidate, crypto), activate=True)
                settings.remember_vault(candidate)
                try:
                    settings.save()
                except OSError:
                    pass
                self._display_active_vault(_("Opened vault: {path}").format(path=vault.path))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_recent_vault(self) -> None:
            options = [(path, path) for path in settings.recent_vaults if Path(path).exists() and Path(path).resolve() != vault.path]
            if not options:
                self._status(_("No other recent vaults are available."))
                return
            self.push_screen(ChoiceScreen(_("Open recent vault"), options), self._finish_recent_vault)

        def _finish_recent_vault(self, path) -> None:
            if path and path is not False:
                self._finish_open_vault(str(path))

        def action_switch_vault(self) -> None:
            if len(sessions) < 2:
                self._status(_("Only one vault is currently open."))
                return
            self.push_screen(VaultSwitcherScreen(), self._finish_switch_vault)

        def _finish_switch_vault(self, result: tuple[str, str | None] | None) -> None:
            nonlocal vault
            if not result:
                return
            action, path = result
            if not path:
                return
            if action == "activate":
                self._activate_opened_vault(path)
                return
            if action == "close":
                try:
                    was_active = sessions.active_path == str(Path(path).expanduser().resolve())
                    replacement = sessions.close(path)
                    if replacement is None:
                        self.exit(("close", None))
                        return
                    if was_active:
                        vault = replacement
                        self._display_active_vault(_("Closed vault; active vault is now {path}.").format(path=vault.path))
                    else:
                        self._status(_("Closed vault: {path}").format(path=path))
                except Exception as exc:
                    self._status(f"{_('Error')}: {exc}")

        def action_close_vault(self) -> None:
            nonlocal vault
            try:
                replacement = sessions.close(vault.path)
                if replacement is None:
                    self.exit(("close", None))
                    return
                vault = replacement
                self._display_active_vault(_("Closed vault; active vault is now {path}.").format(path=vault.path))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_preferences(self) -> None:
            self.push_screen(PreferencesScreen(), lambda saved: self._status(_("Preferences saved. Restart may be required for some changes.")) if saved else None)

        def action_help(self) -> None:
            self.push_screen(ChoiceScreen(_("Help"), [(_("TUI commands"), "TUI_SHORTCUTS.md"), (_("User guide"), "README.md"), (_("Security"), "SECURITY.md"), (_("License"), "LICENSE.md")]), self._finish_help)

        def action_shortcut_help(self) -> None:
            self.push_screen(HelpScreen("TUI_SHORTCUTS.md"))

        def _finish_help(self, resource) -> None:
            if resource and resource is not False:
                self.push_screen(HelpScreen(str(resource)))

        def action_inbox(self) -> None:
            if vault.locked:
                self._status(_("Unlock the vault before reviewing the Inbox.")); return
            self.push_screen(InboxScreen(), lambda _result: self.action_reload_tree())

        def action_trusted_signers(self) -> None:
            self.push_screen(TrustedSignersScreen())

        def _copy(self, value: str, timeout: int, success: str) -> None:
            try:
                copy_secret_cli(value, timeout)
            except Exception as exc:
                try:
                    self.copy_to_clipboard(value)
                except Exception:
                    self._show_clipboard_banner(f"{_('Clipboard error')}: {exc}", "error")
                    return
                self._show_clipboard_banner(
                    _("Copied using the terminal clipboard; automatic clearing could not be verified."), "warning"
                )
                return
            self._show_clipboard_banner(success, "success")

        def action_copy_url(self) -> None:
            if not self.current_entry:
                return
            action = next((a for a in self.current_entry.actions if a.type == "url" and a.url), None)
            if action and action.url:
                self._copy(action.url, settings.clipboard_password_timeout, _("URL copied to clipboard."))

        def action_copy_uuid(self) -> None:
            if self.current_entry:
                self._copy(self.current_entry.id, settings.clipboard_password_timeout, _("UUID copied to clipboard."))

        def action_copy_username(self) -> None:
            if self.current_entry:
                try:
                    value = vault.resolved_username(self.current_entry)
                    if value is not None:
                        self._copy(value, settings.clipboard_password_timeout, _("Username copied to clipboard."))
                except Exception as exc:
                    self._status(f"{_('Reference error')}: {exc}")

        def action_copy_password(self) -> None:
            if self.current_entry:
                try:
                    value = vault.resolved_password(self.current_entry)
                    if value is not None:
                        self._copy(value, settings.clipboard_password_timeout, _("Password copied to clipboard."))
                except Exception as exc:
                    self._status(f"{_('Reference error')}: {exc}")

        def action_copy_notes(self) -> None:
            if self.current_entry and self.current_entry.notes:
                self._copy(self.current_entry.notes, settings.clipboard_password_timeout, _("Notes copied to clipboard."))

        def action_copy_totp(self) -> None:
            if self.current_entry and self.current_entry.totp:
                code, _remaining = generate_totp(self.current_entry.totp[0])
                self._copy(code, settings.clipboard_totp_timeout, _("TOTP copied to clipboard."))

        def action_open_action(self) -> None:
            if not self.current_entry or not self.current_entry.actions:
                return
            try:
                launch_action(
                    vault.resolved_action(self.current_entry, self.current_entry.actions[0]),
                    password=vault.resolved_password(self.current_entry),
                )
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_new_entry(self) -> None:
            if vault.locked:
                self._status(_("Unlock the vault before modifying it."))
                return
            draft = EntryDraft(folder_id=self.current_folder_id)
            self.push_screen(EntryEditorScreen(draft, _("New entry")), self._finish_new_entry)

        def _finish_new_entry(self, draft: EntryDraft | None) -> None:
            if draft is None:
                return
            try:
                entry = build_entry_from_draft(draft)
                vault.save_entry(entry)
                self._refresh_after_mutation(_("Entry created."))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_edit_selected(self) -> None:
            if vault.locked:
                self._status(_("Unlock the vault before modifying it."))
                return
            if self.current_kind == "entry" and self.current_entry:
                entry_id = self.current_entry.id
                self.push_screen(
                    EntryEditorScreen(EntryDraft.from_entry(self.current_entry), _("Edit entry")),
                    lambda draft, entry_id=entry_id: self._finish_edit_entry(entry_id, draft),
                )
            elif self.current_kind == "folder" and self.current_id:
                folder = vault.get_folder(self.current_id)
                self.push_screen(NameScreen(_("Rename folder"), folder.name), self._finish_rename_folder)

        def _finish_edit_entry(self, entry_id: str, draft: EntryDraft | None) -> None:
            if draft is None:
                return
            try:
                # Reload by the captured UUID instead of relying on the UI
                # selection still being current when the modal callback runs.
                existing = vault.get_entry(entry_id)
                entry = build_entry_from_draft(draft, existing)
                vault.save_entry(entry)
                self._refresh_after_mutation(_("Entry updated."))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_new_folder(self) -> None:
            if vault.locked:
                self._status(_("Unlock the vault before modifying it."))
                return
            self.push_screen(NameScreen(_("New folder")), self._finish_new_folder)

        def _finish_new_folder(self, name: str | None) -> None:
            if not name:
                return
            try:
                vault.create_folder(name, self.current_folder_id)
                self._refresh_after_mutation(_("Folder created."))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def _finish_rename_folder(self, name: str | None) -> None:
            folder_id = self.current_id if self.current_kind == "folder" else None
            if not name or not folder_id:
                return
            try:
                vault.rename_folder(folder_id, name)
                self._refresh_after_mutation(_("Folder renamed."))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_move_selected(self) -> None:
            if vault.locked or self.current_kind not in {"entry", "folder"} or not self.current_id:
                return
            selected = self.current_entry.folder_id if self.current_kind == "entry" and self.current_entry else vault.get_folder(self.current_id).parent_id
            exclude = self.current_id if self.current_kind == "folder" else None
            self.push_screen(MoveScreen(_("Move to folder"), selected, exclude), self._finish_move)

        def _finish_move(self, destination: str | None | bool) -> None:
            if destination is False or not self.current_id or self.current_kind not in {"entry", "folder"}:
                return
            try:
                if self.current_kind == "entry":
                    vault.move_entry(self.current_id, destination)
                    message = _("Entry moved.")
                else:
                    vault.move_folder(self.current_id, destination)
                    message = _("Folder moved.")
                self._refresh_after_mutation(message)
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_delete_selected(self) -> None:
            if vault.locked or self.current_kind not in {"entry", "folder"} or not self.current_id:
                return
            message = _("Delete the selected entry permanently?") if self.current_kind == "entry" else _("Delete the selected empty folder?")
            self.push_screen(ConfirmScreen(message, _("Delete"), destructive=True), self._finish_delete)

        def _finish_delete(self, confirmed: bool) -> None:
            if not confirmed or not self.current_id:
                return
            try:
                if self.current_kind == "entry":
                    vault.delete_entry(self.current_id)
                    message = _("Entry deleted.")
                elif self.current_kind == "folder":
                    vault.delete_folder(self.current_id)
                    message = _("Folder deleted.")
                else:
                    return
                self._refresh_after_mutation(message)
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_export_entry(self) -> None:
            if not self.current_entry or vault.locked:
                return
            entry_id = self.current_entry.id
            self.push_screen(
                ConfirmScreen(
                    _("Export the selected entry as plaintext KeePassXC XML? The exported file contains decrypted credential data."),
                    _("Export"),
                ),
                lambda confirmed, selected_id=entry_id: self._finish_export_entry(confirmed, selected_id),
            )

        def _finish_export_entry(self, confirmed: bool, entry_id: str) -> None:
            if not confirmed or vault.locked:
                return
            try:
                entry = vault.get_entry(entry_id)
                safe_title = "".join(ch if ch.isalnum() or ch in "-_. " else "_" for ch in entry.title).strip() or "entry"
                destination = Path.cwd() / f"{safe_title}-{entry.id[:8]}.xml"
                write_export(destination, export_entry_xml(vault, entry.id))
                self._status(_("Exported plaintext XML to {path}. Delete it securely after use.").format(path=destination))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

        def action_lock_vault(self) -> None:
            vault.lock(False)
            self._reset_selection()
            self.query_one("#entry-detail", Static).update(_("Vault locked."))
            self._status(_("Vault locked. Press Ctrl+P to unlock."))

        def action_hard_lock_vault(self) -> None:
            sessions.lock_all()
            vault.crypto.hard_lock()
            self._reset_selection()
            self.query_one("#entry-detail", Static).update(_("All open vaults were hard locked."))
            self._status(_("All vault caches and the GnuPG agent cache were cleared. Press Ctrl+P to unlock the active vault."))

        def action_unlock_vault(self) -> None:
            try:
                vault.unlock()
                self.rebuild_tree(self.query_one("#search", Input).value.strip())
                self.query_one("#tree", Tree).focus()
                self._status(_("Vault unlocked."))
            except Exception as exc:
                self._status(f"{_('Error')}: {exc}")

    while True:
        result = KeysApp().run()
        if not (isinstance(result, tuple) and result):
            break
        action = result[0]
        try:
            vault.lock(False)
        except Exception:
            pass
        if action == "open" and len(result) > 1 and result[1]:
            next_path = choose_vault(str(result[1]))
        elif action == "close":
            next_path = choose_vault(None)
        else:
            break
        if not next_path:
            break
        vault = Vault(next_path, crypto)
        sessions = VaultSessionManager(vault)


if __name__ == "__main__":
    main()
