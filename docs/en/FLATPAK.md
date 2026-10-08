# Building the Keys NG Flatpak on Linux

This guide documents the supported workflow for building the Keys NG Flatpak. The manifest and helper script are in packaging/flatpak/.

## 1. Package design

The Flatpak uses KDE Platform 6.11 and io.qt.PySide.BaseApp. The package contains the GUI, TUI and CLI. The GUI is the default command; the TUI and CLI are started explicitly with the `--command` option.

Keys NG deliberately delegates GnuPG, SSH and RDP operations to the host through flatpak-spawn --host. The host must provide GnuPG/gpg-agent, pinentry, the configured SSH terminal/client and the configured RDP client.

## 2. Prerequisites

On Debian or Ubuntu:

    sudo apt install flatpak flatpak-builder git python3 python3-venv

On Fedora:

    sudo dnf install flatpak flatpak-builder git python3

Add Flathub and install the KDE runtime and SDK:

    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub org.kde.Sdk//6.11 org.kde.Platform//6.11

Verify that flatpak, flatpak-builder, Python 3 and git are available. Package names can differ between distributions.

## 3. Generate Python dependency sources

The manifest expects packaging/flatpak/python3-flatpak-requirements.json. Generate it from requirements.txt before the first build.

The `flatpak-pip-generator` tool requires the Python package `requirements-parser`. Two alternative modes are supported.

### Mode A: install into the user Python environment

Use this mode if the distribution allows packages to be installed into the user site:

    git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
    python3 -m pip install --user --upgrade pip requirements-parser
    FLATPAK_PYTHON=python3 sh packaging/flatpak/generate-python-sources.sh

If the distribution-managed Python blocks this installation, use the virtual environment mode below. Do not run `deactivate` in this mode.

### Mode B: isolated virtual environment (recommended)

    git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
    python3 -m venv .flatpak-tools-venv
    . .flatpak-tools-venv/bin/activate
    python -m pip install --upgrade pip requirements-parser
    FLATPAK_PYTHON=.flatpak-tools-venv/bin/python sh packaging/flatpak/generate-python-sources.sh
    deactivate

`requirements-parser` is only needed by the build tool and is not included in the runtime sandbox. The generated JSON contains the offline dependency sources.

The explicit `pybind11`, `scikit-build-core` and `nanobind` entries in packaging/flatpak/requirements.txt are intentional: Pillow and zxing-cpp are built from source in the Flatpak sandbox and require these build dependencies.

## 4. Build and install locally

Run from the repository root:

    flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml

Launch the GUI, which is the default command:

    flatpak run org.keysng.KeysNG

Launch the three interfaces explicitly:

    flatpak run --command=keys-ng-gui org.keysng.KeysNG
    flatpak run --command=keys-ng-tui org.keysng.KeysNG
    flatpak run --command=keys-ng org.keysng.KeysNG --help

The TUI and CLI must be started from a terminal. CLI arguments are added after the application ID, for example:

    flatpak run --command=keys-ng org.keysng.KeysNG vault-list

## 5. Create a redistributable bundle

First generate a local OSTree repository:

    rm -rf repo-flatpak build-flatpak
    flatpak-builder --repo=repo-flatpak --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml

Then create the single `.flatpak` file:

    flatpak build-bundle repo-flatpak Keys-NG-0.1.24.flatpak org.keysng.KeysNG --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo

The file can be installed on another system with:

    flatpak install --user Keys-NG-0.1.24.flatpak

The `--runtime-repo` option tells Flatpak where to obtain the KDE runtime and BaseApp, which are not fully embedded in the bundle.

To publish a checksum as well:

    sha256sum Keys-NG-0.1.24.flatpak > SHA256SUMS

For Flathub or another public repository, publishing an updateable OSTree repository is preferable to distributing only a local bundle.

## 6. Validation checklist

At minimum, test:

- opening and unlocking a vault under the selected home directory;
- GnuPG key listing and encryption/decryption through the host;
- SSH and RDP launchers, when configured;
- KeePassXC KDBX and XML import;
- clipboard and TOTP behavior;
- launching GUI, TUI and CLI;
- the application menu entry and the GUI version shown under Help.

Useful commands:

    flatpak info org.keysng.KeysNG
    flatpak run org.keysng.KeysNG

## 7. Permissions and security

The manifest currently requests home filesystem access, Wayland and fallback X11 sockets, DRI access, and D-Bus access to org.freedesktop.Flatpak.

These permissions are intentional but broad. The package is not fully isolated from the user's vault or host credential tools: it reuses the host GnuPG keyring/agent and launches host SSH/RDP helpers. Review these permissions before distributing the Flatpak.

## 8. Updating the package

When Python dependencies change, update packaging/flatpak/requirements.txt and regenerate the JSON source module. Build and test again, then update the application version and org.keysng.KeysNG.metainfo.xml for a release.

The Python wheel remains the recommended distribution format for CLI/TUI and for environments where host delegation is not wanted.
