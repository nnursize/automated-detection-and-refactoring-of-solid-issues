"""Class-centric context: selected classes with base-class sources and imports.

Sends ONE batched call per scan rather than one call per class, staying within
free-tier RPD limits. Selects the top N largest classes and builds rich context
around each (target body + base classes + imports + sibling headers).
"""

from __future__ import annotations

from pathlib import Path

from ..models import ClassInfo, FileInfo

# How many classes to include in one batched context.
# Keeps token count manageable while covering the most violation-prone code.
_MAX_CLASSES = 15


def select_target_classes(
    files: list[FileInfo], top_fraction: float = 0.33
) -> list[tuple[FileInfo, ClassInfo]]:
    """Pick the largest classes from the top files — sorted by class size."""
    if not files:
        return []
    count = max(3, int(len(files) * top_fraction))
    selected_files = files[:count]
    pairs: list[tuple[FileInfo, ClassInfo]] = []
    for f in selected_files:
        for ci in f.class_infos:
            pairs.append((f, ci))
    # Sort by class size so we pick the most substantive ones
    pairs.sort(key=lambda p: p[1].line_end - p[1].line_start, reverse=True)
    return pairs[:_MAX_CLASSES]


def build_class_centric_batch(
    targets: list[tuple[FileInfo, ClassInfo]],
    all_files: list[FileInfo],
    token_budget: int,
) -> str:
    """Build one combined context covering all target classes.

    For each target: target class body → base-class bodies → imports → sibling
    headers. Truncates early if the token budget is reached.
    """
    parts: list[str] = []
    used = 0

    for target_file, target_class in targets:
        block = _render_class_block(target_file, target_class, all_files)
        est = len(block) // 4
        if used + est > token_budget:
            parts.append(
                f"\n### NOTE: {len(targets) - len(parts)} more classes omitted (budget).\n"
            )
            break
        parts.append(block)
        used += est

    return "\n".join(parts)


def _render_class_block(
    target_file: FileInfo,
    target_class: ClassInfo,
    all_files: list[FileInfo],
) -> str:
    lines: list[str] = []
    lines.append(
        f"### CLASS: {target_class.name} in {target_file.path} "
        f"(L{target_class.line_start}-L{target_class.line_end})"
    )
    if target_file.imports:
        lines.append("# imports: " + ", ".join(target_file.imports[:20]))

    # Target class body
    body = _slice_lines(target_file, target_class.line_start, target_class.line_end)
    lines.append("```")
    lines.append(body)
    lines.append("```")

    # Base class bodies (one level deep)
    for base in target_class.bases:
        base_simple = base.split(".")[-1]
        base_file, base_ci = _find_class(base_simple, all_files)
        if base_ci is None:
            lines.append(f"# BASE CLASS (external): {base}")
            continue
        base_body = _slice_lines(base_file, base_ci.line_start, base_ci.line_end)
        lines.append(
            f"# BASE CLASS: {base_ci.name} from {base_file.path} "
            f"(L{base_ci.line_start}-L{base_ci.line_end})"
        )
        lines.append("```")
        lines.append(base_body)
        lines.append("```")

    # Sibling class headers (no bodies)
    siblings = [c for c in target_file.class_infos if c.name != target_class.name]
    if siblings:
        lines.append("# siblings in same file:")
        for s in siblings[:5]:
            bases_str = f"({', '.join(s.bases)})" if s.bases else ""
            lines.append(f"#   class {s.name}{bases_str}  L{s.line_start}-L{s.line_end}")

    lines.append("")
    return "\n".join(lines)


def _find_class(
    name: str, files: list[FileInfo]
) -> tuple[FileInfo | None, ClassInfo | None]:
    for f in files:
        for ci in f.class_infos:
            if ci.name == name:
                return f, ci
    return None, None


def _slice_lines(file_info: FileInfo, start: int, end: int) -> str:
    try:
        text = Path(file_info.absolute_path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[max(0, start - 1) : min(len(lines), end)])
