from __future__ import annotations

import secrets
import string

DEFAULT_SYMBOLS = "!#$%&()*+,-./:;<=>?@[]^_{|}~"


def generate_password(
    length: int = 24,
    *,
    uppercase: bool = True,
    lowercase: bool = True,
    digits: bool = True,
    symbols: bool = True,
    ambiguous: bool = False,
) -> str:
    if length < 8:
        raise ValueError("Password length must be at least 8")

    groups: list[str] = []
    if lowercase:
        groups.append(string.ascii_lowercase)
    if uppercase:
        groups.append(string.ascii_uppercase)
    if digits:
        groups.append(string.digits)
    if symbols:
        groups.append(DEFAULT_SYMBOLS)
    if not groups:
        raise ValueError("At least one character class must be enabled")

    if not ambiguous:
        ambiguous_chars = set("0O1lI|`'\"")
        groups = ["".join(ch for ch in group if ch not in ambiguous_chars) for group in groups]

    if length < len(groups):
        raise ValueError("Password is too short for the requested character classes")

    chars = [secrets.choice(group) for group in groups]
    alphabet = "".join(groups)
    chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))

    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)
