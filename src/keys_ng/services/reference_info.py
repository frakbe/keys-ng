"""Metadata-only descriptions of credential references; never return secret values."""
from __future__ import annotations

from dataclasses import dataclass

from keys_ng.errors import ReferenceError
from keys_ng.services.references import parse_entry_reference


@dataclass(frozen=True)
class ReferenceHop:
    entry_id: str
    field: str
    title: str
    path: str


@dataclass(frozen=True)
class ReferenceInfo:
    hops: tuple[ReferenceHop, ...] = ()
    error: str = ""


def inspect_reference(vault, value: str | None, *, source=None) -> ReferenceInfo:
    """Follow at most 32 field references, retaining only identity metadata.

    An optional unsaved source entry overrides its stored counterpart, so editor
    previews detect cycles involving the current draft. Backend exception text
    is deliberately not included in the UI description.
    """
    hops = []
    seen = set()
    if vault.locked:
        return ReferenceInfo(error="locked")
    paths = None
    while True:
        try:
            ref = parse_entry_reference(value)
        except ReferenceError:
            return ReferenceInfo(tuple(hops), "invalid")
        if ref is None:
            if value and value.strip().startswith("{REF:"):
                return ReferenceInfo(tuple(hops), "invalid")
            return ReferenceInfo(tuple(hops), "empty" if hops and not value else "")
        key = (ref.entry_id, ref.field)
        if key in seen:
            return ReferenceInfo(tuple(hops), "cycle")
        if len(hops) >= 32:
            return ReferenceInfo(tuple(hops), "depth")
        seen.add(key)
        try:
            if paths is None:
                paths = vault.folder_paths(catalog_snapshot=True)
            target = source if source is not None and source.id == ref.entry_id else vault.get_entry(ref.entry_id)
        except Exception:  # noqa: BLE001 — report unavailable metadata without leaking backend details
            # Distinguish a missing record from an unreadable or untrusted one.
            try:
                exists = any(item.id == ref.entry_id for item in vault.list_items())
            except Exception:  # noqa: BLE001 — report unavailable metadata without leaking backend details
                exists = True
            return ReferenceInfo(tuple(hops), "unavailable" if exists else "missing")
        hops.append(ReferenceHop(target.id, ref.field, target.title, paths.get(target.folder_id, "")))
        value = (target.usernames[0] if target.usernames else None) if ref.field == "U" else target.password
