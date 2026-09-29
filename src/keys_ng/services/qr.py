from __future__ import annotations

from pathlib import Path

from keys_ng.models import TotpConfig
from keys_ng.services.totp import parse_otpauth_uri


class QRUnavailable(RuntimeError):
    pass


def _decode_image(image) -> TotpConfig:
    try:
        import zxingcpp
    except ImportError as exc:
        raise QRUnavailable("QR import requires the optional 'qr' dependency (zxing-cpp)") from exc
    barcode = zxingcpp.read_barcode(image, formats=zxingcpp.BarcodeFormat.QRCode)
    if barcode is None:
        raise ValueError("No QR code found")
    text = barcode.text.strip()
    if not text.startswith("otpauth://totp/"):
        raise ValueError("QR code does not contain a TOTP otpauth URI")
    return parse_otpauth_uri(text)


def parse_totp_qr_file(path: str | Path) -> TotpConfig:
    try:
        from PIL import Image
    except ImportError as exc:
        raise QRUnavailable("QR import from files requires Pillow") from exc
    with Image.open(Path(path)) as image:
        return _decode_image(image.convert("RGB"))


def parse_totp_qimage(image) -> TotpConfig:
    return _decode_image(image)
