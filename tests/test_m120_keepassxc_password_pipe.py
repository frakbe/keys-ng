from pathlib import Path

import keys_ng.migration.keepassxc as kp


class _FakeProcess:
    def __init__(self, argv, **kwargs):
        self.argv = argv
        self.kwargs = kwargs
        self.returncode = 0
        self.payload = None

    def communicate(self, payload=None):
        self.payload = payload
        return (b"<KeePassFile/>", None)


def test_interactive_kdbx_password_goes_to_stdin_not_argv(monkeypatch, tmp_path: Path):
    db = tmp_path / "db.kdbx"
    db.write_bytes(b"dummy")
    fake = None

    def make_process(argv, **kwargs):
        nonlocal fake
        fake = _FakeProcess(argv, **kwargs)
        return fake

    monkeypatch.setattr(kp.subprocess, "Popen", make_process)
    raw = kp.export_kdbx_to_xml(db, keepassxc_cli="keepassxc-cli", password="top-secret")
    assert raw == b"<KeePassFile/>"
    assert fake is not None
    assert "top-secret" not in fake.argv
    assert fake.payload == b"top-secret\n"


def test_import_report_formatter_contains_counts():
    report = kp.KeePassXCImportReport(entries=3, folders=2, uuid_preserved=2, uuid_remapped=1)
    text = kp.format_import_report(report)
    assert "Entries: 3" in text
    assert "Folders: 2" in text
    assert "2/1/0" in text
