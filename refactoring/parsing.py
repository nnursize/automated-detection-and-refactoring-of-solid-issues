"""Parse SEARCH/REPLACE/CREATE patch blocks from an LLM response."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .models import PatchBlock, PatchKind


@dataclass
class ParsedResponse:
    summary: str = ""
    rationale: str = ""
    files_touched: list[str] = None
    blocks: list[PatchBlock] = None
    parse_warnings: list[str] = None

    def __post_init__(self):
        if self.files_touched is None:
            self.files_touched = []
        if self.blocks is None:
            self.blocks = []
        if self.parse_warnings is None:
            self.parse_warnings = []


_JSON_FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_SEARCH_BLOCK = re.compile(
    r"^<<<<<<<[ \t]+SEARCH[ \t]+(?P<path>\S+)[ \t]*\r?\n"
    r"(?P<search>.*?)\r?\n"
    r"=======[ \t]*\r?\n"
    r"(?P<replace>.*?)\r?\n"
    r">>>>>>>[ \t]+REPLACE[ \t]*$",
    re.DOTALL | re.MULTILINE,
)
_SEARCH_BLOCK_WITHOUT_PATH = re.compile(
    r"^<<<<<<<[ \t]+SEARCH[ \t]*\r?\n"
    r"(?P<search>.*?)\r?\n"
    r"=======[ \t]*\r?\n"
    r"(?P<replace>.*?)\r?\n"
    r">>>>>>>[ \t]+REPLACE[ \t]*$",
    re.DOTALL | re.MULTILINE,
)
_CREATE_BLOCK = re.compile(
    r"^<<<<<<<[ \t]+CREATE[ \t]+(?P<path>\S+)[ \t]*\r?\n"
    r"(?P<content>.*?)\r?\n"
    r">>>>>>>[ \t]+END[ \t]*$",
    re.DOTALL | re.MULTILINE,
)


def parse_response(text: str) -> ParsedResponse:
    out = ParsedResponse()

    json_match = _JSON_FENCE.search(text)
    if json_match:
        try:
            payload = json.loads(json_match.group(1))
            out.summary = str(payload.get("summary", ""))[:500]
            out.rationale = str(payload.get("rationale", ""))[:5000]
            ft = payload.get("files_touched", [])
            if isinstance(ft, list):
                out.files_touched = [str(x) for x in ft]
        except json.JSONDecodeError as e:
            out.parse_warnings.append(f"json header parse error: {e}")
    else:
        out.parse_warnings.append("no ```json header found")

    for m in _SEARCH_BLOCK.finditer(text):
        out.blocks.append(PatchBlock(
            kind=PatchKind.SEARCH_REPLACE,
            file_path=_clean_path(m.group("path")),
            search_text=m.group("search"),
            replace_text=m.group("replace"),
        ))
    if not out.blocks:
        _parse_pathless_search_blocks(text, out)
    for m in _CREATE_BLOCK.finditer(text):
        out.blocks.append(PatchBlock(
            kind=PatchKind.CREATE,
            file_path=_clean_path(m.group("path")),
            search_text=None,
            replace_text=m.group("content"),
        ))

    return out


def _parse_pathless_search_blocks(text: str, out: ParsedResponse) -> None:
    """Recover SEARCH blocks when the model omitted the file path.

    The prompt requires `<<<<<<< SEARCH path/to/file.py`. Some Gemini responses
    instead emit bare `<<<<<<< SEARCH` while still putting exactly one file in
    the JSON `files_touched` list. In that one-file case the target is
    unambiguous, so keep the attempt usable instead of discarding all blocks.
    """
    matches = list(_SEARCH_BLOCK_WITHOUT_PATH.finditer(text))
    if not matches:
        return
    if len(out.files_touched) != 1:
        out.parse_warnings.append(
            "SEARCH blocks omitted paths and files_touched is not a single file"
        )
        return
    path = _clean_path(out.files_touched[0])
    out.parse_warnings.append(
        f"SEARCH blocks omitted paths; inferred target file from files_touched: {path}"
    )
    for m in matches:
        out.blocks.append(PatchBlock(
            kind=PatchKind.SEARCH_REPLACE,
            file_path=path,
            search_text=m.group("search"),
            replace_text=m.group("replace"),
        ))


def _clean_path(p: str) -> str:
    p = p.strip().strip("`").strip("'\"")
    return p.replace("\\", "/")
