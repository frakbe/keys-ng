#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
TOOLS=${FLATPAK_BUILDER_TOOLS:-"$ROOT/.flatpak-builder-tools"}
PYTHON=${FLATPAK_PYTHON:-python3}
if [ ! -x "$TOOLS/pip/flatpak-pip-generator" ]; then
  echo "flatpak-pip-generator not found at $TOOLS/pip/flatpak-pip-generator" >&2
  echo "Clone https://github.com/flatpak/flatpak-builder-tools there or set FLATPAK_BUILDER_TOOLS." >&2
  exit 2
fi
if ! "$PYTHON" -c 'import requirements' >/dev/null 2>&1; then
  echo "The Python interpreter used for flatpak-pip-generator needs requirements-parser." >&2
  echo "Recommended isolated setup:" >&2
  echo "  python3 -m venv .flatpak-tools-venv" >&2
  echo "  . .flatpak-tools-venv/bin/activate" >&2
  echo "  python -m pip install requirements-parser" >&2
  echo "  FLATPAK_PYTHON=.flatpak-tools-venv/bin/python packaging/flatpak/generate-python-sources.sh" >&2
  exit 3
fi
cd "$ROOT/packaging/flatpak"
"$PYTHON" "$TOOLS/pip/flatpak-pip-generator" --requirements-file=requirements.txt --output=python3-flatpak-requirements
