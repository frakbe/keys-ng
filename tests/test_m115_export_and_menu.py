from __future__ import annotations

import base64
import xml.etree.ElementTree as ET
from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.migration.keepassxc import import_keepassxc_xml
from keys_ng.migration.keepassxc_export import export_entry_xml, export_vault_xml, write_export
from keys_ng.models import Action, Entry
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def _strings(entry_node: ET.Element) -> dict[str, str]:
    out = {}
    for node in entry_node.findall("String"):
        key = node.findtext("Key", "")
        value = node.findtext("Value", "")
        out[key] = value
    return out


def test_single_entry_export_is_keepass_xml_and_resolves_refs(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    master = Entry.create("Shared", usernames=["admin"], password="secret")
    vault.save_entry(master)
    consumer = Entry.create(
        "Server",
        usernames=[f"{{REF:U@I:{master.id}}}"],
        password=f"{{REF:P@I:{master.id}}}",
        actions=[Action(type="ssh", host="host.example", port=22)],
    )
    vault.save_entry(consumer)
    raw = export_entry_xml(vault, consumer.id)
    root = ET.fromstring(raw)
    entry_node = root.find("./Root/Group/Entry")
    assert entry_node is not None
    values = _strings(entry_node)
    assert values["UserName"] == "admin"
    assert values["Password"] == "secret"
    assert values["URL"] == "ssh://host.example:22"


def test_full_vault_export_preserves_hierarchy_uuid_and_refs_and_roundtrips(tmp_path):
    source = Vault.init(tmp_path / "source", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    folder = source.create_folder_path("Servers/Prod")
    master = Entry.create("Shared", usernames=["admin"], password="secret")
    source.save_entry(master)
    consumer = Entry.create(
        "Server 01",
        usernames=[f"{{REF:U@I:{master.id}}}"],
        password=f"{{REF:P@I:{master.id}}}",
        actions=[Action(type="ssh", host="server01.example")],
        folder_id=folder.id,
    )
    source.save_entry(consumer)

    raw = export_vault_xml(source)
    root = ET.fromstring(raw)
    uuids = [node.text for node in root.findall(".//Entry/UUID")]
    assert base64.b64encode(__import__('uuid').UUID(master.id).bytes).decode() in uuids
    xml_text = raw.decode("utf-8")
    assert f"{{REF:P@I:{master.id.replace('-', '').upper()}}}" in xml_text

    target = Vault.init(tmp_path / "target", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    report = import_keepassxc_xml(raw, target)
    assert report.entries == 2
    imported_consumer = target.get_entry(consumer.id)
    assert target.resolved_username(imported_consumer) == "admin"
    assert target.resolved_password(imported_consumer) == "secret"
    assert target.folder_path(imported_consumer.folder_id) == "Servers/Prod"


def test_write_export_uses_private_permissions(tmp_path):
    destination = write_export(tmp_path / "entry.xml", b"<x/>")
    assert destination.read_bytes() == b"<x/>"
    if __import__('os').name != 'nt':
        assert destination.stat().st_mode & 0o777 == 0o600


def test_linux_desktop_entry_is_visible_in_application_menu():
    desktop = Path("src/keys_ng/resources/org.keysng.KeysNG.desktop").read_text(encoding="utf-8")
    assert "NoDisplay=false" in desktop
    assert "Exec=keys-ng-gui" in desktop
    assert "TryExec=" not in desktop


def test_frontends_expose_single_entry_export():
    gui = Path("src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    tui = Path("src/keys_ng/tui/main.py").read_text(encoding="utf-8")
    cli = Path("src/keys_ng/cli/main.py").read_text(encoding="utf-8")
    assert "Export as KeePassXC XML" in gui
    assert 'Binding("x", "export_entry"' in tui
    assert 'sub.add_parser("export-entry"' in cli
    assert 'sub.add_parser("export-vault"' in cli


def test_application_menu_paths_are_defined_for_windows_and_macos(monkeypatch, tmp_path):
    import keys_ng.platform.desktop_integration as di

    monkeypatch.setattr(di.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    win = di.user_paths()
    assert win.desktop_file.name == "Keys NG.lnk"
    assert "Start Menu" in str(win.desktop_file)
    assert win.icon_file.suffix == ".ico"

    monkeypatch.setattr(di.sys, "platform", "darwin")
    monkeypatch.setattr(di.Path, "home", classmethod(lambda cls: tmp_path))
    mac = di.user_paths()
    assert mac.desktop_file.name == "Keys NG.app"
    assert mac.icon_file.name == "keys-icon.png"


def test_docs_are_organized_by_language():
    docs = {str(p.relative_to("docs")) for p in Path("docs").rglob("*.md")}
    required = {
        "en/DEVELOPER_GUIDE.md",
        "en/USER_GUIDE.md",
        "it/DEVELOPER_GUIDE.md",
        "it/USER_GUIDE.md",
    }
    assert required <= docs
    assert all(path.startswith(("en/", "it/")) for path in docs)
