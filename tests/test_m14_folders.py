import pytest

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.errors import VaultError
from keys_ng.models import Entry
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def test_nested_folders_and_entry_move(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    cloud = vault.create_folder_path("Personal/Cloud")
    assert cloud is not None
    assert vault.folder_path(cloud.id) == "Personal/Cloud"
    entry = Entry.create("Aruba", folder_id=cloud.id)
    vault.save_entry(entry)
    assert vault.list_items(folder_id=cloud.id)[0].title == "Aruba"
    accounts = vault.create_folder_path("Personal/Accounts")
    vault.move_entry(entry.id, accounts.id)
    assert vault.get_entry(entry.id).folder_id == accounts.id
    assert vault.search("accounts")[0].id == entry.id


def test_folder_cycle_and_nonempty_delete_are_rejected(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    parent = vault.create_folder("Parent")
    child = vault.create_folder("Child", parent.id)
    with pytest.raises(ValueError):
        vault.move_folder(parent.id, child.id)
    entry = Entry.create("Entry", folder_id=child.id)
    vault.save_entry(entry)
    with pytest.raises(VaultError):
        vault.delete_folder(child.id)


def test_existing_pre_folder_vault_remains_readable(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    (vault.path / "folders.gpg").unlink()
    reopened = Vault(vault.path, FakeCrypto())
    assert reopened.list_folders() == []


def test_reindex_preserves_folder_tree(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    folder = vault.create_folder_path("Work/Servers")
    vault.save_entry(Entry.create("prod", folder_id=folder.id))
    rebuilt = vault.reindex()
    assert [f.name for f in rebuilt.folders] == [f.name for f in vault.load_folders().folders]
    assert rebuilt.items[0].folder_id == folder.id
