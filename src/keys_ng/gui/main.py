from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from keys_ng import __version__
from keys_ng.crypto.factory import create_crypto_backend
from keys_ng.i18n import _, configure_language, current_language
from keys_ng.models import Entry
from keys_ng.migration.keepassxc import format_import_report, import_keepassxc
from keys_ng.migration.keepassxc_export import export_entry_xml, export_vault_xml, write_export
from keys_ng.platform.app_identity import apply_qt_identity, configure_process_identity
from keys_ng.platform.desktop_integration import ensure_user_desktop_integration
from keys_ng.services.actions import launch_action
from keys_ng.services.clipboard import copy_secret_qt
from keys_ng.services.diagnostics import configure_diagnostics, elapsed_ms, get_logger
from keys_ng.services.qr import parse_totp_qr_file
from keys_ng.services.passwords import generate_password
from keys_ng.services.ssh_options import format_ssh_options
from keys_ng.services.totp import generate_totp
from keys_ng.services.entry_editor import EntryDraft, build_entry_from_draft
from keys_ng.services.vault_init import VaultInitRequest, available_vault_keys, create_vault
from keys_ng.services.trusted_signers import add_trusted_signer, eligible_signing_keys, list_trusted_signers, remove_trusted_signer
from keys_ng.storage.inbox import delete_inbox_item, import_inbox_item, inspect_inbox, pending_inbox_paths
from keys_ng.storage.settings import AppSettings
from keys_ng.storage.vault import Vault


def main() -> None:
    try:
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QCheckBox,
            QDoubleSpinBox,
            QFileDialog,
            QFormLayout,
            QHBoxLayout,
            QInputDialog,
            QLabel,
            QLineEdit,
            QListWidget,
            QMainWindow,
            QStackedWidget,
            QSpinBox,
            QMessageBox,
            QPushButton,
            QStyle,
            QTabWidget,
            QTextBrowser,
            QTextEdit,
            QTreeWidget,
            QTreeWidgetItem,
            QVBoxLayout,
            QWizard,
            QWizardPage,
            QWidget,
        )
    except ImportError:
        print("keys-ng-gui requires PySide6. Install with: pip install 'keys-ng[gui]'", file=sys.stderr)
        raise SystemExit(2)

    parser = argparse.ArgumentParser(prog="keys-ng-gui")
    parser.add_argument("vault", nargs="*", help="Vault directories to open")
    parser.add_argument("--language", default=None)
    parser.add_argument("--tree-view", choices=("expanded", "compact"), default=None, help="Initial folder tree view")
    args = parser.parse_args()
    settings = AppSettings.load()
    configure_diagnostics(settings, "gui")
    log = get_logger("gui")
    log.info("gui.start")
    configure_language(args.language or settings.language)

    TYPE_ROLE = int(Qt.ItemDataRole.UserRole)
    ID_ROLE = TYPE_ROLE + 1

    class VaultTree(QTreeWidget):
        def __init__(self, on_move, on_reload, parent=None) -> None:
            super().__init__(parent)
            self.on_move = on_move
            self.on_reload = on_reload
            self.setHeaderHidden(True)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(True)
            self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
            self.setDefaultDropAction(Qt.DropAction.MoveAction)

        def dropEvent(self, event) -> None:
            item = self.currentItem()
            if item is None:
                return
            item_type = item.data(0, TYPE_ROLE)
            item_id = item.data(0, ID_ROLE)
            target = self.itemAt(event.position().toPoint())
            parent_id = None
            if target is not None:
                target_type = target.data(0, TYPE_ROLE)
                if target_type == "folder":
                    parent_id = target.data(0, ID_ROLE)
                elif target.parent() is not None and target.parent().data(0, TYPE_ROLE) == "folder":
                    parent_id = target.parent().data(0, ID_ROLE)
            try:
                self.on_move(item_type, item_id, parent_id)
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))
            self.on_reload()
            event.accept()

    class PasswordGeneratorDialog(QDialog):
        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.setWindowTitle(_("Generate password"))
            self.length = QSpinBox(); self.length.setRange(8, 512); self.length.setValue(24)
            self.upper = QCheckBox(_("Uppercase")); self.upper.setChecked(True)
            self.lower = QCheckBox(_("Lowercase")); self.lower.setChecked(True)
            self.digits = QCheckBox(_("Digits")); self.digits.setChecked(True)
            self.symbols = QCheckBox(_("Symbols")); self.symbols.setChecked(True)
            self.ambiguous = QCheckBox(_("Allow ambiguous characters")); self.ambiguous.setChecked(False)
            self.preview = QLineEdit(); self.preview.setReadOnly(True)
            refresh = QPushButton(_("Generate again")); refresh.clicked.connect(self.regenerate)
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
            form = QFormLayout(); form.addRow(_("Length"), self.length)
            form.addRow("", self.upper); form.addRow("", self.lower); form.addRow("", self.digits); form.addRow("", self.symbols); form.addRow("", self.ambiguous)
            form.addRow(_("Generated password"), self.preview); form.addRow("", refresh)
            layout = QVBoxLayout(self); layout.addLayout(form); layout.addWidget(buttons)
            self.length.valueChanged.connect(self.regenerate)
            for box in (self.upper, self.lower, self.digits, self.symbols, self.ambiguous): box.toggled.connect(self.regenerate)
            self.regenerate()
        def regenerate(self) -> None:
            try:
                self.preview.setText(generate_password(
                    self.length.value(), uppercase=self.upper.isChecked(), lowercase=self.lower.isChecked(),
                    digits=self.digits.isChecked(), symbols=self.symbols.isChecked(), ambiguous=self.ambiguous.isChecked(),
                ))
            except Exception as exc:
                self.preview.setText(f"{_('Error')}: {exc}")
        def value(self) -> str:
            return self.preview.text()

    class EntryDialog(QDialog):
        ACTION_TYPES = ("generic", "url", "ssh", "rdp")

        def __init__(self, vault_obj: Vault, parent=None, entry: Entry | None = None, default_folder_id: str | None = None) -> None:
            super().__init__(parent)
            self.vault = vault_obj
            self.setWindowTitle(_("Edit entry") if entry else _("New entry"))
            self.entry = entry
            self.title_edit = QLineEdit(entry.title if entry else "")
            self.username_edit = QLineEdit(entry.usernames[0] if entry and entry.usernames else "")
            self.password_edit = QLineEdit(entry.password or "" if entry else "")
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_toggle = QPushButton(_("Show"))
            self.password_generate = QPushButton(_("Generate…"))
            self.password_generate.setToolTip(_("Generate a cryptographically secure password."))
            self.password_generate.clicked.connect(self.generate_password_value)
            self.password_toggle.setCheckable(True)
            self.password_toggle.setToolTip(_("Temporarily show or hide the password while editing."))
            self.password_toggle.toggled.connect(self.toggle_password_visibility)
            self.username_edit.setToolTip(_("Literal username or {REF:U@I:<UUID>} reference."))
            self.password_edit.setToolTip(_("Literal password or {REF:P@I:<UUID>} reference."))

            self.action_type_combo = QComboBox()
            self.action_type_combo.addItem(_("Generic credential"), "generic")
            self.action_type_combo.addItem(_("Web / URL"), "url")
            self.action_type_combo.addItem(_("SSH connection"), "ssh")
            self.action_type_combo.addItem(_("RDP connection"), "rdp")
            primary_action = next((a for a in (entry.actions if entry else []) if a.type in {"url", "ssh", "rdp"}), None)
            initial_type = primary_action.type if primary_action else "generic"
            type_index = self.action_type_combo.findData(initial_type)
            if type_index >= 0:
                self.action_type_combo.setCurrentIndex(type_index)

            self.url_edit = QLineEdit(primary_action.url if primary_action and primary_action.type == "url" else "")
            self.host_edit = QLineEdit(primary_action.host or "" if primary_action and primary_action.type in {"ssh", "rdp"} else "")
            self.port_edit = QLineEdit(str(primary_action.port) if primary_action and primary_action.type in {"ssh", "rdp"} and primary_action.port else "")
            self.url_label = QLabel(_("URL"))
            self.host_label = QLabel(_("Host"))
            self.port_label = QLabel(_("Port"))
            self.rdp_domain_label = QLabel(_("Domain"))
            self.rdp_domain_edit = QLineEdit(
                (primary_action.rdp_domain or "")
                if primary_action and primary_action.type == "rdp"
                else ""
            )
            self.rdp_domain_edit.setPlaceholderText(".")
            self.rdp_domain_edit.setToolTip(
                _("Optional RDP domain. Leave empty to use the remote computer's local account database (.).")
            )
            self.ssh_x11_label = QLabel(_("X11 forwarding"))
            self.ssh_x11_combo = QComboBox()
            self.ssh_x11_combo.addItem(_("Disabled"), "off")
            self.ssh_x11_combo.addItem(_("X11 forwarding (-X)"), "X")
            self.ssh_x11_combo.addItem(_("Trusted X11 forwarding (-Y)"), "Y")
            self.ssh_options_label = QLabel(_("Advanced SSH options"))
            self.ssh_options_edit = QLineEdit()
            self.ssh_options_edit.setPlaceholderText("-J bastion.example.org -o ServerAliveInterval=30")
            if primary_action and primary_action.type == "ssh":
                x11_index = self.ssh_x11_combo.findData(primary_action.ssh_x11_forwarding)
                if x11_index >= 0:
                    self.ssh_x11_combo.setCurrentIndex(x11_index)
                self.ssh_options_edit.setText(format_ssh_options(primary_action.ssh_options))

            self.tags_edit = QLineEdit(", ".join(entry.tags) if entry else "")
            self.notes_edit = QTextEdit(entry.notes if entry else "")
            self.folder_combo = QComboBox()
            self.folder_combo.addItem(_("(Root)"), None)
            for folder in self.vault.list_folders():
                self.folder_combo.addItem(self.vault.folder_path(folder.id), folder.id)
            selected_folder = entry.folder_id if entry else default_folder_id
            index = self.folder_combo.findData(selected_folder)
            if index >= 0:
                self.folder_combo.setCurrentIndex(index)

            self.totp_edit = QLineEdit("")
            self.totp_secret_edit = QLineEdit("")
            self.totp_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
            if entry and entry.totp:
                from keys_ng.services.totp import build_otpauth_uri
                self.totp_edit.setText(build_otpauth_uri(entry.totp[0]))
                self.totp_secret_edit.setText(entry.totp[0].secret)
            self.qr_button = QPushButton(_("Import TOTP QR…"))
            self.qr_clipboard_button = QPushButton(_("Import TOTP QR from clipboard"))
            self.qr_button.clicked.connect(self.import_qr)
            self.qr_clipboard_button.clicked.connect(self.import_qr_clipboard)

            form = QFormLayout()
            form.addRow(_("Title"), self.title_edit)
            form.addRow(_("Folder"), self.folder_combo)
            form.addRow(_("Entry type"), self.action_type_combo)
            form.addRow(_("Username"), self.username_edit)
            password_row = QWidget()
            password_layout = QHBoxLayout(password_row)
            password_layout.setContentsMargins(0, 0, 0, 0)
            password_layout.addWidget(self.password_edit, 1)
            password_layout.addWidget(self.password_generate)
            password_layout.addWidget(self.password_toggle)
            form.addRow(_("Password"), password_row)
            form.addRow(self.url_label, self.url_edit)
            form.addRow(self.host_label, self.host_edit)
            form.addRow(self.port_label, self.port_edit)
            form.addRow(self.rdp_domain_label, self.rdp_domain_edit)
            form.addRow(self.ssh_x11_label, self.ssh_x11_combo)
            form.addRow(self.ssh_options_label, self.ssh_options_edit)
            form.addRow(_("Tags"), self.tags_edit)
            form.addRow(_("TOTP URI"), self.totp_edit)
            form.addRow(_("TOTP secret"), self.totp_secret_edit)
            form.addRow("", self.qr_button)
            form.addRow("", self.qr_clipboard_button)
            form.addRow(_("Notes"), self.notes_edit)
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout = QVBoxLayout(self)
            layout.addLayout(form)
            layout.addWidget(buttons)

            self.action_type_combo.currentIndexChanged.connect(self.update_action_fields)
            self.update_action_fields()

        def toggle_password_visibility(self, visible: bool) -> None:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)
            self.password_toggle.setText(_("Hide") if visible else _("Show"))

        def generate_password_value(self) -> None:
            dialog = PasswordGeneratorDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.password_edit.setText(dialog.value())

        def update_action_fields(self) -> None:
            action_type = self.action_type_combo.currentData()
            is_url = action_type == "url"
            is_remote = action_type in {"ssh", "rdp"}
            self.url_label.setVisible(is_url)
            self.url_edit.setVisible(is_url)
            self.host_label.setVisible(is_remote)
            self.host_edit.setVisible(is_remote)
            self.port_label.setVisible(is_remote)
            self.port_edit.setVisible(is_remote)
            is_rdp = action_type == "rdp"
            self.rdp_domain_label.setVisible(is_rdp)
            self.rdp_domain_edit.setVisible(is_rdp)
            is_ssh = action_type == "ssh"
            self.ssh_x11_label.setVisible(is_ssh)
            self.ssh_x11_combo.setVisible(is_ssh)
            self.ssh_options_label.setVisible(is_ssh)
            self.ssh_options_edit.setVisible(is_ssh)
            if action_type == "ssh":
                self.port_edit.setPlaceholderText("22")
            elif action_type == "rdp":
                self.port_edit.setPlaceholderText("3389")
            else:
                self.port_edit.setPlaceholderText("")

        def import_qr(self) -> None:
            filename, _selected_filter = QFileDialog.getOpenFileName(self, _("Import TOTP QR"), "", _("Images (*.png *.jpg *.jpeg *.bmp *.webp)"))
            if not filename:
                return
            try:
                token = parse_totp_qr_file(filename)
                from keys_ng.services.totp import build_otpauth_uri
                self.totp_edit.setText(build_otpauth_uri(token))
                self.totp_secret_edit.setText(token.secret)
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def import_qr_clipboard(self) -> None:
            try:
                image = QApplication.clipboard().image()
                if image.isNull():
                    raise ValueError(_("Clipboard does not contain an image."))
                from keys_ng.services.qr import parse_totp_qimage
                from keys_ng.services.totp import build_otpauth_uri
                token = parse_totp_qimage(image)
                self.totp_edit.setText(build_otpauth_uri(token))
                self.totp_secret_edit.setText(token.secret)
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def build_entry(self) -> Entry:
            draft = EntryDraft(
                title=self.title_edit.text(),
                folder_id=self.folder_combo.currentData(),
                action_type=str(self.action_type_combo.currentData()),
                username=self.username_edit.text(),
                password=self.password_edit.text(),
                url=self.url_edit.text(),
                host=self.host_edit.text(),
                port=self.port_edit.text(),
                rdp_domain=self.rdp_domain_edit.text(),
                ssh_x11_forwarding=str(self.ssh_x11_combo.currentData()),
                ssh_options=self.ssh_options_edit.text(),
                tags=self.tags_edit.text(),
                totp_uri=self.totp_edit.text(),
                totp_secret=self.totp_secret_edit.text(),
                notes=self.notes_edit.toPlainText(),
            )
            return build_entry_from_draft(draft, self.entry)

    class HelpDialog(QDialog):
        def __init__(self, parent=None, initial_tab: int = 0) -> None:
            super().__init__(parent)
            self.setWindowTitle(_("Keys NG Help"))
            self.resize(820, 640)
            tabs = QTabWidget(self)
            language = current_language()
            for title, resource_name in (
                (_("Help"), "README.md"),
                (_("Security"), "SECURITY.md"),
                (_("License"), "LICENSE.md"),
            ):
                browser = QTextBrowser()
                browser.setOpenExternalLinks(True)
                try:
                    from importlib.resources import files
                    help_root = files("keys_ng").joinpath("help")
                    resource = help_root.joinpath(language, resource_name)
                    if not resource.is_file():
                        resource = help_root.joinpath("en", resource_name)
                    text = resource.read_text(encoding="utf-8")
                    if resource_name == "LICENSE.md":
                        text = _("**Installed version:** {version}").format(version=__version__) + "\n\n" + text
                except Exception as exc:
                    text = f"{_("Unable to load help document.")}\n\n{exc}"
                browser.setMarkdown(text)
                tabs.addTab(browser, title)
            tabs.setCurrentIndex(max(0, min(initial_tab, tabs.count() - 1)))
            close_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            close_buttons.rejected.connect(self.reject)
            layout = QVBoxLayout(self)
            layout.addWidget(tabs)
            layout.addWidget(close_buttons)

    class KeePassXCImportDialog(QDialog):
        """Preview and import a KeePassXC KDBX/XML source into an open vault."""

        def __init__(self, vault_obj: Vault, parent=None) -> None:
            super().__init__(parent)
            self.vault = vault_obj
            self.setWindowTitle(_("Import KeePassXC database / XML"))
            self.resize(760, 520)
            self.source_edit = QLineEdit()
            source_button = QPushButton(_("Browse…"))
            source_button.clicked.connect(self.browse_source)
            source_row = QWidget(); source_layout = QHBoxLayout(source_row); source_layout.setContentsMargins(0, 0, 0, 0)
            source_layout.addWidget(self.source_edit, 1); source_layout.addWidget(source_button)

            self.key_file_edit = QLineEdit()
            key_button = QPushButton(_("Browse…")); key_button.clicked.connect(self.browse_key_file)
            key_row = QWidget(); key_layout = QHBoxLayout(key_row); key_layout.setContentsMargins(0, 0, 0, 0)
            key_layout.addWidget(self.key_file_edit, 1); key_layout.addWidget(key_button)

            self.password_edit = QLineEdit(); self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_edit.setToolTip(_("Used only for KDBX import; kept in memory only and sent to keepassxc-cli over stdin."))
            self.no_password = QCheckBox(_("KDBX has no password component"))
            self.yubikey_edit = QLineEdit(); self.yubikey_edit.setPlaceholderText("slot[:serial]")
            self.report = QTextEdit(); self.report.setReadOnly(True)
            self.report.setPlaceholderText(_("Use Preview to validate the source without writing to the vault."))

            form = QFormLayout()
            form.addRow(_("KeePassXC KDBX or XML"), source_row)
            form.addRow(_("Key file (optional)"), key_row)
            form.addRow(_("Database password (optional)"), self.password_edit)
            form.addRow("", self.no_password)
            form.addRow(_("YubiKey (optional)"), self.yubikey_edit)

            preview_button = QPushButton(_("Preview / dry run")); preview_button.clicked.connect(self.preview_import)
            import_button = QPushButton(_("Import")); import_button.clicked.connect(self.perform_import)
            close_button = QPushButton(_("Close")); close_button.clicked.connect(self.reject)
            row = QHBoxLayout(); row.addWidget(preview_button); row.addStretch(1); row.addWidget(import_button); row.addWidget(close_button)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel(_("KDBX import uses keepassxc-cli and never writes an intermediate plaintext XML file.")))
            layout.addLayout(form); layout.addWidget(self.report, 1); layout.addLayout(row)

        def browse_source(self) -> None:
            path, selected_filter = QFileDialog.getOpenFileName(self, _("Import KeePassXC"), str(Path.home()), _("KeePassXC database or XML (*.kdbx *.xml);;All files (*)"))
            if path: self.source_edit.setText(path)

        def browse_key_file(self) -> None:
            path, selected_filter = QFileDialog.getOpenFileName(self, _("KeePassXC key file"), str(Path.home()), _("All files (*)"))
            if path: self.key_file_edit.setText(path)

        def _run(self, dry_run: bool):
            source = self.source_edit.text().strip()
            if not source: raise ValueError(_("Choose a KeePassXC KDBX or XML file."))
            password = self.password_edit.text() or None
            return import_keepassxc(
                source, self.vault, source_format="auto",
                key_file=self.key_file_edit.text().strip() or None,
                no_password=self.no_password.isChecked(),
                yubikey=self.yubikey_edit.text().strip() or None,
                dry_run=dry_run, password=password,
            )

        def preview_import(self) -> None:
            try:
                report = self._run(True)
                self.report.setPlainText(format_import_report(report))
            except Exception as exc:
                QMessageBox.critical(self, _("Import preview failed"), str(exc))

        def perform_import(self) -> None:
            if QMessageBox.warning(self, _("Import KeePassXC"), _("Import the validated entries into this vault? Existing UUID collisions will be remapped safely."), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            try:
                report = self._run(False)
                self.report.setPlainText(format_import_report(report))
                QMessageBox.information(self, _("Import complete"), _("KeePassXC import completed successfully."))
                self.accept()
            except Exception as exc:
                QMessageBox.critical(self, _("Import failed"), str(exc))

    class TrustedSignersDialog(QDialog):
        def __init__(self, vault: Vault, parent=None) -> None:
            super().__init__(parent)
            self.vault = vault
            self.setWindowTitle(_("Trusted inbox signers"))
            self.resize(720, 360)
            self.list = QListWidget(self)
            add_button = QPushButton(_("Add…"))
            remove_button = QPushButton(_("Remove"))
            close_button = QPushButton(_("Close"))
            add_button.clicked.connect(self.add_signer)
            remove_button.clicked.connect(self.remove_signer)
            close_button.clicked.connect(self.accept)
            buttons = QHBoxLayout()
            buttons.addWidget(add_button); buttons.addWidget(remove_button); buttons.addStretch(1); buttons.addWidget(close_button)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel(_("Keys listed here may submit correctly signed records to this vault. GnuPG ownertrust is separate from this vault authorization.")))
            layout.addWidget(self.list)
            layout.addLayout(buttons)
            self.refresh()

        def refresh(self) -> None:
            self.list.clear()
            for signer in list_trusted_signers(self.vault):
                role = _("vault signer") if signer.vault_signer else _("trusted inbox signer")
                self.list.addItem(f"{signer.label}\n{role}")
                self.list.item(self.list.count() - 1).setData(Qt.ItemDataRole.UserRole, signer.fingerprint)

        def add_signer(self) -> None:
            trusted = {s.fingerprint for s in list_trusted_signers(self.vault)}
            choices = [key for key in eligible_signing_keys(self.vault) if key.fingerprint not in trusted]
            if not choices:
                QMessageBox.information(self, _("Trusted signers"), _("No additional eligible signing keys are available in the GnuPG keyring."))
                return
            labels = [key.label for key in choices]
            label, ok = QInputDialog.getItem(self, _("Authorize signer"), _("OpenPGP key — verify the full fingerprint before authorizing:"), labels, 0, False)
            if not ok:
                return
            key = choices[labels.index(label)]
            if QMessageBox.question(self, _("Authorize signer"), _("Authorize this signer for future Inbox imports?\n\n{label}").format(label=key.label)) != QMessageBox.StandardButton.Yes:
                return
            add_trusted_signer(self.vault, key.fingerprint)
            self.refresh()

        def remove_signer(self) -> None:
            item = self.list.currentItem()
            if item is None:
                return
            fp = item.data(Qt.ItemDataRole.UserRole)
            try:
                if QMessageBox.question(self, _("Remove signer"), _("Remove this signer from the vault authorization list?\n\n{fingerprint}").format(fingerprint=fp)) != QMessageBox.StandardButton.Yes:
                    return
                remove_trusted_signer(self.vault, fp)
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))


    class InboxDialog(QDialog):
        def __init__(self, vault: Vault, parent=None) -> None:
            super().__init__(parent)
            self.vault = vault
            self.items = []
            self.setWindowTitle(_("Inbox"))
            self.resize(820, 500)
            self.list = QListWidget(self)
            self.details = QLabel("")
            self.details.setWordWrap(True)
            refresh_button = QPushButton(_("Refresh"))
            import_button = QPushButton(_("Import selected"))
            import_trusted_button = QPushButton(_("Import all trusted"))
            authorize_button = QPushButton(_("Authorize signer…"))
            delete_button = QPushButton(_("Delete from Inbox"))
            close_button = QPushButton(_("Close"))
            refresh_button.clicked.connect(self.refresh)
            import_button.clicked.connect(self.import_selected)
            import_trusted_button.clicked.connect(self.import_all_trusted)
            authorize_button.clicked.connect(self.authorize_selected)
            delete_button.clicked.connect(self.delete_selected)
            close_button.clicked.connect(self.accept)
            self.list.currentRowChanged.connect(self.show_details)
            row = QHBoxLayout()
            for button in (refresh_button, import_button, import_trusted_button, authorize_button, delete_button): row.addWidget(button)
            row.addStretch(1); row.addWidget(close_button)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel(_("Inbox items are decrypted only for inspection. Import re-encrypts and signs them using this vault's policy.")))
            layout.addWidget(self.list)
            layout.addWidget(self.details)
            layout.addLayout(row)
            self.refresh()

        def _status_text(self, item) -> str:
            mapping = {
                "trusted": _("VALID / TRUSTED"),
                "untrusted-signer": _("VALID SIGNATURE / SIGNER NOT AUTHORIZED"),
                "unsigned": _("UNSIGNED"),
                "invalid-signature": _("INVALID SIGNATURE"),
                "cannot-decrypt": _("CANNOT DECRYPT"),
                "malformed": _("MALFORMED ENTRY"),
            }
            return mapping.get(item.status, item.status)

        def refresh(self) -> None:
            self.items = inspect_inbox(self.vault)
            self.list.clear()
            for item in self.items:
                title = item.entry.title if item.entry else item.path.name
                self.list.addItem(f"{title} — {self._status_text(item)}")
            if self.items:
                self.list.setCurrentRow(0)
            else:
                self.details.setText(_("Inbox is empty."))

        def show_details(self, row: int) -> None:
            if row < 0 or row >= len(self.items):
                self.details.clear(); return
            item = self.items[row]
            entry = item.entry
            signer = item.signer_fingerprint or _("none")
            title = entry.title if entry else item.path.name
            username = entry.usernames[0] if entry and entry.usernames else "—"
            self.details.setText(_("Title: {title}\nUsername: {username}\nStatus: {status}\nSigner: {signer}").format(title=title, username=username, status=self._status_text(item), signer=signer))

        def import_selected(self) -> None:
            row = self.list.currentRow()
            if row < 0: return
            item = self.items[row]
            accept_unsigned = False
            if item.status == "unsigned":
                if QMessageBox.warning(self, _("Unsigned Inbox item"), _("This item is not signed. Its sender cannot be authenticated. Import it anyway?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                    return
                accept_unsigned = True
            try:
                import_inbox_item(self.vault, item, accept_unsigned=accept_unsigned)
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, _("Import failed"), str(exc))

        def import_all_trusted(self) -> None:
            failures = []
            for item in list(self.items):
                if not item.importable: continue
                try: import_inbox_item(self.vault, item)
                except Exception as exc: failures.append(type(exc).__name__)
            self.refresh()
            if failures: QMessageBox.warning(self, _("Inbox"), _("Some trusted items could not be imported."))

        def authorize_selected(self) -> None:
            row = self.list.currentRow()
            if row < 0: return
            item = self.items[row]
            if item.status != "untrusted-signer" or not item.signer_fingerprint:
                QMessageBox.information(self, _("Authorize signer"), _("The selected item does not have a valid untrusted signer.")); return
            fp = item.signer_fingerprint
            if QMessageBox.question(self, _("Authorize signer"), _("The signature is valid but this signer is not authorized by the vault. Authorize it for future Inbox imports?\n\n{fingerprint}").format(fingerprint=fp)) != QMessageBox.StandardButton.Yes:
                return
            try:
                add_trusted_signer(self.vault, fp)
                self.refresh()
            except Exception as exc: QMessageBox.critical(self, _("Error"), str(exc))

        def delete_selected(self) -> None:
            row = self.list.currentRow()
            if row < 0: return
            item = self.items[row]
            if QMessageBox.warning(self, _("Delete from Inbox"), _("Delete this Inbox file without importing it? This cannot be undone."), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            try:
                delete_inbox_item(self.vault, item.path); self.refresh()
            except Exception as exc: QMessageBox.critical(self, _("Error"), str(exc))

    class VaultPane(QWidget):
        def __init__(self, vault_path: str, parent=None) -> None:
            super().__init__(parent)
            self.vault_path = Path(vault_path).expanduser().resolve()
            self.vault = Vault(self.vault_path, create_crypto_backend(settings.crypto_backend, settings.gpg_executable, settings.gpgconf_executable))
            self.current_id: str | None = None
            self.current_entry: Entry | None = None
            self.current_folder_id: str | None = None
            self.search = QLineEdit()
            self.search.setPlaceholderText(_("Search…"))
            self.search.setClearButtonEnabled(True)
            self.search.setToolTip(_("Search entries and folders (Ctrl+F)"))
            self.entries = VaultTree(self.tree_move, self.reload, self)
            self.title = QLabel("")
            self.uuid_label = QLabel("")
            self.username = QLabel("")
            self.otp = QLabel("")
            self.notes = QTextEdit()
            self.notes.setReadOnly(True)
            self.notes.setMinimumHeight(120)
            self.notes.setToolTip(_("Notes are selectable. Use the normal Copy command or Copy notes."))
            self.path_label = QLabel("")
            self.copy_url = QPushButton(_("Copy URL"))
            self.copy_uuid = QPushButton(_("Copy UUID"))
            self.copy_username = QPushButton(_("Copy username"))
            self.copy_password = QPushButton(_("Copy password"))
            self.copy_notes = QPushButton(_("Copy notes"))
            self.copy_otp = QPushButton(_("Copy TOTP"))
            self.open_action = QPushButton(_("Open"))
            self.new_button = QPushButton(_("New entry"))
            self.edit_button = QPushButton(_("Edit"))
            self.delete_button = QPushButton(_("Delete"))
            self.new_folder_button = QPushButton(_("New folder"))
            self.rename_folder_button = QPushButton(_("Rename folder"))
            self.delete_folder_button = QPushButton(_("Delete folder"))
            self.lock_button = QPushButton(_("Lock"))
            self.hard_lock_button = QPushButton(_("Hard lock"))
            self.unlock_button = QPushButton(_("Unlock"))

            toolbar1 = QHBoxLayout()
            for button in (self.new_button, self.edit_button, self.delete_button, self.new_folder_button, self.rename_folder_button, self.delete_folder_button):
                toolbar1.addWidget(button)
            toolbar2 = QHBoxLayout()
            for button in (self.lock_button, self.hard_lock_button, self.unlock_button):
                toolbar2.addWidget(button)
            left = QVBoxLayout()
            left.addLayout(toolbar1)
            left.addLayout(toolbar2)
            left.addWidget(self.search)
            left.addWidget(self.entries)
            right = QVBoxLayout()
            right.addWidget(self.title)
            right.addWidget(self.path_label)
            right.addWidget(self.uuid_label)
            right.addWidget(self.username)
            right.addWidget(self.otp)
            right.addWidget(self.notes)
            right.addWidget(self.copy_url)
            right.addWidget(self.copy_uuid)
            right.addWidget(self.copy_username)
            right.addWidget(self.copy_password)
            right.addWidget(self.copy_notes)
            right.addWidget(self.copy_otp)
            right.addWidget(self.open_action)
            right.addStretch(1)
            root_layout = QHBoxLayout()
            root_layout.addLayout(left, 2)
            root_layout.addLayout(right, 3)
            self.setLayout(root_layout)

            # A short debounce avoids rebuilding a large tree for every keypress,
            # while the underlying search itself is served from the in-memory
            # encrypted catalog cache.
            self.search_timer = QTimer(self)
            self.search_timer.setSingleShot(True)
            self.search_timer.setInterval(75)
            self.search_timer.timeout.connect(self.reload)
            self.search.textChanged.connect(self.schedule_search)
            self.entries.currentItemChanged.connect(self.select_item)
            self.entries.itemDoubleClicked.connect(lambda _item, _column: self.open_action_clicked())
            self.copy_url.clicked.connect(self.copy_url_clicked)
            self.copy_uuid.clicked.connect(self.copy_uuid_clicked)
            self.copy_username.clicked.connect(self.copy_username_clicked)
            self.copy_password.clicked.connect(self.copy_password_clicked)
            self.copy_notes.clicked.connect(self.copy_notes_clicked)
            self.copy_otp.clicked.connect(self.copy_otp_clicked)
            self.open_action.clicked.connect(self.open_action_clicked)
            self.new_button.clicked.connect(self.new_entry)
            self.edit_button.clicked.connect(self.edit_entry)
            self.delete_button.clicked.connect(self.delete_entry)
            self.new_folder_button.clicked.connect(self.new_folder)
            self.rename_folder_button.clicked.connect(self.rename_folder)
            self.delete_folder_button.clicked.connect(self.delete_folder)
            self.lock_button.clicked.connect(lambda: self.lock(False))
            self.hard_lock_button.clicked.connect(self.request_hard_lock)
            self.unlock_button.clicked.connect(self.unlock)

            self.copy_url.setToolTip(_("Copy URL (Ctrl+U)"))
            self.copy_uuid.setToolTip(_("Copy UUID (Ctrl+Shift+I)"))
            self.copy_username.setToolTip(_("Copy username (Ctrl+B)"))
            self.copy_password.setToolTip(_("Copy password (Ctrl+C)"))
            self.copy_otp.setToolTip(_("Copy TOTP (Ctrl+T)"))
            self.open_action.setToolTip(_("Open (Ctrl+O)"))

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh_otp)
            self.timer.start(1000)
            self.auto_lock_timer = QTimer(self)
            self.auto_lock_timer.setSingleShot(True)
            self.auto_lock_timer.timeout.connect(lambda: self.lock(False))
            if settings.auto_lock_timeout > 0:
                self.auto_lock_timer.start(settings.auto_lock_timeout * 1000)
            self.reload()

        @property
        def display_name(self) -> str:
            return self.vault_path.name or str(self.vault_path)

        def status_message(self, message: str, timeout: int = 0) -> None:
            window = self.window()
            if hasattr(window, "statusBar"):
                window.statusBar().showMessage(message, timeout)

        def focus_search(self) -> None:
            self.search.setFocus()
            self.search.selectAll()
            self.activity()

        def schedule_search(self) -> None:
            self.activity()
            self.search_timer.start()

        def activity(self) -> None:
            if settings.auto_lock_timeout > 0 and not self.vault.locked:
                self.auto_lock_timer.start(settings.auto_lock_timeout * 1000)

        def _theme_icon(self, names: tuple[str, ...], fallback) -> QIcon:
            for name in names:
                icon = QIcon.fromTheme(name)
                if not icon.isNull():
                    return icon
            return self.style().standardIcon(fallback)

        def _folder_icon(self) -> QIcon:
            return self._theme_icon(("folder", "folder-symbolic"), QStyle.StandardPixmap.SP_DirIcon)

        def _entry_icon(self, catalog_item) -> QIcon:
            capabilities = set(catalog_item.capabilities)
            if "action:ssh" in capabilities:
                return self._theme_icon(("utilities-terminal", "terminal", "network-server"), QStyle.StandardPixmap.SP_ComputerIcon)
            if "action:rdp" in capabilities:
                return self._theme_icon(("preferences-desktop-remote-desktop", "computer", "video-display"), QStyle.StandardPixmap.SP_ComputerIcon)
            if "action:url" in capabilities:
                return self._theme_icon(("internet-web-browser", "web-browser", "applications-internet"), QStyle.StandardPixmap.SP_DriveNetIcon)
            if "action:command" in capabilities:
                return self._theme_icon(("utilities-terminal", "terminal"), QStyle.StandardPixmap.SP_ComputerIcon)
            return self._theme_icon(("dialog-password", "key", "password-manager"), QStyle.StandardPixmap.SP_FileIcon)

        def _folder_item(self, folder, parent=None):
            item = QTreeWidgetItem([folder.name])
            item.setIcon(0, self._folder_icon())
            item.setData(0, TYPE_ROLE, "folder")
            item.setData(0, ID_ROLE, folder.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsDragEnabled)
            if parent is None:
                self.entries.addTopLevelItem(item)
            else:
                parent.addChild(item)
            return item

        def _entry_item(self, catalog_item, parent=None, suffix=""):
            text = catalog_item.title + suffix
            item = QTreeWidgetItem([text])
            item.setIcon(0, self._entry_icon(catalog_item))
            item.setData(0, TYPE_ROLE, "entry")
            item.setData(0, ID_ROLE, catalog_item.id)
            item.setFlags((item.flags() | Qt.ItemFlag.ItemIsDragEnabled) & ~Qt.ItemFlag.ItemIsDropEnabled)
            if parent is None:
                self.entries.addTopLevelItem(item)
            else:
                parent.addChild(item)
            return item

        def reload(self) -> None:
            if self.vault.locked:
                return
            try:
                query = self.search.text().strip()
                folders = [] if query else self.vault.list_folders()
                items = self.vault.search(query) if query else self.vault.list_items()
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))
                return
            self.entries.clear()
            self.entries.setDragEnabled(not bool(query))
            if query:
                paths = self.vault.folder_paths(catalog_snapshot=True)
                for catalog_item in items:
                    path = paths.get(catalog_item.folder_id, _("Root")) if catalog_item.folder_id else _("Root")
                    self._entry_item(catalog_item, suffix=f"  —  {path}")
                return
            folder_widgets = {}
            remaining = list(folders)
            while remaining:
                progress = False
                for folder in list(remaining):
                    if folder.parent_id is None or folder.parent_id in folder_widgets:
                        folder_widgets[folder.id] = self._folder_item(folder, folder_widgets.get(folder.parent_id))
                        remaining.remove(folder)
                        progress = True
                if not progress:
                    break
            for catalog_item in items:
                self._entry_item(catalog_item, folder_widgets.get(catalog_item.folder_id))
            if (args.tree_view or settings.tree_startup_view) == "expanded":
                self.entries.expandAll()
            else:
                self.entries.collapseAll()

        def select_item(self, current, _previous) -> None:
            started = time.perf_counter()
            self.activity()
            if current is None or self.vault.locked:
                return
            item_type = current.data(0, TYPE_ROLE)
            item_id = current.data(0, ID_ROLE)
            log.debug("gui.select_item.start kind=%s", item_type)
            if item_type == "folder":
                self.current_folder_id = item_id
                self.current_id = None
                self.current_entry = None
                self.title.setText(f"<b>{current.text(0)}</b>")
                self.path_label.setText(self.vault.folder_path(item_id))
                self.uuid_label.clear(); self.username.clear(); self.otp.clear(); self.notes.clear()
                log.debug("gui.select_item.end kind=folder duration_ms=%.1f", elapsed_ms(started))
                return
            self.current_folder_id = None
            self.current_id = item_id
            decrypt_started = time.perf_counter()
            try:
                self.current_entry = self.vault.get_entry(self.current_id)
            except Exception as exc:
                log.error("gui.select_item.error kind=entry duration_ms=%.1f error_type=%s", elapsed_ms(started), type(exc).__name__)
                QMessageBox.critical(self, _("Error"), str(exc))
                return
            log.debug("gui.select_item.entry_loaded duration_ms=%.1f", elapsed_ms(decrypt_started))
            self.title.setText(f"<b>{self.current_entry.title}</b>")
            self.path_label.setText(self.vault.folder_path(self.current_entry.folder_id) if self.current_entry.folder_id else _("Root"))
            self.uuid_label.setText(f"{_('UUID')}: {self.current_entry.id}")
            try:
                resolved_username = self.vault.resolved_username(self.current_entry)
                raw_username = self.current_entry.usernames[0] if self.current_entry.usernames else None
                if raw_username and raw_username != resolved_username:
                    self.username.setText(f"{resolved_username or '—'}  ({_('reference')})")
                else:
                    self.username.setText(resolved_username or "")
            except Exception as exc:
                self.username.setText(f"{_('Broken reference')}: {exc}")
            self.notes.setText(self.current_entry.notes)
            self.refresh_otp()
            log.info("gui.select_item.end kind=entry duration_ms=%.1f", elapsed_ms(started))

        def clear_details(self) -> None:
            self.current_id = None
            self.current_entry = None
            self.current_folder_id = None
            self.entries.clear()
            self.title.clear(); self.path_label.clear(); self.uuid_label.clear(); self.username.clear(); self.otp.clear(); self.notes.clear()

        def tree_move(self, item_type: str, item_id: str, parent_id: str | None) -> None:
            if self.search.text().strip():
                return
            if item_type == "folder":
                self.vault.move_folder(item_id, parent_id)
            elif item_type == "entry":
                self.vault.move_entry(item_id, parent_id)

        def request_hard_lock(self) -> None:
            window = self.window()
            if hasattr(window, "hard_lock_all"):
                window.hard_lock_all()
            else:
                self.lock(True)

        def lock(self, hard: bool) -> None:
            try:
                self.vault.lock(hard=hard)
                QApplication.clipboard().clear()
                self.clear_details()
                self.status_message(_("Vault locked."))
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def unlock(self) -> None:
            try:
                self.vault.unlock()
                self.reload()
                self.activity()
                self.status_message(_("Vault unlocked."))
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def refresh_otp(self) -> None:
            if self.current_entry and self.current_entry.totp and not self.vault.locked:
                code, remaining = generate_totp(self.current_entry.totp[0])
                self.otp.setText(f"{code} ({remaining}s)")
            else:
                self.otp.setText("")

        def copy_url_clicked(self) -> None:
            self.activity()
            if not self.current_entry or self.vault.locked:
                return
            url_action = next((action for action in self.current_entry.actions if action.type == "url" and action.url), None)
            if url_action and url_action.url:
                copy_secret_qt(url_action.url, settings.clipboard_password_timeout * 1000)
                self.status_message(_("URL copied."), 2000)

        def copy_uuid_clicked(self) -> None:
            self.activity()
            if self.current_entry and not self.vault.locked:
                copy_secret_qt(self.current_entry.id, settings.clipboard_password_timeout * 1000)
                self.status_message(_("UUID copied."), 2000)

        def copy_username_clicked(self) -> None:
            self.activity()
            if self.current_entry and not self.vault.locked:
                try:
                    value = self.vault.resolved_username(self.current_entry)
                    if value is None:
                        return
                    copy_secret_qt(value, settings.clipboard_password_timeout * 1000)
                    self.status_message(_("Username copied."), 2000)
                except Exception as exc:
                    QMessageBox.critical(self, _("Reference error"), str(exc))

        def copy_password_clicked(self) -> None:
            self.activity()
            if self.current_entry and not self.vault.locked:
                try:
                    value = self.vault.resolved_password(self.current_entry)
                    if value is None:
                        return
                    copy_secret_qt(value, settings.clipboard_password_timeout * 1000)
                except Exception as exc:
                    QMessageBox.critical(self, _("Reference error"), str(exc))

        def copy_notes_clicked(self) -> None:
            self.activity()
            if self.current_entry and not self.vault.locked and self.current_entry.notes:
                copy_secret_qt(self.current_entry.notes, settings.clipboard_password_timeout * 1000)
                self.status_message(_("Notes copied."), 2000)

        def copy_otp_clicked(self) -> None:
            self.activity()
            if self.current_entry and self.current_entry.totp and not self.vault.locked:
                code, _remaining = generate_totp(self.current_entry.totp[0])
                copy_secret_qt(code, settings.clipboard_totp_timeout * 1000)

        def open_action_clicked(self) -> None:
            self.activity()
            if self.current_entry and self.current_entry.actions and not self.vault.locked:
                try:
                    launch_action(
                        self.vault.resolved_action(self.current_entry, self.current_entry.actions[0]),
                        password=self.vault.resolved_password(self.current_entry),
                    )
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))

        def export_entry_keepassxc(self) -> None:
            self.activity()
            if not self.current_entry or self.vault.locked:
                return
            safe_title = "".join(ch if ch.isalnum() or ch in "-_. " else "_" for ch in self.current_entry.title).strip() or "entry"
            suggested = f"{safe_title}.xml"
            path, _selected_filter = QFileDialog.getSaveFileName(
                self, _("Export entry as KeePassXC XML"), suggested, _("XML files (*.xml)"),
            )
            if not path:
                return
            try:
                write_export(path, export_entry_xml(self.vault, self.current_entry.id))
                QMessageBox.warning(
                    self, _("Plaintext export"),
                    _("The XML export contains plaintext credentials. Protect it and delete it securely after import."),
                )
                self.status_message(_("Entry exported."), 3000)
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def new_entry(self) -> None:
            self.activity()
            if self.vault.locked:
                return
            dialog = EntryDialog(self.vault, self, default_folder_id=self.current_folder_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    self.vault.save_entry(dialog.build_entry())
                    self.reload()
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))

        def edit_entry(self) -> None:
            self.activity()
            if not self.current_entry or self.vault.locked:
                return
            dialog = EntryDialog(self.vault, self, self.current_entry)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    self.vault.save_entry(dialog.build_entry())
                    self.reload()
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))

        def delete_entry(self) -> None:
            self.activity()
            if not self.current_id or self.vault.locked:
                return
            answer = QMessageBox.question(self, _("Delete entry"), _("Delete the selected entry permanently?"))
            if answer == QMessageBox.StandardButton.Yes:
                try:
                    self.vault.delete_entry(self.current_id)
                    self.clear_details()
                    self.reload()
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))

        def new_folder(self) -> None:
            self.activity()
            if self.vault.locked:
                return
            name, ok = QInputDialog.getText(self, _("New folder"), _("Folder name:"))
            if ok and name.strip():
                try:
                    self.vault.create_folder(name.strip(), self.current_folder_id)
                    self.reload()
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))

        def rename_folder(self) -> None:
            if not self.current_folder_id or self.vault.locked:
                return
            folder = self.vault.get_folder(self.current_folder_id)
            name, ok = QInputDialog.getText(self, _("Rename folder"), _("Folder name:"), text=folder.name)
            if ok and name.strip():
                try:
                    self.vault.rename_folder(folder.id, name.strip())
                    self.reload()
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))

        def delete_folder(self) -> None:
            if not self.current_folder_id or self.vault.locked:
                return
            answer = QMessageBox.question(self, _("Delete folder"), _("Delete the selected empty folder?"))
            if answer == QMessageBox.StandardButton.Yes:
                try:
                    self.vault.delete_folder(self.current_folder_id)
                    self.clear_details()
                    self.reload()
                except Exception as exc:
                    QMessageBox.critical(self, _("Error"), str(exc))


    class NewVaultWizard(QWizard):
        """Guided vault creation using the same initialization service as the CLI."""

        def __init__(self, crypto, parent=None) -> None:
            super().__init__(parent)
            self.crypto = crypto
            self.setWindowTitle(_("Create a new vault"))
            self.resize(760, 520)
            self._choices = available_vault_keys(crypto)

            location = QWizardPage()
            location.setTitle(_("Vault location"))
            location.setSubTitle(_("Choose an empty directory for the encrypted vault."))
            location_layout = QVBoxLayout(location)
            row = QHBoxLayout()
            self.path_edit = QLineEdit()
            browse = QPushButton(_("Browse…"))
            browse.clicked.connect(self._browse)
            row.addWidget(self.path_edit, 1)
            row.addWidget(browse)
            location_layout.addLayout(row)
            self.addPage(location)

            keys_page = QWizardPage()
            keys_page.setTitle(_("OpenPGP keys"))
            keys_page.setSubTitle(_("Select the recipient and signing keys. Full fingerprints are shown for verification."))
            keys_form = QFormLayout(keys_page)
            self.recipient_combo = QComboBox()
            for key in self._choices.recipients:
                self.recipient_combo.addItem(key.label, key.fingerprint)
            self.signer_combo = QComboBox()
            for key in self._choices.signers:
                self.signer_combo.addItem(key.label, key.fingerprint)
            self.require_signature = QCheckBox(_("Require valid signatures"))
            self.require_signature.setChecked(True)
            keys_form.addRow(_("Encryption recipient"), self.recipient_combo)
            keys_form.addRow(_("Signing key"), self.signer_combo)
            keys_form.addRow("", self.require_signature)
            self.addPage(keys_page)

            options = QWizardPage()
            options.setTitle(_("Vault options"))
            options.setSubTitle(_("Choose how much searchable metadata the encrypted catalog contains."))
            options_form = QFormLayout(options)
            self.privacy_combo = QComboBox()
            self.privacy_combo.addItem(_("Minimal"), "minimal")
            self.privacy_combo.addItem(_("Standard"), "standard")
            self.privacy_combo.addItem(_("Full"), "full")
            self.privacy_combo.setCurrentIndex(1)
            options_form.addRow(_("Catalog privacy"), self.privacy_combo)
            self.addPage(options)

            summary = QWizardPage()
            summary.setTitle(_("Confirm creation"))
            summary.setSubTitle(_("Keys NG will run an OpenPGP encrypt/decrypt self-test before writing the vault."))
            summary_layout = QVBoxLayout(summary)
            self.summary_label = QLabel()
            self.summary_label.setWordWrap(True)
            summary_layout.addWidget(self.summary_label)
            self.addPage(summary)
            self.currentIdChanged.connect(self._update_summary)

        def _browse(self) -> None:
            base = str(Path.home())
            path = QFileDialog.getExistingDirectory(self, _("Select an empty vault directory"), base)
            if path:
                self.path_edit.setText(path)

        def _update_summary(self, _page_id: int) -> None:
            recipient = str(self.recipient_combo.currentData() or _("None"))
            signer = str(self.signer_combo.currentData() or _("None"))
            self.summary_label.setText(
                f"{_('Location')}: {self.path_edit.text().strip()}\n\n"
                f"{_('Recipient fingerprint')}: {recipient}\n"
                f"{_('Signer fingerprint')}: {signer}\n"
                f"{_('Catalog privacy')}: {self.privacy_combo.currentData()}"
            )

        def request(self) -> VaultInitRequest:
            recipient = self.recipient_combo.currentData()
            signer = self.signer_combo.currentData()
            if not recipient:
                raise ValueError(_("No usable OpenPGP encryption key is available."))
            if self.require_signature.isChecked() and not signer:
                raise ValueError(_("No usable OpenPGP secret signing key is available."))
            return VaultInitRequest(
                path=self.path_edit.text().strip(),
                recipients=(str(recipient),),
                signer=str(signer) if signer else None,
                require_signature=self.require_signature.isChecked(),
                catalog_privacy=str(self.privacy_combo.currentData()),
            )


    class SettingsDialog(QDialog):
        """Edit the global Keys NG config.toml without exposing TOML syntax."""

        def __init__(self, app_settings: AppSettings, parent=None) -> None:
            super().__init__(parent)
            self.app_settings = app_settings
            self.setWindowTitle(_("Preferences"))
            self.resize(720, 620)
            layout = QVBoxLayout(self)
            tabs = QTabWidget(self)
            layout.addWidget(tabs)

            def help_label(text: str) -> QLabel:
                label = QLabel(text)
                label.setWordWrap(True)
                label.setStyleSheet("color: palette(mid);")
                return label

            # General / UI
            general = QWidget(self)
            general_form = QFormLayout(general)
            self.language_combo = QComboBox()
            for label, value in ((_('Automatic'), 'auto'), ('English', 'en'), ('Italiano', 'it')):
                self.language_combo.addItem(label, value)
            idx = self.language_combo.findData(app_settings.language)
            self.language_combo.setCurrentIndex(max(0, idx))
            general_form.addRow(_("Language"), self.language_combo)
            general_form.addRow('', help_label(_("The interface language. 'Automatic' follows the operating-system locale.")))

            self.tree_combo = QComboBox()
            self.tree_combo.addItem(_("Expanded"), "expanded")
            self.tree_combo.addItem(_("Compact"), "compact")
            idx = self.tree_combo.findData(app_settings.tree_startup_view)
            self.tree_combo.setCurrentIndex(max(0, idx))
            general_form.addRow(_("Initial tree view"), self.tree_combo)
            general_form.addRow('', help_label(_("Choose whether folders are expanded or collapsed when a vault is opened.")))

            self.auto_lock_spin = QSpinBox()
            self.auto_lock_spin.setRange(0, 86400)
            self.auto_lock_spin.setValue(app_settings.auto_lock_timeout)
            self.auto_lock_spin.setSuffix(' s')
            general_form.addRow(_("Automatic lock"), self.auto_lock_spin)
            general_form.addRow('', help_label(_("Seconds of inactivity before locking a vault. Use 0 to disable automatic locking.")))

            self.crypto_combo = QComboBox()
            for value in ('auto', 'gpg', 'gpgme'):
                self.crypto_combo.addItem(value, value)
            idx = self.crypto_combo.findData(app_settings.crypto_backend)
            self.crypto_combo.setCurrentIndex(max(0, idx))
            general_form.addRow(_("Crypto backend"), self.crypto_combo)
            general_form.addRow('', help_label(_("'auto' prefers GPGME when available and otherwise uses the gpg subprocess backend.")))
            self.gpg_path_edit = QLineEdit(app_settings.gpg_executable)
            self.gpg_path_edit.setPlaceholderText(_("automatic discovery"))
            general_form.addRow(_("GnuPG executable"), self.gpg_path_edit)
            self.gpgconf_path_edit = QLineEdit(app_settings.gpgconf_executable)
            self.gpgconf_path_edit.setPlaceholderText(_("automatic discovery"))
            general_form.addRow(_("gpgconf executable"), self.gpgconf_path_edit)
            verify_gpg = QPushButton(_("Verify GnuPG"))
            verify_gpg.clicked.connect(self._verify_gnupg)
            general_form.addRow('', verify_gpg)
            tabs.addTab(general, _("General"))

            # Clipboard
            clipboard = QWidget(self)
            clipboard_form = QFormLayout(clipboard)
            self.password_timeout_spin = QSpinBox()
            self.password_timeout_spin.setRange(1, 3600)
            self.password_timeout_spin.setValue(app_settings.clipboard_password_timeout)
            self.password_timeout_spin.setSuffix(' s')
            clipboard_form.addRow(_("Password / username timeout"), self.password_timeout_spin)
            clipboard_form.addRow('', help_label(_("How long copied usernames, passwords, URLs and UUIDs remain in the clipboard.")))
            self.totp_timeout_spin = QSpinBox()
            self.totp_timeout_spin.setRange(1, 300)
            self.totp_timeout_spin.setValue(app_settings.clipboard_totp_timeout)
            self.totp_timeout_spin.setSuffix(' s')
            clipboard_form.addRow(_("TOTP timeout"), self.totp_timeout_spin)
            clipboard_form.addRow('', help_label(_("How long a copied one-time password remains in the clipboard.")))
            self.tui_notice_background_edit = QLineEdit(app_settings.tui_clipboard_notice_background)
            self.tui_notice_background_edit.setPlaceholderText(_("automatic"))
            clipboard_form.addRow(_("TUI notice background"), self.tui_notice_background_edit)
            clipboard_form.addRow('', help_label(_("Optional Textual color for the high-visibility clipboard banner. Leave empty for the theme's automatic success/warning/error colors.")))
            self.tui_notice_foreground_edit = QLineEdit(app_settings.tui_clipboard_notice_foreground)
            self.tui_notice_foreground_edit.setPlaceholderText(_("automatic"))
            clipboard_form.addRow(_("TUI notice foreground"), self.tui_notice_foreground_edit)
            self.tui_notice_seconds_spin = QDoubleSpinBox()
            self.tui_notice_seconds_spin.setRange(0.5, 10.0)
            self.tui_notice_seconds_spin.setSingleStep(0.5)
            self.tui_notice_seconds_spin.setValue(app_settings.tui_clipboard_notice_seconds)
            self.tui_notice_seconds_spin.setSuffix(' s')
            clipboard_form.addRow(_("TUI notice duration"), self.tui_notice_seconds_spin)
            tabs.addTab(clipboard, _("Clipboard"))

            # SSH
            ssh_page = QWidget(self)
            ssh_form = QFormLayout(ssh_page)
            self.ssh_terminal_edit = QLineEdit(app_settings.ssh_terminal)
            ssh_form.addRow(_("SSH terminal"), self.ssh_terminal_edit)
            ssh_form.addRow('', help_label(_("Use 'auto' to prefer xdg-terminal/xdg-terminal-exec, or enter a terminal executable such as ptyxis.")))
            self.ssh_options_edit = QTextEdit()
            self.ssh_options_edit.setPlainText('\n'.join(app_settings.ssh_terminal_options))
            self.ssh_options_edit.setMaximumHeight(110)
            ssh_form.addRow(_("Terminal options"), self.ssh_options_edit)
            ssh_form.addRow('', help_label(_("One argv item per line. Example for Ptyxis: --tab on one line and -- on the next line.")))
            tabs.addTab(ssh_page, _("SSH"))

            # RDP
            rdp_page = QWidget(self)
            rdp_form = QFormLayout(rdp_page)
            self.rdp_linux_client_edit = QLineEdit(app_settings.rdp_linux_client)
            self.rdp_linux_options_edit = QTextEdit(); self.rdp_linux_options_edit.setPlainText('\n'.join(app_settings.rdp_linux_options)); self.rdp_linux_options_edit.setMaximumHeight(80)
            self.rdp_windows_client_edit = QLineEdit(app_settings.rdp_windows_client)
            self.rdp_windows_options_edit = QTextEdit(); self.rdp_windows_options_edit.setPlainText('\n'.join(app_settings.rdp_windows_options)); self.rdp_windows_options_edit.setMaximumHeight(80)
            self.rdp_macos_client_edit = QLineEdit(app_settings.rdp_macos_client)
            self.rdp_macos_options_edit = QTextEdit(); self.rdp_macos_options_edit.setPlainText('\n'.join(app_settings.rdp_macos_options)); self.rdp_macos_options_edit.setMaximumHeight(80)
            rdp_form.addRow(_("Linux client"), self.rdp_linux_client_edit)
            rdp_form.addRow(_("Linux options"), self.rdp_linux_options_edit)
            rdp_form.addRow(_("Windows client"), self.rdp_windows_client_edit)
            rdp_form.addRow(_("Windows options"), self.rdp_windows_options_edit)
            rdp_form.addRow(_("macOS client"), self.rdp_macos_client_edit)
            rdp_form.addRow(_("macOS options"), self.rdp_macos_options_edit)
            rdp_form.addRow('', help_label(_("RDP options are platform-specific argv items, one per line. Passwords are never added to the command line.")))
            tabs.addTab(rdp_page, _("RDP"))

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

        @staticmethod
        def _lines(widget: QTextEdit) -> list[str]:
            return [line.strip() for line in widget.toPlainText().splitlines() if line.strip()]

        def _verify_gnupg(self) -> None:
            try:
                backend = create_crypto_backend(
                    "gpg",
                    self.gpg_path_edit.text().strip(),
                    self.gpgconf_path_edit.text().strip(),
                )
                details = "\n".join(f"{name}: {'OK' if ok else 'FAIL'} — {detail}" for name, ok, detail in backend.diagnose())
                QMessageBox.information(self, _("GnuPG verification"), details)
            except Exception as exc:
                QMessageBox.critical(self, _("GnuPG verification"), str(exc))

        def apply(self) -> None:
            s = self.app_settings
            s.language = str(self.language_combo.currentData())
            s.tree_startup_view = str(self.tree_combo.currentData())
            s.auto_lock_timeout = self.auto_lock_spin.value()
            s.crypto_backend = str(self.crypto_combo.currentData())
            s.gpg_executable = self.gpg_path_edit.text().strip()
            s.gpgconf_executable = self.gpgconf_path_edit.text().strip()
            s.clipboard_password_timeout = self.password_timeout_spin.value()
            s.clipboard_totp_timeout = self.totp_timeout_spin.value()
            s.tui_clipboard_notice_background = self.tui_notice_background_edit.text().strip()
            s.tui_clipboard_notice_foreground = self.tui_notice_foreground_edit.text().strip()
            s.tui_clipboard_notice_seconds = float(self.tui_notice_seconds_spin.value())
            s.ssh_terminal = self.ssh_terminal_edit.text().strip() or 'auto'
            s.ssh_terminal_options = self._lines(self.ssh_options_edit)
            s.rdp_linux_client = self.rdp_linux_client_edit.text().strip() or 'auto'
            s.rdp_linux_options = self._lines(self.rdp_linux_options_edit)
            s.rdp_windows_client = self.rdp_windows_client_edit.text().strip() or 'mstsc'
            s.rdp_windows_options = self._lines(self.rdp_windows_options_edit)
            s.rdp_macos_client = self.rdp_macos_client_edit.text().strip() or 'auto'
            s.rdp_macos_options = self._lines(self.rdp_macos_options_edit)
            s.save()

    class MainWindow(QMainWindow):
        def __init__(self, initial_vaults: list[str]) -> None:
            super().__init__()
            self.setWindowTitle("Keys NG")
            self.tabs = QTabWidget(self)
            self.tabs.setTabPosition(QTabWidget.TabPosition.West)
            self.tabs.setTabsClosable(True)
            self.tabs.setMovable(True)
            self.tabs.tabCloseRequested.connect(self.close_vault)
            self.tabs.currentChanged.connect(self.update_window_title)

            self.empty_page = QWidget(self)
            empty_layout = QVBoxLayout(self.empty_page)
            empty_layout.addStretch(1)
            empty_label = QLabel(_("No vault is open."))
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_label)
            create_button = QPushButton(_("Create new vault…"))
            create_button.clicked.connect(self.create_vault_wizard)
            empty_layout.addWidget(create_button, alignment=Qt.AlignmentFlag.AlignCenter)
            open_button = QPushButton(_("Open vault…"))
            open_button.clicked.connect(self.open_vault_dialog)
            empty_layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)
            empty_layout.addStretch(1)

            self.stack = QStackedWidget(self)
            self.stack.addWidget(self.empty_page)
            self.stack.addWidget(self.tabs)
            self.setCentralWidget(self.stack)
            self.build_menus()

            self.shortcuts = []
            for sequence, callback in (
                ("Ctrl+Shift+N", self.create_vault_wizard),
                ("Ctrl+Shift+O", self.open_vault_dialog),
                ("Ctrl+W", self.close_current_vault),
                ("Ctrl+F", lambda: self.call_active("focus_search")),
                ("Ctrl+U", lambda: self.call_active("copy_url_clicked")),
                ("Ctrl+Shift+I", lambda: self.call_active("copy_uuid_clicked")),
                ("Ctrl+B", lambda: self.call_active("copy_username_clicked")),
                ("Ctrl+C", self.copy_context_or_password),
                ("Ctrl+Shift+C", lambda: self.call_active("copy_notes_clicked")),
                ("Ctrl+T", lambda: self.call_active("copy_otp_clicked")),
                ("Ctrl+O", lambda: self.call_active("open_action_clicked")),
                ("Ctrl+L", lambda: self.call_active("lock", False)),
                ("Ctrl+Shift+L", self.hard_lock_all),
                ("Ctrl+P", lambda: self.call_active("unlock")),
                ("Ctrl+,", self.show_preferences),
            ):
                shortcut = QShortcut(QKeySequence(sequence), self)
                shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
                shortcut.activated.connect(callback)
                self.shortcuts.append(shortcut)

            for path in initial_vaults:
                self.open_vault(path)
            self._sync_empty_state()

        def _menu_action(self, menu, label: str, callback, shortcut_text: str | None = None):
            text = f"{label}\t{shortcut_text}" if shortcut_text else label
            action = menu.addAction(text)
            action.triggered.connect(callback)
            return action

        def build_menus(self) -> None:
            vault_menu = self.menuBar().addMenu(_("Vault"))
            self._menu_action(vault_menu, _("New vault…"), self.create_vault_wizard, "Ctrl+Shift+N")
            self._menu_action(vault_menu, _("Open vault…"), self.open_vault_dialog, "Ctrl+Shift+O")
            self.recent_menu = vault_menu.addMenu(_("Recent"))
            self.recent_menu.aboutToShow.connect(self.refresh_recent_menu)
            self.refresh_recent_menu()
            self._menu_action(vault_menu, _("Close vault"), self.close_current_vault, "Ctrl+W")
            vault_menu.addSeparator()
            self._menu_action(vault_menu, _("Search"), lambda: self.call_active("focus_search"), "Ctrl+F")
            self._menu_action(vault_menu, _("Inbox…"), self.show_inbox)
            self._menu_action(vault_menu, _("Trusted signers…"), self.show_trusted_signers)
            vault_menu.addSeparator()
            self._menu_action(vault_menu, _("Import KeePassXC database / XML…"), self.show_keepassxc_import)
            self._menu_action(vault_menu, _("Export complete vault as KeePassXC XML…"), self.export_vault_keepassxc)
            vault_menu.addSeparator()
            self._menu_action(vault_menu, _("Lock"), lambda: self.call_active("lock", False), "Ctrl+L")
            self._menu_action(vault_menu, _("Hard lock"), self.hard_lock_all, "Ctrl+Shift+L")
            self._menu_action(vault_menu, _("Unlock"), lambda: self.call_active("unlock"), "Ctrl+P")
            entry_menu = self.menuBar().addMenu(_("Entry"))
            self._menu_action(entry_menu, _("New entry"), lambda: self.call_active("new_entry"))
            self._menu_action(entry_menu, _("Edit"), lambda: self.call_active("edit_entry"))
            self._menu_action(entry_menu, _("Delete"), lambda: self.call_active("delete_entry"))
            entry_menu.addSeparator()
            self._menu_action(entry_menu, _("Copy URL"), lambda: self.call_active("copy_url_clicked"), "Ctrl+U")
            self._menu_action(entry_menu, _("Copy UUID"), lambda: self.call_active("copy_uuid_clicked"), "Ctrl+Shift+I")
            self._menu_action(entry_menu, _("Copy username"), lambda: self.call_active("copy_username_clicked"), "Ctrl+B")
            self._menu_action(entry_menu, _("Copy password"), self.copy_context_or_password, "Ctrl+C")
            self._menu_action(entry_menu, _("Copy notes"), lambda: self.call_active("copy_notes_clicked"), "Ctrl+Shift+C")
            self._menu_action(entry_menu, _("Copy TOTP"), lambda: self.call_active("copy_otp_clicked"), "Ctrl+T")
            entry_menu.addSeparator()
            self._menu_action(entry_menu, _("Open"), lambda: self.call_active("open_action_clicked"), "Ctrl+O")
            entry_menu.addSeparator()
            self._menu_action(entry_menu, _("Export as KeePassXC XML…"), lambda: self.call_active("export_entry_keepassxc"))

            folder_menu = self.menuBar().addMenu(_("Folder"))
            self._menu_action(folder_menu, _("New folder"), lambda: self.call_active("new_folder"))
            self._menu_action(folder_menu, _("Rename folder"), lambda: self.call_active("rename_folder"))
            self._menu_action(folder_menu, _("Delete folder"), lambda: self.call_active("delete_folder"))

            settings_menu = self.menuBar().addMenu(_("Settings"))
            preferences_action = self._menu_action(settings_menu, _("Preferences…"), self.show_preferences, "Ctrl+,")
            preferences_action.setMenuRole(QAction.MenuRole.PreferencesRole)

            help_menu = self.menuBar().addMenu("?")
            self._menu_action(help_menu, _("Help"), lambda: self.show_help(0))
            self._menu_action(help_menu, _("Security"), lambda: self.show_help(1))
            self._menu_action(help_menu, _("License"), lambda: self.show_help(2))

        def copy_context_or_password(self) -> None:
            focus = QApplication.focusWidget()
            if isinstance(focus, QLineEdit) and focus.hasSelectedText():
                focus.copy(); return
            if isinstance(focus, QTextEdit) and focus.textCursor().hasSelection():
                focus.copy(); return
            self.call_active("copy_password_clicked")

        def show_keepassxc_import(self) -> None:
            pane = self.active_pane()
            if pane is None or pane.vault.locked: return
            dialog = KeePassXCImportDialog(pane.vault, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                pane.reload()
                self.statusBar().showMessage(_("KeePassXC import completed."), 4000)

        def export_vault_keepassxc(self) -> None:
            pane = self.active_pane()
            if pane is None or pane.vault.locked: return
            suggested = f"{pane.display_name}.xml"
            path, selected_filter = QFileDialog.getSaveFileName(self, _("Export complete vault as KeePassXC XML"), suggested, _("XML files (*.xml)"))
            if not path: return
            try:
                write_export(path, export_vault_xml(pane.vault))
                QMessageBox.warning(self, _("Plaintext export"), _("The XML export contains plaintext credentials. Protect it and delete it securely after import."))
                self.statusBar().showMessage(_("Vault exported."), 3000)
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def show_inbox(self) -> None:
            pane = self.active_pane()
            if pane is not None:
                InboxDialog(pane.vault, self).exec()
                pane.reload()

        def show_trusted_signers(self) -> None:
            pane = self.active_pane()
            if pane is not None:
                TrustedSignersDialog(pane.vault, self).exec()

        def show_preferences(self) -> None:
            dialog = SettingsDialog(settings, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            try:
                dialog.apply()
                self.statusBar().showMessage(_("Preferences saved. Some changes apply to newly opened vaults or after restarting Keys NG."))
                for index in range(self.tabs.count()):
                    pane = self.tabs.widget(index)
                    if isinstance(pane, VaultPane):
                        pane.reset_auto_lock_timer()
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

        def refresh_recent_menu(self) -> None:
            self.recent_menu.clear()
            recent = list(settings.recent_vaults[:5])
            if not recent:
                action = self.recent_menu.addAction(_("No recent vaults"))
                action.setEnabled(False)
                return
            for path_text in recent:
                path = Path(path_text)
                label = path.name or str(path)
                action = self.recent_menu.addAction(label)
                action.setToolTip(str(path))
                action.triggered.connect(lambda checked=False, p=str(path): self.open_vault(p))

        def show_help(self, tab: int = 0) -> None:
            HelpDialog(self, tab).exec()

        def active_pane(self) -> VaultPane | None:
            widget = self.tabs.currentWidget()
            return widget if isinstance(widget, VaultPane) else None

        def call_active(self, method: str, *args) -> None:
            pane = self.active_pane()
            if pane is None:
                return
            getattr(pane, method)(*args)

        def _sync_empty_state(self) -> None:
            self.stack.setCurrentWidget(self.tabs if self.tabs.count() else self.empty_page)
            self.update_window_title()

        def update_window_title(self, _index: int | None = None) -> None:
            pane = self.active_pane()
            self.setWindowTitle(f"Keys NG — {pane.display_name}" if pane else "Keys NG")

        def create_vault_wizard(self) -> None:
            try:
                crypto = create_crypto_backend(settings.crypto_backend, settings.gpg_executable, settings.gpgconf_executable)
                wizard = NewVaultWizard(crypto, self)
                if wizard.exec() != QDialog.DialogCode.Accepted:
                    return
                request = wizard.request()
                vault_obj = create_vault(request, crypto)
                path = str(vault_obj.path)
                self.open_vault(path)
                self.statusBar().showMessage(_("Vault created and opened."))
            except Exception as exc:
                QMessageBox.critical(self, _("Unable to create vault"), str(exc))

        def open_vault_dialog(self) -> None:
            path = QFileDialog.getExistingDirectory(self, _("Open vault"), str(Path.home()))
            if path:
                self.open_vault(path)

        def open_vault(self, path: str) -> None:
            resolved = Path(path).expanduser().resolve()
            for index in range(self.tabs.count()):
                pane = self.tabs.widget(index)
                if isinstance(pane, VaultPane) and pane.vault_path == resolved:
                    self.tabs.setCurrentIndex(index)
                    self._sync_empty_state()
                    return
            try:
                pane = VaultPane(str(resolved), self)
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))
                return
            index = self.tabs.addTab(pane, pane.display_name)
            self.tabs.setTabToolTip(index, str(resolved))
            self.tabs.setCurrentIndex(index)
            settings.remember_vault(resolved)
            try:
                settings.save()
            except OSError:
                pass
            self.refresh_recent_menu()
            self._sync_empty_state()
            pending = len(pending_inbox_paths(pane.vault))
            if pending:
                answer = QMessageBox.information(
                    self, _("Inbox"),
                    _("This vault contains {count} pending Inbox item(s). Review them now?").format(count=pending),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if answer == QMessageBox.StandardButton.Yes:
                    self.show_inbox()

        def close_current_vault(self) -> None:
            index = self.tabs.currentIndex()
            if index >= 0:
                self.close_vault(index)

        def close_vault(self, index: int) -> None:
            pane = self.tabs.widget(index)
            if isinstance(pane, VaultPane):
                try:
                    pane.vault.lock(hard=False)
                except Exception:
                    pass
                pane.clear_details()
            self.tabs.removeTab(index)
            if pane is not None:
                pane.deleteLater()
            self._sync_empty_state()

        def hard_lock_all(self) -> None:
            panes = [self.tabs.widget(i) for i in range(self.tabs.count())]
            panes = [pane for pane in panes if isinstance(pane, VaultPane)]
            if not panes:
                return
            try:
                for pane in panes:
                    pane.vault.lock(hard=False)
                    pane.clear_details()
                panes[0].vault.crypto.hard_lock()
                QApplication.clipboard().clear()
                self.statusBar().showMessage(_("All vaults hard locked."))
            except Exception as exc:
                QMessageBox.critical(self, _("Error"), str(exc))

    ensure_user_desktop_integration()
    configure_process_identity()
    app = QApplication(sys.argv)
    application_icon = apply_qt_identity(app)
    window = MainWindow(args.vault)
    if application_icon is not None:
        window.setWindowIcon(application_icon)
    window.resize(1180, 720)
    window.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
