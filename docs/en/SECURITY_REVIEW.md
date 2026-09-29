# Keys NG M1.18 Security Review

## Status and scope

This is an **internal engineering review**, not an independent security audit. It covers the source shipped as `0.1.18.dev1`. The review concentrated on cryptographic process invocation, signature policy, record/catalog integrity, filesystem writes, import parsers, references, clipboard handling, external launchers and configuration boundaries.

## Review method

The M1.18 review used source inspection, AST-based security lint, unit/integration tests, deterministic malformed-input tests, fault injection around atomic replacement, and regression tests for rollback/replacement detection. The release also contains an exhaustive bilingual code-review manual whose symbol coverage is enforced by tests.

External Ruff/Bandit/pip-audit binaries were not available in the isolated build environment used to assemble this artifact, so their execution is **not claimed** in this report. They remain declared development tools for connected CI/developer environments. The dependency-free `tools/security_static_check.py` was executed successfully.

## Findings fixed in M1.18

### SR-117-01 — Isolated record rollback/replacement was not rejected on ordinary read

**Previous behavior:** `catalog_health()` could report a ciphertext SHA-256 mismatch, but `get_entry()` decrypted and returned the record without requiring that the record matched the signed catalog.

**Fix:** `Vault.get_entry()` now calls `_verify_record_binding()`. The decrypted payload UUID must match the filename UUID; the catalog must contain the record; ciphertext SHA-256 must match; and entry revision must match the catalog revision. A mismatch fails closed with `VaultError`.

**Residual risk:** an attacker able to roll back both a valid signed catalog and its corresponding valid signed records can still restore an older coherent snapshot. Preventing this requires trusted monotonic state outside the synchronized vault.

### SR-117-02 — POSIX vault directories depended on the caller's umask

**Previous behavior:** ciphertext files were created `0600`, but the vault root and `records/`/`inbox/` directories used normal `mkdir` defaults.

**Fix:** vault initialization creates/chmods these directories to `0700` on POSIX; `vault.json` remains `0600`.

### SR-117-03 — Signature-required configuration could be created without a signer

**Previous behavior:** `require_signature=True` could coexist with `signer=None`, producing a configuration unable to satisfy its own signature policy.

**Fix:** `VaultConfig.validate()` now requires both a signer and at least one trusted signer whenever signature verification is enabled.

### SR-117-04 — Process backend fingerprint syntax accepted values shorter than a full modern fingerprint

**Previous behavior:** any hexadecimal selector of at least 32 characters passed the preliminary syntax test before key-list matching.

**Fix:** `GPGProcessBackend.resolve_fingerprint()` accepts only 40- or 64-hex-character full fingerprints before exact matching against GnuPG output.

## Security properties confirmed by review

- Cryptographic and launcher subprocesses use argv arrays and `shell=False`.
- No `eval`, built-in `exec`, `compile`, `os.system` or `os.popen` is present in `src/keys_ng` according to the M1.18 AST check.
- Private-key passphrases are not accepted by Keys NG APIs; GnuPG/gpg-agent/pinentry own that interaction.
- Atomic vault writes persist ciphertext only, fsync the file, replace atomically and fsync the containing directory on POSIX.
- Legacy Bash records are parsed as text/data and never executed.
- KeePassXC XML import rejects DTD/entity declarations before parsing.
- UUID references are same-vault whole-field references, bounded to 32 levels and cycle-checked.
- Command actions reject `shell=True`; SSH option validation is argv-oriented.
- Unsigned inbox records require explicit operator approval before import.
- Search catalog and folder cache are cleared on normal lock; hard lock additionally asks the crypto backend to terminate gpg-agent.

## Accepted risks / follow-up items

### Coordinated rollback

Current signatures authenticate a snapshot but do not prove freshness. A future design may store a monotonic checkpoint outside the synchronized vault, use an append-only transparency log, or integrate a trusted version service. This must not be added casually because it changes offline recovery semantics.

### Python memory lifetime

Passwords/TOTP seeds can exist in immutable Python `str`/`bytes` objects and may be copied by GUI widgets, JSON decoding and clipboard code. Deterministic zeroization cannot be guaranteed. See `MEMORY_REVIEW.md`.

### Clipboard history

Keys NG clears only the clipboard value it can still identify/control. Desktop clipboard managers may preserve historical copies.

### Same-user endpoint compromise

A malicious process with the same user privileges can potentially read clipboard, process memory, agent sockets or invoke authorized GnuPG operations. Hard lock reduces cached-agent exposure but is not an endpoint-compromise defense.

### Trusted external actions

`shell=False` removes shell metacharacter interpretation by Keys NG. It does not make arbitrary command actions harmless, and OpenSSH options such as `ProxyCommand`/`LocalCommand` can execute programs by design. Records containing such actions are trusted executable configuration.

### Flatpak host access

The Flatpak design intentionally delegates GnuPG/SSH/RDP to the host using `flatpak-spawn --host` and requests access to the Flatpak portal service. This reduces key duplication but broadens the sandbox trust boundary. The final Flatpak manifest should receive an independent packaging-specific review before stable publication.

## Release conclusion

M1.18 materially improves fail-closed integrity behavior and reviewability without changing the fundamental per-record OpenPGP design. It remains a pre-1.0, non-independently-audited password manager. Production use should retain tested backups and an independent recovery path until an external review has been completed.

## M1.18 TUI parity review notes

- GUI and TUI editor conversion now share `services.entry_editor`, reducing validation drift between frontends.
- Folder rename/move validates a cloned `FolderStore`; rejected operations cannot leave the decrypted folder cache partially mutated.
- Folder move rejects duplicate sibling names as well as cycles.
- TUI destructive operations require confirmation; mutation is delegated to `Vault`.
- Clipboard result banners never display the copied secret, only the value category/status. Theme semantic colors are the default; user color overrides affect presentation only.
- TOTP QR import in the TUI reads a user-selected local image path and passes it to the existing QR decoder.
