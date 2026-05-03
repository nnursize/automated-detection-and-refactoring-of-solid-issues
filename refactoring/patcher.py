"""Apply SEARCH/REPLACE/CREATE blocks to a workspace, with fail-fast and syntax check."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import PatchBlock, PatchKind


@dataclass
class ApplyResult:
    ok: bool
    error: str | None = None
    files_touched: list[str] = field(default_factory=list)


def apply(blocks: list[PatchBlock], workspace_root: Path) -> ApplyResult:
    if not blocks:
        return ApplyResult(ok=False, error="no patch blocks produced by LLM")

    pending: dict[str, str] = {}
    creates: dict[str, str] = {}

    for idx, block in enumerate(blocks):
        rel = block.file_path
        abs_path = workspace_root / rel
        if not _is_safe(workspace_root, abs_path):
            return ApplyResult(
                ok=False,
                error=f"block {idx} writes outside workspace: {rel}",
            )
        if block.kind is PatchKind.CREATE:
            if abs_path.exists():
                return ApplyResult(
                    ok=False,
                    error=f"CREATE block targets existing file: {rel}",
                )
            if rel in creates or rel in pending:
                return ApplyResult(
                    ok=False,
                    error=f"duplicate target file across blocks: {rel}",
                )
            creates[rel] = block.replace_text
            continue

        if block.search_text is None:
            return ApplyResult(
                ok=False,
                error=f"block {idx}: SEARCH_REPLACE missing search_text",
            )
        if not abs_path.exists():
            return ApplyResult(
                ok=False,
                error=f"SEARCH block targets missing file: {rel}",
            )
        current = pending.get(rel)
        if current is None:
            current = abs_path.read_text(encoding="utf-8")
        count = current.count(block.search_text)
        if count == 0:
            return ApplyResult(
                ok=False,
                error=f"search_text not found in {rel} (block {idx})",
            )
        if count > 1:
            return ApplyResult(
                ok=False,
                error=f"search_text matches {count} times in {rel} (block {idx}); needs more context",
            )
        new_content = current.replace(block.search_text, block.replace_text, 1)
        pending[rel] = new_content

    touched: list[str] = []
    for rel, content in pending.items():
        (workspace_root / rel).write_text(content, encoding="utf-8")
        touched.append(rel)
    for rel, content in creates.items():
        path = workspace_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        touched.append(rel)

    syntax_error = _check_python_syntax(workspace_root, touched)
    if syntax_error:
        return ApplyResult(ok=False, error=syntax_error, files_touched=touched)

    return ApplyResult(ok=True, files_touched=touched)


def _is_safe(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _check_python_syntax(workspace_root: Path, rel_paths: list[str]) -> str | None:
    for rel in rel_paths:
        if not rel.endswith(".py"):
            continue
        path = workspace_root / rel
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, rel, "exec")
        except SyntaxError as e:
            return f"syntax error in {rel}:{e.lineno}: {e.msg}"
    return None
