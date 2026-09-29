# Keys NG M1.20.2 — GUI KeePassXC file-dialog hotfix

Version: `0.1.20.dev2`

M1.20.2 fixes a GUI crash introduced by the M1.20 KeePassXC import/export dialogs.

## Fixed

- `KeePassXCImportDialog.browse_source()` no longer assigns the `QFileDialog` filter result to `_`, which is also the module's gettext translation function.
- `KeePassXCImportDialog.browse_key_file()` receives the same fix.
- Whole-vault KeePassXC XML export receives the same preventive fix.
- Added an AST regression test that fails if any GUI function both calls gettext `_()` and binds a local variable named `_`.

The bug was pure Python name shadowing: an assignment such as `path, _ = QFileDialog...` makes `_` local to the whole function, so earlier `_('...')` calls raise `UnboundLocalError` before the dialog can open.
