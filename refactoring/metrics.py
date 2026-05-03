"""Code-quality metric snapshots — works across languages.

For Python, uses `radon` for accurate cyclomatic complexity + maintainability
index. For all other supported languages (Java, Kotlin, C/C++, JS/TS, Go, Rust,
Swift, Ruby, shell), we compute simple regex-based approximations:

- LOC, blank lines, comment lines (line-prefix detection per language)
- function/method count (per-language regex)
- approximate cyclomatic complexity from branching-keyword counts

These are best-effort, not Sonar-grade. They're meant to give a rough sense
of "did this refactor make the file simpler / smaller / split it up" — not
to be authoritative quality gates.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import FileMetrics, MetricsSnapshot

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    _RADON_AVAILABLE = True
except ImportError:
    _RADON_AVAILABLE = False


# Languages we have metric heuristics for. Files outside this list are skipped.
_SUPPORTED_EXTS = (
    ".py",
    ".rb",
    ".java", ".kt",
    ".js", ".ts", ".tsx", ".jsx",
    ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
    ".go", ".rs", ".swift",
    ".sh",
)

# Single-line comment markers per extension. Block comments (/* ... */, =begin/=end)
# are not detected — minor undercounting on heavily block-commented files.
_COMMENT_PREFIXES_BY_EXT = {
    ".py": ("#",), ".rb": ("#",), ".sh": ("#",),
    ".java": ("//",), ".kt": ("//",),
    ".js": ("//",), ".ts": ("//",), ".tsx": ("//",), ".jsx": ("//",),
    ".cpp": ("//",), ".cc": ("//",), ".cxx": ("//",),
    ".c": ("//",), ".h": ("//",), ".hpp": ("//",),
    ".go": ("//",), ".rs": ("//",), ".swift": ("//",),
}

# Branching keywords / operators. Each occurrence adds 1 to the file's
# decision-point count, used as a cyclomatic-complexity proxy.
_BRANCH_PATTERNS = re.compile(
    r"(?:\bif\b|\belif\b|\belse\s+if\b|\bfor\b|\bwhile\b|\bcase\b|\bwhen\b"
    r"|\bcatch\b|\brescue\b|\bdo\b|&&|\|\||\?\?)"
)

# Function/method definition patterns. Best-effort regex — accurate enough to
# show "split a class into 3 files" cleanly; will miss exotic cases.
_FUNCTION_PATTERNS_BY_EXT = {
    ".py": (
        re.compile(r"^[ \t]*(?:async\s+)?def\s+\w+\s*\(", re.MULTILINE),
    ),
    ".rb": (
        re.compile(r"^[ \t]*def\s+\w+", re.MULTILINE),
    ),
    ".java": (
        re.compile(
            # method signatures: optional modifiers, return type, name, params, opening brace
            r"^[ \t]*(?:(?:public|private|protected|static|final|synchronized|abstract|native|default)\s+)+"
            r"[\w<>,\[\]\s\?]+?\s+\w+\s*\([^;]*?\)\s*(?:throws\s+[\w,\s\.]+)?\s*\{",
            re.MULTILINE | re.DOTALL,
        ),
    ),
    ".kt": (
        re.compile(
            r"^[ \t]*(?:(?:public|private|protected|internal|override|inline|suspend|operator|tailrec)\s+)*"
            r"fun\s+\w+",
            re.MULTILINE,
        ),
    ),
    ".js": (
        re.compile(r"^[ \t]*(?:async\s+)?function\s+\w+\s*\(", re.MULTILINE),
        re.compile(r"^[ \t]*(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(?[^=]*?\)?\s*=>", re.MULTILINE),
    ),
    ".ts": (
        re.compile(r"^[ \t]*(?:export\s+)?(?:async\s+)?function\s+\w+\s*\(", re.MULTILINE),
        re.compile(r"^[ \t]*(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(?[^=]*?\)?\s*=>", re.MULTILINE),
    ),
    ".cpp": (
        re.compile(r"^[ \t]*[\w:<>,\*&\s]+?\s+\w+\s*::\s*\w+\s*\([^;{]*\)\s*(?:const)?\s*\{", re.MULTILINE),
    ),
    ".c": (
        re.compile(r"^[ \t]*[\w\*\s]+\s+\w+\s*\([^;{]*\)\s*\{", re.MULTILINE),
    ),
    ".go": (
        re.compile(r"^func\s+(?:\(\s*\w+\s+[\w\*]+\s*\))?\s*\w+\s*\(", re.MULTILINE),
    ),
    ".rs": (
        re.compile(r"^[ \t]*(?:pub\s+)?(?:async\s+)?fn\s+\w+", re.MULTILINE),
    ),
    ".swift": (
        re.compile(r"^[ \t]*(?:public\s+|private\s+|internal\s+|fileprivate\s+|open\s+|static\s+|class\s+)*func\s+\w+", re.MULTILINE),
    ),
}
# JSX/TSX share the JS/TS heuristics.
_FUNCTION_PATTERNS_BY_EXT[".jsx"] = _FUNCTION_PATTERNS_BY_EXT[".js"]
_FUNCTION_PATTERNS_BY_EXT[".tsx"] = _FUNCTION_PATTERNS_BY_EXT[".ts"]
# C++ headers and variants reuse the same patterns.
_FUNCTION_PATTERNS_BY_EXT[".cc"] = _FUNCTION_PATTERNS_BY_EXT[".cpp"]
_FUNCTION_PATTERNS_BY_EXT[".cxx"] = _FUNCTION_PATTERNS_BY_EXT[".cpp"]
_FUNCTION_PATTERNS_BY_EXT[".h"] = _FUNCTION_PATTERNS_BY_EXT[".c"]
_FUNCTION_PATTERNS_BY_EXT[".hpp"] = _FUNCTION_PATTERNS_BY_EXT[".cpp"]


def snapshot(workspace_root: Path, rel_paths: list[str]) -> MetricsSnapshot:
    """Compute metrics for every supported file in `rel_paths` (deduplicated)."""
    files: list[FileMetrics] = []
    seen: set[str] = set()
    for rel in rel_paths:
        if rel in seen:
            continue
        seen.add(rel)
        ext = Path(rel).suffix.lower()
        if ext not in _SUPPORTED_EXTS:
            continue
        path = workspace_root / rel
        if not path.exists():
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        files.append(metrics_for_source(rel, source))
    return MetricsSnapshot(files=files)


def metrics_for_source(rel_path: str, source: str) -> FileMetrics:
    """Compute the FileMetrics record for a single (rel_path, source) pair.

    Public so callers (e.g. rerender) can compute against arbitrary file
    content (e.g. content fetched via `git show <ref>:<path>`).
    """
    ext = Path(rel_path).suffix.lower()
    return _metrics_for(rel_path, source, ext)


def _metrics_for(rel_path: str, source: str, ext: str) -> FileMetrics:
    lines = source.splitlines()
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = _count_comment_lines(lines, ext)
    loc = len(lines) - blank_lines - comment_lines

    function_count = _count_functions(source, ext)
    branch_count = _count_branches(source)

    avg_cc = 0.0
    max_cc = 0.0
    mi = 0.0

    if ext == ".py" and _RADON_AVAILABLE:
        try:
            blocks = cc_visit(source)
        except Exception:
            blocks = []
        if blocks:
            complexities = [b.complexity for b in blocks]
            avg_cc = sum(complexities) / len(complexities)
            max_cc = float(max(complexities))
        try:
            mi = float(mi_visit(source, multi=True))
        except Exception:
            mi = 0.0
    else:
        # Approximate CC: every function has implicit complexity 1; each branch
        # adds 1. Spread across the file's functions.
        if function_count > 0:
            avg_cc = 1.0 + (branch_count / function_count)
            max_cc = float(1 + branch_count)
        else:
            avg_cc = float(1 + branch_count)
            max_cc = avg_cc
        # MI requires Halstead measures; not worth approximating for non-Python.

    return FileMetrics(
        file=rel_path,
        loc=loc,
        blank_lines=blank_lines,
        comment_lines=comment_lines,
        function_count=function_count,
        avg_cc=round(avg_cc, 2),
        max_cc=round(max_cc, 2),
        mi=round(mi, 2),
    )


def _count_comment_lines(lines: list[str], ext: str) -> int:
    prefixes = _COMMENT_PREFIXES_BY_EXT.get(ext, ())
    if not prefixes:
        return 0
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped and any(stripped.startswith(p) for p in prefixes):
            count += 1
    return count


def _count_functions(source: str, ext: str) -> int:
    patterns = _FUNCTION_PATTERNS_BY_EXT.get(ext, ())
    if not patterns:
        return 0
    return sum(len(pat.findall(source)) for pat in patterns)


def _count_branches(source: str) -> int:
    return len(_BRANCH_PATTERNS.findall(source))
