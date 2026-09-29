from keys_ng.cli import main as cli
from keys_ng.crypto.backend import CryptoBackend, DecryptionResult


class CliFakeCrypto(CryptoBackend):
    def __init__(self):
        self.signer = None

    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        self.signer = signer
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), self.signer, True)

    def diagnose(self):
        return []

    def resolve_fingerprint(self, selector: str, secret: bool = False) -> str:
        return selector


def test_init_does_not_shadow_gettext_alias(tmp_path, monkeypatch, capsys):
    crypto = CliFakeCrypto()
    monkeypatch.setattr(cli, "_crypto", lambda: crypto)
    args = cli.build_parser().parse_args([
        "init",
        str(tmp_path / "vault"),
        "--recipient", "A" * 40,
        "--signer", "B" * 40,
        "--catalog-privacy", "standard",
    ])

    assert cli.run(args) == 0
    assert "Vault initialized." in capsys.readouterr().out
