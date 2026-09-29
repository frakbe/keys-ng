from __future__ import annotations

import os
import random
import string
from pathlib import Path

import pytest

from keys_ng.errors import VaultError
from keys_ng.models import Catalog, Entry, FolderStore
from keys_ng.storage.atomic import atomic_write_ciphertext
from keys_ng.storage.vault import Vault


class FakeCrypto:
    def encrypt(self, plaintext, recipients, signer=None):
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext):
        from keys_ng.crypto.backend import DecryptionResult
        assert ciphertext.startswith(b"ENC:")
        return DecryptionResult(ciphertext[4:], "SIGNER", True)

    def hard_lock(self):
        pass


def test_vault_directories_are_private_on_posix(tmp_path: Path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    if os.name != "nt":
        assert (vault.path.stat().st_mode & 0o777) == 0o700
        assert ((vault.path / "records").stat().st_mode & 0o777) == 0o700
        assert ((vault.path / "inbox").stat().st_mode & 0o777) == 0o700
        assert ((vault.path / "vault.json").stat().st_mode & 0o777) == 0o600


def test_single_record_rollback_is_rejected(tmp_path: Path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    entry = Entry.create("service", password="first")
    vault.save_entry(entry)
    record = vault.path / "records" / f"{entry.id}.gpg"
    old_ciphertext = record.read_bytes()

    entry.password = "second"
    entry.revision += 1
    vault.save_entry(entry)
    record.write_bytes(old_ciphertext)

    with pytest.raises(VaultError, match="ciphertext hash mismatch"):
        vault.get_entry(entry.id)


def test_record_payload_uuid_must_match_filename(tmp_path: Path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    first = Entry.create("first")
    second = Entry.create("second")
    vault.save_entry(first)
    vault.save_entry(second)
    first_path = vault.path / "records" / f"{first.id}.gpg"
    second_path = vault.path / "records" / f"{second.id}.gpg"
    first_path.write_bytes(second_path.read_bytes())
    # Make the catalog hash match the swapped ciphertext to exercise the UUID check.
    catalog = vault.load_catalog()
    item = next(i for i in catalog.items if i.id == first.id)
    import hashlib
    item.ciphertext_sha256 = hashlib.sha256(first_path.read_bytes()).hexdigest()
    vault._write_catalog(catalog)
    with pytest.raises(VaultError, match="Record id mismatch"):
        vault.get_entry(first.id)


def test_atomic_write_failure_preserves_old_ciphertext_and_cleans_temp(tmp_path: Path, monkeypatch):
    target = tmp_path / "record.gpg"
    target.write_bytes(b"old")

    def fail_replace(src, dst):
        raise OSError("injected replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="injected replace failure"):
        atomic_write_ciphertext(target, b"new")
    assert target.read_bytes() == b"old"
    assert not list(tmp_path.glob(".*.*.tmp"))


def test_parsers_survive_deterministic_garbage_inputs():
    rng = random.Random(117)
    alphabet = string.printable
    parsers = [Entry.from_bytes, FolderStore.from_bytes, Catalog.from_bytes]
    for _ in range(300):
        raw = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 200))).encode("utf-8")
        for parser in parsers:
            try:
                parser(raw)
            except (ValueError, TypeError, KeyError, UnicodeDecodeError, AttributeError):
                pass


def test_signature_policy_requires_a_signer(tmp_path: Path):
    from keys_ng.storage.config import VaultConfig
    with pytest.raises(VaultError, match="signing key"):
        VaultConfig(["RECIPIENT"], None, [], require_signature=True).validate()
    VaultConfig(["RECIPIENT"], None, [], require_signature=False).validate()


def test_gpg_backend_rejects_non_full_fingerprint_without_calling_gpg():
    from keys_ng.crypto.gpg_process import GPGProcessBackend
    from keys_ng.errors import CryptoError
    backend = GPGProcessBackend(executable="definitely-not-called")
    with pytest.raises(CryptoError, match="full OpenPGP fingerprint"):
        backend.resolve_fingerprint("A" * 32)
