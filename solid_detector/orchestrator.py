"""Scan orchestration — runs the 60-scan detection loop.

Dispatches each scan by strategy (full_repo | smell_two_step | class_centric
| skeleton) and aggregates findings into a shared IssueRegistry.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .config import ProjectConfig, get_api_key
from .context import (
    build_class_centric_batch,
    build_skeleton,
    build_whole_repo,
    select_target_classes,
)
from .discovery import discover_files
from .llm.base import LLMProvider
from .llm.gemini import GeminiProvider
from .models import FileInfo, Finding, Principle, ScanRecord, ScanVariation  # Finding used in _reload_scan
from .parsing import parse_llm_response
from .prompts.strategies import build_class_centric as prompt_class_centric
from .prompts.strategies import build_full_repo as prompt_full_repo
from .prompts.strategies import build_skeleton as prompt_skeleton
from .prompts.strategies import build_smell_two_step as prompt_smell
from .prompts.variations import get_variation
from .registry import IssueRegistry


class ScanOrchestrator:
    """Orchestrates the 60 detection scans for a repository."""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.files: list[FileInfo] = []
        self._providers: dict[str, LLMProvider] = {}

        self.scan_dir = Path(config.scan.output_dir) / config.repo.name
        self.scan_dir.mkdir(parents=True, exist_ok=True)

        registry_path = self.scan_dir / "registry.json"
        self.registry = IssueRegistry(str(registry_path))

    def _get_provider(self, provider_name: str) -> LLMProvider:
        if provider_name not in self._providers:
            api_key = get_api_key(provider_name)
            if provider_name == "gemini":
                model = self.config.llm.model
                if model:
                    self._providers[provider_name] = GeminiProvider(api_key, model=model)
                else:
                    self._providers[provider_name] = GeminiProvider(api_key)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        return self._providers[provider_name]

    def discover(self):
        print(f"Discovering files in {self.config.source_abs_path}...")
        self.files = discover_files(self.config)
        print(f"  Found {len(self.files)} source files")
        total_tokens = sum(f.estimated_tokens for f in self.files)
        total_classes = sum(len(f.class_infos) for f in self.files)
        print(f"  Estimated total tokens: {total_tokens:,}")
        print(f"  Classes discovered: {total_classes}")

    def run_all(
        self,
        principle: str | None = None,
        scan_number: int | None = None,
        sleep_seconds: float = 0.0,
        stop_on_error: bool = True,
    ):
        if not self.files:
            self.discover()

        principles = [principle] if principle else self.config.scan.principles
        scan_nums = (
            [scan_number] if scan_number
            else list(range(1, self.config.scan.scans_per_principle + 1))
        )
        jobs = [(p, n) for p in principles for n in scan_nums]
        single_run = len(jobs) == 1

        aborted = False
        for idx, (princ, scan_num) in enumerate(jobs):
            status = self._run_single_scan(princ, scan_num)
            if status == "failed" and stop_on_error:
                print(
                    "\n[STOP] Scan failed. Halting so quota isn't wasted on "
                    "retries while the model is busy.\n"
                    "  Re-run the same command later — resumability will skip "
                    "completed scans and retry the failed one.\n"
                    "  Pass --continue-on-error to run through failures instead."
                )
                aborted = True
                break
            is_last = idx == len(jobs) - 1
            if (
                sleep_seconds > 0 and status == "ok"
                and not is_last and not single_run
            ):
                print(f"  Sleeping {sleep_seconds:.0f}s to respect per-minute quota...")
                time.sleep(sleep_seconds)

        self.registry.save(extra=self.collect_scan_status())
        if aborted:
            print("\nRegistry saved (partial run).")
        else:
            print("\nAll scans complete. Registry saved.")
        print(f"Registry summary: {json.dumps(self.registry.summary(), indent=2)}")

    def collect_scan_status(self) -> dict:
        """Walk scan_dir and summarise per-scan status for the registry file."""
        scans: dict[str, dict] = {}
        totals = {"total": 0, "completed": 0, "failed": 0, "missing": 0}
        expected_principles = self.config.scan.principles
        expected_scans = range(1, self.config.scan.scans_per_principle + 1)

        for princ in expected_principles:
            for scan_num in expected_scans:
                totals["total"] += 1
                scan_key = f"{princ}_{scan_num:02d}"
                scan_subdir = self.scan_dir / princ / f"scan_{scan_num:02d}"
                response_file = scan_subdir / "raw_response.json"

                if not response_file.exists():
                    scans[scan_key] = {"status": "missing"}
                    totals["missing"] += 1
                    continue

                try:
                    saved = json.loads(response_file.read_text(encoding="utf-8"))
                except Exception as e:
                    scans[scan_key] = {"status": "failed", "error": f"unreadable: {e}"}
                    totals["failed"] += 1
                    continue

                if saved.get("error"):
                    scans[scan_key] = {
                        "status": "failed",
                        "model": saved.get("model", ""),
                        "error": saved["error"][:500],
                    }
                    totals["failed"] += 1
                else:
                    scans[scan_key] = {
                        "status": "ok",
                        "model": saved.get("model", ""),
                        "provider": saved.get("provider", ""),
                        "findings": len(saved.get("findings", [])),
                        "parse_errors": saved.get("parse_errors", 0),
                        "duration_ms": saved.get("duration_ms", 0),
                    }
                    totals["completed"] += 1

        return {"scan_summary": totals, "scans": scans}

    def print_status(self):
        """Print a human-readable status table of all scans."""
        data = self.collect_scan_status()
        summary = data["scan_summary"]
        scans = data["scans"]
        print(
            f"\nScans — total: {summary['total']}, "
            f"completed: {summary['completed']}, "
            f"failed: {summary['failed']}, "
            f"missing: {summary['missing']}\n"
        )
        print(f"  {'Scan':<10} {'Status':<9} {'Model':<28} Notes")
        print(f"  {'-'*10} {'-'*9} {'-'*28} {'-'*40}")
        for key, info in scans.items():
            status = info["status"]
            model = info.get("model", "") or "-"
            if status == "ok":
                notes = f"{info['findings']} findings ({info['duration_ms']:.0f}ms)"
            elif status == "failed":
                notes = (info.get("error") or "")[:80]
            else:
                notes = ""
            print(f"  {key:<10} {status:<9} {model:<28} {notes}")
        if summary["failed"]:
            print("\nFailed scan keys (use with --principle + --scan to retry):")
            for key, info in scans.items():
                if info["status"] == "failed":
                    print(f"  {key}")

    def rebuild_registry(self):
        """Clear the registry and rebuild it from parsed_findings.json on disk.

        Use this after deleting a scan folder so the registry no longer holds
        that scan's findings. Re-run the deleted scan afterwards to add its
        new findings back in.
        """
        print("Rebuilding registry from scan data on disk...")
        self.registry.clear()
        if not self.scan_dir.exists():
            print(f"  Scan dir not found: {self.scan_dir}")
            self.registry.save(extra=self.collect_scan_status())
            return

        reloaded = 0
        for principle_dir in sorted(self.scan_dir.iterdir()):
            if not principle_dir.is_dir():
                continue
            for scan_subdir in sorted(principle_dir.iterdir()):
                if not scan_subdir.is_dir():
                    continue
                scan_id = (
                    f"{self.config.repo.name}_{principle_dir.name}"
                    f"_scan_{scan_subdir.name.split('_')[-1]}"
                )
                self._reload_scan(scan_subdir, scan_id)
                reloaded += 1
        self.registry.save(extra=self.collect_scan_status())
        print(f"  Reloaded {reloaded} scan(s). Registry saved.")
        print(f"Registry summary: {json.dumps(self.registry.summary(), indent=2)}")

    def dry_run(self):
        if not self.files:
            self.discover()

        print(f"\n=== DRY RUN for {self.config.repo.name} ===")
        print(f"Language: {self.config.repo.language}")
        print(f"Source root: {self.config.source_abs_path}")
        print(f"Files discovered: {len(self.files)}")
        print(f"\nTop 10 files by size:")
        for f in self.files[:10]:
            print(f"  {f.path} ({f.line_count} lines, ~{f.estimated_tokens} tokens)")
            if f.class_infos:
                sample = ", ".join(
                    f"{c.name}({len(c.methods)}m)" for c in f.class_infos[:5]
                )
                print(f"    Classes: {sample}")
            if f.imports:
                print(f"    Imports: {', '.join(f.imports[:5])}")

        targets = select_target_classes(self.files)
        print(f"\nClass-centric target classes: {len(targets)}")
        for f, ci in targets[:10]:
            bases = f" : {', '.join(ci.bases)}" if ci.bases else ""
            print(f"  {ci.name}{bases}  ({f.path}, {len(ci.methods)} methods)")

        print(f"\nPrinciples: {', '.join(self.config.scan.principles)}")
        print(f"Scans per principle: {self.config.scan.scans_per_principle}")
        total_scans = len(self.config.scan.principles) * self.config.scan.scans_per_principle
        print(f"Total scans: {total_scans}")

        print(f"\nScan schedule:")
        for scan_num in range(1, self.config.scan.scans_per_principle + 1):
            v = get_variation(scan_num)
            print(
                f"  Scan {scan_num:2d}: provider={v.provider_name}, "
                f"strategy={v.strategy}, temp={v.temperature}"
            )

    # ------------------------------------------------------------------
    # Per-scan dispatcher
    # ------------------------------------------------------------------

    def _run_single_scan(self, principle: str, scan_num: int) -> str:
        """Run one scan. Returns "skipped" | "ok" | "failed"."""
        scan_id = f"{self.config.repo.name}_{principle}_scan_{scan_num:02d}"
        scan_output_dir = self.scan_dir / principle / f"scan_{scan_num:02d}"

        # Resumability: skip if a successful response already exists
        response_file = scan_output_dir / "raw_response.json"
        if response_file.exists():
            try:
                saved = json.loads(response_file.read_text(encoding="utf-8"))
                if not saved.get("error"):
                    print(f"[SKIP] {scan_id} — already completed")
                    self._reload_scan(scan_output_dir, scan_id)
                    return "skipped"
                print(f"[RETRY] {scan_id} — previous attempt failed: {saved['error'][:80]}")
            except Exception:
                pass

        variation = get_variation(scan_num)
        print(
            f"\n[SCAN] {scan_id} (provider={variation.provider_name}, "
            f"strategy={variation.strategy}, temp={variation.temperature})"
        )

        try:
            provider = self._get_provider(variation.provider_name)
        except Exception as e:
            print(f"  ERROR: Could not initialize provider: {e}")
            self._save_error_record(scan_output_dir, scan_id, principle, scan_num, variation, str(e))
            return "failed"

        strategy = variation.strategy
        prompt_builders = {
            "full_repo":      lambda: self._build_full_repo_prompt(principle),
            "smell_two_step": lambda: self._build_smell_prompt(principle),
            "skeleton":       lambda: self._build_skeleton_prompt(principle, provider),
            "class_centric":  lambda: self._build_class_centric_prompt(principle, provider),
        }
        if strategy not in prompt_builders:
            raise ValueError(f"Unknown strategy: {strategy}")
        ok = self._scan_single_call(
            scan_id, principle, scan_num, variation, provider, scan_output_dir,
            prompt_builders[strategy](),
        )
        return "ok" if ok else "failed"

    # ------------------------------------------------------------------
    # Prompt builders (return (system, user))
    # ------------------------------------------------------------------

    def _token_budget(self, provider: LLMProvider, cap: int = 200_000) -> int:
        return min(provider.max_context_tokens() - 5000, cap)

    def _build_full_repo_prompt(self, principle: str) -> tuple[str, str]:
        provider = self._get_provider("gemini")
        budget = self._token_budget(provider)
        ctx = build_whole_repo(self.files, budget)
        return prompt_full_repo(principle, self.config.repo.language, ctx)

    def _build_smell_prompt(self, principle: str) -> tuple[str, str]:
        provider = self._get_provider("gemini")
        budget = self._token_budget(provider)
        ctx = build_whole_repo(self.files, budget)
        return prompt_smell(principle, self.config.repo.language, ctx)

    def _build_skeleton_prompt(self, principle: str, provider: LLMProvider) -> tuple[str, str]:
        budget = self._token_budget(provider, cap=100_000)
        ctx = build_skeleton(self.files, budget)
        return prompt_skeleton(principle, self.config.repo.language, ctx)

    def _build_class_centric_prompt(self, principle: str, provider: LLMProvider) -> tuple[str, str]:
        budget = self._token_budget(provider, cap=150_000)
        targets = select_target_classes(self.files)
        ctx = build_class_centric_batch(targets, self.files, budget)
        return prompt_class_centric(principle, self.config.repo.language, ctx)

    # ------------------------------------------------------------------
    # Single-call strategies (full_repo / smell / skeleton)
    # ------------------------------------------------------------------

    def _scan_single_call(
        self,
        scan_id: str,
        principle: str,
        scan_num: int,
        variation: ScanVariation,
        provider: LLMProvider,
        scan_output_dir: Path,
        prompts: tuple[str, str],
    ) -> bool:
        """Return True if the API call succeeded, False on failure."""
        system_prompt, user_prompt = prompts
        start = time.time()
        try:
            response = provider.complete_with_retry(
                system_prompt, user_prompt,
                temperature=variation.temperature,
                max_tokens=self.config.llm.max_output_tokens,
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            self._save_error_record(scan_output_dir, scan_id, principle, scan_num, variation, str(e))
            return False

        duration_ms = (time.time() - start) * 1000
        findings, parse_errors = parse_llm_response(response.raw_text)
        print(
            f"  Found {len(findings)} findings ({parse_errors} parse errors) in {duration_ms:.0f}ms"
        )

        self._register_findings(findings, scan_id)

        record = ScanRecord(
            scan_id=scan_id,
            repo_name=self.config.repo.name,
            principle=Principle(principle),
            scan_number=scan_num,
            provider=response.provider,
            model=response.model,
            temperature=variation.temperature,
            context_mode=variation.context_mode,
            prompt_text=user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt,
            raw_response=response.raw_text,
            findings=findings,
            parse_errors=parse_errors,
            duration_ms=duration_ms,
        )
        self._save_record(scan_output_dir, record)
        self.registry.save(extra=self.collect_scan_status())
        return True

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _register_findings(self, findings: list[Finding], scan_id: str):
        new_count = 0
        for finding in findings:
            issue_id, is_new = self.registry.register(finding, scan_id)
            if is_new:
                new_count += 1
                print(f"    NEW: {issue_id} — {finding.entity_name} ({finding.severity.value})")
        print(f"  {new_count} new issues, {len(findings) - new_count} duplicates")

    def _save_record(self, scan_output_dir: Path, record: ScanRecord):
        scan_output_dir.mkdir(parents=True, exist_ok=True)
        (scan_output_dir / "raw_response.json").write_text(
            json.dumps(record.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )
        (scan_output_dir / "parsed_findings.json").write_text(
            json.dumps(
                [f.model_dump() for f in record.findings],
                indent=2, default=str,
            ),
            encoding="utf-8",
        )

    def _save_error_record(
        self, scan_output_dir: Path, scan_id: str, principle: str,
        scan_num: int, variation: ScanVariation, error: str,
    ):
        record = ScanRecord(
            scan_id=scan_id,
            repo_name=self.config.repo.name,
            principle=Principle(principle),
            scan_number=scan_num,
            provider=variation.provider_name,
            model="error",
            temperature=variation.temperature,
            context_mode=variation.context_mode,
            prompt_text="",
            raw_response="",
            error=error,
        )
        self._save_record(scan_output_dir, record)

    def _reload_scan(self, scan_output_dir: Path, scan_id: str):
        findings_file = scan_output_dir / "parsed_findings.json"
        if findings_file.exists():
            try:
                data = json.loads(findings_file.read_text(encoding="utf-8"))
                for item in data:
                    finding = Finding(**item)
                    self.registry.register(finding, scan_id)
            except Exception:
                pass
