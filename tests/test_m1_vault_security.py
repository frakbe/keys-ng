import pytest

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.errors import VaultError
from keys_ng.models import Action, Entry
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def __init__(self):
        self.hard_locked = False

    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []

    def hard_lock(self):
        self.hard_locked = True


def test_catalog_privacy_standard_hides_username_and_host(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER", catalog_privacy="standard")
    entry = Entry.create(
        "Server",
        usernames=["alice"],
        tags=["prod"],
        actions=[Action(type="ssh", host="secret.example", username="alice")],
    )
    vault.save_entry(entry)
    item = vault.list_items()[0]
    assert item.usernames == []
    assert item.url_hosts == []
    assert item.tags == ["prod"]


def test_lock_and_hard_lock(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    vault.lock(hard=True)
    assert crypto.hard_locked
    with pytest.raises(VaultError):
        vault.list_items()
    vault.unlock()
    assert vault.list_items() == []


def test_catalog_health_detects_record_change(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    entry = Entry.create("Example")
    vault.save_entry(entry)
    ok, issues = vault.catalog_health()
    assert ok and not issues
    record = tmp_path / "vault" / "records" / f"{entry.id}.gpg"
    record.write_bytes(record.read_bytes() + b"tamper")
    ok, issues = vault.catalog_health()
    assert not ok
    assert any("hash mismatch" in issue for issue in issues)


def test_recover_stale_ciphertext_temp(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    stale = vault.path / "records" / ".entry.gpg.deadbeef.tmp"
    stale.write_bytes(b"ciphertext-only")
    reopened = Vault(vault.path, crypto)
    assert not stale.exists()
    assert reopened.recover_interrupted_writes() == 0
