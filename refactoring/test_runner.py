"""Run pytest in the cloned workspace and parse the result. Used by PythonAdapter."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

from .models import TestResult


def run_pytest(
    python_exe: Path,
    workspace_root: Path,
    paths: list[str] | None = None,
    timeout_sec: float = 600.0,
    extra_args: list[str] | None = None,
    fail_fast: bool = False,
    deselect_node_ids: list[str] | None = None,
) -> TestResult:
    args = [str(python_exe), "-m", "pytest", "--tb=short", "-q",
            "--no-header", "-p", "no:cacheprovider"]
    if fail_fast:
        args.append("-x")
    json_report_file = workspace_root / ".pytest_report.json"
    if json_report_file.exists():
        json_report_file.unlink()
    use_json = _has_json_report(python_exe)
    if use_json:
        args += ["--json-report", f"--json-report-file={json_report_file}"]
    if extra_args:
        args += extra_args
    for node_id in deselect_node_ids or []:
        if node_id:
            args.append(f"--deselect={node_id}")
    if paths:
        args += paths
    cmd_str = " ".join(args)
    started = time.time()
    timed_out = False
    try:
        proc = subprocess.run(
            args, cwd=str(workspace_root),
            capture_output=True, text=True,
            timeout=timeout_sec,
        )
        stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or b"").decode("utf-8", errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode("utf-8", errors="ignore") if isinstance(e.stderr, bytes) else (e.stderr or "")
        rc = -1
        timed_out = True
    duration_ms = (time.time() - started) * 1000.0
    output = (stdout or "") + ("\n[stderr]\n" + stderr if stderr else "")
    counts = _parse_counts(json_report_file, output) if not timed_out else {}
    if json_report_file.exists():
        try:
            json_report_file.unlink()
        except OSError:
            pass
    passed_flag = (
        rc == 0
        and not timed_out
        and counts.get("failed_count", 0) == 0
        and counts.get("error_count", 0) == 0
    )
    return TestResult(
        passed=passed_flag,
        command=cmd_str,
        return_code=rc,
        total=counts.get("total", 0),
        passed_count=counts.get("passed_count", 0),
        failed_count=counts.get("failed_count", 0),
        skipped_count=counts.get("skipped_count", 0),
        error_count=counts.get("error_count", 0),
        duration_ms=duration_ms,
        output_tail=_tail(output, 200),
        timed_out=timed_out,
        failed_node_ids=counts.get("failed_node_ids", []),
        error_node_ids=counts.get("error_node_ids", []),
    )


def _has_json_report(python_exe: Path) -> bool:
    try:
        proc = subprocess.run(
            [str(python_exe), "-c", "import pytest_jsonreport"],
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _parse_counts(json_report_file: Path, output: str) -> dict:
    if json_report_file.exists():
        try:
            data = json.loads(json_report_file.read_text(encoding="utf-8"))
            summary = data.get("summary", {})
            failed_ids: list[str] = []
            error_ids: list[str] = []
            for t in data.get("tests", []):
                outcome = t.get("outcome")
                nodeid = t.get("nodeid", "")
                if outcome == "failed":
                    failed_ids.append(nodeid)
                elif outcome == "error":
                    error_ids.append(nodeid)
            return {
                "total": int(summary.get("total", 0)),
                "passed_count": int(summary.get("passed", 0)),
                "failed_count": int(summary.get("failed", 0)),
                "skipped_count": int(summary.get("skipped", 0)),
                "error_count": int(summary.get("error", 0)),
                "failed_node_ids": failed_ids,
                "error_node_ids": error_ids,
            }
        except (OSError, json.JSONDecodeError):
            pass
    return _parse_textual_summary(output)


_SUMMARY_RE = re.compile(
    r"(?:^|\n)=+\s*(?P<body>[^\n]*?(?:passed|failed|error|skipped)[^\n]*?)\s*=+",
    re.IGNORECASE,
)
_PAIR_RE = re.compile(r"(\d+)\s+(passed|failed|skipped|error|errors|warnings)")


def _parse_textual_summary(output: str) -> dict:
    match = None
    for m in _SUMMARY_RE.finditer(output):
        match = m
    if not match:
        return _parse_collection_errors(output)
    counts = {"passed_count": 0, "failed_count": 0, "skipped_count": 0, "error_count": 0}
    for n, label in _PAIR_RE.findall(match.group("body")):
        n = int(n)
        if label == "passed":
            counts["passed_count"] = n
        elif label == "failed":
            counts["failed_count"] = n
        elif label == "skipped":
            counts["skipped_count"] = n
        elif label in ("error", "errors"):
            counts["error_count"] = n
    counts["total"] = (
        counts["passed_count"] + counts["failed_count"]
        + counts["skipped_count"] + counts["error_count"]
    )
    if counts["total"] == 0:
        collection_counts = _parse_collection_errors(output)
        if collection_counts:
            return collection_counts
    return counts


_COLLECTION_RE = re.compile(
    r"(?:^|\n)_+\s+ERROR collecting (?P<node>[^\n]+?)\s+_+",
    re.IGNORECASE,
)
_SHORT_ERROR_RE = re.compile(
    r"(?:^|\n)ERROR\s+(?P<node>[^\n]+?)(?:\s+-\s+|\n)",
    re.IGNORECASE,
)


def _parse_collection_errors(output: str) -> dict:
    error_ids: list[str] = []
    for match in _COLLECTION_RE.finditer(output):
        node = match.group("node").strip()
        if node and node not in error_ids:
            error_ids.append(node)
    for match in _SHORT_ERROR_RE.finditer(output):
        node = match.group("node").strip()
        if node and node not in error_ids:
            error_ids.append(node)
    if not error_ids:
        return {}
    return {
        "total": len(error_ids),
        "passed_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "error_count": len(error_ids),
        "failed_node_ids": [],
        "error_node_ids": error_ids,
    }


def _tail(text: str, lines: int) -> str:
    parts = text.splitlines()
    return "\n".join(parts[-lines:]) if len(parts) > lines else text
