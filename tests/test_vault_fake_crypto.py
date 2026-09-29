from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def test_vault_roundtrip(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    entry = Entry.create("GitHub", usernames=["alice"], password="pw", tags=["dev"])
    vault.save_entry(entry)
    assert vault.get_entry(entry.id).password == "pw"
    assert vault.search("github")[0].id == entry.id
