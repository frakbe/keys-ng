# External security review package

## Purpose

This is the hand-off package for an independent review of Keys NG 0.2.01. It is preparation material, not an audit and not a claim that the implementation has been independently validated.

The reviewer must inspect the exact release tag and commit supplied by the maintainer. The scope includes the Python core, CLI, TUI, GUI, GnuPG integration, vault storage, import/export, clipboard handling, external launchers and Flatpak host delegation.

## Materials to provide

- Exact release tag, commit SHA and source archive SHA256.
- Wheel and wheel SHA256 checksum.
- ROADMAP.md.
- THREAT_MODEL.md, SECURITY_REVIEW.md, MEMORY_REVIEW.md and VAULT_FORMAT_1.0.md.
- English and Italian CODE_REVIEW_MANUAL.md files.
- RELEASE_SECURITY_CHECKLIST.md.
- Full test report with operating system, Python, GnuPG and dependency versions.
- Sanitized test fixtures or a reviewer-created vault. Never provide real credentials, private keys or production vaults.

Use a clean checkout and a separate test keyring. Do not grant access to production vaults or private keys.

## Review scope

### Cryptography and storage

Verify recipient encryption, optional signing, trusted-signer policy, GnuPG process invocation, argv construction, stdin/stdout handling, vault configuration, record UUID binding, catalog integrity, folder storage, atomic writes, filesystem permissions, normal lock and hard-lock behavior, and rollback/replacement detection.

### Untrusted input

Review JSON, catalog, URI, UUID-reference, legacy Keys, KeePassXC XML/KDBX, inbox and configuration parsers. Check DTD/entity rejection, bounded reference resolution, cycle detection, malformed input handling and partial KeePassXC import warnings. Fuzz or property-test parser boundaries.

### Secret handling

Trace passwords, usernames, TOTP seeds and passphrases through Python memory, Qt/Textual widgets, clipboard helpers and subprocess boundaries. Verify that passphrases are delegated to GnuPG/pinentry and never appear in argv or logs. Review clipboard timeout, read-back verification, history limitations, standalone export and inbox approval.

### External execution and packaging

Review SSH, RDP, URL and generic launchers, shell=False, argv tokenization and the deliberate trust implications of OpenSSH options such as ProxyCommand. Review Flatpak host delegation and permissions as a separate sandbox boundary.

### GUI and TUI

Verify lock and unlock parity, preferences, import warnings, standalone export, search navigation, the three-vault recent list, invalid recent paths and global GUI hard-lock with multiple vaults and mixed expanded/collapsed folders. Confirm that errors and diagnostics never expose secrets or decrypted JSON.

## Procedure

1. Freeze the target and record tag, commit SHA, source SHA256 and wheel SHA256.
2. Create a clean isolated environment with no production vault or private-key access.
3. Record OS, Python, GnuPG and dependency versions.
4. Run: python -m compileall -q src tests.
5. Run: python -m pytest -q.
6. Run: python tools/security_static_check.py.
7. In a connected review environment run Ruff, Bandit, pip-audit and Semgrep, recording versions and complete output.
8. Build and smoke-test the wheel in a fresh virtual environment.
9. Create disposable GnuPG keys and a disposable vault. Exercise init, add, search, copy, lock, hard-lock, inbox, standalone export and recovery.
10. Import controlled KeePassXC fixtures with valid references, missing references, cycles, malformed fields, command URLs and custom command fields.
11. Review source using the exhaustive code-review manual, prioritizing storage, crypto, atomic writes, inbox, clipboard, actions, SSH options and migration parsers.
12. Fuzz or property-test parser entry points and retain minimized reproductions.
13. Review Flatpak permissions and host-spawn behavior separately.
14. Record every finding with severity, affected commit/file, reproduction, impact, remediation and verification status.
15. Apply fixes and regression tests in new commits; do not silently rewrite the reviewed target.
16. Request a final report stating scope, exclusions, tools, findings, residual risks and exact commits reviewed.

## Acceptance criteria

Use Critical, High, Medium, Low and Informational severities. Do not accept a release candidate with open Critical or High findings. Medium findings require an owner and an explicit mitigation or deferral decision. Map residual risks to THREAT_MODEL.md.

## Reviewer deliverables

Request an executive summary, scope and commit list, tool/environment inventory, prioritized findings, proof-of-concept or regression test for each actionable finding, remediation verification, residual-risk register and limitations.

## Evidence template

- Review target/tag:
- Commit SHA:
- Source archive SHA256:
- Wheel SHA256:
- Reviewer:
- Review dates:
- Operating systems:
- Python/GnuPG versions:
- Commands executed:
- Findings:
- Accepted residual risks:
- Final decision:


Additional review scope: reference metadata traversal, plain-text rendering, editor clearing at lock, and layout-only Qt settings.
