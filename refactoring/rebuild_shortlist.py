"""Rebuild a refactor shortlist from the master registry, with optional filters.

Use case: a multi-language repo's shortlist contains issues from a language
the refactoring stage doesn't yet support (e.g. Ruby in logstash). Run this
script with `--extensions .java` to drop those issues and refill from the
next-best Java-only issues in the registry, keeping the 12-per-principle quota.

Does NOT call the LLM or modify scans. Pure post-processing of existing
detection output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
_QUOTA_PER_PRINCIPLE = 12
_PRINCIPLES = ["SRP", "OCP", "LSP", "ISP", "DIP"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild a refactor shortlist from the registry, "
                    "filtering issues by file extension.",
    )
    parser.add_argument("--registry", required=True,
                        help="Path to <repo>_registry.json")
    parser.add_argument("--out", required=True,
                        help="Path to write the new <repo>_refactor_shortlist.json")
    parser.add_argument("--extensions", default="",
                        help="Comma-separated allowed extensions, e.g. '.java' "
                             "or '.java,.kt'. Empty = no filter (keep all).")
    parser.add_argument("--quota", type=int, default=_QUOTA_PER_PRINCIPLE,
                        help=f"Issues per principle (default {_QUOTA_PER_PRINCIPLE})")
    parser.add_argument("--repo-name", default=None,
                        help="Override the repo name in the output JSON; "
                             "defaults to the registry's repo_name.")
    args = parser.parse_args()

    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"Registry not found: {registry_path}", file=sys.stderr)
        sys.exit(1)

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    issues = registry.get("issues", [])
    repo_name = args.repo_name or registry.get("repo_name", "unknown")

    allowed_exts = [e.strip().lower() for e in args.extensions.split(",") if e.strip()]
    if allowed_exts:
        before = len(issues)
        issues = [i for i in issues
                  if any(i["canonical_finding"]["file_path"].lower().endswith(ext)
                         for ext in allowed_exts)]
        print(f"Extension filter {allowed_exts}: kept {len(issues)}/{before} issues")

    by_principle: dict[str, list[dict]] = {p: [] for p in _PRINCIPLES}
    for issue in issues:
        p = issue["principle"]
        if p in by_principle:
            by_principle[p].append(issue)

    shortlist_by_principle: dict[str, list[dict]] = {}
    short_of_quota: dict[str, dict] = {}
    total_selected = 0

    for principle in _PRINCIPLES:
        items = by_principle[principle]
        items.sort(key=lambda i: (
            -i["scan_count"],
            _SEVERITY_RANK.get(i["canonical_finding"]["severity"], 99),
            i["canonical_finding"]["file_path"],
            i["canonical_finding"]["line_start"],
        ))
        top = items[: args.quota]
        shortlist_by_principle[principle] = [
            {
                "issue_id": issue["issue_id"],
                "rank": rank,
                "scan_count": issue["scan_count"],
                "severity": issue["canonical_finding"]["severity"],
                "file_path": issue["canonical_finding"]["file_path"],
                "entity_name": issue["canonical_finding"]["entity_name"],
                "entity_type": issue["canonical_finding"]["entity_type"],
                "line_start": issue["canonical_finding"]["line_start"],
                "line_end": issue["canonical_finding"]["line_end"],
                "description": issue["canonical_finding"]["description"],
                "reasoning": issue["canonical_finding"]["reasoning"],
                "first_detected_scan": issue["first_detected_scan"],
                "duplicate_scan_ids": issue["duplicate_scan_ids"],
            }
            for rank, issue in enumerate(top, start=1)
        ]
        total_selected += len(top)
        if len(top) < args.quota:
            short_of_quota[principle] = {"have": len(top), "need": args.quota}

    output = {
        "repo_name": repo_name,
        "per_principle_quota": args.quota,
        "total_selected": total_selected,
        "total_quota": args.quota * len(_PRINCIPLES),
        "short_of_quota": short_of_quota,
        "filters": {"extensions": allowed_exts},
        "by_principle": shortlist_by_principle,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, indent=2, default=str), encoding="utf-8",
    )

    print(f"\nWrote {out_path}")
    print(f"Selected {total_selected} / {args.quota * len(_PRINCIPLES)} issues:")
    for p in _PRINCIPLES:
        items = shortlist_by_principle[p]
        gap = ""
        if p in short_of_quota:
            gap = f"  (short by {args.quota - len(items)})"
        print(f"  {p}: {len(items)} selected{gap}")


if __name__ == "__main__":
    main()
