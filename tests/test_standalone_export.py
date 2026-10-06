from __future__ import annotations

from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry
from keys_ng.services.standalone_export import prepare_standalone_entry, export_standalone_entry
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return (f"{recipients[0]}:{signer or ''}:".encode("utf-8")) + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        _recipient, signer, plaintext = ciphertext.split(b":", 2)
        return DecryptionResult(plaintext, signer.decode("utf-8") or None, bool(signer))

    def diagnose(self):
        return []


def test_standalone_export_gets_new_uuid_and_no_folder(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    entry = Entry.create("Share me", usernames=["alice"], password="secret")
    vault.save_entry(entry)

    exported = prepare_standalone_entry(vault, entry)
    assert exported.id != entry.id
    assert exported.folder_id is None
    assert exported.usernames == ["alice"]
    assert exported.password == "secret"


def test_standalone_export_writes_encrypted_copy(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    entry = Entry.create("Share me", password="secret")
    vault.save_entry(entry)

    destination, exported = export_standalone_entry(
        vault, entry.id, tmp_path / "shared.gpg", "OTHER-RECIPIENT", "SIGNER"
    )

    assert destination == (tmp_path / "shared.gpg").resolve()
    assert destination.exists()
    decrypted = crypto.decrypt(destination.read_bytes())
    assert decrypted.plaintext == exported.to_bytes()
    assert decrypted.signer_fingerprint == "SIGNER"
