# GUI 0.2.01 validation

## Automated release gate

The `Release 0.2.01` workflow runs on the staging branch `release/0.2.01` and
on the final `Release 0.2.01` commit on main. Both Python 3.11 and 3.12 must pass
before the main-branch publish job creates tag `v0.2.01` and uploads the wheel,
source archive and SHA-256 sums. Staging runs never create a release.

Commands used:

```sh
python -m pytest -q
python tools/security_static_check.py
python -m build
python -m venv .release-venv
.release-venv/bin/python -m pip install 'dist/keys_ng-0.2.1-py3-none-any.whl[gui,tui]'
.release-venv/bin/keys-ng --version
.release-venv/bin/keys-ng-tui version
QT_QPA_PLATFORM=offscreen .release-venv/bin/python tools/smoke_gui.py
.release-venv/bin/python tools/smoke_gpg.py
```

The GUI smoke exercises real Qt widgets against synthetic test records: folder
and vault search, selection, reference identity, clipboard expiry, source
navigation, read-only preview preserving a draft, editor clearing at lock,
editing/saving, moving, protected cross-field references, persisted layout,
independent multi-vault lock and global hard lock. It does not launch SSH/RDP.
The GnuPG smoke creates an isolated temporary keyring and validates signed,
encrypted records, reference inspection, lock/unlock and reopening. It never
uses the user's keyring. The temporary agent/keyring are removed afterwards.

Local preparation: 181 regression tests and security static check passed;
offscreen GUI smoke passed on Linux/Python 3.12. Real GnuPG could not run locally
because the execution environment forbids agent sockets (`Operation not
permitted`). Real OpenPGP and Python 3.11 checks are mandatory in GitHub Actions,
not inferred from the local GUI test. See the workflow run for final results.
Ruff reports existing module-wide lint findings; a clean full-project Ruff run
is not claimed. The introduced reference modules pass their targeted check.

## Manual desktop checklist still required

- [ ] Linux Wayland/X11: native clipboard ownership/expiry, pinentry and HiDPI.
- [ ] Windows and macOS: startup, text/controls at 100–200% scale, light/dark theme,
      keyboard focus, column/splitter restoration and native packaging.
- [ ] Drag entries between folders and nested folders; verify contents after reopening.
- [ ] Test the translated Italian editor with long names, paths and reference chains.
- [ ] Launch configured SSH/RDP clients and browser using test accounts.
- [ ] Verify unavailable/trust-failed sources and real agent prompts.
- [ ] Complete independent security review; this release does not replace it.
