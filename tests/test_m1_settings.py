from keys_ng.storage.settings import AppSettings


def test_settings_roundtrip(tmp_path):
    path = tmp_path / "config.toml"
    settings = AppSettings(language="it", clipboard_password_timeout=12, clipboard_totp_timeout=7, auto_lock_timeout=90, crypto_backend="gpg", tree_startup_view="compact")
    settings.save(path)
    restored = AppSettings.load(path)
    assert restored == settings


def test_settings_reject_invalid_tree_startup_view(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[ui]\ntree_startup_view = "invalid"\n', encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="tree_startup_view"):
        AppSettings.load(path)
