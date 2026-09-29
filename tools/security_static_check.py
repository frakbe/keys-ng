#!/usr/bin/env python3
"""Dependency-free security lint used by M1.17 release checks.

This is deliberately small and auditable. It complements (not replaces) Ruff,
Bandit, Semgrep and dependency scanners when those tools are available.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "keys_ng"


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = call_name(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    return ""


def main() -> int:
    findings: list[str] = []
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = call_name(node.func)
            if name in {"subprocess.run", "subprocess.Popen", "subprocess.call", "subprocess.check_call", "subprocess.check_output"}:
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        findings.append(f"{path}:{node.lineno}: subprocess shell=True is forbidden")
            if isinstance(node.func, ast.Name) and name in {"eval", "exec", "compile"}:
                findings.append(f"{path}:{node.lineno}: dynamic code execution via {name} requires explicit review")
            if name in {"os.system", "os.popen"}:
                findings.append(f"{path}:{node.lineno}: shell-like process API {name} is forbidden")
        text = path.read_text(encoding="utf-8")
        if "source " in text and path.name == "legacy_parser.py":
            findings.append(f"{path}: legacy parser contains shell 'source' token")
    if findings:
        print("Security static check FAILED")
        print("\n".join(findings))
        return 1
    print("Security static check OK: no shell=True, eval/exec/compile, os.system/os.popen in src/keys_ng")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
