"""Parse LLM responses into structured findings."""

from __future__ import annotations

import json
import re

from .models import Finding


def parse_llm_response(raw_text: str) -> tuple[list[Finding], int]:
    """Extract findings from raw LLM response text.

    Returns:
        Tuple of (valid findings, number of parse errors).
    """
    json_str = _extract_json(raw_text)
    if json_str is None:
        return [], 1

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # Try to repair common issues
        json_str = _repair_json(json_str)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return [], 1

    if not isinstance(data, dict) or "findings" not in data:
        # Maybe the LLM returned a list directly
        if isinstance(data, list):
            data = {"findings": data}
        else:
            return [], 1

    findings = []
    errors = 0
    for item in data["findings"]:
        try:
            finding = _validate_finding(item)
            if finding:
                findings.append(finding)
            else:
                errors += 1
        except Exception:
            errors += 1

    return findings, errors


def _extract_json(text: str) -> str | None:
    """Extract JSON from text, handling markdown code fences and truncation."""
    # Strip markdown code fences to get raw content
    raw = text.strip()
    fence_match = re.search(r"```(?:json)?\s*\n?(.*)", raw, re.DOTALL)
    if fence_match:
        raw = fence_match.group(1)
        # Remove closing fence if present
        raw = re.sub(r"\n?```\s*$", "", raw).strip()

    brace_start = raw.find("{")
    if brace_start == -1:
        return None

    raw = raw[brace_start:]

    # Try 1: Find the matching closing brace (complete JSON)
    depth = 0
    for i, ch in enumerate(raw):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return raw[: i + 1]

    # Try 2: Response was truncated — recover complete findings up to the last
    # fully-closed finding object. Find the last complete "}," or "}" that closes
    # a finding dict (depth returns to 1, meaning we're back inside "findings": [...]).
    last_complete_end = -1
    depth = 0
    for i, ch in enumerate(raw):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 1:  # closed one finding, still inside outer object
                last_complete_end = i

    if last_complete_end != -1:
        # Reconstruct valid JSON up to the last complete finding
        truncated = raw[: last_complete_end + 1]
        # Close the findings array and outer object
        return truncated + "\n  ]\n}"

    return None


def _repair_json(json_str: str) -> str:
    """Attempt to fix common JSON issues from LLM output."""
    # Remove trailing commas before ] or }
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

    # Fix unescaped newlines inside strings (crude)
    # This is hard to do perfectly, but we try
    json_str = json_str.replace("\n", "\\n")

    # Try to close unclosed arrays/objects
    open_braces = json_str.count("{") - json_str.count("}")
    open_brackets = json_str.count("[") - json_str.count("]")
    json_str += "]" * open_brackets + "}" * open_braces

    return json_str


def _validate_finding(item: dict) -> Finding | None:
    """Validate and create a Finding from a dict. Returns None if invalid."""
    required_fields = ["file_path", "entity_name", "principle"]
    for field in required_fields:
        if field not in item or not item[field]:
            return None

    # Normalize and provide defaults
    item.setdefault("entity_type", "class")
    item.setdefault("line_start", 0)
    item.setdefault("line_end", 0)
    item.setdefault("severity", "medium")
    item.setdefault("description", "No description provided")
    item.setdefault("reasoning", "No reasoning provided")

    # Normalize entity_type
    entity_type = str(item["entity_type"]).lower()
    if entity_type not in ("class", "method", "module"):
        item["entity_type"] = "class"

    # Normalize severity
    severity = str(item["severity"]).lower()
    if severity not in ("high", "medium", "low"):
        item["severity"] = "medium"

    # Normalize principle
    item["principle"] = str(item["principle"]).upper()

    # Ensure line numbers are ints
    item["line_start"] = int(item.get("line_start", 0))
    item["line_end"] = int(item.get("line_end", 0))

    # Normalize file path separators
    item["file_path"] = item["file_path"].replace("\\", "/")

    try:
        return Finding(**item)
    except Exception:
        return None
