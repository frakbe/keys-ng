from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry
from keys_ng.storage.inbox import deposit_entry, import_inbox
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def test_write_only_inbox_import(tmp_path):
    crypto = FakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    entry = Entry.create("Deposited", password="pw")
    deposit = deposit_entry(vault.path, entry, crypto, ["RECIPIENT"], "SIGNER")
    assert deposit.exists()
    result = import_inbox(vault)
    assert result[0][1] == "ok"
    assert not deposit.exists()
    assert vault.get_entry(entry.id).password == "pw"
