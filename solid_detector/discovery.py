"""File discovery and filtering for repository scanning.

Context-building lives in solid_detector.context; this module only walks the
repo, applies include/exclude rules, and populates FileInfo with structural
metadata extracted by solid_detector.analysis.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from .analysis import extract_classes, extract_imports, extract_signatures
from .analysis.class_extractor import attach_signatures_to_classes
from .config import ProjectConfig
from .models import FileInfo

_EXT_TO_LANG = {
    ".py": "python",
    ".java": "java",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".hpp": "cpp", ".hh": "cpp", ".h": "cpp",
    ".ts": "typescript", ".tsx": "typescript",
    ".rb": "ruby",
}


def _detect_language(filename: str, fallback: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return _EXT_TO_LANG.get(ext, fallback)


def discover_files(config: ProjectConfig) -> list[FileInfo]:
    """Walk the source root and collect all matching source files."""
    source_root = Path(config.source_abs_path)
    repo_root = Path(config.repo_abs_path)
    files: list[FileInfo] = []

    for dirpath, _, filenames in os.walk(source_root):
        for filename in filenames:
            abs_path = Path(dirpath) / filename
            rel_path = str(abs_path.relative_to(repo_root)).replace("\\", "/")

            if not any(filename.endswith(ext) for ext in config.repo.file_extensions):
                continue
            if _matches_exclude(rel_path, config.repo.exclude_patterns):
                continue

            try:
                content = abs_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            line_count = len(content.splitlines())
            if line_count < config.repo.min_file_lines:
                continue

            language = _detect_language(filename, config.repo.language)
            class_infos = extract_classes(content, language)
            for ci in class_infos:
                ci.file_path = rel_path
            signatures = extract_signatures(content, language)
            imports = extract_imports(content, language)
            if not any(ci.methods for ci in class_infos):
                attach_signatures_to_classes(class_infos, signatures)

            files.append(
                FileInfo(
                    path=rel_path,
                    absolute_path=str(abs_path),
                    line_count=line_count,
                    char_count=len(content),
                    estimated_tokens=len(content) // 4,
                    classes=[c.name for c in class_infos],
                    functions=[s.name for s in signatures],
                    class_infos=class_infos,
                    signatures=signatures,
                    imports=imports,
                )
            )

    files.sort(key=lambda f: f.line_count, reverse=True)
    return files


def _matches_exclude(rel_path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        if fnmatch.fnmatch(os.path.basename(rel_path), pattern):
            return True
    return False
