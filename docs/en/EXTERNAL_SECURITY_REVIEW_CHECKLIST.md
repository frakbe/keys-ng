# External security review checklist

## Target and evidence

- [ ] Release tag and commit SHA recorded.
- [ ] Source archive SHA256 recorded.
- [ ] Wheel SHA256 recorded.
- [ ] Reviewer, dates, systems and tool versions recorded.
- [ ] Review performed from a clean checkout.
- [ ] Production vaults, credentials and private keys excluded.

## Automated validation

- [ ] python -m compileall -q src tests
- [ ] python -m pytest -q
- [ ] python tools/security_static_check.py
- [ ] Ruff completed and output archived.
- [ ] Bandit completed and output archived.
- [ ] pip-audit completed and output archived.
- [ ] Semgrep completed and output archived.
- [ ] Fresh virtual-environment wheel build and smoke test completed.

## Manual security review

- [ ] GnuPG process backend, argv, stdin/stdout and error handling.
- [ ] Encryption, signing, trusted-signer and fingerprint policy.
- [ ] Vault, record, catalog and folder integrity.
- [ ] Atomic writes and filesystem permissions.
- [ ] Normal lock, hard-lock and cache disposal.
- [ ] Rollback and replacement detection.
- [ ] JSON, URI, UUID-reference and configuration parsers.
- [ ] Legacy Keys and KeePassXC XML/KDBX import.
- [ ] Inbox approval and standalone encrypted export.
- [ ] Clipboard and secret lifetime handling.
- [ ] SSH/RDP/URL/generic launchers and shell boundaries.
- [ ] Flatpak permissions and host delegation.
- [ ] GUI/TUI parity, recent-vault list and hard-lock folder-state behavior.
- [ ] Fuzzing or property testing of parser boundaries.

## Findings and closure

- [ ] Every finding has severity, impact, reproduction and affected commit/file.
- [ ] Critical and High findings are closed or release is rejected.
- [ ] Medium findings have an owner and mitigation/deferral decision.
- [ ] Fixes are committed without rewriting the reviewed target.
- [ ] Regression tests exist for actionable findings.
- [ ] Residual risks are mapped to THREAT_MODEL.md.
- [ ] Final report and acceptance decision are archived.
