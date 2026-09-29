from __future__ import annotations

from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend
from keys_ng.migration.legacy_parser import parse_legacy_record
from keys_ng.models import Action, Entry
from keys_ng.storage.vault import Vault


def _legacy_kind(path: Path) -> tuple[str, str]:
    name = path.name
    for suffix, kind in (("_sites", "website"), ("_cmd", "command"), ("_account", "account")):
        if name.endswith(suffix):
            return name[: -len(suffix)], kind
    return name, "account"


def migrate_legacy_tree(source: Path, vault: Vault, crypto: CryptoBackend, dry_run: bool = False, verify: bool = False) -> list[tuple[Path, str]]:
    results: list[tuple[Path, str]] = []
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        title, kind = _legacy_kind(path)
        try:
            decrypted = crypto.decrypt(path.read_bytes()).plaintext.decode("utf-8")
            values = parse_legacy_record(decrypted)
            relative_dirs = list(path.relative_to(source).parts[:-1])
            tags = relative_dirs
            folder_id = None
            if relative_dirs and not dry_run:
                folder = vault.create_folder_path("/".join(relative_dirs))
                folder_id = folder.id if folder else None
            actions: list[Action] = []
            target = values.get("target", "")
            if kind == "website" and target:
                actions.append(Action(type="url", url=target))
            elif kind == "command" and values.get("comando"):
                command = values["comando"].strip()
                # Preserve legacy semantics as data, not as a shell expression.
                argv = [command]
                if target:
                    argv.append(target)
                actions.append(Action(type="command", argv=argv, shell=False))
            entry = Entry.create(
                title=title,
                kind=kind,
                usernames=[values["user"]] if values.get("user") else [],
                password=values.get("password"),
                actions=actions,
                tags=tags,
                notes=values.get("note", ""),
                folder_id=folder_id,
            )
            if not dry_run:
                vault.save_entry(entry)
                if verify:
                    restored = vault.get_entry(entry.id)
                    if restored.to_bytes() != entry.to_bytes():
                        raise ValueError("post-migration verification failed")
            results.append((path, "ok"))
        except Exception as exc:  # migration must report per-file failures, not abort the tree
            results.append((path, f"error: {exc}"))
    return results
