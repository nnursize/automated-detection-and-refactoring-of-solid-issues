"""CLI entry point for Phase 2 — automated refactoring."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from refactoring import config as rconfig
from refactoring import reporting
from refactoring.models import AttemptStatus
from refactoring.orchestrator import RefactorOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SOLID Phase 2 — automated refactoring framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run — list what would be attempted
  python run_refactoring.py --config configs/seaborn.yaml --dry-run

  # Single issue smoke test
  python run_refactoring.py --config configs/seaborn.yaml --issue SRP-001 --no-final-suite

  # All 12 SRP issues
  python run_refactoring.py --config configs/seaborn.yaml --principle SRP

  # Full 60-issue run
  python run_refactoring.py --config configs/seaborn.yaml --sleep 60

  # Regenerate master reports without re-running
  python run_refactoring.py --config configs/seaborn.yaml --report-only

  # Status table
  python run_refactoring.py --config configs/seaborn.yaml --status
        """,
    )
    parser.add_argument("--config", required=True, help="Path to repo YAML config (same as detection)")
    parser.add_argument("--principle", choices=["SRP", "OCP", "LSP", "ISP", "DIP"],
                        help="Limit run to one principle")
    parser.add_argument("--issue", help="Run only this issue id (e.g. SRP-001)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the issues that would be attempted, do not call LLM or tests")
    parser.add_argument("--report-only", action="store_true",
                        help="Regenerate master reports from existing per-attempt artifacts")
    parser.add_argument("--status", action="store_true",
                        help="Print a status table of all attempts and exit")
    parser.add_argument("--model", help="Override the Gemini model")
    parser.add_argument("--sleep", type=float, default=60.0,
                        help="Seconds between LLM calls (default 60 for free-tier quota)")
    parser.add_argument("--no-final-suite", action="store_true",
                        help="Skip the end-of-run full pytest gate")
    parser.add_argument("--retry-status", default="patch_failed,applied_failed,llm_error",
                        help="Comma-separated statuses to re-attempt on resume")
    parser.add_argument("--full-suite-only", action="store_true",
                        help="Only run the full suite against the current clone state and exit")
    parser.add_argument("--rerender-prs", action="store_true",
                        help="Rebuild pull_request.json + pull_request.md for every "
                             "existing attempt from on-disk patch_blocks.json + "
                             "applied_diff.patch. Useful after upgrading the renderer.")

    args = parser.parse_args()

    try:
        project = rconfig.load(args.config)
    except FileNotFoundError as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    print(f"=== SOLID Refactoring Framework ===")
    print(f"Repository: {project.repo_name} ({project.project.repo.language})")
    print(f"Source repo: {project.project.repo_abs_path}")
    print(f"Workspace clone: {project.workspace_dir}")
    print(f"Shortlist: {project.shortlist_path}")

    orch = RefactorOrchestrator(project, model_override=args.model)
    print(f"Model: {orch.model}")

    if args.dry_run:
        issues = orch.load_issues(principle=args.principle, only_issue=args.issue)
        print(f"\nDRY RUN — would attempt {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, start=1):
            print(f"  {i:>2}. {issue.issue_id} [{issue.principle.value}] "
                  f"rank={issue.rank} scans={issue.scan_count} "
                  f"sev={issue.severity}  {issue.file_path}::{issue.entity_name} "
                  f"(L{issue.line_start}-L{issue.line_end})")
        return

    if args.status:
        _print_status(orch)
        return

    if args.rerender_prs:
        # If the workspace clone exists, wire it through so we can recompute
        # metrics from git history. Otherwise fall back to no-workspace mode
        # (PR text re-rendered, but historical metrics are left alone).
        workspace = None
        if project.workspace_dir.exists() and (project.workspace_dir / ".git").exists():
            from refactoring.workspace import Workspace
            workspace = Workspace(
                source_repo=Path(project.project.repo_abs_path),
                clone_dir=project.workspace_dir,
            )
            print(f"Recomputing metrics from {project.workspace_dir}/.git/ history.")
        n = reporting.rerender_all_prs(project.attempts_dir, workspace=workspace)
        print(f"Re-rendered {n} pull_request.json + pull_request.md file(s) "
              f"under {project.attempts_dir}/")
        # Master reports also depend on per-attempt PRs, so refresh them.
        reporting.write_master_reports(
            repo_name=project.repo_name,
            attempts_root=project.attempts_dir,
            reports_dir=Path(project.refactor.reports_dir),
            final_full_suite_result=_load_existing_full_suite(project),
        )
        print(f"Master reports regenerated under {project.refactor.reports_dir}/")
        return

    if args.report_only:
        reporting.write_master_reports(
            repo_name=project.repo_name,
            attempts_root=project.attempts_dir,
            reports_dir=Path(project.refactor.reports_dir),
            final_full_suite_result=_load_existing_full_suite(project),
        )
        print(f"Master reports regenerated under {project.refactor.reports_dir}/")
        return

    if args.full_suite_only:
        orch.prepare()
        result = orch._run_final_suite()
        out_path = Path(project.refactor.reports_dir) / f"{project.repo_name}_full_suite_final.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"Full suite passed={result.get('passed')} -> {out_path}")
        return

    retry_set = _parse_statuses(args.retry_status)
    orch.run_all(
        principle=args.principle,
        only_issue=args.issue,
        sleep_seconds=args.sleep,
        retry_statuses=retry_set,
        skip_final_suite=args.no_final_suite,
    )


def _parse_statuses(spec: str) -> set[AttemptStatus]:
    out: set[AttemptStatus] = set()
    for token in (spec or "").split(","):
        token = token.strip()
        if not token:
            continue
        try:
            out.add(AttemptStatus(token))
        except ValueError:
            print(f"Warning: unknown status '{token}' (ignored)")
    return out


def _print_status(orch: RefactorOrchestrator) -> None:
    issues = orch.load_issues()
    print(f"\n{'Issue':<10} {'Pri':<4} {'Status':<18} {'Tests':<14} File")
    print("-" * 88)
    for issue in issues:
        pr_path = orch.issue_dir(issue) / "pull_request.json"
        status = "(not run)"
        tests = "-"
        if pr_path.exists():
            try:
                p = json.loads(pr_path.read_text(encoding="utf-8"))
                status = p.get("status", "?")
                tr = p.get("test_results") or {}
                if tr:
                    tests = f"{tr.get('passed_count', 0)}/{tr.get('total', 0)}"
            except (OSError, json.JSONDecodeError):
                status = "(corrupt)"
        print(f"{issue.issue_id:<10} {issue.principle.value:<4} {status:<18} {tests:<14} {issue.file_path}")


def _load_existing_full_suite(project) -> dict | None:
    path = Path(project.refactor.reports_dir) / f"{project.repo_name}_full_suite_final.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


if __name__ == "__main__":
    main()
