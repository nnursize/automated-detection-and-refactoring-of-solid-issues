"""Whole-repository context: concatenate files in size order under a token budget."""

from __future__ import annotations

from pathlib import Path

from ..models import FileInfo


def build_whole_repo(files: list[FileInfo], token_budget: int) -> str:
    """Concatenate source files with delimiters, respecting token budget."""
    parts: list[str] = []
    total_tokens = 0

    for file_info in files:
        if total_tokens + file_info.estimated_tokens > token_budget:
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
