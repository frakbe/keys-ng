from keys_ng.services.passwords import generate_password


def test_password_length_and_classes():
    value = generate_password(32)
    assert len(value) == 32
    assert any(ch.islower() for ch in value)
    assert any(ch.isupper() for ch in value)
    assert any(ch.isdigit() for ch in value)
