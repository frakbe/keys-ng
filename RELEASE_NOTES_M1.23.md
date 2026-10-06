# Keys NG 0.1.23 — TUI standalone export bugfix

## Bug fix

- Fixed the TUI standalone encrypted-entry export screen when no usable recipient public keys are initially available.
- The recipient and signing-key selectors now accept an empty initial state and provide validation feedback instead of raising Textual's EmptySelectError.
- Added regression coverage for the empty-selector behavior.

This release contains the 0.1.22 functionality plus this TUI bug fix.
