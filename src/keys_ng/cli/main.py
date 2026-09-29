from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path
import sys
import time
import os
import tempfile

from keys_ng import __version__
from keys_ng.crypto.factory import create_crypto_backend
from keys_ng.crypto.gpg_process import GPGProcessBackend
from keys_ng.errors import KeysNGError
from keys_ng.i18n import _, configure_language
from keys_ng.migration.migrator import migrate_legacy_tree
from keys_ng.migration.keepassxc import import_keepassxc
from keys_ng.migration.keepassxc_export import export_entry_xml, export_vault_xml, write_export
from keys_ng.models import Action, Entry
from keys_ng.platform.desktop_integration import (
    desktop_integration_status,
    install_user_desktop_integration,
    uninstall_user_desktop_integration,
)
from keys_ng.services.actions import launch_action
from keys_ng.services.clipboard import copy_secret_cli
from keys_ng.services.doctor import collect_doctor_checks
from keys_ng.services.diagnostics import configure_diagnostics, get_logger
from keys_ng.services.passwords import generate_password
from keys_ng.services.qr import parse_totp_qr_file
from keys_ng.services.totp import generate_totp, parse_otpauth_uri
from keys_ng.services.vault_init import VaultInitRequest, create_vault
from keys_ng.services.ssh_options import parse_ssh_options
from keys_ng.services.trusted_signers import add_trusted_signer, list_trusted_signers, remove_trusted_signer
from keys_ng.storage.inbox import import_inbox, write_encrypted_entry
from keys_ng.storage.settings import AppSettings
from keys_ng.storage.vault import Vault


def _settings() -> AppSettings:
    return AppSettings.load()


def _crypto():
    settings = _settings()
    return create_crypto_backend(settings.crypto_backend, settings.gpg_executable, settings.gpgconf_executable)


def _vault(path: str) -> Vault:
    return Vault(path, _crypto())


def _print_items(items) -> None:
    for item in items:
        caps = ",".join(item.capabilities) or "-"
        print(f"{item.id}\t{item.title}\t{item.kind}\t{caps}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="keys-ng", description="OpenPGP password manager")
    p.add_argument("--version", action="version", version=f"Keys NG {__version__}")
    p.add_argument("--language", default=None, help="UI language (e.g. it, en) or auto")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("version", help="Show the installed Keys NG version")

    init = sub.add_parser("init", help="Initialize a vault")
    init.add_argument("vault")
    init.add_argument("--recipient", action="append", required=True, help="Full recipient fingerprint")
    init.add_argument("--signer", help="Full signer fingerprint")
    init.add_argument("--allow-unsigned", action="store_true")
    init.add_argument("--catalog-privacy", choices=["minimal", "standard", "full"], default="standard")

    keys = sub.add_parser("keys", help="List OpenPGP keys and full fingerprints")
    keys.add_argument("--secret", action="store_true")

    add = sub.add_parser("add", help="Add an entry")
    add.add_argument("vault")
    add.add_argument("--title")
    add.add_argument("--username")
    add.add_argument("--url")
    add.add_argument("--ssh-host")
    add.add_argument("--ssh-port", type=int)
    add.add_argument("--ssh-x11", choices=["off", "X", "Y"], default="off", help="SSH X11 forwarding: off, -X, or trusted -Y")
    add.add_argument("--ssh-options", default="", help="Advanced SSH options, e.g. '-J bastion -o ServerAliveInterval=30'")
    add.add_argument("--rdp-host")
    add.add_argument("--rdp-port", type=int)
    add.add_argument("--tag", action="append", default=[])
    add.add_argument("--totp-uri")
    add.add_argument("--totp-qr")
    add.add_argument("--generate-password", type=int, metavar="LENGTH")
    add.add_argument("--folder", help="Folder path, e.g. Personal/Cloud")

    edit = sub.add_parser("edit", help="Edit basic entry fields")
    edit.add_argument("vault")
    edit.add_argument("entry_id")
    edit.add_argument("--title")
    edit.add_argument("--username")
    edit.add_argument("--url")
    edit.add_argument("--ssh-x11", choices=["off", "X", "Y"], default=None, help="Update SSH X11 forwarding")
    edit.add_argument("--ssh-options", default=None, help="Update advanced SSH options")
    edit.add_argument("--folder", help="Folder path; use / for root")

    delete = sub.add_parser("delete", help="Delete an entry")
    delete.add_argument("vault")
    delete.add_argument("entry_id")

    ls = sub.add_parser("list", help="List entries")
    ls.add_argument("vault")
    search = sub.add_parser("search", help="Search the encrypted catalog")
    search.add_argument("vault")
    search.add_argument("query")
    show = sub.add_parser("show", help="Show non-secret entry metadata")
    show.add_argument("vault")
    show.add_argument("entry_id")

    password = sub.add_parser("password", help="Print or copy a password")
    password.add_argument("vault")
    password.add_argument("entry_id")
    password.add_argument("--copy", action="store_true")

    otp = sub.add_parser("otp", help="Generate a TOTP code")
    otp.add_argument("vault")
    otp.add_argument("entry_id")
    otp.add_argument("--index", type=int, default=0)
    otp.add_argument("--watch", action="store_true")
    otp.add_argument("--copy", action="store_true")

    action = sub.add_parser("open", help="Launch a structured entry action")
    action.add_argument("vault")
    action.add_argument("entry_id")
    action.add_argument("--index", type=int, default=0)

    gen = sub.add_parser("generate", help="Generate a password")
    gen.add_argument("--length", type=int, default=24)
    gen.add_argument("--ambiguous", action="store_true")

    reindex = sub.add_parser("reindex", help="Rebuild encrypted catalog")
    reindex.add_argument("vault")
    health = sub.add_parser("catalog-health", help="Check catalog/record consistency")
    health.add_argument("vault")

    lock = sub.add_parser("lock", help="Drop cached GnuPG authorization with --hard")
    lock.add_argument("--hard", action="store_true")

    inbox = sub.add_parser("import-inbox", help="Verify and import write-only inbox records")
    inbox.add_argument("vault")
    inbox.add_argument("--keep", action="store_true")
    inbox.add_argument("--accept-unsigned", action="store_true", help="Explicitly accept public-key-only unsigned inbox items")


    trust = sub.add_parser("trust", help="Manage vault-authorized inbox signers")
    trust_sub = trust.add_subparsers(dest="trust_command", required=True)
    trust_list = trust_sub.add_parser("list", help="List trusted inbox signers")
    trust_list.add_argument("vault")
    trust_add = trust_sub.add_parser("add", help="Authorize a full OpenPGP fingerprint for inbox imports")
    trust_add.add_argument("vault")
    trust_add.add_argument("fingerprint")
    trust_remove = trust_sub.add_parser("remove", help="Remove an authorized inbox signer")
    trust_remove.add_argument("vault")
    trust_remove.add_argument("fingerprint")

    deposit = sub.add_parser("inbox-create", help="Create a standalone encrypted inbox entry using only recipient public keys")
    deposit.add_argument("--recipient", action="append", default=[], help="Full recipient public-key fingerprint already present in the local GnuPG keyring (repeatable)")
    deposit.add_argument("--public-key", action="append", default=[], metavar="FILE", help="Public-key file to use in an isolated temporary GnuPG keyring (repeatable)")
    deposit.add_argument("--signer", help="Optional full secret-key fingerprint to sign the item")
    deposit.add_argument("--output", required=True, help="Destination .gpg file; copy it manually into the vault inbox")
    deposit.add_argument("--title")
    deposit.add_argument("--username")
    deposit.add_argument("--url")
    deposit.add_argument("--ssh-host")
    deposit.add_argument("--ssh-port", type=int)
    deposit.add_argument("--ssh-x11", choices=["off", "X", "Y"], default="off")
    deposit.add_argument("--ssh-options", default="")
    deposit.add_argument("--rdp-host")
    deposit.add_argument("--rdp-port", type=int)
    deposit.add_argument("--tag", action="append", default=[])
    deposit.add_argument("--totp-uri")
    deposit.add_argument("--totp-qr")
    deposit.add_argument("--generate-password", type=int, metavar="LENGTH")
    deposit.add_argument("--notes", default="")

    doctor = sub.add_parser("doctor", help="Diagnose Keys NG, GnuPG and optional desktop dependencies")

    desktop = sub.add_parser("desktop", help="Manage per-user application-menu integration")
    desktop_sub = desktop.add_subparsers(dest="desktop_command", required=True)
    desktop_sub.add_parser("install", help="Install the per-user application-menu launcher and icon")
    desktop_sub.add_parser("status", help="Show application-menu integration status")
    desktop_sub.add_parser("uninstall", help="Remove per-user application-menu integration")

    folder = sub.add_parser("folder", help="Manage encrypted folders")
    folder_sub = folder.add_subparsers(dest="folder_command", required=True)
    folder_list = folder_sub.add_parser("list", help="List folders")
    folder_list.add_argument("vault")
    folder_create = folder_sub.add_parser("create", help="Create a folder path")
    folder_create.add_argument("vault")
    folder_create.add_argument("path")
    folder_rename = folder_sub.add_parser("rename", help="Rename a folder")
    folder_rename.add_argument("vault")
    folder_rename.add_argument("folder_id")
    folder_rename.add_argument("name")
    folder_move = folder_sub.add_parser("move", help="Move a folder under another folder")
    folder_move.add_argument("vault")
    folder_move.add_argument("folder_id")
    folder_move.add_argument("parent", help="Parent folder path, or / for root")
    folder_delete = folder_sub.add_parser("delete", help="Delete an empty folder")
    folder_delete.add_argument("vault")
    folder_delete.add_argument("folder_id")

    move = sub.add_parser("move", help="Move an entry to a folder")
    move.add_argument("vault")
    move.add_argument("entry_id")
    move.add_argument("folder", help="Folder path, or / for root")

    migrate = sub.add_parser("migrate-legacy", help="Migrate a Keys 1.0.1 KEYROOT tree")
    migrate.add_argument("source")
    migrate.add_argument("vault")
    migrate.add_argument("--dry-run", action="store_true")
    migrate.add_argument("--verify", action="store_true")

    kp = sub.add_parser("import-keepassxc", help="Import a KeePassXC KDBX database or XML export")
    kp.add_argument("source")
    kp.add_argument("vault")
    kp.add_argument("--format", dest="source_format", choices=["auto", "kdbx", "xml"], default="auto")
    kp.add_argument("--key-file", help="KeePassXC key file used to unlock a KDBX database")
    kp.add_argument("--no-password", action="store_true", help="KDBX does not use a password component")
    kp.add_argument("--yubikey", help="KeePassXC YubiKey slot[:serial]")
    kp.add_argument("--dry-run", action="store_true")

    export_entry = sub.add_parser("export-entry", help="Export one entry as KeePassXC-compatible XML")
    export_entry.add_argument("vault")
    export_entry.add_argument("entry_id")
    export_entry.add_argument("output")

    export_vault = sub.add_parser("export-vault", help="Export a complete vault as KeePassXC-compatible XML")
    export_vault.add_argument("vault")
    export_vault.add_argument("output")
    return p


def run(args: argparse.Namespace) -> int:
    if args.command == "version":
        print(f"Keys NG {__version__}")
        return 0

    if args.command == "desktop":
        if args.desktop_command == "install":
            paths = install_user_desktop_integration()
            print(_("Desktop integration installed."))
            print(paths.desktop_file)
            print(paths.icon_file)
            return 0
        if args.desktop_command == "status":
            ok, paths = desktop_integration_status()
            print("OK" if ok else "MISSING")
            print(paths.desktop_file)
            print(paths.icon_file)
            return 0 if ok else 1
        if args.desktop_command == "uninstall":
            uninstall_user_desktop_integration()
            print(_("Desktop integration removed."))
            return 0

    crypto = _crypto()
    if args.command == "init":
        request = VaultInitRequest(
            path=args.vault,
            recipients=tuple(args.recipient),
            signer=args.signer,
            require_signature=not args.allow_unsigned,
            catalog_privacy=args.catalog_privacy,
        )
        create_vault(request, crypto)
        print(_("Vault initialized."))
        return 0
    if args.command == "keys":
        for key in crypto.list_keys(secret=args.secret):
            flags = []
            if key.can_encrypt: flags.append("encrypt")
            if key.can_sign: flags.append("sign")
            if key.revoked: flags.append("revoked")
            if key.expired: flags.append("expired")
            print(f"{key.fingerprint}\t{','.join(flags) or '-'}\t{'; '.join(key.user_ids)}")
        return 0
    if args.command == "generate":
        print(generate_password(args.length, ambiguous=args.ambiguous))
        return 0
    if args.command == "doctor":
        failed_required = False
        for check in collect_doctor_checks(crypto, _settings()):
            state = "OK" if check.ok else ("WARN" if check.optional else "FAIL")
            print(f"[{state}] {check.name}: {check.detail}")
            if not check.ok and not check.optional:
                failed_required = True
        return 1 if failed_required else 0
    if args.command == "lock":
        if args.hard:
            crypto.hard_lock()
            print(_("GnuPG agent cache cleared."))
        else:
            print(_("CLI commands are stateless; use --hard to clear gpg-agent."))
        return 0
    if args.command == "inbox-create":
        if not args.recipient and not args.public_key:
            raise KeysNGError("Provide at least one --recipient fingerprint or --public-key file")
        deposit_crypto = crypto
        temporary_home = None
        if args.public_key:
            if args.signer:
                raise KeysNGError("--signer cannot be combined with isolated --public-key mode")
            temporary_home = tempfile.TemporaryDirectory(prefix="keys-ng-pubkey-")
            if os.name != "nt":
                os.chmod(temporary_home.name, 0o700)
            deposit_crypto = GPGProcessBackend(homedir=temporary_home.name)
            imported: list[str] = []
            for key_path in args.public_key:
                imported.extend(deposit_crypto.import_public_key(Path(key_path).expanduser().read_bytes()))
            imported = list(dict.fromkeys(imported))
            recipients = [deposit_crypto.resolve_fingerprint(fp, secret=False) for fp in args.recipient] if args.recipient else imported
            if not recipients:
                temporary_home.cleanup()
                raise KeysNGError("No usable encryption-capable public key found in --public-key files")
            signer = None
        else:
            recipients = [deposit_crypto.resolve_fingerprint(fp, secret=False) for fp in args.recipient]
            signer = deposit_crypto.resolve_fingerprint(args.signer, secret=True) if args.signer else None
        title = args.title or input(_("Title: ")).strip()
        username = args.username if args.username is not None else input(_("Username: ")).strip()
        password = generate_password(args.generate_password) if args.generate_password else (getpass(_("Password (leave empty for none): ")) or None)
        actions = []
        if args.url:
            actions.append(Action(type="url", url=args.url))
        if args.ssh_host:
            actions.append(Action(type="ssh", host=args.ssh_host, port=args.ssh_port, username=username or None, ssh_x11_forwarding=args.ssh_x11, ssh_options=parse_ssh_options(args.ssh_options)))
        if args.rdp_host:
            actions.append(Action(type="rdp", host=args.rdp_host, port=args.rdp_port, username=username or None))
        totp = []
        if args.totp_uri:
            totp.append(parse_otpauth_uri(args.totp_uri))
        if args.totp_qr:
            totp.append(parse_totp_qr_file(args.totp_qr))
        entry = Entry.create(title=title, usernames=[username] if username else [], password=password, actions=actions, tags=args.tag, totp=totp, notes=args.notes)
        destination = write_encrypted_entry(args.output, entry, deposit_crypto, recipients, signer)
        if temporary_home is not None:
            temporary_home.cleanup()
        print(destination)
        print(entry.id)
        return 0

    vault = Vault(args.vault, crypto)
    if args.command == "trust":
        if args.trust_command == "list":
            for signer in list_trusted_signers(vault):
                flags = ["vault-signer"] if signer.vault_signer else ["inbox-signer"]
                if not signer.present: flags.append("key-missing")
                if signer.revoked: flags.append("revoked")
                if signer.expired: flags.append("expired")
                print(f"{signer.fingerprint}\t{','.join(flags)}\t{signer.label}")
            return 0
        if args.trust_command == "add":
            signer = add_trusted_signer(vault, args.fingerprint)
            print(_("Trusted signer added."))
            print(signer.fingerprint)
            return 0
        if args.trust_command == "remove":
            remove_trusted_signer(vault, args.fingerprint)
            print(_("Trusted signer removed."))
            return 0
    if args.command == "folder":
        if args.folder_command == "list":
            for folder in vault.list_folders():
                print(f"{folder.id}\t{vault.folder_path(folder.id)}")
        elif args.folder_command == "create":
            folder = vault.create_folder_path(args.path)
            if folder:
                print(f"{folder.id}\t{vault.folder_path(folder.id)}")
        elif args.folder_command == "rename":
            folder = vault.rename_folder(args.folder_id, args.name)
            print(f"{folder.id}\t{vault.folder_path(folder.id)}")
        elif args.folder_command == "move":
            parent_id = None if args.parent.strip() in {"", "/", "\\"} else vault.resolve_folder_path(args.parent)
            folder = vault.move_folder(args.folder_id, parent_id)
            print(f"{folder.id}\t{vault.folder_path(folder.id)}")
        elif args.folder_command == "delete":
            vault.delete_folder(args.folder_id)
        return 0
    if args.command == "move":
        folder_id = None if args.folder.strip() in {"", "/", "\\"} else vault.resolve_folder_path(args.folder)
        vault.move_entry(args.entry_id, folder_id)
        return 0
    if args.command == "list":
        _print_items(vault.list_items())
    elif args.command == "search":
        _print_items(vault.search(args.query))
    elif args.command == "show":
        entry = vault.get_entry(args.entry_id)
        print(f"ID: {entry.id}\nTitle: {entry.title}\nKind: {entry.kind}")
        print(f"Usernames: {', '.join(entry.usernames)}\nTags: {', '.join(entry.tags)}\nTOTP: {len(entry.totp)}\nNotes: {entry.notes}")
    elif args.command == "password":
        entry = vault.get_entry(args.entry_id)
        password_value = vault.resolved_password(entry)
        if password_value is None:
            raise KeysNGError("Entry has no password")
        if args.copy:
            copy_secret_cli(password_value, _settings().clipboard_password_timeout)
            print(_("Password copied to clipboard."))
        else:
            print(password_value)
    elif args.command == "otp":
        entry = vault.get_entry(args.entry_id)
        try:
            token = entry.totp[args.index]
        except IndexError as exc:
            raise KeysNGError("TOTP token not found") from exc
        if args.copy:
            code, remaining = generate_totp(token)
            copy_secret_cli(code, _settings().clipboard_totp_timeout)
            print(_("TOTP copied to clipboard."))
        elif args.watch:
            try:
                while True:
                    code, remaining = generate_totp(token)
                    print(f"\r{code}  ({remaining:2d}s)", end="", flush=True)
                    time.sleep(1)
            except KeyboardInterrupt:
                print()
        else:
            code, remaining = generate_totp(token)
            print(f"{code}\t{remaining}s")
    elif args.command == "open":
        entry = vault.get_entry(args.entry_id)
        try:
            action = vault.resolved_action(entry, entry.actions[args.index])
            launch_action(action)
        except IndexError as exc:
            raise KeysNGError("Action not found") from exc
    elif args.command == "reindex":
        catalog = vault.reindex()
        print(_("Catalog rebuilt: {count} entries.").format(count=len(catalog.items)))
    elif args.command == "catalog-health":
        ok, issues = vault.catalog_health()
        if ok:
            print("OK")
        else:
            for issue in issues: print(issue)
            return 1
    elif args.command == "add":
        title = args.title or input(_("Title: ")).strip()
        username = args.username if args.username is not None else input(_("Username: ")).strip()
        password = generate_password(args.generate_password) if args.generate_password else (getpass(_("Password (leave empty for none): ")) or None)
        actions = []
        if args.url: actions.append(Action(type="url", url=args.url))
        if args.ssh_host: actions.append(Action(type="ssh", host=args.ssh_host, port=args.ssh_port, username=username or None, ssh_x11_forwarding=args.ssh_x11, ssh_options=parse_ssh_options(args.ssh_options)))
        if args.rdp_host: actions.append(Action(type="rdp", host=args.rdp_host, port=args.rdp_port, username=username or None))
        totp = []
        if args.totp_uri: totp.append(parse_otpauth_uri(args.totp_uri))
        if args.totp_qr: totp.append(parse_totp_qr_file(args.totp_qr))
        folder_id = vault.resolve_folder_path(args.folder) if args.folder else None
        entry = Entry.create(title=title, usernames=[username] if username else [], password=password, actions=actions, tags=args.tag, totp=totp, folder_id=folder_id)
        vault.save_entry(entry)
        print(entry.id)
    elif args.command == "edit":
        entry = vault.get_entry(args.entry_id)
        if args.title is not None: entry.title = args.title
        if args.username is not None:
            entry.usernames = [args.username] if args.username else []
            for action in entry.actions:
                if action.type in {"ssh", "rdp"}:
                    action.username = args.username or None
        if args.url is not None:
            entry.actions = [a for a in entry.actions if a.type != "url"]
            if args.url: entry.actions.insert(0, Action(type="url", url=args.url))
        if args.ssh_x11 is not None or args.ssh_options is not None:
            ssh_action = next((a for a in entry.actions if a.type == "ssh"), None)
            if ssh_action is None:
                raise KeysNGError("Entry has no SSH action")
            if args.ssh_x11 is not None:
                ssh_action.ssh_x11_forwarding = args.ssh_x11
            if args.ssh_options is not None:
                ssh_action.ssh_options = parse_ssh_options(args.ssh_options)
        if args.folder is not None:
            entry.folder_id = None if args.folder.strip() in {"", "/", "\\"} else vault.resolve_folder_path(args.folder)
        entry.revision += 1
        vault.save_entry(entry)
    elif args.command == "delete":
        vault.delete_entry(args.entry_id)
    elif args.command == "import-inbox":
        results = import_inbox(vault, delete_after=not args.keep, accept_unsigned=args.accept_unsigned)
        failures = 0
        for path, status in results:
            print(f"{status}\t{path.name}")
            failures += status != "ok"
        return 1 if failures else 0
    elif args.command == "migrate-legacy":
        results = migrate_legacy_tree(Path(args.source), vault, crypto, dry_run=args.dry_run, verify=args.verify)
        failures = 0
        for path, status in results:
            print(f"{status}\t{path}")
            failures += status != "ok"
        return 1 if failures else 0
    elif args.command == "export-entry":
        destination = write_export(args.output, export_entry_xml(vault, args.entry_id))
        print(destination)
        print(_("WARNING: XML exports contain plaintext credentials. Protect and delete them securely after use."), file=sys.stderr)
        return 0
    elif args.command == "export-vault":
        destination = write_export(args.output, export_vault_xml(vault))
        print(destination)
        print(_("WARNING: XML exports contain plaintext credentials. Protect and delete them securely after use."), file=sys.stderr)
        return 0
    elif args.command == "import-keepassxc":
        report = import_keepassxc(
            args.source,
            vault,
            source_format=args.source_format,
            key_file=args.key_file,
            no_password=args.no_password,
            yubikey=args.yubikey,
            dry_run=args.dry_run,
        )
        print(_("Imported {entries} entries in {folders} folders; TOTP: {totp}; custom fields: {fields}.").format(
            entries=report.entries, folders=report.folders, totp=report.totp_tokens, fields=report.custom_fields
        ))
        print(_("UUID preserved: {preserved}; remapped: {remapped}; generated: {generated}; references validated: {refs}.").format(
            preserved=report.uuid_preserved, remapped=report.uuid_remapped, generated=report.uuid_generated, refs=report.references_validated
        ))
        for warning in report.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        return 0
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = _settings()
    configure_diagnostics(settings, "cli")
    get_logger("cli").info("cli.start command=%s", args.command)
    configure_language(args.language or settings.language)
    try:
        raise SystemExit(run(args))
    except (KeysNGError, ValueError, RuntimeError) as exc:
        print(f"keys-ng: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
