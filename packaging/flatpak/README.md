# Keys NG Flatpak

Keys NG uses the Flathub `io.qt.PySide.BaseApp` on KDE/Qt 6.11. External GnuPG,
SSH and RDP programs are intentionally started on the host through
`flatpak-spawn --host`; this preserves the user's existing `gpg-agent`, keyring,
terminal emulator and RDP client. The manifest therefore requests access to
`org.freedesktop.Flatpak`.

Generate offline Python dependency sources, then build:

```sh
git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
packaging/flatpak/generate-python-sources.sh
flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
flatpak run org.keysng.KeysNG
```

To produce a single-file bundle:

```sh
flatpak build-bundle ~/.local/share/flatpak/repo Keys-NG.flatpak org.keysng.KeysNG
```

### Generator dependency (M1.17 clarification)

`flatpak-pip-generator` itself imports the PyPI package `requirements-parser`. Do not install that package into a distro-managed Python. Use a small build-only virtual environment instead:

```bash
python3 -m venv .flatpak-tools-venv
. .flatpak-tools-venv/bin/activate
python -m pip install requirements-parser
FLATPAK_PYTHON=.flatpak-tools-venv/bin/python packaging/flatpak/generate-python-sources.sh
deactivate
```

The virtual environment is only a build tool and is not included in the resulting Flatpak. Release source archives should ideally include the generated `python3-flatpak-requirements.json`; if it is absent, the command above is the supported regeneration path.
