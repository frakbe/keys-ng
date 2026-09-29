import pytest

from keys_ng.errors import LegacyFormatError
from keys_ng.migration.legacy_parser import parse_legacy_record


def test_parse_legacy_website_record():
    parsed = parse_legacy_record("target='https://example.com'\nuser='alice'\npassword='pw'\nnote='hello'\n")
    assert parsed["target"] == "https://example.com"
    assert parsed["password"] == "pw"


def test_reject_command_substitution():
    with pytest.raises(LegacyFormatError):
        parse_legacy_record("user=$(id)\n")
