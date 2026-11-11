"""Exercise real OpenPGP storage with a disposable, isolated test keyring."""
import os
from pathlib import Path
import subprocess
import tempfile

from keys_ng.crypto.gpg_process import GPGProcessBackend
from keys_ng.models import Entry
from keys_ng.services.reference_info import inspect_reference
from keys_ng.services.references import make_entry_reference
from keys_ng.storage.vault import Vault


def run():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        home = root / 'gnupg'
        home.mkdir(mode=0o700)
        base = ['gpg', '--homedir', str(home), '--batch']
        try:
            subprocess.run(base + ['--pinentry-mode', 'loopback', '--passphrase', '', '--quick-generate-key',
                                  'Keys NG disposable smoke <smoke@example.invalid>', 'rsa2048', 'sign,encr', '1d'],
                           check=True, capture_output=True)
            listing = subprocess.run(base + ['--with-colons', '--list-secret-keys'], check=True, capture_output=True, text=True).stdout
            fingerprint = next(line.split(':')[9] for line in listing.splitlines() if line.startswith('fpr:'))
            backend = GPGProcessBackend(homedir=str(home))
            vault = Vault.init(root / 'vault', backend, [fingerprint], fingerprint)
            folder = vault.create_folder('Accounts')
            origin = Entry.create('Origin', usernames=['smoke-user'], password='synthetic-smoke-secret', folder_id=folder.id)
            consumer = Entry.create('Consumer', usernames=[make_entry_reference('U', origin.id)], password=make_entry_reference('P', origin.id))
            vault.save_entry(origin)
            vault.save_entry(consumer)
            assert vault.resolved_password(consumer) == 'synthetic-smoke-secret'
            info = inspect_reference(vault, consumer.password)
            assert info.hops[0].title == 'Origin' and info.hops[0].path == 'Accounts'
            assert not info.error and 'synthetic-smoke-secret' not in repr(info)
            vault.lock(hard=False)
            assert inspect_reference(vault, consumer.password).error == 'locked'
            vault.unlock()
            assert vault.resolved_username(consumer.id) == 'smoke-user'
            reopened = Vault(root / 'vault', backend)
            assert reopened.resolved_password(consumer.id) == 'synthetic-smoke-secret'
            assert all(b'synthetic-smoke-secret' not in p.read_bytes() for p in (root / 'vault').rglob('*.gpg'))
        finally:
            subprocess.run(['gpgconf', '--homedir', str(home), '--kill', 'all'], check=False, capture_output=True)
    print('GnuPG smoke passed: signed encrypted CRUD, reference metadata, lock/unlock, reopen; temporary keyring removed')


if __name__ == '__main__':
    run()
