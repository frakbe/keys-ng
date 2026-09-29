# Keys NG M1.19 — Building Windows MSI packages with Briefcase

This document records the Windows build procedure validated during the M1.18.1/M1.19 packaging work. It is intended for maintainers and release reviewers. The build host is Windows; the resulting MSI must then be tested on a clean Windows account or VM.

## 1. Build environment versus runtime environment

| Component | Build host | End-user runtime | Purpose |
|---|---:|---:|---|
| Python 3.11+ | required | bundled by Briefcase | build tooling/application runtime |
| Git for Windows | required for the verified build workflow | no | Briefcase/template/source operations used by the build |
| Briefcase | required | no | create/build/package |
| WiX/toolchain downloaded/used by Briefcase | required during packaging | no | MSI generation |
| Gpg4win / GnuPG | strongly recommended for smoke tests | required | OpenPGP, gpg-agent, pinentry |
| PySide6/Textual/application dependencies | resolved by Briefcase | bundled | GUI/TUI runtime |

Git is **not a runtime dependency of Keys NG**. However, the Windows Briefcase build used for this project failed when Git was absent. Install **Git for Windows** from `https://git-scm.com` before running Briefcase.

## 2. Prerequisites

Install a supported 64-bit Python and Git for Windows. For runtime tests also install Gpg4win and create or import at least one test key pair.

Open PowerShell and verify:

```powershell
py --version
git --version
Get-Command git
```

For GnuPG runtime tests:

```powershell
gpg --version
gpgconf --version
```

M1.19 can automatically discover common Gpg4win/GnuPG installations even when `gpg.exe` is not on `PATH`. For an older build, the temporary diagnostic workaround was:

```powershell
$env:Path += ";C:\Program Files\GnuPG\bin"
```

That workaround should normally be unnecessary with M1.19.

## 3. Prepare an isolated build environment

From the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install briefcase
```

Verify:

```powershell
python --version
git --version
python -m briefcase --version
```

## 4. Packaging metadata that must remain valid

The project uses PEP 639 metadata:

```toml
[project]
license = "GPL-3.0-or-later"
license-files = ["LICENSE"]
```

The file `LICENSE` must exist in the repository root. Do not revert to the deprecated `license = { file = ... }` form.

Briefcase application names must match a source package. M1.19 provides:

```text
keys_ng      -> src/keys_ng       -> GUI
keys_ng_cli  -> src/keys_ng_cli   -> CLI wrapper
keys_ng_tui  -> src/keys_ng_tui   -> TUI wrapper
```

The GUI launcher is `src/keys_ng/__main__.py`; the console wrappers delegate to `keys_ng.cli.main` and `keys_ng.tui.main`.

## 5. Build the GUI MSI

Create the native Windows project:

```powershell
python -m briefcase create windows -a keys_ng
```

Build it:

```powershell
python -m briefcase build windows -a keys_ng
```

Run it **before packaging**:

```powershell
python -m briefcase run windows -a keys_ng
```

Then create the MSI:

```powershell
python -m briefcase package windows -a keys_ng -p msi
```

The MSI is written under `dist\`.

## 6. Build the CLI and TUI console applications

CLI:

```powershell
python -m briefcase create windows -a keys_ng_cli
python -m briefcase build windows -a keys_ng_cli
python -m briefcase run windows -a keys_ng_cli -- version
python -m briefcase package windows -a keys_ng_cli -p msi
```

TUI:

```powershell
python -m briefcase create windows -a keys_ng_tui
python -m briefcase build windows -a keys_ng_tui
python -m briefcase run windows -a keys_ng_tui -- --version
python -m briefcase package windows -a keys_ng_tui -p msi
```

The `--` separator passes following arguments to the packaged console application rather than Briefcase.

## 7. Clean rebuild after structural configuration changes

If `pyproject.toml`, application names, `sources`, license metadata, or launchers change, do not trust a stale Briefcase scaffold. From PowerShell:

```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force windows -ErrorAction SilentlyContinue
```

Then repeat `briefcase create` and `briefcase build`.

## 8. Runtime smoke test checklist

On a Windows system with Gpg4win installed:

```text
[ ] MSI installs without administrative surprises
[ ] Start-menu entry and icon are correct
[ ] GUI starts
[ ] `keys-ng doctor` reports the resolved gpg.exe and gpgconf.exe paths
[ ] `keys-ng keys` lists the test key(s)
[ ] GnuPG pinentry appears when private-key authorization is needed
[ ] existing vault opens
[ ] New Vault wizard can create and immediately open a vault
[ ] create/edit/save entry works
[ ] Show/Hide password works
[ ] clipboard timed clearing behaves as documented
[ ] TOTP generation works
[ ] lock and hard-lock work
[ ] CLI works from a terminal
[ ] TUI starts and can create/open a vault
[ ] uninstall removes the application cleanly
```

## 9. Troubleshooting from real packaging tests

### `sources ... does not include a package named ...`

The Briefcase app name and its source package are inconsistent. M1.19 deliberately uses `keys_ng` for the GUI because the real package is `src/keys_ng`.

### `does not define either sources or external_package_path`

A stale subsection such as `[tool.briefcase.app.keys_ng_gui.windows]` can make Briefcase interpret `keys_ng_gui` as another application. Search the entire `pyproject.toml` for obsolete app names.

```powershell
Select-String -Path pyproject.toml -Pattern "keys_ng_gui"
```

### `Your project does not include any license files`

Verify both PEP 639 metadata and the physical `LICENSE` file:

```powershell
Test-Path .\LICENSE
```

### Git not found / Briefcase cannot complete project creation

Install Git for Windows from `https://git-scm.com`, open a new PowerShell session, and verify:

```powershell
git --version
Get-Command git
```

### `Unable to execute GnuPG: [WinError 2]`

M1.19 searches `PATH`, Windows installation information and standard Gpg4win/GnuPG locations. Run:

```powershell
keys-ng doctor
```

If required, set explicit paths in Keys NG Preferences or in `config.toml`:

```toml
[gnupg]
gpg = "C:\\Program Files\\GnuPG\\bin\\gpg.exe"
gpgconf = "C:\\Program Files\\GnuPG\\bin\\gpgconf.exe"
```

### Changes to Briefcase configuration seem ignored

Delete `build`/`windows` as described in section 7 and recreate the native project.

## 10. Release rule

A successful `package` command is not sufficient for release. The maintainer must run `create`, `build`, `run`, and `package`, then perform the runtime checklist on a Windows environment with Gpg4win. Keep the resulting MSI hashes with the release artifacts.
