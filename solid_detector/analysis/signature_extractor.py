"""Extract method/function signatures without bodies.

Used for the 'skeleton' context mode which feeds signatures-only view to the LLM.
"""

from __future__ import annotations

import ast
import re

from ..models import MethodSignature
from .class_extractor import _normalize_language, _python_method_sig


def extract_signatures(content: str, language: str) -> list[MethodSignature]:
    """Return every function/method signature in the file (top-level + class members)."""
    lang = _normalize_language(language)
    if lang == "python":
        try:
            return _extract_python(content)
        except SyntaxError:
            pass
    return _extract_regex(content, lang)


def _extract_python(content: str) -> list[MethodSignature]:
    tree = ast.parse(content)
    out: list[MethodSignature] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(_python_method_sig(node))
    return out


_FUNC_PATTERNS: dict[str, re.Pattern] = {
    "java": re.compile(
        r"^\s*(?P<mods>(?:public|private|protected|static|final|abstract|synchronized|native|default|\s)*)\s+"
        r"(?P<ret>[\w<>\[\],.\s]+?)\s+"
        r"(?P<name>\w+)\s*"
        r"\((?P<params>[^)]*)\)\s*"
        r"(?:throws\s+[\w.,\s]+)?\s*[{;]",
        re.MULTILINE,
    ),
    "cpp": re.compile(
        r"^\s*(?P<ret>[\w:<>*&\s]+?)\s+"
        r"(?P<name>~?\w+(?:::\w+)*)\s*"
        r"\((?P<params>[^)]*)\)\s*(?:const|noexcept|override|final|\s)*\s*[{;]",
        re.MULTILINE,
    ),
    "typescript": re.compile(
        r"^\s*(?:export\s+)?(?:public|private|protected|static|readonly|async|\s)*\s*"
        r"(?P<name>\w+)\s*"
        r"\((?P<params>[^)]*)\)\s*"
        r"(?::\s*(?P<ret>[\w<>\[\],.\s|&]+?))?\s*[{;]",
        re.MULTILINE,
    ),
    "ruby": re.compile(
        r"^\s*def\s+(?:self\.)?(?P<name>\w+[\?!=]?)\s*(?:\((?P<params>[^)]*)\))?",
        re.MULTILINE,
    ),
}


def _extract_regex(content: str, language: str) -> list[MethodSignature]:
    pat = _FUNC_PATTERNS.get(language)
    if pat is None:
        return []
    out: list[MethodSignature] = []
    for m in pat.finditer(content):
        name = (m.groupdict().get("name") or "").strip()
        if not name or name in {"if", "for", "while", "switch", "return", "new", "catch"}:
            continue
        params = (m.groupdict().get("params") or "").strip()
        ret = (m.groupdict().get("ret") or "").strip()
        line_start = content[: m.start()].count("\n") + 1
        mods = (m.groupdict().get("mods") or "")
        is_abstract = "abstract" in mods
        out.append(
            MethodSignature(
                name=name,
                params=params,
                return_type=ret,
                line_start=line_start,
                line_end=line_start,
                is_abstract=is_abstract,
            )
        )
    return out
