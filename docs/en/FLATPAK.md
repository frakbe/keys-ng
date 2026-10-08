# Building the Keys NG Flatpak on Linux

This guide documents the supported local build workflow for the Keys NG GUI Flatpak. The manifest and helper script are in packaging/flatpak/.

## 1. Package design

The Flatpak uses KDE Platform 6.11 and io.qt.PySide.BaseApp. It packages the GUI; the CLI and TUI remain available through the Python wheel or other native packages.

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

    git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
    python3 -m venv .flatpak-tools-venv
    . .flatpak-tools-venv/bin/activate
    python -m pip install --upgrade pip requirements-parser
    FLATPAK_PYTHON=.flatpak-tools-venv/bin/python sh packaging/flatpak/generate-python-sources.sh
    deactivate

requirements-parser is a build-tool dependency and should not be installed into a distribution-managed system Python. The generated JSON contains offline source definitions and is not part of the runtime sandbox.

The explicit `pybind11` entry in packaging/flatpak/requirements.txt is intentional: Pillow is built from source in the Flatpak sandbox and needs `pybind11` available before its metadata is generated.

## 4. Build and install locally

Run from the repository root:

    flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
    flatpak run org.keysng.KeysNG

## 5. Create a repository or bundle

To create a local OSTree repository:

    flatpak-builder --repo=repo-flatpak --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
    flatpak --user remote-add --if-not-exists keys-ng-local repo-flatpak
    flatpak --user install keys-ng-local org.keysng.KeysNG

To create a single-file bundle:

    flatpak build-bundle repo-flatpak Keys-NG.flatpak org.keysng.KeysNG

For Flathub or another public repository, publish the manifest and source metadata rather than relying only on a local bundle.

## 6. Validation checklist

At minimum, test:

- opening and unlocking a vault under the selected home directory;
- GnuPG key listing and encryption/decryption through the host;
- SSH and RDP launchers, when configured;
- KeePassXC KDBX and XML import;
- clipboard and TOTP behavior;
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
