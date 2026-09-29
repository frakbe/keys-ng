# Keys NG M1.18 Memory and Secret-Lifetime Review

Keys NG deliberately avoids persistent plaintext files, but this does **not** mean plaintext never exists. Decryption necessarily creates plaintext in process memory.

## Secret-bearing objects

- `DecryptionResult.plaintext`: immutable Python `bytes` returned by the crypto backend.
- `Entry.password`: Python `str` after JSON decoding.
- `TotpConfig.secret`: Python `str`.
- Resolved UUID references: returned as Python strings and may transiently duplicate another entry's username/password.
- Generated passwords and TOTP codes: Python strings.
- GUI widget text and clipboard MIME data: copies managed partly by Qt/platform services.
- CLI clipboard helper stdin: a pipe containing UTF-8 secret bytes until consumed by the helper.

## What M1.18 does well

- Decrypted credential records are not intentionally written to persistent storage.
- The encrypted catalog never includes passwords or TOTP seeds.
- Catalog/folder plaintext caches are cleared by `Vault.lock()`; entry objects are not globally cached by the core vault service.
- Secrets are not intentionally placed in subprocess argv or environment variables by clipboard/GnuPG paths.
- Clipboard helper receives the secret over stdin rather than argv.
- GnuPG passphrases remain outside Python.

## Limits imposed by Python/Qt

Immutable `str` and `bytes` objects cannot be reliably wiped in place. JSON parsing and GUI assignment can create additional copies with lifetimes controlled by CPython/Qt internals. Deleting a Python reference or letting it go out of scope does not prove that the backing memory was overwritten immediately.

For this reason M1.18 makes no `secure_zero()` claim. A reviewer should treat a same-user memory-reading attacker as outside the confidentiality guarantee while a secret has been used recently.

## Recommended future work

- Minimize conversion between `bytes` and `str` in security-critical paths.
- Avoid long-lived entry caches containing password/TOTP material.
- Keep detail widgets cleared immediately on lock/tab close.
- Consider a narrowly scoped mutable secret-buffer abstraction only where it measurably reduces copies; do not advertise guaranteed zeroization unless verified for the full Python/Qt path.
- Add process-memory experiments on each supported OS as empirical tests, clearly separated from formal guarantees.

## M1.18 TUI editor lifetime

The modal `EntryEditorScreen` holds username/password/TOTP fields in Textual widget objects while the editor is visible. Dismissing the screen releases application references, but Python and Textual do not provide a verifiable secure-zero guarantee. The implementation avoids persistence before `Vault.save_entry()` and never places these secrets in command-line arguments; reviewers should nevertheless treat recently edited secrets as potentially recoverable from process memory under a same-user memory-read compromise.
