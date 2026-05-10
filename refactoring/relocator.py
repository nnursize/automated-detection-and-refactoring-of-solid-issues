"""Re-locate the violating entity in the *current* source of the clone.

The shortlist's line numbers go stale as soon as one earlier refactor edits the
same file. We use the entity_name to find it again, and slice the file content
based on the freshly-found bounds.
"""

from __future__ import annotations

from dataclasses import dataclass

from solid_detector.analysis.class_extractor import extract_classes
from solid_detector.analysis.signature_extractor import extract_signatures


@dataclass
class EntityLocation:
    file_path: str
    entity_name: str
    kind: str
    line_start: int
    line_end: int
    content_slice: str
    full_file_content: str


def relocate(
    full_file_content: str,
    file_path: str,
    entity_name: str,
    language: str = "python",
) -> EntityLocation | None:
    """Find entity_name in the current file content and return its location.

    Handles three name shapes:
      - "ClassName"            -> class
      - "ClassName.method"     -> method inside class
      - "module_function"      -> top-level function
    """
    if not full_file_content.strip():
        return None

    classes = extract_classes(full_file_content, language)
    signatures = extract_signatures(full_file_content, language)

    lookup_name = _lookup_entity_name(entity_name, language)

    if "." in lookup_name:
        class_name, member = lookup_name.split(".", 1)
        for ci in classes:
            if ci.name != class_name:
                continue
            for sig in signatures:
                if sig.name != member:
                    continue
                if ci.line_start <= sig.line_start <= ci.line_end:
                    return _slice(full_file_content, file_path, entity_name,
                                  "method", sig.line_start, sig.line_end)
            return _slice(full_file_content, file_path, entity_name,
                          "class", ci.line_start, ci.line_end)
        return None

    for ci in classes:
        if ci.name == lookup_name:
            return _slice(full_file_content, file_path, entity_name,
                          "class", ci.line_start, ci.line_end)
    for sig in signatures:
        if sig.name == lookup_name:
            inside_class = any(
                ci.line_start <= sig.line_start <= ci.line_end
                for ci in classes
            )
            if inside_class:
                continue
            return _slice(full_file_content, file_path, entity_name,
                          "function", sig.line_start, sig.line_end)
    return None


def _lookup_entity_name(entity_name: str, language: str) -> str:
    """Convert detector entity names into names extractors can match.

    C/C++ detections often include namespace qualifiers, e.g.
    ``Catch::Benchmark::Benchmark``. The regex extractor records the declared
    entity name itself, so the final qualifier is the best relocation key.
    """
    lang = (language or "").lower().strip()
    if lang in {"c++", "cpp", "cxx", "cc", "hpp", "h++"} and "::" in entity_name:
        return entity_name.rsplit("::", 1)[-1]
    return entity_name


def _slice(content: str, file_path: str, entity_name: str, kind: str,
           line_start: int, line_end: int) -> EntityLocation:
    lines = content.splitlines()
    actual_end = min(line_end, len(lines))
    slice_text = "\n".join(lines[line_start - 1:actual_end])
    return EntityLocation(
        file_path=file_path,
        entity_name=entity_name,
        kind=kind,
        line_start=line_start,
        line_end=actual_end,
        content_slice=slice_text,
        full_file_content=content,
    )
