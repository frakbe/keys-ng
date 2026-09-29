# Keys NG M1.19.1 — Diagnostics and Windows GnuPG hotfix

Version: `0.1.19.dev1`

M1.19.1 is a diagnostic/hotfix release based on M1.19.

## Changes

- Persistent, opt-in rotating diagnostic logs configured through `[diagnostics]` in `config.toml`.
- Timing traces for GUI entry selection, vault read/decrypt/parse/binding, and GnuPG subprocesses.
- Diagnostic status/path in `keys-ng doctor`.
- Windows `CREATE_NO_WINDOW` for GnuPG and `gpgconf`, preventing transient console-window flashes.
- Diagnostics disabled by default.
- GnuPG logs expose operation names only; argument values, fingerprints and filenames are omitted.
- GUI diagnostic errors record exception type rather than exception text.
- EN/IT user/developer docs and exhaustive code-review manuals updated.
- Regression tests for settings and diagnostic argument redaction.

## Enable diagnostics

```toml
[diagnostics]
enabled = true
level = "DEBUG"
log_file = ""
max_bytes = 2000000
backup_count = 3
```

Restart Keys NG, reproduce the problem, close it, then use `keys-ng doctor` to identify the default log location. Review the log before sharing it and disable diagnostics afterwards if continuous logging is not required.

Diagnostic code does not intentionally record credential plaintext, usernames, URLs, TOTP values, clipboard contents, entry titles, UUIDs or GnuPG argument values.
