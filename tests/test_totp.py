from keys_ng.models import TotpConfig
from keys_ng.services.totp import generate_totp, parse_otpauth_uri


def test_rfc6238_sha1_vector():
    # RFC 6238 shared secret "12345678901234567890", Base32 encoded.
    cfg = TotpConfig(secret="GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", digits=8, period=30, algorithm="SHA1")
    code, _ = generate_totp(cfg, at_time=59)
    assert code == "94287082"


def test_parse_otpauth_uri():
    cfg = parse_otpauth_uri("otpauth://totp/Example:alice?secret=JBSWY3DPEHPK3PXP&issuer=Example")
    assert cfg.issuer == "Example"
    assert cfg.account_name == "alice"


def test_totp_from_manual_secret_normalizes_and_generates():
    from keys_ng.services.totp import totp_from_secret

    cfg = totp_from_secret(
        "jbsw y3dp ehpk 3pxp",
        issuer="Example",
        account_name="alice",
    )
    assert cfg.secret == "JBSWY3DPEHPK3PXP"
    assert cfg.issuer == "Example"
    assert cfg.account_name == "alice"
    code, remaining = generate_totp(cfg, at_time=0)
    assert len(code) == 6
    assert remaining == 30


def test_totp_from_manual_secret_rejects_invalid_base32():
    from keys_ng.services.totp import totp_from_secret
    import pytest

    with pytest.raises(ValueError, match="Invalid Base32"):
        totp_from_secret("not-a-valid-secret!")
