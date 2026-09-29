# Keys NG M1.20.1 — TUI Preferences binding hotfix

Version: `0.1.20.dev1`

This hotfix fixes TUI startup on current Textual releases. The M1.20 binding `ctrl+,` for Preferences is not a valid Textual binding key because Textual treats comma as a separator between alternative bindings, producing an empty binding and raising `InvalidBinding` while the `App` class is created.

The TUI Preferences shortcut is now `Ctrl+Shift+P`. The Preferences feature itself is unchanged. A regression test rejects literal-comma binding keys that would recreate this startup failure.
