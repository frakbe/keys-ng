from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time
from urllib.parse import parse_qs, quote, unquote, urlparse

from keys_ng.models import TotpConfig

_HASHES = {"SHA1": hashlib.sha1, "SHA256": hashlib.sha256, "SHA512": hashlib.sha512}


def _decode_base32(secret: str) -> bytes:
    compact = "".join(secret.split()).upper()
    padding = "=" * ((8 - len(compact) % 8) % 8)
    return base64.b32decode(compact + padding, casefold=True)



def totp_from_secret(
    secret: str,
    *,
    issuer: str = "",
    account_name: str = "",
    algorithm: str = "SHA1",
    digits: int = 6,
    period: int = 30,
) -> TotpConfig:
    """Build and validate a TOTP configuration from a raw Base32 secret."""
    normalized = "".join(secret.split()).upper()
    if not normalized:
        raise ValueError("TOTP secret is empty")
    try:
        _decode_base32(normalized)
    except Exception as exc:
        raise ValueError("Invalid Base32 TOTP secret") from exc
    config = TotpConfig(
        secret=normalized,
        issuer=issuer.strip(),
        account_name=account_name.strip(),
        algorithm=algorithm.upper(),
        digits=digits,
        period=period,
    )
    config.validate()
    return config

def generate_totp(config: TotpConfig, at_time: int | float | None = None) -> tuple[str, int]:
    config.validate()
    now = int(time.time() if at_time is None else at_time)
    counter = now // config.period
    key = _decode_base32(config.secret)
    digest = hmac.new(key, struct.pack(">Q", counter), _HASHES[config.algorithm.upper()]).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    code = str(binary % (10**config.digits)).zfill(config.digits)
    remaining = config.period - (now % config.period)
    return code, remaining


def parse_otpauth_uri(uri: str) -> TotpConfig:
    parsed = urlparse(uri)
    if parsed.scheme != "otpauth" or parsed.netloc.lower() != "totp":
        raise ValueError("Only otpauth://totp URIs are supported")
    params = parse_qs(parsed.query)
    secret = params.get("secret", [""])[0]
    if not secret:
        raise ValueError("Missing TOTP secret")
    label = unquote(parsed.path.lstrip("/"))
    issuer_from_label, sep, account = label.partition(":")
    issuer = params.get("issuer", [issuer_from_label if sep else ""])[0]
    account_name = account if sep else label
    config = TotpConfig(
        secret=secret,
        issuer=issuer,
        account_name=account_name,
        algorithm=params.get("algorithm", ["SHA1"])[0].upper(),
        digits=int(params.get("digits", ["6"])[0]),
        period=int(params.get("period", ["30"])[0]),
    )
    config.validate()
    return config


def build_otpauth_uri(config: TotpConfig) -> str:
    config.validate()
    label = f"{config.issuer}:{config.account_name}" if config.issuer else config.account_name
    params = [
        f"secret={quote(config.secret)}",
        f"algorithm={quote(config.algorithm.upper())}",
        f"digits={config.digits}",
        f"period={config.period}",
    ]
    if config.issuer:
        params.append(f"issuer={quote(config.issuer)}")
    return f"otpauth://totp/{quote(label)}?{'&'.join(params)}"
