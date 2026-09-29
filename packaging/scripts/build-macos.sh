#!/bin/sh
set -eu
python3 -m pip install --upgrade briefcase
briefcase create macOS
briefcase build macOS
# Use real signing/notarization for public releases. Ad-hoc is for CI/testing.
briefcase package macOS -p dmg --adhoc-sign
