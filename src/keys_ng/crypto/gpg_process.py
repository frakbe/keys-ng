from __future__ import annotations

import os
import subprocess
import time
from typing import Iterable

from keys_ng.crypto.backend import CryptoBackend, DecryptionResult, KeyInfo
from keys_ng.crypto.discovery import discover_gnupg_executable
from keys_ng.errors import CryptoError
from keys_ng.services.diagnostics import elapsed_ms, get_logger, safe_operation_args
from keys_ng.platform.host import host_argv

_STATUS_PREFIX = "[GNUPG:] "
_LOG = get_logger("crypto.gpg_process")


def _windows_creationflags() -> int:
    """Suppress transient console windows for GnuPG helpers on Windows."""
    if os.name == "nt":
        return int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return 0


class GPGProcessBackend(CryptoBackend):
    """GnuPG backend using argv arrays and pipes only; never invokes a shell."""

    def __init__(
        self,
        executable: str | None = None,
        gpgconf_executable: str | None = None,
        homedir: str | None = None,
    ) -> None:
        gpg = discover_gnupg_executable("gpg", executable or "")
        gpgconf = discover_gnupg_executable("gpgconf", gpgconf_executable or "")
        self.executable = gpg.path or executable or "gpg"
        self.executable_discovery = gpg
        self.gpgconf_executable = gpgconf.path or gpgconf_executable or "gpgconf"
        self.gpgconf_discovery = gpgconf
        self.homedir = homedir
        _LOG.debug(
            "gpg.backend.init gpg_method=%s gpgconf_method=%s gpg_found=%s gpgconf_found=%s",
            gpg.method, gpgconf.method, bool(gpg.path), bool(gpgconf.path),
        )

    def _base_args(self) -> list[str]:
        return ["--homedir", self.homedir] if self.homedir else []

    def _run(self, args: Iterable[str], data: bytes = b"", *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        arg_list = list(args)
        operation = safe_operation_args(arg_list)
        argv = host_argv([self.executable, *self._base_args(), *arg_list])
        started = time.perf_counter()
        _LOG.debug(
            "gpg.run.start operation=%s input_bytes=%d discovery=%s",
            operation, len(data), self.executable_discovery.method,
        )
        try:
            proc = subprocess.run(
                argv,
                input=data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                shell=False,
                env=os.environ.copy(),
                creationflags=_windows_creationflags(),
            )
        except OSError as exc:
            detail = self.executable_discovery.method
            _LOG.exception(
                "gpg.run.os_error operation=%s duration_ms=%.1f discovery=%s",
                operation, elapsed_ms(started), detail,
            )
            raise CryptoError(f"Unable to execute GnuPG ({detail}): {exc}") from exc
        duration = elapsed_ms(started)
        _LOG.debug(
            "gpg.run.end operation=%s duration_ms=%.1f returncode=%d stdout_bytes=%d stderr_bytes=%d",
            operation, duration, proc.returncode, len(proc.stdout or b""), len(proc.stderr or b""),
        )
        if check and proc.returncode != 0:
            message = proc.stderr.decode("utf-8", "replace").strip()
            raise CryptoError(f"GnuPG failed with status {proc.returncode}: {message}")
        return proc

    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        if not recipients:
            raise CryptoError("At least one recipient is required")
        args = ["--batch", "--yes", "--no-tty", "--trust-model", "always", "--output", "-"]
        for recipient in recipients:
            args.extend(["--recipient", recipient])
        if signer:
            args.extend(["--local-user", signer, "--sign"])
        args.append("--encrypt")
        return self._run(args, plaintext).stdout

    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        proc = self._run(["--batch", "--yes", "--no-tty", "--status-fd", "2", "--decrypt", "--output", "-"], ciphertext)
        signer: str | None = None
        primary_signer: str | None = None
        valid = False
        for raw_line in proc.stderr.decode("utf-8", "replace").splitlines():
            if not raw_line.startswith(_STATUS_PREFIX):
                continue
            status = raw_line[len(_STATUS_PREFIX) :]
            if status.startswith("VALIDSIG "):
                parts = status.split()
                if len(parts) >= 2:
                    signer = parts[1].upper()
                    # GnuPG appends the primary-key fingerprint when a signing
                    # subkey produced the signature.  Authorisation is attached
                    # to the primary identity, not to a rotatable subkey.
                    if len(parts) >= 11 and len(parts[10]) in {40, 64}:
                        primary_signer = parts[10].upper()
                    else:
                        primary_signer = signer
                    valid = True
        return DecryptionResult(proc.stdout, signer, valid, primary_signer)

    def list_keys(self, secret: bool = False) -> list[KeyInfo]:
        command = "--list-secret-keys" if secret else "--list-keys"
        proc = self._run(["--batch", "--with-colons", "--fixed-list-mode", "--fingerprint", "--fingerprint", command])
        keys: list[KeyInfo] = []
        current: dict | None = None
        for line in proc.stdout.decode("utf-8", "replace").splitlines():
            fields = line.split(":")
            kind = fields[0]
            if kind in {"pub", "sec"}:
                if current and current.get("fingerprint"):
                    keys.append(KeyInfo(**current))
                validity = fields[1]
                caps = fields[11] if len(fields) > 11 else ""
                current = {
                    "fingerprint": "",
                    "user_ids": (),
                    "can_encrypt": "e" in caps.lower(),
                    "can_sign": "s" in caps.lower(),
                    "secret": kind == "sec",
                    "revoked": validity == "r",
                    "expired": validity == "e",
                }
            elif kind == "fpr" and current is not None and not current["fingerprint"]:
                current["fingerprint"] = fields[9].upper()
            elif kind == "uid" and current is not None:
                current["user_ids"] = (*current["user_ids"], fields[9])
        if current and current.get("fingerprint"):
            keys.append(KeyInfo(**current))
        return keys

    def import_public_key(self, key_data: bytes) -> list[str]:
        self._run(["--batch", "--yes", "--import"], key_data)
        return [key.fingerprint for key in self.list_keys(secret=False) if key.can_encrypt and not key.revoked and not key.expired]

    def resolve_fingerprint(self, selector: str, secret: bool = False) -> str:
        needle = selector.strip().upper()
        if len(needle) not in {40, 64} or any(ch not in "0123456789ABCDEF" for ch in needle):
            raise CryptoError("Keys NG requires a full OpenPGP fingerprint (40 or 64 hexadecimal characters), not a name or key ID")
        matches = [key for key in self.list_keys(secret=secret) if key.fingerprint == needle]
        if len(matches) != 1:
            raise CryptoError(f"OpenPGP fingerprint not found: {selector}")
        return matches[0].fingerprint

    def hard_lock(self) -> None:
        if not self.gpgconf_discovery.path and self.gpgconf_executable == "gpgconf":
            raise CryptoError("gpgconf is not available; cannot hard-lock gpg-agent")
        args = [self.gpgconf_executable]
        if self.homedir:
            args += ["--homedir", self.homedir]
        args += ["--kill", "gpg-agent"]
        try:
            proc = subprocess.run(
                host_argv(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False, shell=False, creationflags=_windows_creationflags(),
            )
        except OSError as exc:
            raise CryptoError(f"Unable to execute gpgconf ({self.gpgconf_discovery.method}): {exc}") from exc
        if proc.returncode != 0:
            raise CryptoError(proc.stderr.decode("utf-8", "replace").strip() or "Unable to stop gpg-agent")

    def diagnose(self) -> list[tuple[str, bool, str]]:
        exe = self.executable_discovery.path
        checks = [("gpg", bool(exe), f"{exe or 'not found'} ({self.executable_discovery.method})")]
        agent = self.gpgconf_discovery.path
        checks.append(("gpgconf", bool(agent), f"{agent or 'not found'} ({self.gpgconf_discovery.method})"))
        if exe:
            try:
                proc = self._run(["--version"], check=False)
                first = proc.stdout.decode("utf-8", "replace").splitlines()[0] if proc.stdout else "unknown version"
                checks.append(("gpg-version", proc.returncode == 0, first))
                public = self.list_keys(secret=False)
                secret = self.list_keys(secret=True)
                checks.append(("public-keys", bool(public), f"{len(public)} usable/listed"))
                checks.append(("secret-keys", bool(secret), f"{len(secret)} usable/listed"))
            except (OSError, CryptoError) as exc:
                checks.append(("gpg-version", False, str(exc)))
        return checks
