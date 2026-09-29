from __future__ import annotations

import gettext
import locale
from pathlib import Path

_DOMAIN = "keys-ng"
_translation: gettext.NullTranslations = gettext.NullTranslations()
_current_language = "en"


def _locales_dir() -> Path:
    # During development locales live at repository root; installed builds may
    # vendor compiled catalogs under keys_ng/i18n/locales.
    package_dir = Path(__file__).resolve().parent
    bundled = package_dir / "locales"
    if bundled.exists():
        return bundled
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "locales"
        if candidate.exists():
            return candidate
    return bundled


def _language_code(value: str | None) -> str:
    if not value:
        return "en"
    return value.replace("-", "_").split("_", 1)[0].lower() or "en"


def configure_language(language: str | None = None) -> None:
    global _translation, _current_language
    languages = None
    if language and language != "auto":
        languages = [language]
        _current_language = _language_code(language)
    else:
        detected = locale.getlocale()[0]
        languages = [detected] if detected else None
        _current_language = _language_code(detected)
    _translation = gettext.translation(_DOMAIN, localedir=_locales_dir(), languages=languages, fallback=True)


def current_language() -> str:
    return _current_language


def _(message: str) -> str:
    return _translation.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    return _translation.ngettext(singular, plural, n)


def pgettext(context: str, message: str) -> str:
    fn = getattr(_translation, "pgettext", None)
    return fn(context, message) if fn else message
