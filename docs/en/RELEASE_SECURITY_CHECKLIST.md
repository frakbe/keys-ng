# M1.18 Release Security Checklist

- [x] Version synchronized as `0.1.18.dev1` in Python and Briefcase metadata.
- [x] Full test suite passes.
- [x] Python sources compile with `compileall`.
- [x] Dependency-free AST security check passes.
- [x] No `shell=True`, built-in `eval`/`exec`/`compile`, `os.system` or `os.popen` in application source.
- [x] POSIX vault directory permissions covered by tests.
- [x] Atomic-replace failure injection covered by tests.
- [x] Deterministic malformed JSON parser corpus covered by tests.
- [x] Single-record rollback/replacement fails closed on ordinary read.
- [x] Record payload UUID/filename mismatch fails closed.
- [x] Signature-required config cannot omit signer/trusted signers.
- [x] GnuPG process backend requires 40/64-character full fingerprints.
- [x] Vault format 1.0 documented/frozen for review.
- [x] Threat model documented in English and Italian.
- [x] Memory/secret-lifetime limitations documented.
- [x] Every Python class/function documented in both code-review manuals and coverage-tested.
- [ ] Independent code review — external requirement.
- [ ] Independent penetration/security audit — external requirement.
- [ ] Ruff/Bandit/pip-audit/Semgrep execution in a connected environment — not claimed by this offline assembly.
- [ ] Real Windows/macOS packaging smoke tests — require corresponding OS runners/hardware.
- [ ] Hardware-token matrix (YubiKey/OpenPGP card) — requires physical devices.

## M1.18 parity delta

- [x] Shared GUI/TUI entry conversion and validation.
- [x] Folder move/rename failure leaves decrypted cache unchanged.
- [x] Cycle and duplicate-sibling move regressions tested.
- [x] TUI create/edit/move/delete source surface covered by tests.
- [x] Clipboard banner configuration round-trip tested.
- [x] Bilingual exhaustive code-review manual regenerated from M1.18 source.

## M1.19 additions

- [x] Vault creation is centralized in `services.vault_init` and validates a non-empty recipient set, full fingerprints and target directory state.
- [x] A cryptographic encrypt/decrypt/signature self-test occurs before vault files are created.
- [x] GUI and TUI new-vault flows use the same core service as CLI `init`.
- [x] Windows GnuPG discovery is centralized and does not invoke a shell.
- [x] Explicit GnuPG executable overrides are stored only as paths, not credentials.
- [x] PEP 639 license metadata is present for packaging.
- [x] Source tests and static security check pass in the release assembly environment.
- [ ] Re-run Briefcase `create/build/run/package` for M1.19 on a real Windows host; the procedure is documented in `WINDOWS_MSI_BUILD.md`.
