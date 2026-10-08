from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.migration.keepassxc import import_keepassxc_xml
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<KeePassFile>
  <Meta><RecycleBinUUID>RECYCLE</RecycleBinUUID></Meta>
  <Root>
    <Group>
      <UUID>ROOT</UUID><Name>Passwords</Name>
      <Entry>
        <String><Key>Title</Key><Value>Home</Value></String>
        <String><Key>UserName</Key><Value>alice</Value></String>
        <String><Key>Password</Key><Value>rootpw</Value></String>
        <String><Key>URL</Key><Value>https://example.org/login</Value></String>
      </Entry>
      <Group>
        <UUID>CLOUD</UUID><Name>Cloud</Name>
        <Entry>
          <String><Key>Title</Key><Value>GitHub</Value></String>
          <String><Key>UserName</Key><Value>alice@example.org</Value></String>
          <String><Key>Password</Key><Value>secret</Value></String>
          <String><Key>URL</Key><Value>https://github.com/login</Value></String>
          <String><Key>otp</Key><Value>otpauth://totp/GitHub:alice?secret=JBSWY3DPEHPK3PXP&amp;issuer=GitHub</Value></String>
          <String><Key>Recovery email</Key><Value>recovery@example.org</Value></String>
          <Tags>dev;cloud</Tags>
        </Entry>
        <Entry>
          <String><Key>Title</Key><Value>Prod SSH</Value></String>
          <String><Key>UserName</Key><Value>root</Value></String>
          <String><Key>URL</Key><Value>ssh://root@server.example.org:2222</Value></String>
        </Entry>
      </Group>
      <Group><UUID>RECYCLE</UUID><Name>Recycle Bin</Name>
        <Entry><String><Key>Title</Key><Value>Deleted</Value></String></Entry>
      </Group>
    </Group>
  </Root>
</KeePassFile>'''


def test_keepassxc_xml_import_preserves_hierarchy_totp_and_custom_fields(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    report = import_keepassxc_xml(XML, vault)
    assert report.entries == 3
    assert report.folders == 1
    assert report.totp_tokens == 1
    assert report.custom_fields == 1
    assert report.skipped_recycle_bin is True

    cloud_id = vault.resolve_folder_path("Cloud")
    github_item = next(item for item in vault.list_items() if item.title == "GitHub")
    assert github_item.folder_id == cloud_id
    assert "action:url" in github_item.capabilities
    github = vault.get_entry(github_item.id)
    assert github.totp[0].issuer == "GitHub"
    assert github.custom_fields["Recovery email"] == "recovery@example.org"
    assert github.tags == ["dev", "cloud"]

    ssh_item = next(item for item in vault.list_items() if item.title == "Prod SSH")
    assert "action:ssh" in ssh_item.capabilities
    ssh = vault.get_entry(ssh_item.id)
    assert ssh.actions[0].host == "server.example.org"
    assert ssh.actions[0].port == 2222

    home = next(item for item in vault.list_items() if item.title == "Home")
    assert home.folder_id is None


def test_keepassxc_xml_import_rejects_doctype(tmp_path):
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    evil = b'<!DOCTYPE x [<!ENTITY xx SYSTEM "file:///etc/passwd">]><KeePassFile />'
    try:
        import_keepassxc_xml(evil, vault)
    except ValueError as exc:
        assert "DOCTYPE" in str(exc)
    else:
        raise AssertionError("DOCTYPE should be rejected")


def test_kdbx_bridge_uses_keepassxc_cli_stdout(tmp_path):
    from keys_ng.migration.keepassxc import export_kdbx_to_xml

    fake_cli = tmp_path / "keepassxc-cli"
    fake_cli.write_text("#!/bin/sh\nprintf '%s' '<KeePassFile><Root><Group><Name>Root</Name></Group></Root></KeePassFile>'\n", encoding="utf-8")
    fake_cli.chmod(0o755)
    database = tmp_path / "test.kdbx"
    database.write_bytes(b"not-a-real-kdbx")
    raw = export_kdbx_to_xml(database, keepassxc_cli=str(fake_cli))
    assert raw.startswith(b"<KeePassFile>")


def _kp_uuid(value: str) -> str:
    import base64
    import uuid
    return base64.b64encode(uuid.UUID(value).bytes).decode("ascii")


def test_keepassxc_import_preserves_entry_uuid_and_uuid_references(tmp_path):
    source_credentials = "033054d4-45c6-48c5-9092-cc1d661b1b71"
    source_server = "1c2d12ca-9668-4828-8687-f676dbd6cf10"
    ref_user = source_credentials.replace("-", "").upper()
    xml = f'''<KeePassFile>
      <Meta />
      <Root><Group><UUID>{_kp_uuid("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")}</UUID><Name>Root</Name>
        <Entry>
          <UUID>{_kp_uuid(source_credentials)}</UUID>
          <String><Key>Title</Key><Value>Shared credentials</Value></String>
          <String><Key>UserName</Key><Value>administrator</Value></String>
          <String><Key>Password</Key><Value>rotating-secret</Value></String>
        </Entry>
        <Entry>
          <UUID>{_kp_uuid(source_server)}</UUID>
          <String><Key>Title</Key><Value>Server 01</Value></String>
          <String><Key>UserName</Key><Value>{{REF:U@I:{ref_user}}}</Value></String>
          <String><Key>Password</Key><Value>{{REF:P@I:{ref_user}}}</Value></String>
          <String><Key>URL</Key><Value>ssh://server01.example.org</Value></String>
        </Entry>
      </Group></Root>
    </KeePassFile>'''.encode()

    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    report = import_keepassxc_xml(xml, vault)

    assert report.entries == 2
    assert report.uuid_preserved == 2
    assert report.uuid_remapped == 0
    assert report.references_found >= 2
    assert report.references_validated >= 2

    credentials = vault.get_entry(source_credentials)
    server = vault.get_entry(source_server)
    assert credentials.id == source_credentials
    assert server.id == source_server
    assert server.usernames[0] == f"{{REF:U@I:{source_credentials}}}"
    assert server.password == f"{{REF:P@I:{source_credentials}}}"
    assert vault.resolved_username(server) == "administrator"
    assert vault.resolved_password(server) == "rotating-secret"
    assert vault.resolved_action(server, server.actions[0]).username == "administrator"


def test_keepassxc_uuid_collision_remaps_imported_entry_and_references(tmp_path):
    source_credentials = "033054d4-45c6-48c5-9092-cc1d661b1b71"
    source_server = "1c2d12ca-9668-4828-8687-f676dbd6cf10"
    ref_user = source_credentials.replace("-", "").upper()
    xml = f'''<KeePassFile><Meta /><Root><Group><Name>Root</Name>
      <Entry>
        <UUID>{_kp_uuid(source_credentials)}</UUID>
        <String><Key>Title</Key><Value>Imported shared credentials</Value></String>
        <String><Key>UserName</Key><Value>imported-admin</Value></String>
        <String><Key>Password</Key><Value>imported-secret</Value></String>
      </Entry>
      <Entry>
        <UUID>{_kp_uuid(source_server)}</UUID>
        <String><Key>Title</Key><Value>Imported server</Value></String>
        <String><Key>UserName</Key><Value>{{REF:U@I:{ref_user}}}</Value></String>
        <String><Key>Password</Key><Value>{{REF:P@I:{ref_user}}}</Value></String>
      </Entry>
    </Group></Root></KeePassFile>'''.encode()

    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    from keys_ng.models import Entry
    existing = Entry.create(title="Existing unrelated record", usernames=["existing"], password="existing-secret")
    existing.id = source_credentials
    vault.save_entry(existing)

    report = import_keepassxc_xml(xml, vault)
    assert report.uuid_remapped == 1
    assert report.uuid_preserved == 1
    assert report.references_remapped >= 2

    imported_credentials_item = next(item for item in vault.list_items() if item.title == "Imported shared credentials")
    assert imported_credentials_item.id != source_credentials
    server = vault.get_entry(source_server)
    assert server.password == f"{{REF:P@I:{imported_credentials_item.id}}}"
    assert server.usernames[0] == f"{{REF:U@I:{imported_credentials_item.id}}}"
    assert vault.resolved_username(server) == "imported-admin"
    assert vault.resolved_password(server) == "imported-secret"
    # The pre-existing colliding record is not accidentally used as the target.
    assert vault.get_entry(source_credentials).password == "existing-secret"


def test_keepassxc_dangling_reference_fails_before_writing_entries(tmp_path):
    missing = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    missing_ref = missing.replace("-", "").upper()
    source = "1c2d12ca-9668-4828-8687-f676dbd6cf10"
    xml = f'''<KeePassFile><Meta /><Root><Group><Name>Root</Name>
      <Group><Name>Servers</Name>
        <Entry>
          <UUID>{_kp_uuid(source)}</UUID>
          <String><Key>Title</Key><Value>Broken server</Value></String>
          <String><Key>Password</Key><Value>{{REF:P@I:{missing_ref}}}</Value></String>
        </Entry>
      </Group>
    </Group></Root></KeePassFile>'''.encode()

    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    try:
        import_keepassxc_xml(xml, vault)
    except ValueError as exc:
        assert "dangling reference" in str(exc)
    else:
        raise AssertionError("dangling KeePassXC reference should abort import")
    assert vault.list_items() == []
    assert vault.load_folders().folders == []


def test_keepassxc_dry_run_validates_references_without_writing(tmp_path):
    source_credentials = "033054d4-45c6-48c5-9092-cc1d661b1b71"
    source_server = "1c2d12ca-9668-4828-8687-f676dbd6cf10"
    ref_user = source_credentials.replace("-", "").upper()
    xml = f'''<KeePassFile><Meta /><Root><Group><Name>Root</Name>
      <Entry><UUID>{_kp_uuid(source_credentials)}</UUID>
        <String><Key>Title</Key><Value>Credentials</Value></String>
        <String><Key>Password</Key><Value>secret</Value></String>
      </Entry>
      <Entry><UUID>{_kp_uuid(source_server)}</UUID>
        <String><Key>Title</Key><Value>Consumer</Value></String>
        <String><Key>Password</Key><Value>{{REF:P@I:{ref_user}}}</Value></String>
      </Entry>
    </Group></Root></KeePassFile>'''.encode()
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")
    report = import_keepassxc_xml(xml, vault, dry_run=True)
    assert report.uuid_preserved == 2
    assert report.references_validated >= 1
    assert vault.list_items() == []


def test_keepassxc_import_preserves_unmapped_commands_in_notes_and_report(tmp_path):
    xml = b"""<KeePassFile>
      <Meta />
      <Root><Group><Name>Servers</Name>
        <Entry>
          <String><Key>Title</Key><Value>Veeam server</Value></String>
          <String><Key>UserName</Key><Value>admin</Value></String>
          <String><Key>Password</Key><Value>secret</Value></String>
          <String><Key>URL</Key><Value>cmd://xfreerdp /u:{USERNAME} /p:{PASSWORD} /v:server.example.org</Value></String>
          <String><Key>Command</Key><Value>xfreerdp /cert-ignore</Value></String>
          <String><Key>Notes</Key><Value>Keep the existing note.</Value></String>
        </Entry>
      </Group></Root>
    </KeePassFile>"""
    vault = Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")

    report = import_keepassxc_xml(xml, vault)

    assert len(report.partial_entries) == 1
    title, folder, reasons = report.partial_entries[0]
    assert title == "Veeam server"
    assert folder == ""
    assert any("command or URL" in reason for reason in reasons)
    assert any("Command" in reason for reason in reasons)

    item = next(item for item in vault.list_items() if item.title == "Veeam server")
    entry = vault.get_entry(item.id)
    assert "Keep the existing note." in entry.notes
    assert "[Imported KeePassXC command/URL not converted]" in entry.notes
    assert "cmd://xfreerdp /u:{USERNAME} /p:{PASSWORD} /v:server.example.org" in entry.notes
    assert "[Imported KeePassXC field: Command]" in entry.notes
    assert "xfreerdp /cert-ignore" in entry.notes
