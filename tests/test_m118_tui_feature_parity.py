from pathlib import Path

import pytest

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Action, Entry
from keys_ng.services.entry_editor import EntryDraft, build_entry_from_draft
from keys_ng.storage.settings import AppSettings
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def test_shared_entry_draft_builds_same_rich_fields_and_preserves_command_actions():
    existing = Entry.create(
        "old",
        actions=[Action(type="command", argv=["printf", "safe"])],
        custom_fields={"owner": "ops"},
    )
    draft = EntryDraft(
        title="server",
        action_type="ssh",
        username="alice",
        password="secret",
        host="host.example",
        port="2222",
        ssh_x11_forwarding="Y",
        ssh_options="-J bastion.example -o ServerAliveInterval=30",
        tags="prod, ssh",
        totp_secret="JBSWY3DPEHPK3PXP",
        notes="critical host",
    )
    updated = build_entry_from_draft(draft, existing)
    assert updated.title == "server"
    assert updated.kind == "ssh"
    assert updated.usernames == ["alice"]
    assert updated.password == "secret"
    assert updated.tags == ["prod", "ssh"]
    assert updated.notes == "critical host"
    assert updated.totp and updated.totp[0].secret == "JBSWY3DPEHPK3PXP"
    assert updated.actions[0].type == "ssh"
    assert updated.actions[0].host == "host.example"
    assert updated.actions[0].port == 2222
    assert updated.actions[0].ssh_x11_forwarding == "Y"
    assert "-J" in updated.actions[0].ssh_options
    assert any(a.type == "command" for a in updated.actions)
    assert updated.custom_fields == {"owner": "ops"}
    assert updated.revision == 2


def test_entry_draft_roundtrip_preserves_gui_tui_editable_surface():
    entry = Entry.create(
        "Example",
        usernames=["u"],
        password="p",
        actions=[Action(type="url", url="https://example.test")],
        tags=["one", "two"],
        notes="notes",
    )
    draft = EntryDraft.from_entry(entry)
    assert draft.title == "Example"
    assert draft.action_type == "url"
    assert draft.url == "https://example.test"
    assert draft.tags == "one, two"
    rebuilt = build_entry_from_draft(draft, entry)
    assert rebuilt.actions[0].url == "https://example.test"


def test_folder_reorganization_rejects_cycle_without_poisoning_cache(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    parent = vault.create_folder("Parent")
    child = vault.create_folder("Child", parent.id)
    with pytest.raises(ValueError):
        vault.move_folder(parent.id, child.id)
    assert vault.get_folder(parent.id).parent_id is None
    assert vault.get_folder(child.id).parent_id == parent.id
    assert vault.folder_path(child.id) == "Parent/Child"


def test_folder_move_rejects_duplicate_sibling_name(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    left = vault.create_folder("Left")
    right = vault.create_folder("Right")
    vault.create_folder("Same", left.id)
    moving = vault.create_folder("Same", right.id)
    with pytest.raises(Exception, match="already exists"):
        vault.move_folder(moving.id, left.id)
    assert vault.get_folder(moving.id).parent_id == right.id


def test_tui_source_exposes_create_edit_move_delete_and_high_visibility_clipboard():
    source = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    for action in ("new_entry", "new_folder", "edit_selected", "move_selected", "delete_selected"):
        assert f'"{action}"' in source
    assert "EntryEditorScreen" in source
    assert "MoveScreen" in source
    assert "ConfirmScreen" in source
    assert "build_entry_from_draft" in source
    assert "vault.create_folder" in source
    assert "vault.rename_folder" in source
    assert "vault.move_entry" in source
    assert "vault.move_folder" in source
    assert "#clipboard-banner" in source
    assert "tui_clipboard_notice_background" in source
    assert "tui_clipboard_notice_foreground" in source
    assert "command-hints" in source


def test_tui_clipboard_notice_settings_roundtrip(tmp_path):
    path = tmp_path / "config.toml"
    settings = AppSettings(
        tui_clipboard_notice_background="#112233",
        tui_clipboard_notice_foreground="#fefefe",
        tui_clipboard_notice_seconds=4.0,
    )
    settings.save(path)
    loaded = AppSettings.load(path)
    assert loaded.tui_clipboard_notice_background == "#112233"
    assert loaded.tui_clipboard_notice_foreground == "#fefefe"
    assert loaded.tui_clipboard_notice_seconds == 4.0
