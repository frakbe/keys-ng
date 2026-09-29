from __future__ import annotations

import re

from keys_ng.errors import LegacyFormatError

_ALLOWED = {"target", "user", "password", "note", "comando"}
_ASSIGNMENT = re.compile(r"^(target|user|password|note|comando)='((?:[^'\\]|\\.)*)'$", re.DOTALL)


def _unescape_single_quoted_legacy(value: str) -> str:
    # Keys 1.0.1 normally wrote raw form values between single quotes. We accept
    # only backslash escapes for a quote or backslash; no expansion is performed.
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "\\":
            if i + 1 >= len(value) or value[i + 1] not in {"\\", "'"}:
                raise LegacyFormatError("Unsupported escape sequence in legacy record")
            out.append(value[i + 1])
            i += 2
        else:
            out.append(value[i])
            i += 1
    return "".join(out)


def parse_legacy_record(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        match = _ASSIGNMENT.fullmatch(line)
        if not match:
            raise LegacyFormatError(f"Unsupported legacy syntax on line {lineno}")
        key, raw_value = match.groups()
        if key not in _ALLOWED or key in values:
            raise LegacyFormatError(f"Invalid or duplicate field on line {lineno}")
        values[key] = _unescape_single_quoted_legacy(raw_value)
    if not values:
        raise LegacyFormatError("Legacy record is empty")
    return values
