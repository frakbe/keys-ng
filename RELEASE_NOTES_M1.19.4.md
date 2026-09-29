# Keys NG M1.19.4 — TUI Select sentinel hotfix

Version: `0.1.19.dev4`

This hotfix fixes a TUI crash triggered when Textual emits `Select.NULL` while rebuilding Inbox or trusted-signer options. The Inbox `Import all trusted` action refreshes the Select widget; newer Textual releases may temporarily set the selection to `Select.NULL`. M1.19.3 only treated `None` and `Select.BLANK` as empty, then attempted `int(str(Select.NULL))`.

M1.19.4 centralizes empty-selection handling and accepts `None`, `Select.BLANK`, and `Select.NULL` when present. The same guard is applied to the Trusted Signers screen. Regression tests ensure sentinel values are checked before converting selection values.
