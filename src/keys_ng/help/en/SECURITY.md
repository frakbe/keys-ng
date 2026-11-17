# Security model (development draft)

Keys NG is security-sensitive software. Version `0.2.2` is a usable alpha awaiting independent security review and is not yet recommended as a sole password store.

## Design invariants

- Normal vault operations do not write decrypted records to persistent files. Explicit plaintext exports are an exception and must be protected by the user.
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
- The GPGME adapter is disabled in this build; the supported backend invokes GnuPG. Hardware-token integration still requires platform testing.
- External security review is required before a stable release.

## Reporting

Do not include real credentials, private keys, TOTP seeds, or decrypted vault data in bug reports.

## Inbox authorization boundary (M1.19.2)

A cryptographically valid OpenPGP signature is necessary but not sufficient for signed Inbox import. The signer's primary-key fingerprint must be present in the destination vault's `trusted_signers`. GnuPG ownertrust is not treated as vault authorization. Signing subkeys are normalized to their primary fingerprint when GnuPG supplies it via `VALIDSIG`. Unsigned import remains an explicit exceptional action; invalid signatures are rejected. Successful imports are re-encrypted and signed under the destination vault policy before the Inbox source is removed.

## Storage, tags and deletion (0.2.2)

Records are bound to catalog UUID, ciphertext SHA-256 and revision; this detects
record-only replacement, not rollback of a complete signed vault. Trash is an
encrypted folder and retains the original entry UUID and secrets. It is not a
security isolation boundary: references and explicit reads still work. Permanent
deletion unlinks ciphertext and updates the catalog; it is not secure erasure of
backups or filesystem snapshots. Multi-file updates are not a single transaction;
use catalog health checks and reviewed reindex recovery after interrupted writes.

Tags remain in encrypted records and, for `standard`/`full` privacy, in the
encrypted catalog. `minimal` excludes them from the catalog; editor suggestions
read records only while unlocked. No separate plaintext tag database is created.

## Review and implementation references

- [Release security checklist](https://github.com/frakbe/keys-ng/blob/v0.2.2/docs/en/RELEASE_SECURITY_CHECKLIST.md)
- [External security review](https://github.com/frakbe/keys-ng/blob/v0.2.2/docs/en/EXTERNAL_SECURITY_REVIEW.md)
- [Code review manual for 0.2.2](https://github.com/frakbe/keys-ng/blob/v0.2.2/docs/en/CODE_REVIEW_MANUAL.md)
- [Vault implementation](https://github.com/frakbe/keys-ng/blob/v0.2.2/src/keys_ng/storage/vault.py)
- [GnuPG agent and cache options](https://www.gnupg.org/documentation/manuals/gnupg/Agent-Options.html)
- [GnuPG trust model](https://www.gnupg.org/documentation/manuals/gnupg/GPG-Configuration-Options.html)
- [Python subprocess security considerations](https://docs.python.org/3/library/subprocess.html#security-considerations)
