from pathlib import Path


def test_gui_exposes_copy_username_action():
    source = (Path(__file__).parents[1] / "src/keys_ng/gui/main.py").read_text(encoding="utf-8")
    assert 'QPushButton(_("Copy username"))' in source
    assert 'self.copy_username.clicked.connect(self.copy_username_clicked)' in source
    assert 'self.current_entry.usernames[0]' in source
