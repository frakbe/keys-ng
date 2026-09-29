from pathlib import Path


def test_gui_defines_folder_and_action_icons():
    source = (Path(__file__).parents[1] / "src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert "SP_DirIcon" in source
    assert '"action:url"' in source
    assert '"action:ssh"' in source
    assert '"action:rdp"' in source
    assert "setIcon(0" in source
