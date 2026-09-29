# Security model (development draft)

Keys NG is security-sensitive software. Version `0.1.7.dev0` is a development foundation and is not yet recommended as a sole password store.

## Design invariants

- Decrypted credential records are not intentionally written to persistent files.
- Python never asks for, stores, or forwards the private-key passphrase; GnuPG delegates this to `gpg-agent`/Pinentry.
- Subprocess execution never uses `shell=True` for cryptographic or migrated legacy operations.
- Credentials are encrypted as independent OpenPGP ciphertext files.
- Search metadata is stored in an encrypted, rebuildable catalog.
- Decrypted search catalog and folder metadata may be cached in RAM only while a vault is unlocked; normal and hard lock discard these caches. Passwords and TOTP seeds are never placed in the search catalog.
- Passwords and TOTP seeds are excluded from the catalog.
- Persistent temporary files used by atomic writes contain ciphertext only.
- Legacy Bash records are parsed as data and never sourced/executed.
- Signed vaults reject missing/invalid/untrusted signatures.

## Known limitations before a production release

- Python cannot guarantee deterministic zeroization of immutable secret objects in memory.
- Clipboard managers can retain copies after Keys NG clears the live clipboard.
- Rollback resistance requires further design beyond ordinary OpenPGP signatures.
- Multi-writer/cloud conflict handling is not complete.
- GUI/platform-specific auto-type is not implemented yet.
- GPGME backend and hardware-token integration require packaging/integration testing.
- External security review is required before a stable release.

## Reporting

Do not include real credentials, private keys, TOTP seeds, or decrypted vault data in bug reports.

## Inbox authorization boundary (M1.19.2)

A cryptographically valid OpenPGP signature is necessary but not sufficient for signed Inbox import. The signer's primary-key fingerprint must be present in the destination vault's `trusted_signers`. GnuPG ownertrust is not treated as vault authorization. Signing subkeys are normalized to their primary fingerprint when GnuPG supplies it via `VALIDSIG`. Unsigned import remains an explicit exceptional action; invalid signatures are rejected. Successful imports are re-encrypted and signed under the destination vault policy before the Inbox source is removed.
