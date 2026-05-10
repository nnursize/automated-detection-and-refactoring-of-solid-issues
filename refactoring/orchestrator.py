"""Per-issue refactor loop: relocate -> prompt -> apply -> test -> commit/revert.

The test strategy is **full suite, fail-fast** (per LanguageAdapter):
  - Once per workspace, capture pre-existing failures (`fail_fast=False`).
  - Per attempt, run with `fail_fast=True`. Any failure that's not in the
    baseline is a regression and the patch is reverted.
  - If the only observed failure is a known pre-existing one, re-run the suite
    once without fail-fast to confirm no NEW failures slipped in.
  - At the end of the run, one final regression-gate suite (no fail-fast).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from solid_detector.config import get_api_key
from solid_detector.llm.gemini import GeminiProvider
from solid_detector.models import Principle

from . import metrics, parsing, patcher, prompts, reporting
from .adapters import get_adapter
from .config import RefactorProject
from .models import (
    AttemptStatus,
    IssueRef,
    RefactorAttempt,
    TestResult,
)
from .relocator import relocate
from .workspace import Workspace, WorkspaceError


PRINCIPLE_ORDER = ["SRP", "OCP", "LSP", "ISP", "DIP"]
_BASELINE_KEY = "__full_suite__"

# Substrings that indicate the model/server is unavailable in a way that won't
# self-resolve quickly. We halt the run to preserve quota and let the user
# resume later (the failed attempt is recorded as llm_error and will be retried
# by default on the next run).
_FATAL_LLM_ERROR_TOKENS = (
    "Server unavailable",
    "503",
    "UNAVAILABLE",
    "Model not found",
    "404",
    "NOT_FOUND",
)


class FatalLLMError(RuntimeError):
    """Signals the orchestrator should halt the per-issue loop right now."""


def _is_truncated_response(finish_reason: str | None) -> bool:
    return "MAX_TOKENS" in (finish_reason or "")


def _truncation_error(finish_reason: str | None, completion_tokens: int) -> str:
    return (
        f"LLM response was truncated (finish_reason={finish_reason}, "
        f"completion_tokens={completion_tokens}). Parsed patch blocks were "
        f"discarded and no changes were applied. Try splitting the issue into "
        f"a smaller refactor or switching models."
    )


class RefactorOrchestrator:
    def __init__(self, project: RefactorProject, model_override: str | None = None):
        self.project = project
        self.model_override = model_override
        self.workspace = Workspace(
            source_repo=Path(project.project.repo_abs_path),
            clone_dir=project.workspace_dir,
        )
        self.adapter = get_adapter(
            project.project.repo.language,
            project.refactor,
            workspace_root=project.workspace_dir,
        )
        model = model_override or project.project.llm.model or "gemini-2.5-flash"
        self.model = model
        self._provider: GeminiProvider | None = None
        self._detection_labels: dict[str, dict] | None = None

    @property
    def provider(self) -> GeminiProvider:
        if self._provider is None:
            self._provider = GeminiProvider(get_api_key("gemini"), model=self.model)
        return self._provider

    def load_issues(
        self,
        principle: str | None = None,
        only_issue: str | None = None,
    ) -> list[IssueRef]:
        path = self.project.shortlist_path
        if not path.exists():
            raise FileNotFoundError(
                f"Refactor shortlist not found: {path}. "
                f"Run detection first (run_detection.py)."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        out: list[IssueRef] = []
        for principle_key in PRINCIPLE_ORDER:
            if principle and principle_key != principle:
                continue
            entries = data.get("by_principle", {}).get(principle_key, [])
            for entry in entries:
                if only_issue and entry["issue_id"] != only_issue:
                    continue
                out.append(IssueRef(
                    issue_id=entry["issue_id"],
                    principle=Principle(principle_key),
                    rank=entry["rank"],
                    scan_count=entry["scan_count"],
                    severity=entry["severity"],
                    file_path=entry["file_path"],
                    entity_name=entry["entity_name"],
                    entity_type=entry["entity_type"],
                    line_start=entry["line_start"],
                    line_end=entry["line_end"],
                    description=entry["description"],
                    reasoning=entry["reasoning"],
                ))
        return out

    def detection_labels(self) -> dict[str, dict]:
        if self._detection_labels is not None:
            return self._detection_labels
        path = self.project.labels_path
        labels: dict[str, dict] = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = []
            if isinstance(data, list):
                for entry in data:
                    if not isinstance(entry, dict):
                        continue
                    issue_id = str(entry.get("issue_id", "")).strip()
                    if issue_id:
                        labels[issue_id] = entry
        self._detection_labels = labels
        return labels

    def detection_label_for(self, issue: IssueRef) -> dict | None:
        return self.detection_labels().get(issue.issue_id)

    def issue_dir(self, issue: IssueRef) -> Path:
        return self.project.attempts_dir / issue.principle.value / issue.issue_id

    def is_already_passed(self, issue: IssueRef) -> bool:
        pr_path = self.issue_dir(issue) / "pull_request.json"
        if not pr_path.exists():
            return False
        try:
            payload = json.loads(pr_path.read_text(encoding="utf-8"))
            return payload.get("status") in (
                AttemptStatus.APPLIED_PASSED.value,
                AttemptStatus.APPLIED_UNVERIFIED.value,
            )
        except (OSError, json.JSONDecodeError):
            return False

    def prepare(self) -> None:
        self.workspace.prepare()
        if self.adapter.supports_testing:
            self.adapter.setup_environment(self.workspace.clone_dir)

    def run_all(
        self,
        principle: str | None = None,
        only_issue: str | None = None,
        sleep_seconds: float = 60.0,
        retry_statuses: set[AttemptStatus] | None = None,
        skip_final_suite: bool = False,
    ) -> None:
        if retry_statuses is None:
            retry_statuses = {
                AttemptStatus.PATCH_FAILED,
                AttemptStatus.APPLIED_FAILED,
                AttemptStatus.LLM_ERROR,
            }

        issues = self.load_issues(principle=principle, only_issue=only_issue)
        print(f"Loaded {len(issues)} issue(s) from shortlist.")

        self.prepare()
        baseline_ref = self.workspace.head_commit()
        print(f"Baseline commit: {baseline_ref}")

        if self.adapter.supports_testing:
            baseline_failures = self._ensure_baseline_failures()
            if baseline_failures:
                print(f"Baseline pre-existing failures: {len(baseline_failures)}")
            else:
                print("Baseline: no pre-existing failures detected.")
        else:
            print(f"Adapter '{self.adapter.name}' does not support automated testing — "
                  f"applying patches without test verification (status: applied_unverified).")
            baseline_failures = set()

        first_call = True
        halted = False
        for idx, issue in enumerate(issues, start=1):
            print(f"\n[{idx}/{len(issues)}] {issue.issue_id} "
                  f"({issue.principle.value}, rank {issue.rank}) "
                  f"-> {issue.file_path}::{issue.entity_name}")
            label = self.detection_label_for(issue)
            if label is not None and label.get("label") is False:
                print("  Detection label is false; marking as detection_rejected.")
                self._mark_detection_rejected(issue, label)
                continue

            decision = self._decide(issue, retry_statuses)
            if decision == "skip":
                print("  Already applied + passed; skipping.")
                continue
            if decision == "skip_terminal":
                print("  Previous attempt is in a terminal status that wasn't selected for retry; skipping.")
                continue

            if not first_call:
                if sleep_seconds > 0:
                    print(f"  Sleeping {sleep_seconds:.0f}s before LLM call...")
                    time.sleep(sleep_seconds)
            first_call = False

            try:
                self._run_one(issue, baseline_ref, baseline_failures)
            except FatalLLMError as e:
                print(f"\n*** Halting run to preserve quota/state: {e}")
                print(f"    Issue {issue.issue_id} is recorded as llm_error and "
                      f"will be retried automatically when you re-run the same command.")
                halted = True
                break

        if halted:
            print("\nWriting master reports for the partial run...")
            reporting.write_master_reports(
                repo_name=self.project.repo_name,
                attempts_root=self.project.attempts_dir,
                reports_dir=Path(self.project.refactor.reports_dir),
                final_full_suite_result=None,
            )
            print(f"Master reports written to {self.project.refactor.reports_dir}/")
            return

        if skip_final_suite or only_issue or not self.adapter.supports_testing:
            print("\nSkipping final full-suite gate.")
            final = None
        else:
            print("\nRunning final full-suite regression gate...")
            final = self._run_final_suite()

        reporting.write_master_reports(
            repo_name=self.project.repo_name,
            attempts_root=self.project.attempts_dir,
            reports_dir=Path(self.project.refactor.reports_dir),
            final_full_suite_result=final,
        )
        print(f"\nMaster reports written to {self.project.refactor.reports_dir}/")

    def _decide(self, issue: IssueRef, retry_statuses: set[AttemptStatus]) -> str:
        pr_path = self.issue_dir(issue) / "pull_request.json"
        if not pr_path.exists():
            return "run"
        try:
            payload = json.loads(pr_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return "run"
        status = payload.get("status")
        if status in (
            AttemptStatus.APPLIED_PASSED.value,
            AttemptStatus.APPLIED_UNVERIFIED.value,
            AttemptStatus.DETECTION_REJECTED.value,
        ):
            return "skip"
        try:
            status_enum = AttemptStatus(status)
        except ValueError:
            return "run"
        if status_enum in retry_statuses:
            return "run"
        return "skip_terminal"

    def _mark_detection_rejected(self, issue: IssueRef, label: dict) -> None:
        out_dir = self.issue_dir(issue)
        out_dir.mkdir(parents=True, exist_ok=True)
        attempt = RefactorAttempt(
            issue_id=issue.issue_id,
            principle=issue.principle,
            model=self.model,
            temperature=self.project.refactor.temperature,
            status=AttemptStatus.DETECTION_REJECTED,
            detection_label=False,
            detection_label_explanation=str(label.get("explanation", "")),
        )
        self._save_diff(out_dir, "")
        self._finalize(attempt, issue, out_dir, time.time(), diff="")

    def _run_one(
        self,
        issue: IssueRef,
        baseline_ref: str,
        baseline_failures: set[str],
    ) -> None:
        out_dir = self.issue_dir(issue)
        out_dir.mkdir(parents=True, exist_ok=True)

        attempt_started = time.time()
        attempt = RefactorAttempt(
            issue_id=issue.issue_id,
            principle=issue.principle,
            model=self.model,
            temperature=self.project.refactor.temperature,
            status=AttemptStatus.LLM_ERROR,
        )

        try:
            full_path = self.workspace.clone_dir / issue.file_path
            if not full_path.exists():
                attempt.status = AttemptStatus.OBSOLETE
                attempt.obsolete_reason = (
                    f"file `{issue.file_path}` no longer exists in the working copy "
                    f"(removed by an earlier refactor)"
                )
                self._finalize(attempt, issue, out_dir, attempt_started, diff="")
                return

            current = full_path.read_text(encoding="utf-8")
            location = relocate(current, issue.file_path, issue.entity_name,
                                language=self.project.project.repo.language)
            if location is None:
                attempt.status = AttemptStatus.OBSOLETE
                attempt.obsolete_reason = (
                    f"entity `{issue.entity_name}` not found in current source of "
                    f"`{issue.file_path}` — likely renamed/removed by an earlier refactor"
                )
                self._finalize(attempt, issue, out_dir, attempt_started, diff="")
                return

            metrics_before = metrics.snapshot(self.workspace.clone_dir,
                                              [issue.file_path])
            attempt.metrics_before = metrics_before

            siblings = self.adapter.list_sibling_sources(
                self.workspace.clone_dir, issue.file_path,
            )
            user_prompt = prompts.build_user_prompt(
                issue, location,
                sibling_files=siblings,
                language=self.project.project.repo.language,
                max_full_file_lines=self.project.refactor.max_full_file_lines,
            )
            system_prompt = prompts.build_system_prompt(issue.principle.value)
            attempt.prompt_text = (
                "[SYSTEM]\n" + system_prompt + "\n\n[USER]\n" + user_prompt
            )
            (out_dir / "prompt.txt").write_text(attempt.prompt_text, encoding="utf-8")

            print(f"  Calling Gemini ({self.model})...")
            try:
                resp = self.provider.complete_with_retry(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=self.project.refactor.temperature,
                    max_tokens=self.project.refactor.max_output_tokens,
                )
            except Exception as e:
                attempt.status = AttemptStatus.LLM_ERROR
                attempt.error = str(e)
                self._finalize(attempt, issue, out_dir, attempt_started, diff="")
                err_str = str(e)
                if any(tok in err_str for tok in _FATAL_LLM_ERROR_TOKENS):
                    raise FatalLLMError(err_str) from e
                return
            attempt.response_text = resp.raw_text
            attempt.llm_finish_reason = resp.finish_reason
            attempt.prompt_tokens = resp.prompt_tokens
            attempt.completion_tokens = resp.completion_tokens
            (out_dir / "raw_response.json").write_text(
                json.dumps({
                    "model": resp.model,
                    "provider": resp.provider,
                    "latency_ms": resp.latency_ms,
                    "prompt_tokens": resp.prompt_tokens,
                    "completion_tokens": resp.completion_tokens,
                    "finish_reason": resp.finish_reason,
                    "raw_text": resp.raw_text,
                }, indent=2, default=str),
                encoding="utf-8",
            )

            parsed = parsing.parse_response(resp.raw_text)
            attempt.patch_blocks = parsed.blocks
            (out_dir / "patch_blocks.json").write_text(
                json.dumps([b.model_dump() for b in parsed.blocks],
                           indent=2, default=str),
                encoding="utf-8",
            )

            if _is_truncated_response(resp.finish_reason):
                attempt.status = AttemptStatus.PATCH_FAILED
                attempt.patch_blocks = []
                attempt.files_touched = []
                attempt.apply_error = _truncation_error(resp.finish_reason,
                                                        resp.completion_tokens)
                self._save_diff(out_dir, "")
                self._finalize(attempt, issue, out_dir, attempt_started, diff="")
                return

            apply_result = patcher.apply(parsed.blocks, self.workspace.clone_dir)
            if not apply_result.ok:
                attempt.status = AttemptStatus.PATCH_FAILED
                err = apply_result.error or "patch did not apply"
                # If the LLM was truncated, the parser will have found 0 blocks
                # and we'll fall through to here with a generic message. Surface
                # the finish_reason so the user knows it was a token-budget hit
                # (recoverable) vs. malformed output (LLM regression).
                if not parsed.blocks and "MAX_TOKENS" in (resp.finish_reason or ""):
                    err = (
                        f"LLM response was truncated (finish_reason="
                        f"{resp.finish_reason}, completion_tokens={resp.completion_tokens}). "
                        f"No complete patch blocks emitted. "
                        f"Try increasing `refactor.max_output_tokens` in the YAML, "
                        f"or split the issue manually."
                    )
                attempt.apply_error = err
                attempt.files_touched = apply_result.files_touched
                self._save_diff(out_dir, "")
                self._safe_revert()
                self._finalize(attempt, issue, out_dir, attempt_started, diff="")
                return

            attempt.files_touched = apply_result.files_touched
            diff_text = self.workspace.diff_working_tree_for_paths(
                apply_result.files_touched
            )
            self._save_diff(out_dir, diff_text)
            if not diff_text.strip():
                attempt.status = AttemptStatus.PATCH_FAILED
                attempt.apply_error = (
                    "patch applied but produced no net source changes; "
                    "the LLM replacement was likely identical to the matched text"
                )
                self._safe_revert()
                self._finalize(attempt, issue, out_dir, attempt_started, diff="")
                return

            syntax_err = self.adapter.syntax_check(
                self.workspace.clone_dir, apply_result.files_touched,
            )
            if syntax_err:
                attempt.status = AttemptStatus.PATCH_FAILED
                attempt.apply_error = f"syntax check failed: {syntax_err}"
                self._safe_revert()
                self._finalize(attempt, issue, out_dir, attempt_started, diff=diff_text)
                return

            if not self.adapter.supports_testing:
                # Non-testing adapter (Java/Kotlin/etc.): commit unverified.
                # Manual review of the diff/PR is the verification step.
                metrics_after = metrics.snapshot(
                    self.workspace.clone_dir, apply_result.files_touched,
                )
                attempt.metrics_after = metrics_after
                head = self.workspace.checkpoint(
                    f"refactor({issue.issue_id}): {issue.principle.value}",
                )
                attempt.head_commit = head
                attempt.status = AttemptStatus.APPLIED_UNVERIFIED
                print(f"  APPLIED (unverified) — committed as {head[:8]}")
                self._save_metrics(out_dir, attempt)
                self._finalize(attempt, issue, out_dir, attempt_started, diff=diff_text)
                return

            baseline_deselect = sorted(baseline_failures)
            if baseline_deselect:
                print(f"  Running full test suite (fail-fast, skipping "
                      f"{len(baseline_deselect)} baseline failure(s))...")
            else:
                print(f"  Running full test suite (fail-fast)...")
            tr = self.adapter.run_tests(
                workspace_root=self.workspace.clone_dir,
                timeout_sec=self.project.refactor.test_timeout_sec,
                fail_fast=True,
                deselect_node_ids=baseline_deselect,
            )
            tr = self._reconcile_with_baseline(
                tr, baseline_failures,
                baseline_failures_deselected=bool(baseline_deselect),
                workspace_root=self.workspace.clone_dir,
            )
            attempt.test_result = tr
            (out_dir / "test_results.json").write_text(
                json.dumps(tr.model_dump(), indent=2, default=str),
                encoding="utf-8",
            )

            if tr.passed:
                metrics_after = metrics.snapshot(
                    self.workspace.clone_dir, apply_result.files_touched,
                )
                attempt.metrics_after = metrics_after
                head = self.workspace.checkpoint(
                    f"refactor({issue.issue_id}): {issue.principle.value}",
                )
                attempt.head_commit = head
                attempt.status = AttemptStatus.APPLIED_PASSED
                print(f"  PASSED — committed as {head[:8]}")
            else:
                attempt.status = AttemptStatus.APPLIED_FAILED
                self._safe_revert()
                print(f"  FAILED — reverted "
                      f"({len(tr.new_failures)} new failure(s), "
                      f"{tr.failed_count} reported failure(s) total)")

            self._save_metrics(out_dir, attempt)
            self._finalize(attempt, issue, out_dir, attempt_started, diff=diff_text)
        except Exception as e:
            attempt.error = f"unhandled error: {type(e).__name__}: {e}"
            attempt.status = AttemptStatus.LLM_ERROR
            self._safe_revert()
            self._finalize(attempt, issue, out_dir, attempt_started, diff="")

    def _reconcile_with_baseline(
        self,
        tr: TestResult,
        baseline_failures: set[str],
        workspace_root: Path,
        baseline_failures_deselected: bool = False,
    ) -> TestResult:
        """Compute new vs pre-existing failures.

        Per-attempt pytest runs deselect known baseline failures before using
        fail-fast, so the first observed failure should be a new regression.
        If an old failure still appears (for example a collection error that
        pytest could not deselect), treat it as pre-existing instead of running
        a second full suite.
        """
        if tr.timed_out:
            tr.passed = False
            return tr

        observed = set(tr.failed_node_ids) | set(tr.error_node_ids)
        new_failures = sorted(observed - baseline_failures)
        pre_existing = sorted(observed & baseline_failures)

        if not tr.passed and not observed:
            tr.new_failures = [
                f"pytest exited with code {tr.return_code} but produced no "
                "parseable failure node id",
            ]
            tr.pre_existing_failures = []
            tr.passed = False
            return tr

        if observed and not new_failures and baseline_failures_deselected:
            tr.new_failures = []
            tr.pre_existing_failures = pre_existing
            tr.passed = True
            return tr

        if observed and not new_failures:
            # All observed failures are in baseline — fail-fast may have masked
            # real regressions. Re-run the full suite without -x.
            print("  Only pre-existing failures observed under fail-fast — "
                  "re-running full suite to confirm no new failures...")
            tr2 = self.adapter.run_tests(
                workspace_root=workspace_root,
                timeout_sec=self.project.refactor.test_timeout_sec,
                fail_fast=False,
            )
            if tr2.timed_out:
                tr2.passed = False
                tr2.new_failures = []
                tr2.pre_existing_failures = []
                return tr2
            observed2 = set(tr2.failed_node_ids) | set(tr2.error_node_ids)
            tr2.new_failures = sorted(observed2 - baseline_failures)
            tr2.pre_existing_failures = sorted(observed2 & baseline_failures)
            if not tr2.passed and not observed2:
                tr2.new_failures = [
                    f"pytest exited with code {tr2.return_code} but produced "
                    "no parseable failure node id",
                ]
                tr2.pre_existing_failures = []
                tr2.passed = False
                return tr2
            tr2.passed = not tr2.new_failures
            return tr2

        tr.new_failures = new_failures
        tr.pre_existing_failures = pre_existing
        tr.passed = not new_failures
        return tr

    def _ensure_baseline_failures(self) -> set[str]:
        """Compute (and cache on disk) the set of node IDs that fail on the
        unmodified workspace. Run once per workspace.
        """
        cache = self.workspace.load_baseline()
        if _BASELINE_KEY in cache:
            return set(cache.get(_BASELINE_KEY, []))

        if not self.workspace.is_clean():
            print("  WARNING: workspace not clean; skipping baseline capture.")
            return set()

        print("Capturing baseline failures (full suite, no fail-fast)...")
        tr = self.adapter.run_tests(
            workspace_root=self.workspace.clone_dir,
            timeout_sec=self.project.refactor.full_suite_timeout_sec,
            fail_fast=False,
        )
        if tr.timed_out:
            print("  WARNING: baseline run timed out; treating baseline as empty.")
            ids: list[str] = []
        else:
            ids = sorted(set(tr.failed_node_ids) | set(tr.error_node_ids))
        cache[_BASELINE_KEY] = ids
        self.workspace.save_baseline(cache)
        return set(ids)

    def _save_metrics(self, out_dir: Path, attempt: RefactorAttempt) -> None:
        if attempt.metrics_before is not None:
            (out_dir / "metrics_before.json").write_text(
                json.dumps(attempt.metrics_before.model_dump(),
                           indent=2, default=str),
                encoding="utf-8",
            )
        if attempt.metrics_after is not None:
            (out_dir / "metrics_after.json").write_text(
                json.dumps(attempt.metrics_after.model_dump(),
                           indent=2, default=str),
                encoding="utf-8",
            )

    def _save_diff(self, out_dir: Path, diff: str) -> None:
        (out_dir / "applied_diff.patch").write_text(diff, encoding="utf-8")

    def _safe_revert(self) -> None:
        try:
            self.workspace.revert()
        except WorkspaceError as e:
            print(f"  WARNING: revert failed: {e}")

    def _finalize(
        self,
        attempt: RefactorAttempt,
        issue: IssueRef,
        out_dir: Path,
        started: float,
        diff: str,
    ) -> None:
        attempt.duration_ms = (time.time() - started) * 1000.0
        try:
            attempt.head_commit = self.workspace.head_commit()
        except WorkspaceError:
            pass
        reporting.write_pull_request(attempt, issue, diff, out_dir)

    def _run_final_suite(self) -> dict:
        if not self.adapter.supports_testing:
            return {
                "command": f"(skipped — adapter '{self.adapter.name}' "
                           f"does not support automated testing)",
                "passed": None,
                "duration_ms": 0.0,
                "output_tail": "",
            }
        cmd_override = self.project.refactor.full_suite_command
        if cmd_override:
            import subprocess
            started = time.time()
            try:
                proc = subprocess.run(
                    cmd_override, cwd=str(self.workspace.clone_dir),
                    capture_output=True, text=True,
                    timeout=self.project.refactor.full_suite_timeout_sec,
                )
                rc, out, err = proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired as e:
                out = (e.stdout or "") if isinstance(e.stdout, str) else (e.stdout or b"").decode("utf-8", errors="ignore")
                err = (e.stderr or "") if isinstance(e.stderr, str) else (e.stderr or b"").decode("utf-8", errors="ignore")
                rc = -1
            duration_ms = (time.time() - started) * 1000.0
            return {
                "command": " ".join(cmd_override),
                "passed": rc == 0,
                "duration_ms": duration_ms,
                "output_tail": "\n".join((out + err).splitlines()[-300:]),
            }
        tr = self.adapter.run_tests(
            workspace_root=self.workspace.clone_dir,
            timeout_sec=self.project.refactor.full_suite_timeout_sec,
            fail_fast=False,
        )
        return {
            "command": tr.command,
            "passed": tr.passed,
            "return_code": tr.return_code,
            "total": tr.total,
            "passed_count": tr.passed_count,
            "failed_count": tr.failed_count,
            "skipped_count": tr.skipped_count,
            "error_count": tr.error_count,
            "duration_ms": tr.duration_ms,
            "timed_out": tr.timed_out,
            "output_tail": tr.output_tail,
        }
