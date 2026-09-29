from keys_ng.models import Action, Entry, TotpConfig


def test_entry_round_trip():
    entry = Entry.create(
        "Example",
        usernames=["alice"],
        password="secret",
        totp=[TotpConfig(secret="JBSWY3DPEHPK3PXP")],
        actions=[Action(type="url", url="https://example.com")],
    )
    restored = Entry.from_bytes(entry.to_bytes())
    assert restored.id == entry.id
    assert restored.password == "secret"
    assert restored.totp[0].secret == "JBSWY3DPEHPK3PXP"
