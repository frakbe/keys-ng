from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry
from keys_ng.storage.vault import Vault


class CountingCrypto(CryptoBackend):
    def __init__(self):
        self.decrypt_calls = 0

    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        self.decrypt_calls += 1
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def test_search_uses_one_catalog_decrypt_and_then_ram_cache(tmp_path):
    setup_crypto = CountingCrypto()
    vault = Vault.init(tmp_path / "vault", setup_crypto, ["RECIPIENT"], "SIGNER")
    folder = vault.create_folder_path("Personal/Cloud/Providers")
    assert folder is not None
    for index in range(260):
        vault.save_entry(Entry.create(f"Provider {index}", usernames=[f"user{index}"], folder_id=folder.id))

    crypto = CountingCrypto()
    reopened = Vault(vault.path, crypto)
    result = reopened.search("provider 259")
    assert [item.title for item in result] == ["Provider 259"]
    assert crypto.decrypt_calls == 1

    reopened.search("cloud")
    reopened.search("user259")
    assert crypto.decrypt_calls == 1


def test_lock_drops_decrypted_metadata_caches(tmp_path):
    setup_crypto = CountingCrypto()
    vault = Vault.init(tmp_path / "vault", setup_crypto, ["RECIPIENT"], "SIGNER")
    vault.save_entry(Entry.create("Entry"))
    crypto = CountingCrypto()
    reopened = Vault(vault.path, crypto)
    reopened.search("entry")
    assert crypto.decrypt_calls == 1
    reopened.lock()
    reopened.unlock()
    # unlock validates both catalog and folders after clearing caches
    assert crypto.decrypt_calls == 3
