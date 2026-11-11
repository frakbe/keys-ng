from dataclasses import asdict
import pytest
from keys_ng.models import Entry
from keys_ng.services.references import make_entry_reference
from keys_ng.services.reference_info import inspect_reference
from test_m112_entry_references import make_vault


def test_chain_describes_origin_without_returning_values(tmp_path):
    vault = make_vault(tmp_path)
    folder = vault.create_folder('Accounts')
    origin = Entry.create('<b>Origin</b>', password='TOP-SECRET', folder_id=folder.id)
    middle = Entry.create('Middle', password=make_entry_reference('P', origin.id))
    vault.save_entry(origin)
    vault.save_entry(middle)
    info = inspect_reference(vault, make_entry_reference('P', middle.id))
    assert [h.title for h in info.hops] == ['Middle', '<b>Origin</b>']
    assert info.hops[-1].path == 'Accounts'
    assert not info.error
    assert 'TOP-SECRET' not in repr(asdict(info))


def test_unsaved_source_cycles_and_empty_fields(tmp_path):
    vault = make_vault(tmp_path)
    source = Entry.create('Source', password='stored')
    vault.save_entry(source)
    source.password = make_entry_reference('P', source.id)
    assert inspect_reference(vault, source.password, source=source).error == 'cycle'
    source.password = ''
    vault.save_entry(source)
    assert inspect_reference(vault, make_entry_reference('P', source.id)).error == 'empty'


@pytest.mark.parametrize('value', ['{REF:P@I:bad}', '{REF:U@I:------------------------------------}', '{REF:T@I:033054D445C648C59092CC1D661B1B71}'])
def test_malformed_reference(tmp_path, value):
    assert inspect_reference(make_vault(tmp_path), value).error == 'invalid'


def test_missing_locked_and_untrusted(tmp_path, monkeypatch):
    vault = make_vault(tmp_path)
    source = Entry.create('Source', password='secret')
    ref = make_entry_reference('P', source.id)
    assert inspect_reference(vault, ref).error == 'missing'
    vault.save_entry(source)
    def fail(entry_id):
        raise RuntimeError('secret must not appear')
    monkeypatch.setattr(vault, 'get_entry', fail)
    info = inspect_reference(vault, ref)
    assert info.error == 'unavailable'
    assert 'secret' not in repr(info)
    vault.lock(hard=False)
    assert inspect_reference(vault, ref).error == 'locked'


def test_depth_limit(tmp_path):
    vault = make_vault(tmp_path)
    value = 'end'
    for n in range(33):
        entry = Entry.create(str(n), password=value)
        vault.save_entry(entry)
        value = make_entry_reference('P', entry.id)
    assert inspect_reference(vault, value).error == 'depth'
