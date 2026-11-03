# Keys NG — Building native macOS packages with Briefcase

This guide describes how to build, test, sign and distribute the native macOS packages for Keys NG. The build must run on macOS. A successful build is not sufficient for distribution: the resulting app or installer must be tested on a clean macOS user account or VM.

## 1. Build host and runtime

| Component | Build host | End-user runtime | Purpose |
|---|---:|---:|---|
| macOS on supported Apple hardware | required | required | Briefcase and Apple signing/notarization |
| Python 3.11+ | required | bundled by Briefcase | build tooling/application runtime |
| Xcode Command Line Tools | required | no | compiler, codesign and packaging tools |
| Git | required | no | source and Briefcase operations |
| Briefcase | required | no | create, build, run and package |
| GnuPG and pinentry | recommended for tests | required by Keys NG | OpenPGP, gpg-agent and passphrase entry |
| PySide6/Textual/application dependencies | resolved by Briefcase | bundled | application runtime |

Keys NG does not bundle or replace macOS GnuPG. The packaged application still needs a working GnuPG installation and pinentry configuration on the target Mac.

## 2. Prerequisites

Install Xcode Command Line Tools if they are not already present:

    xcode-select --install

Verify the host:

    sw_vers
    uname -m
    python3 --version
    git --version
    xcode-select -p
    xcrun --find clang
    codesign --version
    hdiutil -help | head

Install GnuPG for runtime tests. Homebrew is one possible method:

    brew install gnupg pinentry-mac
    gpg --version
    gpgconf --version

Create or import only disposable test keys. Do not use production private keys during packaging tests.

## 3. Prepare an isolated environment

From the project root:

    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install briefcase

Verify:

    python --version
    python -m briefcase --version

Use the same Python architecture as the target build. On Apple Silicon, check whether the build is arm64 or universal before producing a public artifact. Do not assume that an arm64 build runs on Intel Macs.

## 4. Packaging metadata

The native applications are configured in pyproject.toml:

    keys_ng      -> src/keys_ng       -> GUI
    keys_ng_cli  -> src/keys_ng_cli   -> CLI wrapper
    keys_ng_tui  -> src/keys_ng_tui   -> TUI wrapper

The GUI uses the macOS icon configured by Briefcase. The project must contain the corresponding .icns resource and the root LICENSE file. Keep the PEP 639 metadata and Briefcase version synchronized with keys_ng.__version__.

The runtime dependency on GnuPG is intentional. It must be documented to users and verified on the target Mac rather than silently replaced by a bundled private-key implementation.

## 5. Build and run the GUI app

Create the native macOS project:

    python -m briefcase create macOS -a keys_ng

Build it:

    python -m briefcase build macOS -a keys_ng

Run it before packaging:

    python -m briefcase run macOS -a keys_ng

Create the development DMG:

    python -m briefcase package macOS -a keys_ng -p dmg

The output is written below dist/. The DMG produced without a Developer ID identity is for local testing only.

## 6. Build the CLI and TUI applications

For a console application, macOS distribution should use a PKG rather than a DMG:

    python -m briefcase create macOS -a keys_ng_cli
    python -m briefcase build macOS -a keys_ng_cli
    python -m briefcase run macOS -a keys_ng_cli -- version
    python -m briefcase package macOS -a keys_ng_cli -p pkg

For the TUI:

    python -m briefcase create macOS -a keys_ng_tui
    python -m briefcase build macOS -a keys_ng_tui
    python -m briefcase run macOS -a keys_ng_tui -- --version
    python -m briefcase package macOS -a keys_ng_tui -p pkg

The separator -- passes following arguments to the packaged application. Validate the generated console packages on a clean account before distributing them.

A zipped app can also be produced for controlled testing:

    python -m briefcase package macOS -a keys_ng -p zip

## 7. Clean rebuilds

After changing pyproject.toml, application names, sources, dependencies, icon, license metadata or launcher configuration, remove the old Briefcase scaffold and recreate it:

    rm -rf build macOS
    python -m briefcase create macOS -a keys_ng
    python -m briefcase build macOS -a keys_ng

Do not remove a directory containing a release artifact before copying its checksums elsewhere. Run cleanup only from the project root after verifying the paths.

## 8. Development signing and verification

For local testing, an ad-hoc signature may be sufficient. It is not a distribution signature and does not establish developer identity. Inspect available identities:

    security find-identity -v -p codesigning

Verify an app bundle:

    codesign --verify --deep --strict --verbose=2 "dist/Keys NG.app"
    spctl --assess --type execute --verbose=4 "dist/Keys NG.app"

The exact app path can differ by Briefcase version. Use find dist -maxdepth 3 -name '*.app' to locate it.

For public distribution, use a Developer ID Application identity issued for the Apple Developer account. If producing a signed PKG, use a matching Developer ID Installer identity. Keep signing identities in the macOS keychain or CI secret store; never commit certificates, private keys or notarization credentials.

## 9. Signing, notarization and stapling

The normal release flow should use Briefcase signing/notarization options supported by the installed Briefcase version. Check the command help first:

    python -m briefcase package macOS --help

For a signed GUI DMG, provide the Developer ID Application identity as required by the installed Briefcase release and allow notarization. For a PKG, provide the installer identity as well. Development-only builds can explicitly disable notarization, but such artifacts must not be presented as production releases.

After notarization, verify the app and staple the ticket if the packaging flow has not already done so:

    xcrun stapler validate "dist/Keys NG.app"
    spctl --assess --type execute --verbose=4 "dist/Keys NG.app"

For an existing notarization submission, use the submission identifier printed by Briefcase with the supported resume option rather than starting an unrelated second submission. Record the submission ID and final status in the release evidence.

Before release, verify that the artifact contains no development path, test key, private credential or debug-only configuration.

## 10. Runtime smoke-test checklist

    [ ] DMG opens on the build Mac
    [ ] app can be copied to Applications
    [ ] app starts from Finder and from the terminal
    [ ] app identity and icon are correct
    [ ] keys-ng doctor resolves gpg and gpgconf
    [ ] keys-ng keys lists disposable test keys
    [ ] pinentry appears when private-key authorization is needed
    [ ] an existing test vault opens
    [ ] New Vault creates and opens a vault
    [ ] entry create/edit/save works
    [ ] clipboard timeout works
    [ ] TOTP generation works
    [ ] normal lock and global hard-lock work
    [ ] GUI recent-vault list opens a test vault
    [ ] CLI package starts from a terminal
    [ ] TUI package starts and can open a vault
    [ ] package works on a clean macOS account or VM
    [ ] signed artifact passes codesign verification
    [ ] notarized artifact passes spctl assessment
    [ ] DMG or PKG hash is recorded

## 11. Troubleshooting

### Briefcase cannot create the macOS project

Check Python, Git, Xcode Command Line Tools and the Briefcase version. Delete the stale build/macOS scaffold and recreate it after structural changes.

### The app starts but cannot open a vault

Install GnuPG and pinentry on the target system. Run keys-ng doctor and configure explicit gpg and gpgconf paths in Preferences or config.toml if automatic discovery fails.

### codesign or notarization fails

Confirm that the Developer ID certificate is present in the login keychain, that the signing identity matches the Apple Developer Team, and that the bundle identifier is stable. Inspect the complete Briefcase output and do not distribute an artifact produced with a failed or skipped signature.

### spctl rejects the app

Check the signature, entitlements, quarantine state and notarization result. Re-run codesign verification, query the notarization status with the Apple tooling available on the host, and package again after correcting the first reported error.

### The icon is missing

Confirm that the configured .icns resource exists and that the Briefcase scaffold was recreated after an icon or metadata change.

### A dependency is missing in the packaged app

Inspect the Briefcase build output and application requirements in pyproject.toml. Recreate the scaffold after changing requirements, then run the app before packaging.

## 12. Release evidence

A macOS release must retain:

- exact Git commit and release tag;
- Briefcase and Python versions;
- macOS version and architecture;
- DMG, PKG or ZIP SHA256 checksums;
- codesign verification output;
- notarization submission/status and stapler verification;
- smoke-test results on the build host and a clean target host.

A successful package command alone is not a release validation.
