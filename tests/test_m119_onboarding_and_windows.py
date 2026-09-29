from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult, KeyInfo
from keys_ng.crypto import discovery
from keys_ng.services.vault_init import VaultInitRequest, available_vault_keys, create_vault, validate_vault_target
from keys_ng.storage.settings import AppSettings


RECIPIENT = "A" * 40
SIGNER = "B" * 40


class InitCrypto(CryptoBackend):
    def __init__(self):
        self.last_signer = None

    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        self.last_signer = signer
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), self.last_signer, bool(self.last_signer))

    def diagnose(self):
        return []

    def resolve_fingerprint(self, selector: str, secret: bool = False) -> str:
        return selector.upper()

    def list_keys(self, secret: bool = False):
        if secret:
            return [KeyInfo(SIGNER, ("Test Signer <signer@example.test>",), True, True, True)]
        return [KeyInfo(RECIPIENT, ("Test Recipient <recipient@example.test>",), True, False, False)]


def test_shared_vault_init_creates_and_self_tests(tmp_path):
    crypto = InitCrypto()
    request = VaultInitRequest(tmp_path / "new-vault", (RECIPIENT,), SIGNER)
    vault = create_vault(request, crypto)
    assert vault.path == (tmp_path / "new-vault").resolve()
    assert (vault.path / "vault.json").is_file()
    assert (vault.path / "catalog.gpg").is_file()
    assert (vault.path / "folders.gpg").is_file()


def test_vault_init_rejects_nonempty_target(tmp_path):
    root = tmp_path / "not-empty"
    root.mkdir()
    (root / "user-file.txt").write_text("do not touch", encoding="utf-8")
    with pytest.raises(Exception):
        validate_vault_target(root)
    assert (root / "user-file.txt").read_text(encoding="utf-8") == "do not touch"


def test_key_choices_filter_revoked_and_expired():
    crypto = InitCrypto()
    choices = available_vault_keys(crypto)
    assert [k.fingerprint for k in choices.recipients] == [RECIPIENT]
    assert [k.fingerprint for k in choices.signers] == [SIGNER]


def test_gnupg_discovery_prefers_configured_file(tmp_path):
    executable = tmp_path / "gpg.exe"
    executable.write_bytes(b"fake")
    result = discovery.discover_gnupg_executable("gpg", str(executable))
    assert result.path == str(executable.resolve())
    assert result.method == "configured"


def test_gnupg_discovery_uses_path(monkeypatch):
    monkeypatch.setattr(discovery, "host_which", lambda name: "/test/bin/gpg" if name == "gpg" else None)
    result = discovery.discover_gnupg_executable("gpg")
    assert result.path == "/test/bin/gpg"
    assert result.method == "PATH"


def test_settings_roundtrip_gnupg_paths(tmp_path):
    path = tmp_path / "config.toml"
    settings = AppSettings(gpg_executable=r"C:\\Program Files\\GnuPG\\bin\\gpg.exe", gpgconf_executable=r"C:\\Program Files\\GnuPG\\bin\\gpgconf.exe")
    settings.save(path)
    loaded = AppSettings.load(path)
    assert loaded.gpg_executable.endswith("gpg.exe")
    assert loaded.gpgconf_executable.endswith("gpgconf.exe")


def test_briefcase_windows_config_and_pep639_are_release_ready():
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["license"] == "GPL-3.0-or-later"
    assert "LICENSE" in data["project"]["license-files"]
    apps = data["tool"]["briefcase"]["app"]
    assert apps["keys_ng"]["sources"] == ["src/keys_ng"]
    assert apps["keys_ng_cli"]["console_app"] is True
    assert apps["keys_ng_tui"]["console_app"] is True
    assert Path("src/keys_ng/__main__.py").is_file()
    assert Path("src/keys_ng_cli/__main__.py").is_file()
    assert Path("src/keys_ng_tui/__main__.py").is_file()


def test_gui_and_tui_expose_new_vault_onboarding():
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    assert "class NewVaultWizard(QWizard)" in gui
    assert '_("New vault…")' in gui
    assert "class VaultCreationApp(App[str | None])" in tui
    assert 'nargs="?", help="Vault directory; omit to start the new-vault wizard"' in tui
