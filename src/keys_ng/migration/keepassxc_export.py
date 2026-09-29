from __future__ import annotations

import base64
from pathlib import Path
import re
import uuid
import xml.etree.ElementTree as ET

from keys_ng.models import Action, Entry, Folder
from keys_ng.services.references import parse_entry_reference
from keys_ng.services.ssh_options import format_ssh_options
from keys_ng.services.totp import build_otpauth_uri
from keys_ng.storage.vault import Vault

_REF_RE = re.compile(r"\{REF:([UP])@I:([0-9A-Fa-f-]{32,36})\}", re.IGNORECASE)


def _keepass_uuid(value: str) -> str:
    """Encode an RFC-4122 UUID as KeePass XML's base64Binary UUID."""
    return base64.b64encode(uuid.UUID(value).bytes).decode("ascii")


def _reference_to_keepass(value: str | None) -> str:
    if not value:
        return value or ""

    def repl(match: re.Match[str]) -> str:
        field, raw_uuid = match.groups()
        canonical = uuid.UUID(raw_uuid)
        return f"{{REF:{field.upper()}@I:{canonical.hex.upper()}}}"

    return _REF_RE.sub(repl, value)


def _add_string(parent: ET.Element, key: str, value: str, *, protected: bool = False) -> None:
    string = ET.SubElement(parent, "String")
    ET.SubElement(string, "Key").text = key
    value_node = ET.SubElement(string, "Value")
    if protected:
        value_node.set("Protected", "False")
    value_node.text = value


def _action_url(action: Action | None) -> str:
    if action is None:
        return ""
    if action.type == "url":
        return action.url or ""
    if action.type in {"ssh", "rdp"} and action.host:
        scheme = "ssh" if action.type == "ssh" else "rdp"
        port = f":{action.port}" if action.port else ""
        return f"{scheme}://{action.host}{port}"
    return ""


def _entry_xml(entry: Entry, vault: Vault, *, resolve_references: bool) -> ET.Element:
    node = ET.Element("Entry")
    ET.SubElement(node, "UUID").text = _keepass_uuid(entry.id)
    if entry.tags:
        ET.SubElement(node, "Tags").text = ";".join(entry.tags)

    raw_username = entry.usernames[0] if entry.usernames else ""
    raw_password = entry.password or ""
    if resolve_references:
        username = vault.resolved_username(entry) or ""
        password = vault.resolved_password(entry) or ""
    else:
        username = _reference_to_keepass(raw_username)
        password = _reference_to_keepass(raw_password)

    primary = entry.actions[0] if entry.actions else None
    _add_string(node, "Title", entry.title)
    _add_string(node, "UserName", username)
    _add_string(node, "Password", password, protected=True)
    _add_string(node, "URL", _action_url(primary))
    _add_string(node, "Notes", entry.notes)

    if entry.totp:
        _add_string(node, "otp", build_otpauth_uri(entry.totp[0]), protected=True)

    for key, value in sorted(entry.custom_fields.items()):
        if key not in {"Title", "UserName", "Password", "URL", "Notes", "otp"}:
            _add_string(node, key, _reference_to_keepass(value) if not resolve_references else value)

    # Preserve Keys NG-specific action details as ordinary KeePassXC custom fields.
    if primary:
        _add_string(node, "KeysNG Action Type", primary.type)
        if primary.type == "ssh":
            _add_string(node, "KeysNG SSH X11", primary.ssh_x11_forwarding)
            if primary.ssh_options:
                _add_string(node, "KeysNG SSH Options", format_ssh_options(primary.ssh_options))
        if primary.username and primary.username != raw_username:
            action_user = primary.username
            if not resolve_references:
                action_user = _reference_to_keepass(action_user)
            _add_string(node, "KeysNG Action Username", action_user)
        if primary.type == "command" and primary.argv:
            _add_string(node, "KeysNG Command argv", "\n".join(primary.argv))

    return node


def _new_group(name: str, group_id: str | None = None) -> ET.Element:
    node = ET.Element("Group")
    ET.SubElement(node, "UUID").text = _keepass_uuid(group_id or str(uuid.uuid4()))
    ET.SubElement(node, "Name").text = name
    ET.SubElement(node, "IsExpanded").text = "True"
    return node


def _document(root_group: ET.Element, database_name: str) -> bytes:
    root = ET.Element("KeePassFile")
    meta = ET.SubElement(root, "Meta")
    ET.SubElement(meta, "Generator").text = "Keys NG"
    ET.SubElement(meta, "DatabaseName").text = database_name
    ET.SubElement(meta, "DatabaseDescription").text = "Exported by Keys NG"
    ET.SubElement(meta, "RecycleBinEnabled").text = "False"
    root_node = ET.SubElement(root, "Root")
    root_node.append(root_group)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def export_entry_xml(vault: Vault, entry_id: str) -> bytes:
    """Export one entry as a standalone KeePass/KeePassXC XML document.

    Credential references are resolved because their target entries are not part
    of a single-entry export.
    """
    entry = vault.get_entry(entry_id)
    group = _new_group("Keys NG Export")
    group.append(_entry_xml(entry, vault, resolve_references=True))
    return _document(group, entry.title)


def export_vault_xml(vault: Vault) -> bytes:
    """Export the complete vault hierarchy as KeePass/KeePassXC XML.

    Entry UUIDs are preserved, so Keys NG UUID references can be translated to
    KeePassXC UUID-reference syntax without resolving shared credentials.
    """
    root_group = _new_group(vault.path.name or "Keys NG")
    folders = vault.list_folders()
    group_by_id: dict[str, ET.Element] = {}
    remaining = list(folders)
    while remaining:
        progress = False
        for folder in list(remaining):
            if folder.parent_id is None or folder.parent_id in group_by_id:
                node = _new_group(folder.name, folder.id)
                parent = group_by_id.get(folder.parent_id, root_group)
                parent.append(node)
                group_by_id[folder.id] = node
                remaining.remove(folder)
                progress = True
        if not progress:
            raise ValueError("Folder hierarchy is inconsistent")

    for item in vault.list_items():
        entry = vault.get_entry(item.id)
        parent = group_by_id.get(entry.folder_id, root_group)
        parent.append(_entry_xml(entry, vault, resolve_references=False))

    return _document(root_group, vault.path.name or "Keys NG")


def write_export(path: str | Path, raw: bytes) -> Path:
    """Write a plaintext XML export with restrictive permissions where possible."""
    import os

    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    if os.name != "nt":
        os.chmod(destination, 0o600)
    return destination
