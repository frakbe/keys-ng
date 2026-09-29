import pytest

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult
from keys_ng.errors import ReferenceError
from keys_ng.models import Action, Entry
from keys_ng.services.references import make_entry_reference, parse_entry_reference
from keys_ng.storage.vault import Vault


class FakeCrypto(CryptoBackend):
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        return b"ENC:" + plaintext

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        return DecryptionResult(ciphertext.removeprefix(b"ENC:"), "SIGNER", True)

    def diagnose(self):
        return []


def make_vault(tmp_path):
    return Vault.init(tmp_path / "vault", FakeCrypto(), ["RECIPIENT"], "SIGNER")


def test_reference_parser_accepts_keepass_and_canonical_uuid():
    entry_id = "033054d4-45c6-48c5-9092-cc1d661b1b71"
    canonical = parse_entry_reference(f"{{REF:U@I:{entry_id}}}")
    keepass = parse_entry_reference("{REF:P@I:033054D445C648C59092CC1D661B1B71}")
    assert canonical.entry_id == entry_id
    assert canonical.field == "U"
    assert keepass.entry_id == entry_id
    assert keepass.field == "P"


def test_reusable_credentials_resolve_and_update(tmp_path):
    vault = make_vault(tmp_path)
    master = Entry.create("Shared credentials", usernames=["alice"], password="first-secret")
    vault.save_entry(master)
    consumer = Entry.create(
        "Server 1",
        usernames=[make_entry_reference("U", master.id)],
        password=make_entry_reference("P", master.id),
        actions=[Action(type="ssh", host="server1.example", username=make_entry_reference("U", master.id))],
    )
    vault.save_entry(consumer)

    loaded = vault.get_entry(consumer.id)
    assert vault.resolved_username(loaded) == "alice"
    assert vault.resolved_password(loaded) == "first-secret"
    assert vault.resolved_action(loaded, loaded.actions[0]).username == "alice"

    master.password = "rotated-secret"
    master.usernames = ["alice-new"]
    master.revision += 1
    vault.save_entry(master)

    assert vault.resolved_username(consumer.id) == "alice-new"
    assert vault.resolved_password(consumer.id) == "rotated-secret"


def test_nested_references_and_cycle_detection(tmp_path):
    vault = make_vault(tmp_path)
    a = Entry.create("A", usernames=["user-a"], password="secret-a")
    vault.save_entry(a)
    b = Entry.create("B", usernames=[make_entry_reference("U", a.id)], password=make_entry_reference("P", a.id))
    vault.save_entry(b)
    c = Entry.create("C", usernames=[make_entry_reference("U", b.id)], password=make_entry_reference("P", b.id))
    vault.save_entry(c)
    assert vault.resolved_username(c) == "user-a"
    assert vault.resolved_password(c) == "secret-a"

    a.password = make_entry_reference("P", c.id)
    a.revision += 1
    vault.save_entry(a)
    with pytest.raises(ReferenceError, match="cycle"):
        vault.resolved_password(c)


def test_missing_reference_is_reported(tmp_path):
    vault = make_vault(tmp_path)
    broken = Entry.create("Broken", password="{REF:P@I:033054D445C648C59092CC1D661B1B71}")
    vault.save_entry(broken)
    with pytest.raises(ReferenceError, match="not found"):
        vault.resolved_password(broken)


def test_gui_and_tui_expose_uuid_copy_and_reference_resolution():
    gui = open("src/keys_ng/gui/main.py", encoding="utf-8").read()
    tui = open("src/keys_ng/tui/main.py", encoding="utf-8").read()
    assert "Copy UUID" in gui
    assert "copy_uuid_clicked" in gui
    assert "resolved_username" in gui and "resolved_password" in gui
    assert 'Binding("f4", "copy_uuid"' in tui
    assert "resolved_username" in tui and "resolved_password" in tui
