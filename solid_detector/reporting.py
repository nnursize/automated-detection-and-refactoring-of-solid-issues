"""Report generation — Markdown, JSON, and CSV outputs."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path

from .models import Principle, ScanRecord
from .registry import IssueRegistry


_SHORTLIST_PER_PRINCIPLE = 12
_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}


def generate_all_reports(
    registry: IssueRegistry,
    scan_dir: Path,
    reports_dir: Path,
    repo_name: str,
):
    """Generate all report types."""
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Per-principle Markdown reports
    for principle in Principle:
        report = generate_principle_report(registry, principle.value, repo_name)
        output_path = reports_dir / f"{repo_name}_{principle.value}_report.md"
        output_path.write_text(report, encoding="utf-8")
        print(f"  Written: {output_path}")

    # Master summary report
    summary = generate_summary_report(registry, repo_name)
    summary_path = reports_dir / f"{repo_name}_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"  Written: {summary_path}")

    # Master JSON registry (copy)
    json_path = reports_dir / f"{repo_name}_registry.json"
    registry_data = {
        "repo_name": repo_name,
        "summary": registry.summary(),
        "issues": [issue.model_dump() for issue in registry.issues],
    }
    json_path.write_text(
        json.dumps(registry_data, indent=2, default=str), encoding="utf-8"
    )
    print(f"  Written: {json_path}")

    # Refactor shortlist (top 12 per principle) — JSON + Markdown
    shortlist = build_refactor_shortlist(registry, repo_name)
    shortlist_json = reports_dir / f"{repo_name}_refactor_shortlist.json"
    shortlist_json.write_text(
        json.dumps(shortlist, indent=2, default=str), encoding="utf-8"
    )
    print(f"  Written: {shortlist_json}")

    shortlist_md = reports_dir / f"{repo_name}_refactor_shortlist.md"
    shortlist_md.write_text(
        render_shortlist_md(shortlist), encoding="utf-8"
    )
    print(f"  Written: {shortlist_md}")

    # Scan summary CSV
    csv_path = reports_dir / f"{repo_name}_scan_summary.csv"
    csv_content = generate_scan_csv(scan_dir)
    csv_path.write_text(csv_content, encoding="utf-8")
    print(f"  Written: {csv_path}")


def generate_principle_report(
    registry: IssueRegistry, principle: str, repo_name: str
) -> str:
    """Generate a Markdown report for a single SOLID principle."""
    issues = registry.get_issues_by_principle(principle)
    issues.sort(key=lambda i: i.scan_count, reverse=True)

    lines = [
        f"# {principle} Violation Report: {repo_name}",
        "",
        "## Summary",
        f"- **Total unique issues**: {len(issues)}",
        f"- **High severity**: {sum(1 for i in issues if i.canonical_finding.severity.value == 'high')}",
        f"- **Medium severity**: {sum(1 for i in issues if i.canonical_finding.severity.value == 'medium')}",
        f"- **Low severity**: {sum(1 for i in issues if i.canonical_finding.severity.value == 'low')}",
        f"- **Found by multiple scans**: {sum(1 for i in issues if i.scan_count > 1)}/{len(issues)}",
        "",
        "## Issues",
        "",
    ]

    for issue in issues:
        f = issue.canonical_finding
        severity_badge = f"[{f.severity.value.upper()}]"
        lines.extend([
            f"### {issue.issue_id} {severity_badge} {f.file_path} — {f.entity_name}",
            f"- **Confidence**: Found in {issue.scan_count} scan(s)",
            f"- **Lines**: {f.line_start}–{f.line_end}",
            f"- **Type**: {f.entity_type.value}",
            f"- **Description**: {f.description}",
            f"- **Reasoning**: {f.reasoning}",
            "",
        ])

    if not issues:
        lines.append("*No violations detected for this principle.*\n")

    return "\n".join(lines)


def generate_summary_report(registry: IssueRegistry, repo_name: str) -> str:
    """Generate a master summary report across all principles."""
    summary = registry.summary()
    lines = [
        f"# SOLID Violation Detection Summary: {repo_name}",
        "",
        f"**Total unique issues**: {summary['total_issues']}",
        "",
        "## By Principle",
        "",
        "| Principle | Issues | Multi-scan |",
        "|-----------|--------|------------|",
    ]

    for principle, stats in summary["by_principle"].items():
        lines.append(
            f"| {principle} | {stats['total']} | {stats['multi_scan']} |"
        )

    lines.extend([
        "",
        "## All Issues (sorted by confidence)",
        "",
    ])

    all_issues = sorted(registry.issues, key=lambda i: i.scan_count, reverse=True)
    for issue in all_issues:
        f = issue.canonical_finding
        lines.append(
            f"- **{issue.issue_id}** [{f.severity.value.upper()}] "
            f"`{f.file_path}` — {f.entity_name} "
            f"(found {issue.scan_count}x): {f.description}"
        )

    return "\n".join(lines)


def build_refactor_shortlist(registry: IssueRegistry, repo_name: str) -> dict:
    """Pick up to 12 issues per principle, ranked by scan_count desc, severity.

    The PDF budget requires exactly 60 refactors (12 × 5 principles). This
    produces the list Phase 2 should consume. If a principle has fewer than
    12 issues, include whatever exists (including low-confidence ones).
    """
    per_principle: dict[str, list[dict]] = {}
    totals = {"selected": 0, "short_of_quota": {}}

    for principle in Principle:
        issues = registry.get_issues_by_principle(principle.value)
        issues.sort(
            key=lambda i: (
                -i.scan_count,
                _SEVERITY_RANK.get(i.canonical_finding.severity.value, 99),
                i.canonical_finding.file_path,
                i.canonical_finding.line_start,
            )
        )
        top = issues[:_SHORTLIST_PER_PRINCIPLE]
        per_principle[principle.value] = [
            {
                "issue_id": issue.issue_id,
                "rank": rank,
                "scan_count": issue.scan_count,
                "severity": issue.canonical_finding.severity.value,
                "file_path": issue.canonical_finding.file_path,
                "entity_name": issue.canonical_finding.entity_name,
                "entity_type": issue.canonical_finding.entity_type.value,
                "line_start": issue.canonical_finding.line_start,
                "line_end": issue.canonical_finding.line_end,
                "description": issue.canonical_finding.description,
                "reasoning": issue.canonical_finding.reasoning,
                "first_detected_scan": issue.first_detected_scan,
                "duplicate_scan_ids": issue.duplicate_scan_ids,
            }
            for rank, issue in enumerate(top, start=1)
        ]
        totals["selected"] += len(top)
        if len(top) < _SHORTLIST_PER_PRINCIPLE:
            totals["short_of_quota"][principle.value] = {
                "have": len(top),
                "need": _SHORTLIST_PER_PRINCIPLE,
            }

    return {
        "repo_name": repo_name,
        "per_principle_quota": _SHORTLIST_PER_PRINCIPLE,
        "total_selected": totals["selected"],
        "total_quota": _SHORTLIST_PER_PRINCIPLE * len(Principle),
        "short_of_quota": totals["short_of_quota"],
        "by_principle": per_principle,
    }


def render_shortlist_md(shortlist: dict) -> str:
    lines = [
        f"# Refactor Shortlist: {shortlist['repo_name']}",
        "",
        f"Quota: {shortlist['per_principle_quota']} issues × "
        f"{len(shortlist['by_principle'])} principles = "
        f"{shortlist['total_quota']} total.",
        f"Selected: **{shortlist['total_selected']}**.",
        "",
    ]
    if shortlist["short_of_quota"]:
        lines.append("> **Note:** the following principles have fewer issues "
                     "than the quota. Per the project brief, seed violations "
                     "manually to fill the gap:")
        for p, info in shortlist["short_of_quota"].items():
            lines.append(f"> - {p}: {info['have']} / {info['need']}")
        lines.append("")

    lines.append("Ranking: `scan_count` desc, then severity (high > medium > "
                 "low), then file_path, then line_start.")
    lines.append("")

    for principle, items in shortlist["by_principle"].items():
        lines.append(f"## {principle} ({len(items)} selected)")
        lines.append("")
        if not items:
            lines.append("*No issues detected.*\n")
            continue
        lines.append("| # | Issue ID | Confidence | Severity | Location | Description |")
        lines.append("|---|----------|-----------:|----------|----------|-------------|")
        for item in items:
            loc = f"`{item['file_path']}` {item['entity_name']} "\
                  f"(L{item['line_start']}–{item['line_end']})"
            lines.append(
                f"| {item['rank']} | {item['issue_id']} | "
                f"{item['scan_count']} scan(s) | {item['severity']} | "
                f"{loc} | {item['description']} |"
            )
        lines.append("")

    return "\n".join(lines)


def generate_scan_csv(scan_dir: Path) -> str:
    """Generate a CSV summarizing all scans."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "scan_id", "principle", "scan_number", "provider", "model",
        "temperature", "context_mode", "findings_count", "parse_errors",
        "duration_ms", "error",
    ])

    # Walk scan directories
    for principle_dir in sorted(scan_dir.iterdir()):
        if not principle_dir.is_dir() or principle_dir.name == "__pycache__":
            continue
        for scan_subdir in sorted(principle_dir.iterdir()):
            if not scan_subdir.is_dir():
                continue
            response_file = scan_subdir / "raw_response.json"
            if not response_file.exists():
                continue
            try:
                data = json.loads(response_file.read_text(encoding="utf-8"))
                writer.writerow([
                    data.get("scan_id", ""),
                    data.get("principle", ""),
                    data.get("scan_number", ""),
                    data.get("provider", ""),
                    data.get("model", ""),
                    data.get("temperature", ""),
                    data.get("context_mode", ""),
                    len(data.get("findings", [])),
                    data.get("parse_errors", 0),
                    data.get("duration_ms", 0),
                    data.get("error", ""),
                ])
            except Exception:
                continue

    return output.getvalue()
