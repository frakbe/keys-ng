# Keys NG M1.18 Threat Model

## Scope

This threat model covers Keys NG `0.1.18.dev1`, its Python core, CLI/TUI/GUI front ends, GnuPG subprocess backend, encrypted vault layout, clipboard helpers, external action launchers, import/export paths and desktop packaging. It does not claim to secure a fully compromised operating system.

## Assets

The primary assets are credential passwords, usernames where sensitive, TOTP seeds, notes/custom fields, private OpenPGP keys, the integrity of record/folder/catalog metadata, and the user's ability to recover the vault. Public OpenPGP fingerprints, UUID filenames, application settings and `vault.json` policy are not treated as secret, although they can reveal operational metadata.

## Trust boundaries

1. **Python process memory.** Decrypted entries and generated OTP/password strings exist here. Python cannot guarantee deterministic zeroization of immutable objects.
2. **GnuPG / gpg-agent / Pinentry.** Keys NG delegates private-key operations and passphrase entry/cache to these components. The private-key passphrase is never intentionally requested by Keys NG.
3. **Persistent vault storage.** Credential records, catalog and folders are expected to be OpenPGP ciphertext. Atomic-write temporary files contain ciphertext only.
4. **Cleartext configuration.** `vault.json` and the per-user TOML settings contain policy/preferences, never credential secrets by design.
5. **Clipboard.** Once a secret is copied, the desktop clipboard service and any history manager become part of the trust boundary.
6. **External programs.** SSH/RDP/browser/command actions execute programs outside Keys NG. `shell=False` prevents shell parsing, but OpenSSH options such as `ProxyCommand` and `LocalCommand` can themselves execute commands and are therefore trusted record configuration.
7. **Flatpak host bridge.** When packaged as Flatpak, host delegation intentionally crosses the sandbox boundary to use the host GnuPG agent and launchers. This permission is security-sensitive and must be reviewed as packaging evolves.

## Attacker classes

### Stolen or copied vault only

The attacker obtains the vault directory or a cloud-synchronized copy, but not a usable private key. Confidentiality depends on OpenPGP recipient encryption. Signed vault objects also provide authenticity against arbitrary ciphertext substitution.

### Cloud synchronization attacker

The attacker can add, remove, replace or replay synchronized ciphertext files. M1.18 verifies signatures and additionally binds each opened record to the signed catalog through the ciphertext SHA-256 and entry revision. This detects a record-only rollback/replacement while the catalog remains current. Coordinated rollback of both the record and the signed catalog is **not** prevented without an external monotonic state or trusted version service.

### Local unprivileged process

The attacker runs under another account without permission to read the vault. On POSIX, M1.18 creates the vault root, `records/` and `inbox/` with mode `0700`; ciphertext/config files are written with restrictive permissions. OS ACLs and administrator/root access remain outside this control.

### Same-user malware

A process running as the same user may read process memory, clipboard, input events, GnuPG agent sockets or invoke GnuPG while authorization is cached. Neither Keys NG nor KeePass-style password managers can provide strong confidentiality against a fully compromised user session. Hard lock kills the shared `gpg-agent`, but this has global side effects for other applications.

### Malicious imported data

KeePassXC XML, legacy records, inbox deposits, QR data and configuration are untrusted inputs. Legacy records are parsed as data and never sourced. XML import rejects DTD/entity constructs. Model validation constrains UUIDs, actions, TOTP parameters and folder topology. Fuzz-oriented regression tests exercise parser failure paths.

### Malicious vault author / trusted record

An authorized signer can place command actions and advanced SSH options in a record. Keys NG does not invoke a shell, but launching a trusted command or OpenSSH option can intentionally execute external code. This is an authorization boundary, not an injection defense failure.

## Security objectives

- No intentional plaintext credential persistence.
- No private-key passphrase handling by Python.
- No shell interpretation for crypto/import/launch paths.
- Full-signature verification for signed vault policy.
- Per-record cryptographic compartmentalization.
- Encrypted search/folder metadata with RAM-only caches while unlocked.
- Fail closed on record/catalog mismatch.
- Explicit opt-in for unsigned inbox import.
- Bounded recursive reference resolution with cycle detection.
- Portable emergency recovery through CLI/GnuPG.

## Explicit non-goals and residual risks

- Protection against kernel/root compromise or same-user malware with memory/input access.
- Guaranteed erasure of Python string/bytes objects from RAM.
- Guaranteed deletion from clipboard history managers.
- Coordinated rollback protection for an entire signed vault snapshot.
- Hiding vault existence, record count, UUID filenames, file sizes or update timing.
- Preventing trusted external programs from mishandling a secret after Keys NG hands control to them.
- Formal verification of OpenPGP/GnuPG or third-party GUI/runtime libraries.

## Security decision points for an independent reviewer

A review should prioritize `storage/vault.py`, `crypto/gpg_process.py`, `storage/atomic.py`, `storage/inbox.py`, `services/clipboard*.py`, `services/actions.py`, `services/ssh_options.py`, migration parsers, and all code that turns untrusted serialized input into domain objects. The bilingual `CODE_REVIEW_MANUAL.md` files provide a source-line and call-map index for every executable symbol.

### Interactive TUI mutation boundary

M1.18 adds create/edit/move/delete workflows to the Textual frontend. The TUI does not write vault files directly: it converts editor state through the shared `services.entry_editor` validation path and delegates persistence/reorganization to `Vault`. Password and TOTP values are plaintext in Textual/Python widget memory while an editor is open; a same-user process-memory attacker remains outside the confidentiality guarantee.
