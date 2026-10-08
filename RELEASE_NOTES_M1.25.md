# Keys NG 0.1.25 — TUI preferences and launcher configuration

## Changes

- Aligned the TUI Preferences screen with the GUI Preferences dialog.
- Added TUI configuration for SSH terminal options and Linux, Windows and macOS RDP client options.
- Fixed TUI and GUI action launching to use the configured launcher settings.
- Removed the diagnostic logging checkbox from the TUI Preferences screen to keep the interface aligned with the GUI.
- Added visible, editable multiline fields for launcher argv options in the TUI.
- Added Flatpak build documentation for user Python and virtual-environment setup, interface commands and redistributable bundles.
- Added Flatpak build dependencies required by Pillow and zxing-cpp source builds.

The Flatpak continues to delegate GnuPG, SSH and RDP helpers to the host by design; review the documented permissions before distributing it.
