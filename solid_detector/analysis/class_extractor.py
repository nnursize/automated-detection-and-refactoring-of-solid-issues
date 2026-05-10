"""Extract class declarations with inheritance and member info.

Python path uses ast; other languages fall back to regex.
"""

from __future__ import annotations

import ast
import re

from ..models import ClassInfo, MethodSignature


def extract_classes(content: str, language: str) -> list[ClassInfo]:
    """Return all classes in the source with their bases, methods, attributes."""
    lang = _normalize_language(language)
    if lang == "python":
        try:
            return _extract_python(content)
        except SyntaxError:
            pass
    return _extract_regex(content, lang)


# ---------- Python (AST) ----------

def _extract_python(content: str) -> list[ClassInfo]:
    tree = ast.parse(content)
    out: list[ClassInfo] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = [_ast_name(b) for b in node.bases]
        methods: list[MethodSignature] = []
        attributes: list[str] = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(_python_method_sig(item))
            elif isinstance(item, ast.Assign):
                for tgt in item.targets:
                    if isinstance(tgt, ast.Name):
                        attributes.append(tgt.id)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attributes.append(item.target.id)
        out.append(
            ClassInfo(
                name=node.name,
                bases=[b for b in bases if b],
                line_start=node.lineno,
                line_end=getattr(node, "end_lineno", node.lineno) or node.lineno,
                methods=methods,
                attributes=attributes,
            )
        )
    return out


def _ast_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_ast_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _ast_name(node.func)
    return ""


def _python_method_sig(node: ast.FunctionDef | ast.AsyncFunctionDef) -> MethodSignature:
    args = node.args
    parts: list[str] = []
    posonly = getattr(args, "posonlyargs", []) or []
    defaults = list(args.defaults or [])
    all_pos = posonly + list(args.args)
    n_pos = len(all_pos)
    pad = n_pos - len(defaults)
    for i, a in enumerate(all_pos):
        s = a.arg
        if a.annotation is not None:
            s += f": {ast.unparse(a.annotation)}"
        if i >= pad:
            s += f" = {ast.unparse(defaults[i - pad])}"
        parts.append(s)
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for i, a in enumerate(args.kwonlyargs or []):
        s = a.arg
        if a.annotation is not None:
            s += f": {ast.unparse(a.annotation)}"
        default = (args.kw_defaults or [None])[i]
        if default is not None:
            s += f" = {ast.unparse(default)}"
        parts.append(s)
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    decorators = [ast.unparse(d) for d in node.decorator_list]
    ret = ast.unparse(node.returns) if node.returns is not None else ""
    return MethodSignature(
        name=node.name,
        params=", ".join(parts),
        return_type=ret,
        decorators=decorators,
        line_start=node.lineno,
        line_end=getattr(node, "end_lineno", node.lineno) or node.lineno,
        is_abstract=_is_abstract_python(node),
    )


def _is_abstract_python(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for d in node.decorator_list:
        name = _ast_name(d)
        if name.endswith("abstractmethod"):
            return True
    body = node.body
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Raise) and stmt.exc is not None:
            if _ast_name(stmt.exc).endswith("NotImplementedError"):
                return True
        if isinstance(stmt, ast.Pass):
            return True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            return True  # docstring-only bodies count as abstract-ish
    return False


# ---------- Other languages (regex) ----------

_CLASS_PATTERNS: dict[str, re.Pattern] = {
    "python": re.compile(r"^\s*class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:", re.MULTILINE),
    "java": re.compile(
        r"^\s*(?:public|private|protected|\s)*\s*(?:abstract|final|static|\s)*\s*class\s+(\w+)"
        r"\s*(?:extends\s+([\w.<>]+))?\s*(?:implements\s+([\w.,<>\s]+))?",
        re.MULTILINE,
    ),
    "cpp": re.compile(
        r"^\s*(?:template\s*<[^>]*>\s*)?(?:class|struct)\s+(\w+)"
        r"(?:\s+(?:final|abstract))?"
        r"\s*(?::\s*((?:public|private|protected)\s+[\w:]+(?:\s*,\s*(?:public|private|protected)\s+[\w:]+)*))?",
        re.MULTILINE,
    ),
    "typescript": re.compile(
        r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)"
        r"(?:\s+extends\s+([\w.<>]+))?"
        r"(?:\s+implements\s+([\w.,<>\s]+))?",
        re.MULTILINE,
    ),
    "ruby": re.compile(
        r"^\s*class\s+(\w+)(?:\s*<\s*([\w:]+))?",
        re.MULTILINE,
    ),
}


def _normalize_language(language: str) -> str:
    lang = (language or "").lower().strip()
    if lang in {"c++", "cpp", "cxx", "cc", "hpp", "h++"}:
        return "cpp"
    return lang


def _extract_regex(content: str, language: str) -> list[ClassInfo]:
    pat = _CLASS_PATTERNS.get(language)
    if pat is None:
        return []
    out: list[ClassInfo] = []
    lines = content.splitlines()
    for m in pat.finditer(content):
        name = m.group(1)
        bases: list[str] = []
        # groups 2+ depend on language
        for g in m.groups()[1:]:
            if not g:
                continue
            for token in re.split(r"[,\s]+", g.strip()):
                token = token.strip().lstrip(":").strip()
                if token and token not in {"public", "private", "protected"}:
                    bases.append(token)
        line_start = content[: m.start()].count("\n") + 1
        line_end = _estimate_block_end(lines, line_start - 1, language)
        out.append(
            ClassInfo(
                name=name,
                bases=bases,
                line_start=line_start,
                line_end=line_end,
            )
        )
    return out


def _estimate_block_end(lines: list[str], start_idx: int, language: str) -> int:
    """Rough block-end estimator for regex path.

    Python: find next dedented non-empty line.
    Brace languages: track brace depth.
    """
    if not lines or start_idx >= len(lines):
        return start_idx + 1
    if language == "python":
        base_indent = _indent(lines[start_idx])
        for j in range(start_idx + 1, len(lines)):
            line = lines[j]
            if line.strip() == "":
                continue
            if _indent(line) <= base_indent:
                return j
        return len(lines)
    if language == "ruby":
        return _ruby_block_end(lines, start_idx)
    # brace-based
    depth = 0
    saw_open = False
    for j in range(start_idx, len(lines)):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
                saw_open = True
            elif ch == "}":
                depth -= 1
                if saw_open and depth == 0:
                    return j + 1
    return len(lines)


_RUBY_OPENER_HEAD = re.compile(
    r"^\s*(class|module|def|if|unless|case|begin|while|until)\b"
)
_RUBY_DO_OPENER = re.compile(r"\bdo\b(?:\s*\|[^|]*\|)?\s*(?:#.*)?$")
_RUBY_END = re.compile(r"\bend\b")


def _ruby_block_end(lines: list[str], start_idx: int) -> int:
    depth = 0
    saw_open = False
    for j in range(start_idx, len(lines)):
        line = lines[j]
        stripped = line.split("#", 1)[0]
        if _RUBY_OPENER_HEAD.match(stripped):
            depth += 1
            saw_open = True
        elif _RUBY_DO_OPENER.search(stripped):
            depth += 1
            saw_open = True
        for _ in _RUBY_END.finditer(stripped):
            depth -= 1
            if saw_open and depth <= 0:
                return j + 1
    return len(lines)


def _indent(line: str) -> int:
    i = 0
    while i < len(line) and line[i] in " \t":
        i += 1
    return i


def attach_signatures_to_classes(
    classes: list[ClassInfo], signatures: list[MethodSignature]
) -> None:
    """Attach each signature to the innermost class whose line-range contains it."""
    if not classes or not signatures:
        return
    for sig in signatures:
        best: ClassInfo | None = None
        best_span = None
        for ci in classes:
            if ci.line_start <= sig.line_start <= ci.line_end:
                span = ci.line_end - ci.line_start
                if best is None or span < best_span:
                    best = ci
                    best_span = span
        if best is not None:
            best.methods.append(sig)
