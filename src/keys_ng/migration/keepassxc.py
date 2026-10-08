from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from shutil import which
import os
import sys
import base64
import binascii
import re
import subprocess
import uuid
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from keys_ng.errors import ReferenceError, VaultError
from keys_ng.models import Action, Entry, TotpConfig
from keys_ng.services.references import normalize_entry_uuid, parse_entry_reference
from keys_ng.services.totp import parse_otpauth_uri, totp_from_secret
from keys_ng.storage.vault import Vault

_MAX_XML_BYTES = 128 * 1024 * 1024
_STANDARD_KEYS = {"Title", "UserName", "Password", "URL", "Notes"}
_TOTP_KEYS = {
    "otp",
    "TimeOtp-Secret",
    "TimeOtp-Secret-Base32",
    "TimeOtp-Secret-Base64",
    "TimeOtp-Secret-Hex",
    "TimeOtp-Length",
    "TimeOtp-Period",
    "TimeOtp-Algorithm",
    "TOTP Seed",
    "TOTP Settings",
}
# Unlike the runtime parser, this expression is intentionally not anchored: an
# imported KeePassXC field may contain a UUID reference inside a longer string.
# Keys NG currently resolves whole-field U/P references at runtime, but rewriting
# embedded references here keeps UUID relationships intact for future support.
_UUID_REFERENCE_RE = re.compile(r"\{REF:([UP])@I:([0-9A-Fa-f-]{32,36})\}", re.IGNORECASE)


@dataclass(slots=True)
class KeePassXCImportReport:
    entries: int = 0
    folders: int = 0
    totp_tokens: int = 0
    custom_fields: int = 0
    skipped_recycle_bin: bool = False
    uuid_preserved: int = 0
    uuid_remapped: int = 0
    uuid_generated: int = 0
    references_found: int = 0
    references_remapped: int = 0
    references_validated: int = 0
    # (title, folder path, reasons) for entries that could not be represented fully.
    partial_entries: list[tuple[str, str, list[str]]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class _PendingEntry:
    entry: Entry
    folder_path: str
    source_uuid: str | None


def _safe_xml_root(raw: bytes) -> ET.Element:
    if len(raw) > _MAX_XML_BYTES:
        raise ValueError("KeePassXC XML export is too large")
    head = raw[:8192].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("DOCTYPE/entity declarations are not accepted in KeePassXC XML imports")
    try:
        return ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid KeePassXC XML export: {exc}") from exc


def _text(parent: ET.Element, path: str, default: str = "") -> str:
    node = parent.find(path)
    return (node.text or "") if node is not None else default


def _strings(entry_node: ET.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for node in entry_node.findall("String"):
        key = _text(node, "Key")
        value = _text(node, "Value")
        if key:
            values[key] = value
    return values


def _decode_keepass_uuid(value: str) -> str | None:
    """Convert a KeePass XML UUID to Keys NG's canonical RFC-4122 form.

    KDBX XML serializes UUID elements as base64Binary containing 16 UUID bytes.
    For robustness, canonical/32-hex UUID strings are accepted too; this is useful
    with hand-written exports and tests, but real KeePassXC XML normally uses Base64.
    """
    raw = value.strip()
    if not raw:
        return None
    try:
        return str(uuid.UUID(raw))
    except ValueError:
        pass
    try:
        decoded = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"Invalid KeePass UUID encoding: {raw!r}") from exc
    if len(decoded) != 16:
        raise ValueError("KeePass UUID must decode to exactly 16 bytes")
    return str(uuid.UUID(bytes=decoded))


def _uuid_compare_key(value: str) -> str:
    """Normalize UUIDs when possible, otherwise preserve opaque legacy test IDs."""
    raw = value.strip()
    if not raw:
        return ""
    try:
        return _decode_keepass_uuid(raw) or ""
    except ValueError:
        return raw


def _normalize_totp_algorithm(value: str) -> str:
    normalized = value.strip().upper().replace("HMAC-", "").replace("HMAC", "")
    if normalized in {"SHA1", "SHA256", "SHA512"}:
        return normalized
    return "SHA1"


def _parse_totp(fields: dict[str, str], title: str, username: str) -> list[TotpConfig]:
    otp = fields.get("otp", "").strip()
    if otp:
        try:
            if otp.lower().startswith("otpauth://"):
                return [parse_otpauth_uri(otp)]
            return [totp_from_secret(otp, issuer=title, account_name=username)]
        except ValueError:
            pass

    secret = fields.get("TimeOtp-Secret-Base32", "").strip() or fields.get("TOTP Seed", "").strip()
    if not secret:
        return []
    try:
        digits = int(fields.get("TimeOtp-Length", "6") or 6)
    except ValueError:
        digits = 6
    try:
        period = int(fields.get("TimeOtp-Period", "30") or 30)
    except ValueError:
        period = 30
    algorithm = _normalize_totp_algorithm(fields.get("TimeOtp-Algorithm", "SHA1"))
    return [totp_from_secret(secret, issuer=title, account_name=username, algorithm=algorithm, digits=digits, period=period)]


def _action_from_url(value: str, username: str) -> tuple[list[Action], str | None]:
    value = value.strip()
    if not value:
        return [], None
    parsed = urlparse(value)
    scheme = parsed.scheme.lower()
    if scheme in {"http", "https"}:
        return [Action(type="url", url=value)], None
    if scheme == "ssh" and parsed.hostname:
        return [Action(type="ssh", host=parsed.hostname, port=parsed.port, username=parsed.username or username or None)], None
    if scheme in {"rdp", "ms-rd"} and parsed.hostname:
        return [Action(type="rdp", host=parsed.hostname, port=parsed.port, username=parsed.username or username or None)], None
    return [], value


def _parse_tags(entry_node: ET.Element) -> list[str]:
    raw = _text(entry_node, "Tags").strip()
    if not raw:
        return []
    separator = ";" if ";" in raw else ","
    return [part.strip() for part in raw.split(separator) if part.strip()]


def _entry_from_xml(entry_node: ET.Element, report: KeePassXCImportReport) -> tuple[Entry, list[str]]:
    fields = _strings(entry_node)
    title = fields.get("Title", "").strip()
    username = fields.get("UserName", "").strip()
    password = fields.get("Password", "")
    url = fields.get("URL", "").strip()
    notes = fields.get("Notes", "")
    if not title:
        title = username or url or "Imported entry"

    actions, preserved_url = _action_from_url(url, username)
    totp = _parse_totp(fields, title, username)
    custom = {
        key: value
        for key, value in fields.items()
        if key not in _STANDARD_KEYS and key not in _TOTP_KEYS
    }
    if preserved_url:
        custom.setdefault("Imported URL", preserved_url)

    partial_reasons: list[str] = []
    note_blocks = [notes.rstrip()] if notes.rstrip() else []
    if preserved_url:
        note_blocks.append("[Imported KeePassXC command/URL not converted]\n" + preserved_url)
        partial_reasons.append("command or URL stored in Notes instead of an action")

    # KeePassXC permits arbitrary custom fields. Preserve command-like fields in
    # Notes as well, because the normal Keys NG editor does not expose all of
    # KeePassXC's command/action extensions.
    for key, value in custom.items():
        normalized_key = re.sub(r"[^a-z0-9]+", "", key.casefold())
        is_command_field = (
            "command" in normalized_key
            or normalized_key in {"exec", "executable", "execcommand", "commandline"}
        )
        if is_command_field and value.strip():
            note_blocks.append(f"[Imported KeePassXC field: {key}]\n{value}")
            partial_reasons.append(f"custom command field '{key}' preserved in Notes")

    notes = "\n\n".join(note_blocks)
    report.custom_fields += len(custom)
    report.totp_tokens += len(totp)

    return Entry.create(
        title=title,
        usernames=[username] if username else [],
        password=password if password != "" else None,
        actions=actions,
        tags=_parse_tags(entry_node),
        notes=notes,
        custom_fields=custom,
        totp=totp,
        folder_id=None,
    ), partial_reasons


def _new_unique_uuid(reserved: set[str]) -> str:
    while True:
        candidate = str(uuid.uuid4())
        if candidate not in reserved:
            reserved.add(candidate)
            return candidate


def _rewrite_reference_text(value: str | None, uuid_map: dict[str, str], report: KeePassXCImportReport) -> str | None:
    if value is None or "{REF:" not in value.upper():
        return value

    def replace(match: re.Match[str]) -> str:
        field_name, raw_uuid = match.groups()
        try:
            source_id = normalize_entry_uuid(raw_uuid)
        except ReferenceError:
            return match.group(0)
        target_id = uuid_map.get(source_id, source_id)
        report.references_found += 1
        if target_id != source_id:
            report.references_remapped += 1
        return f"{{REF:{field_name.upper()}@I:{target_id}}}"

    return _UUID_REFERENCE_RE.sub(replace, value)


def _rewrite_entry_references(entry: Entry, uuid_map: dict[str, str], report: KeePassXCImportReport) -> None:
    entry.title = _rewrite_reference_text(entry.title, uuid_map, report) or entry.title
    entry.usernames = [(_rewrite_reference_text(value, uuid_map, report) or "") for value in entry.usernames]
    entry.password = _rewrite_reference_text(entry.password, uuid_map, report)
    entry.notes = _rewrite_reference_text(entry.notes, uuid_map, report) or ""
    entry.custom_fields = {
        key: (_rewrite_reference_text(value, uuid_map, report) or "")
        for key, value in entry.custom_fields.items()
    }
    for action in entry.actions:
        action.username = _rewrite_reference_text(action.username, uuid_map, report)
        action.url = _rewrite_reference_text(action.url, uuid_map, report)
        action.argv = [(_rewrite_reference_text(value, uuid_map, report) or "") for value in action.argv]
        action.ssh_options = [(_rewrite_reference_text(value, uuid_map, report) or "") for value in action.ssh_options]


def _validate_import_references(pending: list[_PendingEntry], vault: Vault, report: KeePassXCImportReport) -> None:
    """Resolve every whole-field imported U/P reference before any record is saved."""
    planned = {item.entry.id: item.entry for item in pending}
    existing_ids = {item.id for item in vault.list_items()}
    checked: set[tuple[str, str]] = set()

    def load_entry(entry_id: str) -> Entry:
        if entry_id in planned:
            return planned[entry_id]
        if entry_id in existing_ids:
            return vault.get_entry(entry_id)
        raise ValueError(f"KeePassXC import contains a dangling reference to UUID {entry_id}")

    def resolve(value: str | None, stack: tuple[tuple[str, str], ...] = ()) -> str | None:
        ref = parse_entry_reference(value)
        if ref is None:
            return value
        key = (ref.entry_id, ref.field)
        if key in stack:
            chain = " -> ".join(f"{entry_id}:{field}" for entry_id, field in (*stack, key))
            raise ValueError(f"KeePassXC import contains a reference cycle: {chain}")
        target = load_entry(ref.entry_id)
        raw = (target.usernames[0] if target.usernames else None) if ref.field == "U" else target.password
        if raw is None:
            raise ValueError(f"KeePassXC reference target {ref.entry_id} has an empty {ref.field_name}")
        checked.add(key)
        return resolve(raw, (*stack, key))

    for item in pending:
        entry = item.entry
        if entry.usernames:
            resolve(entry.usernames[0])
        resolve(entry.password)
        for action in entry.actions:
            resolve(action.username)
    report.references_validated = len(checked)


def import_keepassxc_xml(raw: bytes, vault: Vault, *, dry_run: bool = False) -> KeePassXCImportReport:
    """Import KeePassXC XML using UUID-preserving, reference-safe two-pass migration.

    Pass 1 collects the entire source tree and source UUIDs. Pass 2 assigns target
    UUIDs, rewrites all UUID references, validates whole-field U/P reference chains,
    and only then writes folders/entries to the destination vault.
    """
    root = _safe_xml_root(raw)
    if root.tag != "KeePassFile":
        raise ValueError("Not a KeePass/KeePassXC XML export")
    root_group = root.find("./Root/Group")
    if root_group is None:
        raise ValueError("KeePassXC XML export has no root group")

    recycle_raw = _text(root, "./Meta/RecycleBinUUID").strip()
    recycle_key = _uuid_compare_key(recycle_raw)
    report = KeePassXCImportReport()
    pending: list[_PendingEntry] = []
    source_seen: set[str] = set()

    def collect_group(group_node: ET.Element, parent_path: str, create_folder: bool) -> None:
        group_raw_uuid = _text(group_node, "UUID").strip()
        group_key = _uuid_compare_key(group_raw_uuid)
        if recycle_key and group_key and group_key == recycle_key:
            report.skipped_recycle_bin = True
            return

        group_name = _text(group_node, "Name").strip() or "Imported"
        path = parent_path
        if create_folder:
            path = f"{parent_path}/{group_name}" if parent_path else group_name
            report.folders += 1

        for entry_node in group_node.findall("Entry"):
            entry, partial_reasons = _entry_from_xml(entry_node, report)
            source_raw = _text(entry_node, "UUID").strip()
            source_uuid = _decode_keepass_uuid(source_raw) if source_raw else None
            if source_uuid:
                if source_uuid in source_seen:
                    raise ValueError(f"KeePassXC XML contains duplicate entry UUID {source_uuid}")
                source_seen.add(source_uuid)
            pending.append(_PendingEntry(entry=entry, folder_path=path, source_uuid=source_uuid))
            if partial_reasons:
                report.partial_entries.append((entry.title, path, partial_reasons))
            report.entries += 1

        for child in group_node.findall("Group"):
            collect_group(child, path, True)

    collect_group(root_group, "", False)

    # Assign every destination UUID before examining references. Source UUIDs are
    # preserved whenever possible; collisions with existing Keys NG records get a
    # fresh UUID, and references to that source UUID are rewritten to the fresh ID.
    reserved = {item.id for item in vault.list_items()}
    uuid_map: dict[str, str] = {}
    for item in pending:
        if item.source_uuid:
            if item.source_uuid not in reserved:
                target_uuid = item.source_uuid
                reserved.add(target_uuid)
                report.uuid_preserved += 1
            else:
                target_uuid = _new_unique_uuid(reserved)
                report.uuid_remapped += 1
                report.warnings.append(
                    f"KeePassXC UUID collision {item.source_uuid}; imported entry remapped to {target_uuid}."
                )
            uuid_map[item.source_uuid] = target_uuid
            item.entry.id = target_uuid
        else:
            # Some old/hand-written XML exports omit UUID. Such entries remain
            # importable, but cannot be the target of KeePass UUID references.
            item.entry.id = _new_unique_uuid(reserved)
            report.uuid_generated += 1

    for item in pending:
        _rewrite_entry_references(item.entry, uuid_map, report)

    # Validate before writing to prevent an apparently successful import with
    # broken credential references. Existing destination entries may be valid
    # external reference targets, so they are included in resolution.
    _validate_import_references(pending, vault, report)

    if not dry_run:
        folder_ids: dict[str, str | None] = {"": None}
        for item in pending:
            if item.folder_path not in folder_ids:
                folder = vault.create_folder_path(item.folder_path)
                folder_ids[item.folder_path] = folder.id if folder else None
            item.entry.folder_id = folder_ids[item.folder_path]
            vault.save_entry(item.entry)

        # Final validation uses the actual encrypted records, exercising the same
        # resolver used later by CLI/TUI/GUI. It should only fail if a write or
        # serialization bug escaped the preflight pass.
        for item in pending:
            entry = vault.get_entry(item.entry.id)
            if entry.usernames and parse_entry_reference(entry.usernames[0]):
                vault.resolved_username(entry)
            if parse_entry_reference(entry.password):
                vault.resolved_password(entry)
            for action in entry.actions:
                if parse_entry_reference(action.username):
                    vault.resolved_action(entry, action)

    if root.find(".//Binary") is not None:
        report.warnings.append("Attachments/custom binaries are not imported by Keys NG yet.")
    if root.find(".//History") is not None:
        report.warnings.append("KeePass entry history is not imported; only the current entry version is migrated.")
    return report


def export_kdbx_to_xml(
    database: str | Path,
    *,
    key_file: str | Path | None = None,
    no_password: bool = False,
    yubikey: str | None = None,
    keepassxc_cli: str | None = None,
    password: str | None = None,
) -> bytes:
    executable = keepassxc_cli or which("keepassxc-cli") or which("keepassxc-cli.exe")
    if not executable:
        candidates: list[Path] = []
        if os.name == "nt":
            for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
                base = os.environ.get(env_name)
                if base:
                    candidates.append(Path(base) / "KeePassXC" / "keepassxc-cli.exe")
        elif sys.platform == "darwin":
            candidates.append(Path("/Applications/KeePassXC.app/Contents/MacOS/keepassxc-cli"))
        executable = next((str(path) for path in candidates if path.is_file()), None)
    if not executable:
        raise RuntimeError("keepassxc-cli was not found; install KeePassXC or import an XML export instead")
    argv = [str(executable), "export", "--format", "xml"]
    if key_file:
        argv.extend(["--key-file", str(Path(key_file).expanduser())])
    if no_password:
        argv.append("--no-password")
    if yubikey:
        argv.extend(["--yubikey", yubikey])
    argv.append(str(Path(database).expanduser()))

    # CLI callers may still let keepassxc-cli own its terminal prompt. Interactive
    # GUI/TUI frontends can supply a password that exists only transiently in RAM;
    # it is sent over stdin and is never placed in argv, environment or a file.
    if password is None:
        process = subprocess.Popen(argv, stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
    else:
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        payload = (password + "\n").encode("utf-8")
        stdout, _ = process.communicate(payload)
    if process.returncode != 0:
        raise RuntimeError(f"keepassxc-cli export failed with exit status {process.returncode}")
    if not stdout:
        raise RuntimeError("keepassxc-cli returned an empty export")
    return stdout


def import_keepassxc(
    source: str | Path,
    vault: Vault,
    *,
    source_format: str = "auto",
    key_file: str | Path | None = None,
    no_password: bool = False,
    yubikey: str | None = None,
    dry_run: bool = False,
    password: str | None = None,
) -> KeePassXCImportReport:
    path = Path(source).expanduser()
    fmt = source_format.lower()
    if fmt == "auto":
        fmt = "kdbx" if path.suffix.lower() == ".kdbx" else "xml"
    if fmt == "kdbx":
        raw = export_kdbx_to_xml(path, key_file=key_file, no_password=no_password, yubikey=yubikey, password=password)
    elif fmt == "xml":
        raw = path.read_bytes()
    else:
        raise ValueError("KeePassXC import format must be auto, kdbx, or xml")
    return import_keepassxc_xml(raw, vault, dry_run=dry_run)


def format_import_report(report: KeePassXCImportReport) -> str:
    """Render a concise, frontend-neutral KeePassXC import summary."""
    lines = [
        f"Entries: {report.entries}",
        f"Folders: {report.folders}",
        f"TOTP tokens: {report.totp_tokens}",
        f"Custom fields: {report.custom_fields}",
        f"UUID preserved/remapped/generated: {report.uuid_preserved}/{report.uuid_remapped}/{report.uuid_generated}",
        f"References found/remapped/validated: {report.references_found}/{report.references_remapped}/{report.references_validated}",
    ]
    if report.skipped_recycle_bin:
        lines.append("Recycle bin: skipped")
    if report.partial_entries:
        lines.append(f"Partially imported entries: {len(report.partial_entries)}")
        for title, folder, reasons in report.partial_entries:
            location = f"{title} [{folder}]" if folder else title
            lines.append(f"- {location}: {'; '.join(reasons)}")
    if report.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report.warnings)
    return "\n".join(lines)
