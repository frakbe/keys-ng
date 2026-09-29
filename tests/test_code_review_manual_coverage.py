from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "keys_ng"


def _module_name(path: Path) -> str:
    return ".".join(path.relative_to(ROOT / "src").with_suffix("").parts)


def _symbols(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []

    def walk(body, parent=""):
        for node in body:
            if isinstance(node, ast.ClassDef):
                q = f"{parent}.{node.name}" if parent else node.name
                out.append(q)
                walk(node.body, q)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f"{parent}.{node.name}" if parent else node.name
                out.append(q)
                walk(node.body, q)

    walk(tree.body)
    return out


def test_bilingual_code_review_manual_covers_every_python_symbol():
    manuals = [
        (ROOT / "docs/en/CODE_REVIEW_MANUAL.md").read_text(encoding="utf-8"),
        (ROOT / "docs/it/CODE_REVIEW_MANUAL.md").read_text(encoding="utf-8"),
    ]
    expected = []
    for path in sorted(SRC.rglob("*.py")):
        module = _module_name(path)
        expected.extend(f"<!-- symbol:{module}:{symbol} -->" for symbol in _symbols(path))
    assert expected
    for manual in manuals:
        missing = [marker for marker in expected if marker not in manual]
        assert not missing, f"Undocumented Python symbols: {missing}"
