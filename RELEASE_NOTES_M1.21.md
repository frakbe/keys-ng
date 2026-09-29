# Keys NG 0.1.21 — RDP credentials and TUI notification fixes

Version: `0.1.21`

## Changes

- Linux RDP now passes the entry password to FreeRDP through stdin using `/from-stdin:force`; passwords are not placed in process arguments.
- RDP entries now expose an optional domain field in GUI and TUI. Empty domain uses `/d:.` for local accounts unless the username already embeds a domain.
- TUI vault-switch messages use the existing temporary banner instead of remaining permanently in the status area.
- TUI clipboard notifications are displayed sooner: the clipboard helper acknowledges immediately after a successful write instead of delaying the UI for the read-back verification.
- Linux RDP extra options remain separate argv items: one option per line in Preferences, or one string per item in the TOML `options` array.

## Linux RDP options example

```toml
[launchers.rdp.linux]
client = "auto"
options = ["/dynamic-resolution", "+clipboard", "/f", "/cert:ignore"]
```
