# Keys NG 0.1.26

## Bug fixes and usability improvements

- KeePassXC XML/KDBX imports no longer abort when an entry contains a dangling UUID reference. The original reference is retained, the affected entry is reported as partial, and the import continues.
- GUI and TUI search fields accept Down to move focus to the result list.
- GUI and TUI preserve expanded/collapsed folder state across normal vault lock/unlock.
- Release metadata and documentation are aligned with 0.1.26.

Malformed XML, reference cycles, and empty referenced fields still abort import because they cannot be safely represented as a completed migration.
