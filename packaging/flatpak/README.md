# Keys NG Flatpak

Guida operativa completa: docs/en/FLATPAK.md e docs/it/FLATPAK.md.

Keys NG uses the Flathub `io.qt.PySide.BaseApp` on KDE/Qt 6.11. The Flatpak
contains the GUI, TUI and CLI. External GnuPG, SSH and RDP programs are
intentionally started on the host through `flatpak-spawn --host`; this
preserves the user's existing `gpg-agent`, keyring, terminal emulator and RDP
client. The manifest therefore requests access to `org.freedesktop.Flatpak`.

Generate offline Python dependency sources, then build:

```sh
git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
python3 -m pip install --user --upgrade pip requirements-parser
FLATPAK_PYTHON=python3 sh packaging/flatpak/generate-python-sources.sh
flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
flatpak run org.keysng.KeysNG
```

Alternatively, use an isolated virtual environment:

```sh
python3 -m venv .flatpak-tools-venv
. .flatpak-tools-venv/bin/activate
python -m pip install --upgrade pip requirements-parser
FLATPAK_PYTHON=.flatpak-tools-venv/bin/python sh packaging/flatpak/generate-python-sources.sh
deactivate
```

The three interfaces can be started explicitly:

```sh
flatpak run --command=keys-ng-gui org.keysng.KeysNG
flatpak run --command=keys-ng-tui org.keysng.KeysNG
flatpak run --command=keys-ng org.keysng.KeysNG --help
```

To produce a redistributable single-file bundle:

```sh
rm -rf repo-flatpak build-flatpak
flatpak-builder --repo=repo-flatpak --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
flatpak build-bundle repo-flatpak Keys-NG-0.1.24.flatpak org.keysng.KeysNG --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo
```

Install it with:

```sh
flatpak install --user Keys-NG-0.1.24.flatpak
```

The bundle refers to Flathub for the KDE runtime and BaseApp; it does not embed them completely.

### Generator dependency (M1.17 clarification)

`flatpak-pip-generator` itself imports the PyPI package `requirements-parser`. The two supported setup modes are:

- user installation: `python3 -m pip install --user --upgrade pip requirements-parser`, then use `FLATPAK_PYTHON=python3`;
- isolated virtual environment: create and activate `.flatpak-tools-venv`, install `requirements-parser`, then use its Python through `FLATPAK_PYTHON`.

The virtual environment is only a build tool and is not included in the resulting Flatpak. Release source archives should ideally include the generated `python3-flatpak-requirements.json`; if it is absent, regenerate it before building.

The explicit `pybind11`, `scikit-build-core` and `nanobind` entries in `packaging/flatpak/requirements.txt` are intentional: Pillow and zxing-cpp are built from source and need these build dependencies.
