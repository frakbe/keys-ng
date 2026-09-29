from __future__ import annotations

from pathlib import Path

from keys_ng.services.diagnostics import safe_operation_args
from keys_ng.storage.settings import AppSettings


def test_diagnostics_settings_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    settings = AppSettings(
        diagnostics_enabled=True,
        diagnostics_level="DEBUG",
        diagnostics_log_file=str(tmp_path / "debug.log"),
        diagnostics_max_bytes=123456,
        diagnostics_backup_count=4,
    )
    settings.save(path)
    loaded = AppSettings.load(path)
    assert loaded.diagnostics_enabled is True
    assert loaded.diagnostics_level == "DEBUG"
    assert loaded.diagnostics_log_file.endswith("debug.log")
    assert loaded.diagnostics_max_bytes == 123456
    assert loaded.diagnostics_backup_count == 4


def test_gpg_diagnostic_summary_does_not_expose_argument_values() -> None:
    fingerprint = "A" * 40
    secret_filename = r"C:\Users\Alice\secret-record.gpg"
    args = [
        "--recipient", fingerprint,
        "--output", secret_filename,
        "--decrypt",
    ]
    summary = safe_operation_args(args)
    assert summary == "decrypt"
    assert fingerprint not in summary
    assert secret_filename not in summary


def test_diagnostics_default_disabled() -> None:
    settings = AppSettings()
    assert settings.diagnostics_enabled is False
    assert settings.diagnostics_level == "DEBUG"
