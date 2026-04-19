"""Extract import statements per file — used by class-centric context builder."""

from __future__ import annotations

import ast
import re


def extract_imports(content: str, language: str) -> list[str]:
    """Return flat list of imported module / header / namespace names."""
    lang = (language or "").lower()
    if lang == "python":
        try:
            return _python_imports(content)
        except SyntaxError:
            pass
    return _regex_imports(content, lang)


def _python_imports(content: str) -> list[str]:
    tree = ast.parse(content)
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            prefix = "." * (node.level or 0)
            base = f"{prefix}{mod}".rstrip(".")
            for alias in node.names:
                out.append(f"{base}.{alias.name}" if base else alias.name)
    return out


_IMPORT_PATTERNS: dict[str, re.Pattern] = {
    "java": re.compile(r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;", re.MULTILINE),
    "cpp": re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]', re.MULTILINE),
    "typescript": re.compile(
        r"""^\s*import\s+(?:(?:[\w*{},\s]+?)\s+from\s+)?['"]([^'"]+)['"]""",
        re.MULTILINE,
    ),
    "ruby": re.compile(
        r"""^\s*(?:require|require_relative|load)\s+['"]([^'"]+)['"]""",
        re.MULTILINE,
    ),
}


def _regex_imports(content: str, language: str) -> list[str]:
    pat = _IMPORT_PATTERNS.get(language)
    if pat is None:
        return []
    return [m.group(1) for m in pat.finditer(content)]
