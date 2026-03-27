"""File discovery, filtering, and chunking for repository scanning."""

from __future__ import annotations

import ast
import fnmatch
import os
import re
from pathlib import Path

from .config import ProjectConfig
from .models import FileInfo


def discover_files(config: ProjectConfig) -> list[FileInfo]:
    """Walk the source root and collect all matching source files."""
    source_root = Path(config.source_abs_path)
    repo_root = Path(config.repo_abs_path)
    files: list[FileInfo] = []

    for dirpath, _, filenames in os.walk(source_root):
        for filename in filenames:
            abs_path = Path(dirpath) / filename
            rel_path = str(abs_path.relative_to(repo_root)).replace("\\", "/")

            # Check extension
            if not any(filename.endswith(ext) for ext in config.repo.file_extensions):
                continue

            # Check exclude patterns
            if _matches_exclude(rel_path, config.repo.exclude_patterns):
                continue

            # Read file and compute metadata
            try:
                content = abs_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.splitlines()
            line_count = len(lines)

            # Skip trivially small files
            if line_count < config.repo.min_file_lines:
                continue

            char_count = len(content)
            classes, functions = _extract_symbols(
                content, config.repo.language, rel_path
            )

            files.append(
                FileInfo(
                    path=rel_path,
                    absolute_path=str(abs_path),
                    line_count=line_count,
                    char_count=char_count,
                    estimated_tokens=char_count // 4,
                    classes=classes,
                    functions=functions,
                )
            )

    # Sort by line count descending (largest files first — most likely to have violations)
    files.sort(key=lambda f: f.line_count, reverse=True)
    return files


def _matches_exclude(rel_path: str, patterns: list[str]) -> bool:
    """Check if a relative path matches any exclude pattern."""
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        # Also check just the filename part
        if fnmatch.fnmatch(os.path.basename(rel_path), pattern):
            return True
    return False


def _extract_symbols(
    content: str, language: str, file_path: str
) -> tuple[list[str], list[str]]:
    """Extract class and function names from source code."""
    if language == "python":
        return _extract_python_symbols(content)
    else:
        return _extract_symbols_regex(content, language)


def _extract_python_symbols(content: str) -> tuple[list[str], list[str]]:
    """Use Python AST to extract class and function names."""
    classes = []
    functions = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
    except SyntaxError:
        # Fall back to regex
        return _extract_symbols_regex(content, "python")
    return classes, functions


def _extract_symbols_regex(
    content: str, language: str
) -> tuple[list[str], list[str]]:
    """Regex-based symbol extraction for any language."""
    classes = []
    functions = []

    # Class patterns by language
    class_patterns = {
        "python": r"^class\s+(\w+)",
        "java": r"(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)",
        "cpp": r"class\s+(\w+)",
        "typescript": r"(?:export\s+)?class\s+(\w+)",
    }

    # Function patterns by language
    func_patterns = {
        "python": r"^def\s+(\w+)",
        "java": r"(?:public|private|protected)\s+\w+\s+(\w+)\s*\(",
        "cpp": r"(?:\w+(?:::\w+)*\s+)+(\w+)\s*\([^)]*\)\s*(?:const)?\s*\{",
        "typescript": r"(?:export\s+)?(?:async\s+)?function\s+(\w+)",
    }

    lang = language.lower()
    if lang in class_patterns:
        classes = re.findall(class_patterns[lang], content, re.MULTILINE)
    if lang in func_patterns:
        functions = re.findall(func_patterns[lang], content, re.MULTILINE)

    return classes, functions


def prepare_full_repo_context(files: list[FileInfo], token_budget: int) -> str:
    """Concatenate source files with delimiters, respecting token budget."""
    parts = []
    total_tokens = 0

    for file_info in files:
        if total_tokens + file_info.estimated_tokens > token_budget:
            # Add a note about truncation
            parts.append(
                f"\n### NOTE: {len(files) - len(parts)} more files omitted due to context limit.\n"
            )
            break

        try:
            content = Path(file_info.absolute_path).read_text(
                encoding="utf-8", errors="ignore"
            )
        except Exception:
            continue

        parts.append(f"### FILE: {file_info.path}\n```\n{content}\n```\n")
        total_tokens += file_info.estimated_tokens

    return "\n".join(parts)


def prepare_per_file_context(
    files: list[FileInfo], file_selection: str = "largest"
) -> list[tuple[str, str]]:
    """Prepare individual file contexts for per-file scanning.

    Args:
        files: Discovered files sorted by size.
        file_selection: "largest" for top files, "medium" for mid-range files.

    Returns:
        List of (file_path, content) tuples.
    """
    if not files:
        return []

    if file_selection == "largest":
        # Top 30% of files by size
        count = max(3, len(files) // 3)
        selected = files[:count]
    elif file_selection == "medium":
        # Middle 30% of files
        start = len(files) // 3
        end = start + max(3, len(files) // 3)
        selected = files[start:end]
    else:
        selected = files

    result = []
    for file_info in selected:
        try:
            content = Path(file_info.absolute_path).read_text(
                encoding="utf-8", errors="ignore"
            )
            result.append((file_info.path, content))
        except Exception:
            continue

    return result
