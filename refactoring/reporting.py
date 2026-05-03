"""Mock-PR generation per attempt + master summaries across all attempts."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path

from . import metrics as metrics_mod
from .models import (
    AttemptStatus,
    IssueRef,
    MetricsSnapshot,
    PatchKind,
    RefactorAttempt,
)


_MD_PREVIEW_LINES = 60   # cap each code block in pull_request.md


def _truncate_block(text: str, max_lines: int = _MD_PREVIEW_LINES) -> tuple[str, int]:
    """Return (possibly-truncated text, total_line_count)."""
    lines = (text or "").splitlines()
    n = len(lines)
    if n > max_lines:
        text = "\n".join(lines[:max_lines]) + f"\n... ({n - max_lines} more line(s) truncated)"
    return text, n


def write_pull_request(
    attempt: RefactorAttempt,
    issue: IssueRef,
    diff_text: str,
    out_dir: Path,
) -> dict:
    """Write pull_request.json and pull_request.md, return the JSON payload."""
    payload = build_pull_request_payload(attempt, issue, diff_text)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pull_request.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    (out_dir / "pull_request.md").write_text(
        render_pull_request_md(payload), encoding="utf-8"
    )
    return payload


def rerender_attempt_pr(out_dir: Path, workspace=None) -> dict | None:
    """Rebuild pull_request.json + pull_request.md from existing on-disk artifacts.

    Reads the existing `pull_request.json` (for issue/status metadata),
    `patch_blocks.json` (for structured changes) and `applied_diff.patch` (for
    the unified diff), then re-renders both PR files in the current format.

    If `workspace` is provided, also recomputes metrics_before / metrics_after
    by reading the file content at the appropriate commits via `git show`. This
    backfills metrics for older runs that didn't compute non-Python metrics.

    Used by `--rerender-prs`: bring older artifacts up to date with renderer
    improvements without re-calling the LLM.

    Returns the regenerated payload, or None if the directory is incomplete.
    """
    pr_path = out_dir / "pull_request.json"
    if not pr_path.exists():
        return None
    try:
        existing = json.loads(pr_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    blocks_path = out_dir / "patch_blocks.json"
    blocks: list[dict] = []
    if blocks_path.exists():
        try:
            blocks = json.loads(blocks_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            blocks = []

    changes = []
    files_created: list[str] = []
    files_modified: list[str] = []
    for raw in blocks:
        kind = raw.get("kind", "")
        fp = raw.get("file_path", "")
        if kind == "create":
            files_created.append(fp)
            new_content = raw.get("replace_text", "")
            changes.append({
                "kind": "create",
                "file_path": fp,
                "new_content": new_content,
                "new_content_lines": (new_content.count("\n") + 1) if new_content else 0,
            })
        elif kind == "search_replace":
            files_modified.append(fp)
            search_text = raw.get("search_text") or ""
            replace_text = raw.get("replace_text") or ""
            changes.append({
                "kind": "search_replace",
                "file_path": fp,
                "search_text": search_text,
                "replace_text": replace_text,
                "search_lines": (search_text.count("\n") + 1) if search_text else 0,
                "replace_lines": (replace_text.count("\n") + 1) if replace_text else 0,
            })
    files_created = sorted(set(files_created))
    files_modified = sorted(set(files_modified))

    fl = existing.get("fix_logic")
    if fl is not None:
        fl["files_created"] = files_created
        fl["files_modified"] = files_modified
        fl["changes"] = changes
        fl["patch_blocks_count"] = len(blocks)

    raw_path = out_dir / "raw_response.json"
    if raw_path.exists():
        try:
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            existing["llm_response"] = {
                "finish_reason": raw.get("finish_reason"),
                "prompt_tokens": raw.get("prompt_tokens", 0),
                "completion_tokens": raw.get("completion_tokens", 0),
            }
        except (OSError, json.JSONDecodeError):
            pass

    diff_path = out_dir / "applied_diff.patch"
    recomputed_diff = None
    if workspace is not None:
        head = existing.get("head_commit")
        status = existing.get("status")
        if head and status in (
            AttemptStatus.APPLIED_PASSED.value,
            AttemptStatus.APPLIED_UNVERIFIED.value,
        ):
            try:
                recomputed_diff = workspace.diff_between(f"{head}~1", head)
                diff_path.write_text(recomputed_diff, encoding="utf-8")
            except Exception:
                recomputed_diff = None

    if recomputed_diff is not None:
        existing["diff"] = recomputed_diff
    elif diff_path.exists():
        try:
            existing["diff"] = diff_path.read_text(encoding="utf-8")
        except OSError:
            pass

    # Recompute metrics if a workspace is supplied and the attempt was committed.
    if workspace is not None:
        before, after = _recompute_metrics_for_attempt(
            workspace, existing,
            files_touched=(files_modified + files_created),
        )
        if before is not None or after is not None:
            existing["metrics"] = {
                "before": _snapshot_to_list(before) if before else None,
                "after": _snapshot_to_list(after) if after else None,
            }
            # Persist alongside the PR for backwards compatibility.
            if before is not None:
                (out_dir / "metrics_before.json").write_text(
                    json.dumps(before.model_dump(), indent=2, default=str),
                    encoding="utf-8",
                )
            if after is not None:
                (out_dir / "metrics_after.json").write_text(
                    json.dumps(after.model_dump(), indent=2, default=str),
                    encoding="utf-8",
                )

    pr_path.write_text(
        json.dumps(existing, indent=2, default=str), encoding="utf-8"
    )
    (out_dir / "pull_request.md").write_text(
        render_pull_request_md(existing), encoding="utf-8"
    )
    return existing


def _recompute_metrics_for_attempt(
    workspace, payload: dict, files_touched: list[str],
) -> tuple[MetricsSnapshot | None, MetricsSnapshot | None]:
    """Recompute (before, after) metrics from git history.

    `before` = file content at parent of attempt's head_commit (or None for
    files that were CREATEd in this attempt — they didn't exist before).
    `after` = file content at attempt's head_commit.

    Returns (None, None) if the attempt was never committed (no head_commit on
    the payload — happens for patch_failed/applied_failed/llm_error/obsolete).
    """
    head = payload.get("head_commit")
    status = payload.get("status")
    # Only attempts that produced a real commit have meaningful before/after.
    if not head or status not in (
        AttemptStatus.APPLIED_PASSED.value,
        AttemptStatus.APPLIED_UNVERIFIED.value,
    ):
        return None, None
    parent = f"{head}~1"
    before_files = []
    after_files = []
    for rel in files_touched:
        before_content = workspace.file_at_commit(parent, rel)
        if before_content is not None:
            before_files.append(metrics_mod.metrics_for_source(rel, before_content))
        after_content = workspace.file_at_commit(head, rel)
        if after_content is not None:
            after_files.append(metrics_mod.metrics_for_source(rel, after_content))
    return MetricsSnapshot(files=before_files), MetricsSnapshot(files=after_files)


def rerender_all_prs(attempts_root: Path, workspace=None) -> int:
    """Walk attempts_root and rerender every per-attempt PR. Returns count rerendered.

    If `workspace` is provided, metrics are also recomputed from git history.
    """
    if not attempts_root.exists():
        return 0
    count = 0
    for principle_dir in sorted(attempts_root.iterdir()):
        if not principle_dir.is_dir():
            continue
        for issue_dir in sorted(principle_dir.iterdir()):
            if not issue_dir.is_dir():
                continue
            if rerender_attempt_pr(issue_dir, workspace=workspace) is not None:
                count += 1
    return count


def build_pull_request_payload(
    attempt: RefactorAttempt,
    issue: IssueRef,
    diff_text: str,
) -> dict:
    fix_logic = None
    files_created = sorted({
        b.file_path for b in attempt.patch_blocks if b.kind == PatchKind.CREATE
    })
    files_modified = sorted({
        b.file_path for b in attempt.patch_blocks if b.kind == PatchKind.SEARCH_REPLACE
    })
    if attempt.status in {AttemptStatus.APPLIED_PASSED, AttemptStatus.APPLIED_FAILED,
                         AttemptStatus.APPLIED_UNVERIFIED, AttemptStatus.PATCH_FAILED}:
        fix_logic = {
            "model": attempt.model,
            "temperature": attempt.temperature,
            "summary": _extract_summary(attempt.response_text),
            "rationale": _extract_rationale(attempt.response_text),
            "files_touched": attempt.files_touched,
            "files_created": files_created,
            "files_modified": files_modified,
            "patch_blocks_count": len(attempt.patch_blocks),
            "changes": [_serialize_block(b) for b in attempt.patch_blocks],
        }
    test_results = None
    if attempt.test_result is not None:
        tr = attempt.test_result
        test_results = {
            "command": tr.command,
            "passed": tr.passed,
            "total": tr.total,
            "passed_count": tr.passed_count,
            "failed_count": tr.failed_count,
            "skipped_count": tr.skipped_count,
            "error_count": tr.error_count,
            "duration_ms": tr.duration_ms,
            "timed_out": tr.timed_out,
            "new_failures_count": len(tr.new_failures),
            "pre_existing_failures_count": len(tr.pre_existing_failures),
            "new_failures": tr.new_failures[:25],
            "pre_existing_failures": tr.pre_existing_failures[:25],
            "output_tail": tr.output_tail,
        }
    return {
        "issue_id": issue.issue_id,
        "principle": issue.principle.value,
        "title": _title_for(issue, attempt),
        "branch": f"refactor/{issue.issue_id}",
        "base": "main",
        "head_commit": attempt.head_commit,
        "status": attempt.status.value,
        "obsolete_reason": attempt.obsolete_reason,
        "apply_error": attempt.apply_error,
        "error": attempt.error,
        "detection_label": {
            "label": attempt.detection_label,
            "explanation": attempt.detection_label_explanation,
        },
        "llm_response": {
            "finish_reason": attempt.llm_finish_reason,
            "prompt_tokens": attempt.prompt_tokens,
            "completion_tokens": attempt.completion_tokens,
        },
        "detected_issue": {
            "file_path": issue.file_path,
            "entity_name": issue.entity_name,
            "entity_type": issue.entity_type,
            "line_start": issue.line_start,
            "line_end": issue.line_end,
            "severity": issue.severity,
            "scan_count": issue.scan_count,
            "description": issue.description,
            "reasoning": issue.reasoning,
        },
        "fix_logic": fix_logic,
        "test_results": test_results,
        "metrics": {
            "before": _snapshot_to_list(attempt.metrics_before),
            "after":  _snapshot_to_list(attempt.metrics_after),
        },
        "diff": diff_text,
        "duration_ms": attempt.duration_ms,
    }


def render_pull_request_md(p: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {p['title']}")
    lines.append("")
    lines.append(f"**Status:** `{p['status']}`  ")
    lines.append(f"**Branch:** `{p['branch']}` -> `{p['base']}`  ")
    if p.get("head_commit"):
        lines.append(f"**Head commit:** `{p['head_commit']}`  ")
    lr = p.get("llm_response") or {}
    if any(lr.get(k) for k in ("finish_reason", "prompt_tokens", "completion_tokens")):
        lines.append(
            f"**LLM finish:** `{lr.get('finish_reason') or ''}` "
            f"(prompt {lr.get('prompt_tokens', 0)}, "
            f"completion {lr.get('completion_tokens', 0)})  "
        )
    lines.append("")

    di = p["detected_issue"]
    lines.append("## Detected issue")
    lines.append("")
    lines.append(f"- **File**: `{di['file_path']}`")
    lines.append(f"- **Entity**: `{di['entity_name']}` ({di['entity_type']})")
    lines.append(f"- **Lines (at detection time)**: L{di['line_start']}–L{di['line_end']}")
    lines.append(f"- **Severity**: {di['severity']}")
    lines.append(f"- **Confidence**: detected by {di['scan_count']} scan(s)")
    lines.append("")
    lines.append(f"**Description.** {di['description']}")
    lines.append("")
    lines.append(f"**Reasoning.** {di['reasoning']}")
    lines.append("")

    if p.get("obsolete_reason"):
        lines.append("## Obsolete")
        lines.append("")
        lines.append(p["obsolete_reason"])
        lines.append("")

    dl = p.get("detection_label") or {}
    if dl.get("label") is not None:
        lines.append("## Detection label")
        lines.append("")
        lines.append(f"- **Label**: `{str(dl.get('label')).lower()}`")
        if dl.get("explanation"):
            lines.append("")
            lines.append(dl["explanation"])
        lines.append("")

    fl = p.get("fix_logic")
    if fl:
        lines.append("## Fix logic")
        lines.append("")
        lines.append(f"- **Model**: `{fl['model']}` (temperature {fl['temperature']})")
        lines.append(f"- **Patch blocks**: {fl['patch_blocks_count']}")
        if fl.get("files_created"):
            lines.append(f"- **Files created** ({len(fl['files_created'])}): "
                         + ", ".join(f"`{f}`" for f in fl["files_created"]))
        if fl.get("files_modified"):
            lines.append(f"- **Files modified** ({len(fl['files_modified'])}): "
                         + ", ".join(f"`{f}`" for f in fl["files_modified"]))
        if not fl.get("files_created") and not fl.get("files_modified") and fl.get("files_touched"):
            lines.append(f"- **Files touched**: " + ", ".join(f"`{f}`" for f in fl["files_touched"]))
        lines.append("")
        if fl.get("summary"):
            lines.append(f"**Summary.** {fl['summary']}")
            lines.append("")
        if fl.get("rationale"):
            lines.append(f"**Rationale.** {fl['rationale']}")
            lines.append("")

        changes = fl.get("changes") or []
        if changes:
            lines.append("## Changes overview")
            lines.append("")
            lines.append(f"_{len(changes)} patch block(s). Code blocks are previewed up to "
                         f"{_MD_PREVIEW_LINES} lines each — full text is in `pull_request.json` "
                         f"(`fix_logic.changes`)._")
            lines.append("")
            for i, ch in enumerate(changes, start=1):
                if ch["kind"] == "create":
                    new_lines = ch.get("new_content_lines", 0)
                    lines.append(f"### {i}. CREATE `{ch['file_path']}` ({new_lines} line(s))")
                    lines.append("")
                    body, _ = _truncate_block(ch.get("new_content", ""))
                    lang = _md_lang_for(ch["file_path"])
                    lines.append(f"```{lang}")
                    lines.append(body)
                    lines.append("```")
                    lines.append("")
                else:  # search_replace
                    sn = ch.get("search_lines", 0)
                    rn = ch.get("replace_lines", 0)
                    lines.append(f"### {i}. EDIT `{ch['file_path']}` "
                                 f"({sn}-line block → {rn}-line replacement)")
                    lines.append("")
                    lang = _md_lang_for(ch["file_path"])
                    s_body, _ = _truncate_block(ch.get("search_text", ""))
                    lines.append("**Replaces:**")
                    lines.append("")
                    lines.append(f"```{lang}")
                    lines.append(s_body)
                    lines.append("```")
                    lines.append("")
                    r_body, _ = _truncate_block(ch.get("replace_text", ""))
                    lines.append("**With:**")
                    lines.append("")
                    lines.append(f"```{lang}")
                    lines.append(r_body)
                    lines.append("```")
                    lines.append("")

    if p.get("apply_error"):
        lines.append("## Apply error")
        lines.append("")
        lines.append(f"```\n{p['apply_error']}\n```")
        lines.append("")
    if p.get("error"):
        lines.append("## LLM / runtime error")
        lines.append("")
        lines.append(f"```\n{p['error']}\n```")
        lines.append("")

    tr = p.get("test_results")
    if tr:
        lines.append("## Test results")
        lines.append("")
        passmark = "PASSED" if tr["passed"] else "FAILED"
        lines.append(f"**{passmark}** — {tr['passed_count']}/{tr['total']} passed, "
                     f"{tr['failed_count']} failed, {tr['skipped_count']} skipped, "
                     f"{tr['error_count']} errored "
                     f"(duration {tr['duration_ms']:.0f} ms"
                     + (", **timed out**" if tr.get("timed_out") else "")
                     + ").")
        nfc = tr.get("new_failures_count", 0)
        pfc = tr.get("pre_existing_failures_count", 0)
        if nfc or pfc:
            lines.append("")
            lines.append(f"- New failures introduced by this refactor: **{nfc}**")
            lines.append(f"- Pre-existing failures (unrelated to this refactor): **{pfc}**")
            new_list = tr.get("new_failures") or []
            if new_list:
                lines.append("")
                lines.append("New-failure node IDs (first 25):")
                lines.append("")
                for nid in new_list:
                    lines.append(f"  - `{nid}`")
        lines.append("")
        lines.append(f"Command: `{tr['command']}`")
        lines.append("")
        if tr.get("output_tail"):
            lines.append("<details><summary>Output tail</summary>")
            lines.append("")
            lines.append("```")
            lines.append(tr["output_tail"])
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    metrics = p.get("metrics") or {}
    before = metrics.get("before") or []
    after = metrics.get("after") or []
    if before or after:
        lines.append("## Code-quality metrics")
        lines.append("")
        lines.append("Per file. Cells show `before → after`. For non-Python files, "
                     "MI is unavailable and CC is approximate "
                     "(branching-keyword count divided by detected functions).")
        lines.append("")
        lines.append("| File | LOC | Funcs | Avg CC | Max CC | MI |")
        lines.append("|------|-----|------:|-------:|-------:|---:|")
        files = sorted({m["file"] for m in (before + after)})
        before_map = {m["file"]: m for m in before}
        after_map = {m["file"]: m for m in after}
        for f in files:
            b = before_map.get(f, {})
            a = after_map.get(f, {})
            lines.append(
                f"| `{f}` "
                f"| {_pair(b.get('loc'), a.get('loc'))} "
                f"| {_pair(b.get('function_count'), a.get('function_count'))} "
                f"| {_pair(b.get('avg_cc'), a.get('avg_cc'))} "
                f"| {_pair(b.get('max_cc'), a.get('max_cc'))} "
                f"| {_pair(b.get('mi'), a.get('mi'))} |"
            )
        lines.append("")

    diff = p.get("diff") or ""
    lines.append("## Diff")
    lines.append("")
    if diff.strip():
        lines.append("```diff")
        lines.append(diff if diff.endswith("\n") else diff)
        lines.append("```")
    else:
        lines.append("*(no diff — patch was not applied)*")
    lines.append("")
    return "\n".join(lines)


def write_master_reports(
    repo_name: str,
    attempts_root: Path,
    reports_dir: Path,
    final_full_suite_result: dict | None = None,
) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    pull_requests: list[dict] = []
    rows: list[dict] = []

    if not attempts_root.exists():
        # Nothing to summarise — write empty registry placeholders so callers
        # that expect the files always get something readable.
        (reports_dir / f"{repo_name}_pull_requests.json").write_text(
            json.dumps({"repo_name": repo_name, "count": 0, "pull_requests": []},
                       indent=2),
            encoding="utf-8",
        )
        (reports_dir / f"{repo_name}_refactor_summary.csv").write_text("", encoding="utf-8")
        (reports_dir / f"{repo_name}_refactor_summary.md").write_text(
            f"# Refactor summary: {repo_name}\n\n"
            f"_No attempts found under `{attempts_root}` yet._\n",
            encoding="utf-8",
        )
        (reports_dir / f"{repo_name}_refactor_registry.json").write_text(
            json.dumps({"repo_name": repo_name, "rows": [],
                        "final_full_suite": final_full_suite_result},
                       indent=2, default=str),
            encoding="utf-8",
        )
        return

    for principle_dir in sorted(attempts_root.iterdir()):
        if not principle_dir.is_dir():
            continue
        for issue_dir in sorted(principle_dir.iterdir()):
            pr_path = issue_dir / "pull_request.json"
            if not pr_path.exists():
                continue
            try:
                payload = json.loads(pr_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            pull_requests.append(payload)
            rows.append(_row_for(payload))

    json_path = reports_dir / f"{repo_name}_pull_requests.json"
    json_path.write_text(
        json.dumps({"repo_name": repo_name, "count": len(pull_requests),
                    "pull_requests": pull_requests}, indent=2, default=str),
        encoding="utf-8",
    )

    csv_path = reports_dir / f"{repo_name}_refactor_summary.csv"
    csv_path.write_text(_render_csv(rows), encoding="utf-8")

    md_path = reports_dir / f"{repo_name}_refactor_summary.md"
    md_path.write_text(_render_summary_md(repo_name, rows, final_full_suite_result),
                       encoding="utf-8")

    registry_path = reports_dir / f"{repo_name}_refactor_registry.json"
    registry_path.write_text(
        json.dumps({"repo_name": repo_name, "rows": rows,
                    "final_full_suite": final_full_suite_result},
                   indent=2, default=str),
        encoding="utf-8",
    )

    if final_full_suite_result is not None:
        full_path = reports_dir / f"{repo_name}_full_suite_final.json"
        full_path.write_text(
            json.dumps(final_full_suite_result, indent=2, default=str),
            encoding="utf-8",
        )


def _row_for(p: dict) -> dict:
    tr = p.get("test_results") or {}
    fl = p.get("fix_logic") or {}
    before = (p.get("metrics") or {}).get("before") or []
    after = (p.get("metrics") or {}).get("after") or []
    return {
        "issue_id": p["issue_id"],
        "principle": p["principle"],
        "status": p["status"],
        "detection_label": (p.get("detection_label") or {}).get("label"),
        "file_path": p["detected_issue"]["file_path"],
        "entity": p["detected_issue"]["entity_name"],
        "model": fl.get("model", ""),
        "patch_blocks": fl.get("patch_blocks_count", 0),
        "tests_total": tr.get("total", 0),
        "tests_passed": tr.get("passed_count", 0),
        "tests_failed": tr.get("failed_count", 0),
        "tests_skipped": tr.get("skipped_count", 0),
        "tests_duration_ms": tr.get("duration_ms", 0.0),
        "avg_cc_before": _avg([m["avg_cc"] for m in before]) if before else None,
        "avg_cc_after":  _avg([m["avg_cc"] for m in after]) if after else None,
        "mi_before": _avg([m["mi"] for m in before]) if before else None,
        "mi_after":  _avg([m["mi"] for m in after]) if after else None,
        "head_commit": p.get("head_commit") or "",
    }


def _avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else None


def _render_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def _render_summary_md(
    repo_name: str, rows: list[dict], final: dict | None,
) -> str:
    by_status: dict[str, int] = {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    lines = [
        f"# Refactor summary: {repo_name}",
        "",
        f"- Total attempts: **{len(rows)}**",
    ]
    for status in ["applied_passed", "applied_unverified", "applied_failed",
                   "patch_failed", "detection_rejected", "obsolete", "llm_error"]:
        if status in by_status:
            lines.append(f"  - `{status}`: {by_status[status]}")
    if final is not None:
        passed = final.get("passed")
        if passed is True:
            lines.append("- Final full-suite gate: **PASSED**")
        elif passed is False:
            lines.append("- Final full-suite gate: **FAILED**")
        else:
            lines.append("- Final full-suite gate: not run")
    lines.append("")
    lines.append("## All attempts")
    lines.append("")
    lines.append("| Issue | Principle | Status | Tests passed/total | CC before -> after | MI before -> after | File |")
    lines.append("|-------|-----------|--------|--------------------|--------------------|--------------------|------|")
    for r in rows:
        tests = (
            f"{r['tests_passed']}/{r['tests_total']}"
            if r["tests_total"] else "-"
        )
        cc = (
            f"{r['avg_cc_before']} -> {r['avg_cc_after']}"
            if r["avg_cc_before"] is not None and r["avg_cc_after"] is not None
            else "-"
        )
        mi = (
            f"{r['mi_before']} -> {r['mi_after']}"
            if r["mi_before"] is not None and r["mi_after"] is not None
            else "-"
        )
        lines.append(
            f"| {r['issue_id']} | {r['principle']} | `{r['status']}` | "
            f"{tests} | {cc} | {mi} | `{r['file_path']}` |"
        )
    return "\n".join(lines)


def _snapshot_to_list(snapshot: MetricsSnapshot | None):
    if snapshot is None:
        return None
    return [m.model_dump() for m in snapshot.files]


def _title_for(issue: IssueRef, attempt: RefactorAttempt) -> str:
    head = issue.description.strip()
    if len(head) > 80:
        head = head[:77].rstrip() + "..."
    return f"Refactor {issue.issue_id} ({issue.principle.value}): {head}"


def _pair(before, after) -> str:
    """Render a 'before → after' cell, stripping decimals on integer-typed values."""
    def fmt(v):
        if v is None:
            return "-"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    return f"{fmt(before)} → {fmt(after)}"


_LANG_BY_EXT = {
    ".py": "python", ".java": "java", ".kt": "kotlin",
    ".rb": "ruby", ".js": "javascript", ".ts": "typescript",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "c", ".h": "c",
    ".rs": "rust", ".go": "go", ".sh": "bash", ".yaml": "yaml", ".yml": "yaml",
    ".xml": "xml", ".html": "html", ".css": "css", ".json": "json",
}


def _md_lang_for(file_path: str) -> str:
    """Pick the best-effort fenced-code-block language hint from a file path."""
    from pathlib import Path
    return _LANG_BY_EXT.get(Path(file_path).suffix, "")


def _serialize_block(b) -> dict:
    """Per-block dict for the structured changes list in pull_request.json.

    Includes the *full* search/replace/new-content text — labelers can read
    everything they need without opening patch_blocks.json or applied_diff.patch.
    """
    out = {"kind": b.kind.value, "file_path": b.file_path}
    if b.kind == PatchKind.SEARCH_REPLACE:
        out["search_text"] = b.search_text or ""
        out["replace_text"] = b.replace_text
        out["search_lines"] = (b.search_text or "").count("\n") + 1 if b.search_text else 0
        out["replace_lines"] = b.replace_text.count("\n") + 1 if b.replace_text else 0
    else:  # CREATE
        out["new_content"] = b.replace_text
        out["new_content_lines"] = b.replace_text.count("\n") + 1 if b.replace_text else 0
    return out


def _extract_summary(response_text: str) -> str:
    return _extract_json_field(response_text, "summary")


def _extract_rationale(response_text: str) -> str:
    return _extract_json_field(response_text, "rationale")


def _extract_json_field(response_text: str, key: str) -> str:
    import re
    m = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if not m:
        return ""
    try:
        payload = json.loads(m.group(1))
    except json.JSONDecodeError:
        return ""
    val = payload.get(key, "")
    return str(val)
