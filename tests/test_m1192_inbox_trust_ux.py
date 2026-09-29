from __future__ import annotations

from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult, KeyInfo
from keys_ng.models import Entry
from keys_ng.services.trusted_signers import add_trusted_signer, list_trusted_signers, remove_trusted_signer
from keys_ng.storage.inbox import import_inbox_item, inspect_inbox, pending_inbox_paths, write_encrypted_entry
from keys_ng.storage.vault import Vault

WINDOWS = "79DC1F35D867DBA6FA0F3702900081906240F4F0"
LINUX = "6364882317F5D6F26B0B05D289B022BDB724DE7E"


class TwoUserCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        signer_bytes = (signer or "").encode("ascii")
        return b"ENC:" + signer_bytes + b":" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        assert ciphertext.startswith(b"ENC:")
        signer, plaintext = ciphertext[4:].split(b":", 1)
        fp = signer.decode("ascii") or None
        return DecryptionResult(plaintext, fp, bool(fp), fp)

    def diagnose(self):
        return []

    def list_keys(self, secret: bool = False):
        keys = [
            KeyInfo(WINDOWS, ("Windows colleague <windows@example.test>",), True, True, secret),
            KeyInfo(LINUX, ("Linux colleague <linux@example.test>",), True, True, secret),
        ]
        return keys


def test_two_colleague_inbox_requires_vault_authorization(tmp_path: Path):
    crypto = TwoUserCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, [WINDOWS], WINDOWS)
    entry = Entry.create("VSCA root credentials", usernames=["root"], password="secret")
    path = vault.path / "inbox" / "VSCA.gpg"
    write_encrypted_entry(path, entry, crypto, [WINDOWS], LINUX)

    assert pending_inbox_paths(vault) == [path]
    inspection = inspect_inbox(vault)[0]
    assert inspection.signature_valid is True
    assert inspection.signer_authorized is False
    assert inspection.status == "untrusted-signer"

    add_trusted_signer(vault, LINUX)
    inspection = inspect_inbox(vault)[0]
    assert inspection.status == "trusted"
    import_inbox_item(vault, inspection)

    assert not path.exists()
    assert vault.get_entry(entry.id).password == "secret"
    reloaded = Vault(vault.path, crypto)
    assert LINUX in reloaded.config.trusted_signers


def test_vault_signer_cannot_be_removed(tmp_path: Path):
    crypto = TwoUserCrypto()
    vault = Vault.init(tmp_path / "vault", crypto, [WINDOWS], WINDOWS)
    add_trusted_signer(vault, LINUX)
    remove_trusted_signer(vault, LINUX)
    assert [s.fingerprint for s in list_trusted_signers(vault)] == [WINDOWS]
    try:
        remove_trusted_signer(vault, WINDOWS)
    except Exception as exc:
        assert "cannot be removed" in str(exc)
    else:
        raise AssertionError("vault signer removal must fail")


def test_gui_and_tui_expose_inbox_workflows():
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert '_("Inbox…")' in gui
    assert "InboxDialog" in gui and "TrustedSignersDialog" in gui
    assert 'Binding("i", "inbox"' in tui
    assert "InboxScreen" in tui and "TrustedSignersScreen" in tui
