"""Offscreen GUI interaction smoke test with an isolated synthetic vault.

Run against the installed package. FakeCrypto is test-only and never used by
application code; this smoke checks widgets, not OpenPGP cryptography.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtTest import QTest
from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry, Action
from keys_ng.services.references import make_entry_reference
from keys_ng.storage.vault import Vault
from keys_ng.storage.settings import AppSettings
from keys_ng.gui.main import main


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext, recipients, signer=None):
        return b'ENC:' + plaintext
    def decrypt(self, ciphertext):
        return DecryptionResult(ciphertext.removeprefix(b'ENC:'), 'SIGNER', True)
    def diagnose(self):
        return []
    def hard_lock(self):
        pass


def run():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        os.environ['XDG_CONFIG_HOME'] = str(root / 'config')
        os.environ['XDG_DATA_HOME'] = str(root / 'data')
        vault = Vault.init(root / 'vault', FakeCrypto(), ['RECIPIENT'], 'SIGNER')
        folder = vault.create_folder('Servers')
        origin = Entry.create('Shared admin', usernames=['alice'], password='never-display-this')
        target = Entry.create('Accounting', usernames=[make_entry_reference('U', origin.id)],
                              password=make_entry_reference('P', origin.id), folder_id=folder.id,
                              notes='<b>Literal notes</b>', actions=[Action(type='rdp', host='server.example')])
        vault.save_entry(origin)
        vault.save_entry(target)
        failures = []
        def error_hook(*args):
            failures.append(args)
        def exercise(*unused):
            app = QApplication.instance()
            window = next(w for w in app.topLevelWidgets() if hasattr(w, 'active_pane'))
            pane = window.active_pane()
            assert pane.results.topLevelItemCount() == 2
            # Folder scope excludes root entries, while vault scope finds them.
            folder_item = next(pane.entries.topLevelItem(i) for i in range(pane.entries.topLevelItemCount()) if pane.entries.topLevelItem(i).text(0) == 'Servers')
            pane.entries.setCurrentItem(folder_item)
            assert pane.results.topLevelItemCount() == 1
            pane.search.setText('Shared')
            pane.search_timer.stop()
            pane.search_scope.setCurrentIndex(1)
            pane.reload()
            assert pane.results.topLevelItemCount() == 0
            pane.search_scope.setCurrentIndex(0)
            assert pane.results.topLevelItemCount() == 1
            pane.open_origin(target.id)
            assert pane.current_id == target.id
            assert pane.open_action.text() == 'Connect RDP'
            assert pane.notes.toPlainText() == '<b>Literal notes</b>'
            assert 'Shared admin' in pane.username_reference.label.text()
            assert 'Shared admin' in pane.password_reference.label.text()
            assert 'never-display-this' not in pane.password_reference.label.text()
            assert pane.password_label.text() == '••••••••••••'
            pane.copy_password_clicked()
            assert QApplication.clipboard().text() == 'never-display-this'
            assert 'Password copied' in window.statusBar().currentMessage()
            QTest.qWait(1200)
            assert QApplication.clipboard().text() == ''
            pane.password_reference.open_source()
            assert pane.current_id == origin.id
            pane.search.setText('Accounting')
            pane.search_timer.stop()
            pane.reload()
            assert pane.results.topLevelItemCount() == 1
            pane.focus_results()
            assert pane.current_id == target.id
            pane.search.setText('missing')
            pane.search_timer.stop()
            pane.reload()
            assert pane.current_entry is None
            assert not pane.copy_password.isEnabled()
            pane.open_origin(target.id)
            # Exercise the real entry editor without entering a second event loop.
            def edit_dialog(dialog):
                assert 'Shared admin' in dialog.password_reference.label.text()
                dialog.title_edit.setText('Unsaved draft')
                dialog.username_edit.setText('new-user')
                dialog.refresh_references()
                assert dialog.username_reference.isHidden()
                assert dialog.title_edit.text() == 'Unsaved draft'
                # Nested preview must leave the draft intact.
                def preview(preview_dialog):
                    assert preview_dialog.windowTitle() == 'Source entry — read only'
                    return QDialog.DialogCode.Rejected
                with patch.object(QDialog, 'exec', preview):
                    dialog.preview_origin(origin.id)
                assert dialog.title_edit.text() == 'Unsaved draft'
                pane.lock(False)
                assert dialog.password_edit.text() == ''
                assert dialog.entry is None
                return QDialog.DialogCode.Rejected
            with patch.object(QDialog, 'exec', edit_dialog):
                pane.edit_entry()
            assert pane.results.topLevelItemCount() == 0
            assert pane.password_reference.isHidden()
            assert not QApplication.clipboard().text()
            pane.unlock()
            pane.open_origin(target.id)
            pane.tree_move('entry', target.id, None)
            pane.reload()
            assert pane.vault.get_entry(target.id).folder_id is None
            def save_dialog(dialog):
                dialog.notes_edit.setPlainText('Edited smoke note')
                return QDialog.DialogCode.Accepted
            with patch.object(QDialog, 'exec', save_dialog):
                pane.edit_entry()
            assert pane.current_id == target.id
            assert pane.vault.get_entry(target.id).notes == 'Edited smoke note'
            # A username pointing at a password must not display that password.
            changed = pane.vault.get_entry(target.id)
            changed.usernames = [make_entry_reference('P', origin.id)]
            pane.vault.save_entry(changed)
            pane.reload()
            assert 'never-display-this' not in pane.username.text()
            assert 'Protected reference' in pane.username.text()
            pane.compact.setChecked(True)
            pane.save_layout()
            pane.open_origin(target.id)
            app.processEvents()
            screenshot = os.environ.get('KEYS_NG_SMOKE_SCREENSHOT')
            if screenshot:
                window.grab().save(screenshot)
            other = Vault.init(root / 'other-vault', FakeCrypto(), ['RECIPIENT'], 'SIGNER')
            other.save_entry(Entry.create('Other vault', password='other-secret'))
            window.open_vault(str(other.path))
            other_pane = window.active_pane()
            assert other_pane is not pane
            other_pane.lock(False)
            assert not pane.vault.locked
            other_pane.unlock()
            window.hard_lock_all()
            assert other_pane.vault.locked
            assert pane.vault.locked and pane.current_entry is None
            assert not failures, failures
            window.close()
            return 0
        with patch('keys_ng.gui.main.create_crypto_backend', return_value=FakeCrypto()), \
             patch('keys_ng.gui.main.ensure_user_desktop_integration'), \
             patch.object(AppSettings, 'load', return_value=AppSettings(language='en', auto_lock_timeout=300, clipboard_password_timeout=1)), \
             patch.object(AppSettings, 'save'), \
             patch.object(QApplication, 'exec', exercise), \
             patch.object(QMessageBox, 'critical', side_effect=lambda *a: (_ for _ in ()).throw(AssertionError(a[2]))), \
             patch.object(sys, 'argv', ['keys-ng-gui', str(vault.path)]), \
             patch.object(sys, 'excepthook', error_hook):
            try:
                main()
            except SystemExit as exc:
                assert exc.code == 0
        print('GUI smoke passed: selection, search, references, draft preview, clipboard, lock, move, layout, hard lock')


if __name__ == '__main__':
    run()
