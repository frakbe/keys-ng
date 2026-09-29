from __future__ import annotations

from dataclasses import dataclass

from keys_ng.i18n import _
from keys_ng.models import Action, Entry
from keys_ng.services.ssh_options import parse_ssh_options
from keys_ng.services.totp import parse_otpauth_uri, totp_from_secret


@dataclass(slots=True)
class EntryDraft:
    """Frontend-neutral editable representation of one credential.

    GUI and TUI deliberately use the same conversion routine so validation and
    preservation rules cannot silently diverge between front ends.
    """

    title: str = ""
    folder_id: str | None = None
    action_type: str = "generic"
    username: str = ""
    password: str = ""
    url: str = ""
    host: str = ""
    port: str = ""
    rdp_domain: str = ""
    ssh_x11_forwarding: str = "off"
    ssh_options: str = ""
    tags: str = ""
    totp_uri: str = ""
    totp_secret: str = ""
    notes: str = ""

    @classmethod
    def from_entry(cls, entry: Entry) -> "EntryDraft":
        primary = next((a for a in entry.actions if a.type in {"url", "ssh", "rdp"}), None)
        action_type = primary.type if primary else "generic"
        from keys_ng.services.ssh_options import format_ssh_options
        from keys_ng.services.totp import build_otpauth_uri

        return cls(
            title=entry.title,
            folder_id=entry.folder_id,
            action_type=action_type,
            username=entry.usernames[0] if entry.usernames else "",
            password=entry.password or "",
            url=primary.url or "" if primary and primary.type == "url" else "",
            host=primary.host or "" if primary and primary.type in {"ssh", "rdp"} else "",
            port=str(primary.port) if primary and primary.port else "",
            rdp_domain=(primary.rdp_domain or "") if primary and primary.type == "rdp" else "",
            ssh_x11_forwarding=primary.ssh_x11_forwarding if primary and primary.type == "ssh" else "off",
            ssh_options=format_ssh_options(primary.ssh_options) if primary and primary.type == "ssh" else "",
            tags=", ".join(entry.tags),
            totp_uri=build_otpauth_uri(entry.totp[0]) if entry.totp else "",
            totp_secret=entry.totp[0].secret if entry.totp else "",
            notes=entry.notes,
        )


def build_entry_from_draft(draft: EntryDraft, existing: Entry | None = None) -> Entry:
    """Validate a frontend draft and create/update the domain Entry.

    Imported/legacy command actions and custom fields are preserved during an
    edit because the desktop editor does not expose them directly.
    """
    title = draft.title.strip()
    username = draft.username.strip()
    password = draft.password or None
    tags = [tag.strip() for tag in draft.tags.split(",") if tag.strip()]
    action_type = draft.action_type.strip().lower() or "generic"
    if action_type not in {"generic", "url", "ssh", "rdp"}:
        raise ValueError(_("Unsupported entry type."))

    actions = [a for a in existing.actions if a.type == "command"] if existing else []
    if action_type == "url":
        url = draft.url.strip()
        if not url:
            raise ValueError(_("URL is required for a Web entry."))
        actions.insert(0, Action(type="url", url=url))
    elif action_type in {"ssh", "rdp"}:
        host = draft.host.strip()
        if not host:
            raise ValueError(_("Host is required for SSH/RDP entries."))
        port_text = draft.port.strip()
        try:
            port = int(port_text) if port_text else None
        except ValueError as exc:
            raise ValueError(_("Port must be a number.")) from exc
        if action_type == "ssh":
            actions.insert(
                0,
                Action(
                    type="ssh",
                    host=host,
                    port=port,
                    username=username or None,
                    ssh_x11_forwarding=draft.ssh_x11_forwarding,
                    ssh_options=parse_ssh_options(draft.ssh_options),
                ),
            )
        else:
            actions.insert(
                0,
                Action(
                    type="rdp",
                    host=host,
                    port=port,
                    username=username or None,
                    rdp_domain=draft.rdp_domain.strip() or None,
                ),
            )

    totp = []
    uri = draft.totp_uri.strip()
    secret = draft.totp_secret.strip()
    if uri:
        token = parse_otpauth_uri(uri)
        if secret and secret.replace(" ", "").upper() != token.secret.replace(" ", "").upper():
            token = totp_from_secret(
                secret,
                issuer=token.issuer,
                account_name=token.account_name,
                algorithm=token.algorithm,
                digits=token.digits,
                period=token.period,
            )
        totp = [token]
    elif secret:
        old = existing.totp[0] if existing and existing.totp else None
        totp = [
            totp_from_secret(
                secret,
                issuer=old.issuer if old else title,
                account_name=old.account_name if old else username,
                algorithm=old.algorithm if old else "SHA1",
                digits=old.digits if old else 6,
                period=old.period if old else 30,
            )
        ]

    kind = {"url": "website", "ssh": "ssh", "rdp": "rdp", "generic": "account"}[action_type]
    if existing:
        existing.title = title
        existing.kind = kind
        existing.usernames = [username] if username else []
        existing.password = password
        existing.tags = tags
        existing.notes = draft.notes
        existing.actions = actions
        existing.totp = totp
        existing.folder_id = draft.folder_id
        existing.revision += 1
        existing.validate()
        return existing

    entry = Entry.create(
        title=title,
        kind=kind,
        usernames=[username] if username else [],
        password=password,
        tags=tags,
        notes=draft.notes,
        actions=actions,
        totp=totp,
        folder_id=draft.folder_id,
    )
    entry.validate()
    return entry
