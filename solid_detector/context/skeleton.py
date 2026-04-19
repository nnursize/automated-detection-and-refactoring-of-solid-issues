"""Skeleton context: class headers + method signatures only (no bodies).

Good for ISP (fat interface detection) and LSP (contract-shape reasoning). Fits
orders of magnitude more code into the window than full-source context.
"""

from __future__ import annotations

from ..models import ClassInfo, FileInfo, MethodSignature


def build_skeleton(files: list[FileInfo], token_budget: int) -> str:
    """Emit a signatures-only view of every class across all files."""
    parts: list[str] = []
    used = 0

    for file_info in files:
        block = _render_file_skeleton(file_info)
        if not block.strip():
            continue
        est = len(block) // 4
        if used + est > token_budget:
            parts.append(f"\n### NOTE: skeleton truncated, {len(files) - len(parts)} files omitted.\n")
            break
        parts.append(block)
        used += est

    return "\n".join(parts)


def _render_file_skeleton(file_info: FileInfo) -> str:
    lines: list[str] = [f"### FILE: {file_info.path}"]

    if file_info.imports:
        lines.append("imports: " + ", ".join(file_info.imports[:20]))

    if not file_info.class_infos and not file_info.signatures:
        return ""

    for ci in file_info.class_infos:
        lines.append("")
        lines.append(_render_class_header(ci))
        for attr in ci.attributes[:20]:
            lines.append(f"    {attr}")
        for m in ci.methods:
            lines.append(_render_method_line(m, indent="    "))

    # Orphan top-level functions (not inside any class in class_infos)
    class_method_names: set[str] = set()
    for ci in file_info.class_infos:
        for m in ci.methods:
            class_method_names.add(m.name)
    top_level = [s for s in file_info.signatures if s.name not in class_method_names]
    if top_level:
        lines.append("")
        lines.append("# top-level functions:")
        for m in top_level:
            lines.append(_render_method_line(m, indent=""))

    lines.append("")
    return "\n".join(lines)


def _render_class_header(ci: ClassInfo) -> str:
    bases = f"({', '.join(ci.bases)})" if ci.bases else ""
    return f"class {ci.name}{bases}:   # L{ci.line_start}-L{ci.line_end}"


def _render_method_line(m: MethodSignature, indent: str) -> str:
    decos = "".join(f"{indent}@{d}\n" for d in m.decorators)
    ret = f" -> {m.return_type}" if m.return_type else ""
    marker = "  # abstract" if m.is_abstract else ""
    return f"{decos}{indent}def {m.name}({m.params}){ret}: ...{marker}  # L{m.line_start}"
