from __future__ import annotations

from io import StringIO

from keys_ng.services import clipboard_helper


def test_native_clipboard_ack_precedes_readback(monkeypatch):
    events = []

    class Output(StringIO):
        def write(self, value):
            if value.startswith("READY"):
                events.append("ready")
            return super().write(value)

    monkeypatch.setattr(clipboard_helper, "set_native_clipboard", lambda secret: events.append("set") or "xclip")
    monkeypatch.setattr(clipboard_helper, "read_native_clipboard", lambda backend: events.append("read") or "secret")
    monkeypatch.setattr(clipboard_helper, "clear_native_clipboard", lambda backend: events.append("clear"))
    monkeypatch.setattr(clipboard_helper.time, "sleep", lambda seconds: events.append("sleep"))
    monkeypatch.setattr(clipboard_helper.sys, "stdout", Output())

    clipboard_helper._native_worker("secret", 1)

    assert events.index("ready") < events.index("read")
