from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.models import Entry
from keys_ng.storage.inbox import import_inbox, write_encrypted_entry
from keys_ng.storage.settings import AppSettings
from keys_ng.storage.vault import Vault


class UnsignedFakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        prefix = b"SIGNED:" if signer else b"UNSIGNED:"
        return prefix + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        if ciphertext.startswith(b"SIGNED:"):
            return DecryptionResult(ciphertext[len(b"SIGNED:"):], "SIGNER", True)
        return DecryptionResult(ciphertext[len(b"UNSIGNED:"):], None, False)

    def diagnose(self):
        return []


def test_recent_vaults_persist_and_cap_at_five(tmp_path):
    config = tmp_path / "config.toml"
    settings = AppSettings()
    paths = [tmp_path / f"vault-{n}" for n in range(7)]
    for path in paths:
        settings.remember_vault(path)
    settings.save(config)
    restored = AppSettings.load(config)
    assert restored.recent_vaults == [str(path.resolve()) for path in reversed(paths[-5:])]
    restored.remember_vault(paths[4])
    assert restored.recent_vaults[0] == str(paths[4].resolve())
    assert len(restored.recent_vaults) == 5


def test_unsigned_public_key_deposit_requires_explicit_approval(tmp_path):
    crypto = UnsignedFakeCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, ["RECIPIENT"], "SIGNER")
    entry = Entry.create("External deposit", usernames=["alice"], password="pw")
    inbox_file = vault.path / "inbox" / "external.gpg"
    write_encrypted_entry(inbox_file, entry, crypto, ["RECIPIENT"], signer=None)

    rejected = import_inbox(vault)
    assert rejected[0][1].startswith("error:")
    assert inbox_file.exists()

    accepted = import_inbox(vault, accept_unsigned=True)
    assert accepted[0][1] == "ok"
    assert not inbox_file.exists()
    assert vault.get_entry(entry.id).password == "pw"


def test_gui_source_contains_recent_menu():
    source = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert 'addMenu(_("Recent"))' in source
    assert "remember_vault" in source


def test_cli_source_exposes_public_key_only_inbox_create():
    source = Path("src/keys_ng/cli/main.py").read_text(encoding="utf-8")
    assert 'sub.add_parser("inbox-create"' in source
    assert '"--public-key"' in source
    assert '"--accept-unsigned"' in source
