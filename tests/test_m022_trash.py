import pytest

from keys_ng.errors import VaultError
from keys_ng.models import Entry, FolderStore
from keys_ng.storage.vault import Vault
from test_m14_folders import FakeCrypto


def test_trash_lifecycle_and_restore(tmp_path):
    vault = Vault.init(tmp_path / 'vault', FakeCrypto(), ['RECIPIENT'], 'SIGNER')
    entry = vault.save_entry(Entry.create('Credential', password='synthetic', tags=['work', 'vpn']))
    vault.delete_entry(entry.id)
    trashed = vault.get_entry(entry.id)
    assert trashed.folder_id == vault.trash_folder_id
    assert trashed.password == 'synthetic' and trashed.tags == ['work', 'vpn']
    assert trashed.revision == entry.revision + 1
    vault = Vault(vault.path, FakeCrypto())
    assert vault.catalog_health() == (True, [])
    vault.move_entry(entry.id, None)
    assert vault.get_entry(entry.id).folder_id is None
    vault.delete_entry(entry.id)
    vault.delete_entry(entry.id)
    with pytest.raises(VaultError):
        vault.get_entry(entry.id)
    assert vault.catalog_health() == (True, [])


def test_migration_idempotency_and_protection(tmp_path):
    vault = Vault.init(tmp_path / 'vault', FakeCrypto(), ['RECIPIENT'], 'SIGNER')
    vault._write_folders(FolderStore())
    vault._write_catalog(vault._sync_catalog_folders(store=FolderStore()))
    vault = Vault(vault.path, FakeCrypto())
    trash = vault.trash_folder_id
    assert len(vault.list_folders()) == 1
    assert Vault(vault.path, FakeCrypto()).trash_folder_id == trash
    for operation in (lambda: vault.rename_folder(trash, 'Other'),
                      lambda: vault.move_folder(trash, None), lambda: vault.delete_folder(trash)):
        with pytest.raises(VaultError):
            operation()
    assert vault.catalog_health() == (True, [])


def test_empty_trash_preserves_active_entries_and_lock(tmp_path):
    vault = Vault.init(tmp_path / 'vault', FakeCrypto(), ['RECIPIENT'], 'SIGNER')
    active = vault.save_entry(Entry.create('Active'))
    for index in range(3):
        item = vault.save_entry(Entry.create(str(index)))
        vault.delete_entry(item.id)
    nested = vault.create_folder('Old trash subfolder', vault.trash_folder_id)
    vault.save_entry(Entry.create('Nested', folder_id=nested.id))
    vault.lock()
    with pytest.raises(VaultError):
        vault.empty_trash()
    vault.unlock()
    vault.empty_trash()
    assert [i.id for i in vault.list_items()] == [active.id]
    assert vault.get_folder(vault.trash_folder_id).name == 'Trash'
    vault.empty_trash()
    assert vault.catalog_health() == (True, [])


@pytest.mark.parametrize('privacy', ['minimal', 'standard', 'full'])
def test_used_tags_respects_catalog_privacy(tmp_path, privacy):
    vault = Vault.init(tmp_path / 'vault', FakeCrypto(), ['RECIPIENT'], 'SIGNER', catalog_privacy=privacy)
    vault.save_entry(Entry.create('A', tags=['work', 'vpn']))
    vault.save_entry(Entry.create('B', tags=['work', 'personal']))
    assert vault.used_tags() == ['personal', 'vpn', 'work']
    if privacy == 'minimal':
        assert all(not item.tags for item in vault.list_items())
