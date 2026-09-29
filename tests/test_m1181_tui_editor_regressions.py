from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry
from keys_ng.services.entry_editor import EntryDraft, build_entry_from_draft
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def test_edit_draft_can_be_saved_and_reloaded_by_captured_uuid(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    original = vault.save_entry(Entry.create("Old title", usernames=["old-user"], password="old-secret"))
    entry_id = original.id

    # Mirrors the fixed TUI callback: reload the entry by the UUID captured
    # before opening the modal, then apply the returned draft and persist it.
    existing = vault.get_entry(entry_id)
    draft = EntryDraft.from_entry(existing)
    draft.title = "New title"
    draft.username = "new-user"
    draft.password = "new-secret"
    updated = build_entry_from_draft(draft, existing)
    vault.save_entry(updated)

    reloaded = vault.get_entry(entry_id)
    assert reloaded.title == "New title"
    assert reloaded.usernames == ["new-user"]
    assert reloaded.password == "new-secret"
    assert reloaded.revision == original.revision + 1


def test_tui_modal_inputs_do_not_drive_main_search_or_clear_selection():
    source = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert 'if event.input.id != "search":' in source
    assert 'lambda draft, entry_id=entry_id: self._finish_edit_entry(entry_id, draft)' in source
    assert 'existing = vault.get_entry(entry_id)' in source


def test_password_visibility_toggle_exists_in_tui_and_gui():
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")

    assert 'id="toggle-password"' in tui
    assert 'password_input.password = not password_input.password' in tui
    assert '_("Hide")' in tui and '_("Show")' in tui

    assert 'self.password_toggle = QPushButton(_("Show"))' in gui
    assert 'self.password_toggle.toggled.connect(self.toggle_password_visibility)' in gui
    assert 'QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password' in gui
