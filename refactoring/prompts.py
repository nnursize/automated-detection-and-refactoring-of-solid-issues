"""Prompt construction for refactoring."""

from __future__ import annotations

from solid_detector.prompts.templates import PRINCIPLE_DEFINITIONS

from .models import IssueRef
from .relocator import EntityLocation


SYSTEM_PROMPT = """You are a senior software engineer performing an automated refactoring task.

You will be given:
- A specific design-principle violation that another LLM detected.
- The current source code of the file(s) involved.
- A precise output format you MUST follow so a separate program can apply your fix programmatically.

Your job is to produce the smallest set of edits that resolves the violation \
while keeping all existing behaviour intact (the repository's test suite will \
be run against your changes).

Hard rules:
1. Preserve public API and existing behaviour. The tests must still pass.
2. Do not rename existing public symbols unless absolutely necessary; if you do, keep a backwards-compatible alias.
3. Do not delete unrelated code, comments, or imports.
4. Output the JSON header and the SEARCH/REPLACE/CREATE blocks exactly as specified — no other prose.
5. Each SEARCH block must match a UNIQUE, contiguous slice of the current file byte-for-byte. \
If the same text appears more than once, include enough surrounding context to make it unique.
6. **Keep SEARCH blocks small.** A SEARCH block should typically be a single \
method/function (or just its signature + body) plus enough adjacent lines to be unique — \
NOT whole classes or whole files. Large SEARCH blocks waste output tokens and risk being \
truncated mid-emission. Prefer many small SEARCH/REPLACE blocks over one giant one.
7. CREATE blocks may only create files that do not already exist.
8. If a safe fix would require moving/copying hundreds of lines, extracting many new files, \
or otherwise risks an incomplete response, do NOT start emitting a partial refactor. \
Output NO blocks and an empty files_touched list instead.
9. If you cannot safely refactor the violation in one shot, output NO blocks and an empty files_touched list \
in the JSON header — that signals "give up on this issue cleanly."
"""


OUTPUT_FORMAT = """## Output format

Respond with EXACTLY one JSON object on a fenced ```json``` block describing your reasoning, \
followed by zero or more SEARCH/REPLACE blocks and zero or more CREATE blocks. No other prose.

```json
{
  "summary": "one-line description of the fix",
  "rationale": "why this fix resolves the violation",
  "files_touched": ["path/to/file.py", "path/to/new_file.py"]
}
```

For each modification of an existing file, emit:

<<<<<<< SEARCH path/to/file.py
exact existing text to find — must match byte-for-byte, including indentation and blank lines
=======
new text to replace it with
>>>>>>> REPLACE

The file path after `<<<<<<< SEARCH` is mandatory on every SEARCH block. \
Do not write a bare `<<<<<<< SEARCH` line.

For each new file, emit:

<<<<<<< CREATE path/to/new_file.py
full content of the new file
>>>>>>> END

The path must be relative to the repository root (e.g. `seaborn/categorical.py`). \
Do not include backticks around the path. \
The fences `<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE`, `<<<<<<< CREATE`, and `>>>>>>> END` \
must each appear on their own line."""


_USER_PROMPT_TMPL = """## Detected violation

- **Issue ID**: {issue_id}
- **Principle**: {principle_name} ({principle_abbr})
- **File**: `{file_path}`
- **Entity**: `{entity_name}` (current lines L{line_start}-L{line_end} in the file as shown below)
- **Severity**: {severity}
- **Confidence**: detected by {scan_count} independent scans

### Description
{description}

### Reasoning
{reasoning}

## Principle reference
**{principle_name}** — {definition}

What typically signals a violation:
{look_for}

## Current source

NOTE: The line numbers in the violation above were taken from the original detection scan. \
Earlier refactors in this run may have shifted them. The file content below is the CURRENT \
state of the file in the working copy — use it as the source of truth and write SEARCH \
blocks that match this content exactly.

### File: `{file_path}`
```{language}
{file_content}
```
{sibling_files_block}
{format_section}
"""


def build_system_prompt(principle: str) -> str:
    return SYSTEM_PROMPT


def build_user_prompt(
    issue: IssueRef,
    location: EntityLocation,
    sibling_files: list[str] | None = None,
    language: str = "python",
    max_full_file_lines: int = 1500,
) -> str:
    info = PRINCIPLE_DEFINITIONS[issue.principle.value]
    full_file = location.full_file_content
    line_count = full_file.count("\n") + 1
    if line_count > max_full_file_lines:
        file_content = _windowed(full_file, location.line_start,
                                 location.line_end, padding=120)
    else:
        file_content = full_file
    sibling_block = ""
    if sibling_files:
        sibling_block = (
            "\n## Sibling files in the same package (for plausible new-module names)\n"
            + "\n".join(f"- `{p}`" for p in sibling_files)
            + "\n"
        )
    return _USER_PROMPT_TMPL.format(
        issue_id=issue.issue_id,
        principle_name=info["name"],
        principle_abbr=issue.principle.value,
        file_path=issue.file_path,
        entity_name=issue.entity_name,
        line_start=location.line_start,
        line_end=location.line_end,
        severity=issue.severity,
        scan_count=issue.scan_count,
        description=issue.description,
        reasoning=issue.reasoning,
        definition=info["definition"],
        look_for=info["look_for"],
        language=language,
        file_content=file_content,
        sibling_files_block=sibling_block,
        format_section=OUTPUT_FORMAT,
    )


def _windowed(content: str, line_start: int, line_end: int, padding: int) -> str:
    lines = content.splitlines()
    lo = max(0, line_start - 1 - padding)
    hi = min(len(lines), line_end + padding)
    head = []
    if lo > 0:
        head.append(f"# ... {lo} earlier lines elided ...")
    body = lines[lo:hi]
    tail = []
    if hi < len(lines):
        tail.append(f"# ... {len(lines) - hi} later lines elided ...")
    return "\n".join(head + body + tail)
