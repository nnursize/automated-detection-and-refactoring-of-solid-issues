"""Scan orchestration — runs the 60-scan detection loop."""

from __future__ import annotations

import json
import time
from pathlib import Path

from .config import ProjectConfig, get_api_key
from .discovery import (
    discover_files,
    prepare_full_repo_context,
    prepare_per_file_context,
)
from .llm.base import LLMProvider
from .llm.gemini import GeminiProvider
from .models import ContextMode, FileInfo, Principle, ScanRecord
from .parsing import parse_llm_response
from .prompts.templates import (
    build_full_repo_prompt,
    build_per_file_prompt,
    build_system_prompt,
)
from .prompts.variations import get_file_selection, get_variation
from .registry import IssueRegistry


class ScanOrchestrator:
    """Orchestrates the 60 detection scans for a repository."""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.files: list[FileInfo] = []
        self._providers: dict[str, LLMProvider] = {}

        # Set up output directories
        self.scan_dir = Path(config.scan.output_dir) / config.repo.name
        self.scan_dir.mkdir(parents=True, exist_ok=True)

        # Set up registry
        registry_path = self.scan_dir / "registry.json"
        self.registry = IssueRegistry(str(registry_path))

    def _get_provider(self, provider_name: str) -> LLMProvider:
        """Get or create an LLM provider by name."""
        if provider_name not in self._providers:
            api_key = get_api_key(provider_name)
            if provider_name == "gemini":
                self._providers[provider_name] = GeminiProvider(api_key)
            elif provider_name == "groq":
                # Import here to avoid requiring groq if not used
                from .llm.groq import GroqProvider
                self._providers[provider_name] = GroqProvider(api_key)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        return self._providers[provider_name]

    def discover(self):
        """Run file discovery on the repository."""
        print(f"Discovering files in {self.config.source_abs_path}...")
        self.files = discover_files(self.config)
        print(f"  Found {len(self.files)} source files")
        total_tokens = sum(f.estimated_tokens for f in self.files)
        print(f"  Estimated total tokens: {total_tokens:,}")

    def run_all(self, principle: str | None = None, scan_number: int | None = None):
        """Run all scans (or a subset).

        Args:
            principle: If set, run only scans for this principle.
            scan_number: If set, run only this scan number (1-12).
        """
        if not self.files:
            self.discover()

        principles = (
            [principle] if principle else self.config.scan.principles
        )

        for princ in principles:
            scans = (
                [scan_number] if scan_number
                else range(1, self.config.scan.scans_per_principle + 1)
            )
            for scan_num in scans:
                self._run_single_scan(princ, scan_num)

        # Save registry after all scans
        self.registry.save()
        print("\nAll scans complete. Registry saved.")
        print(f"Registry summary: {json.dumps(self.registry.summary(), indent=2)}")

    def dry_run(self):
        """Show what would be scanned without calling LLMs."""
        if not self.files:
            self.discover()

        print(f"\n=== DRY RUN for {self.config.repo.name} ===")
        print(f"Language: {self.config.repo.language}")
        print(f"Source root: {self.config.source_abs_path}")
        print(f"Files discovered: {len(self.files)}")
        print(f"\nTop 10 files by size:")
        for f in self.files[:10]:
            print(f"  {f.path} ({f.line_count} lines, ~{f.estimated_tokens} tokens)")
            if f.classes:
                print(f"    Classes: {', '.join(f.classes[:5])}")

        print(f"\nPrinciples: {', '.join(self.config.scan.principles)}")
        print(f"Scans per principle: {self.config.scan.scans_per_principle}")
        total_scans = len(self.config.scan.principles) * self.config.scan.scans_per_principle
        print(f"Total scans: {total_scans}")

        print(f"\nScan schedule:")
        for scan_num in range(1, self.config.scan.scans_per_principle + 1):
            v = get_variation(scan_num)
            print(
                f"  Scan {scan_num:2d}: provider={v.provider_name}, "
                f"mode={v.context_mode.value}, temp={v.temperature}"
            )

    def _run_single_scan(self, principle: str, scan_num: int):
        """Run a single scan for one principle."""
        scan_id = f"{self.config.repo.name}_{principle}_scan_{scan_num:02d}"

        # Check if already completed successfully (resumability)
        scan_output_dir = self.scan_dir / principle / f"scan_{scan_num:02d}"
        response_file = scan_output_dir / "raw_response.json"
        if response_file.exists():
            # Only skip if it was a successful scan (no error field)
            try:
                import json as _json
                saved = _json.loads(response_file.read_text(encoding="utf-8"))
                if not saved.get("error"):
                    print(f"[SKIP] {scan_id} — already completed")
                    self._reload_scan(scan_output_dir, scan_id)
                    return
                else:
                    print(f"[RETRY] {scan_id} — previous attempt failed: {saved['error'][:80]}")
            except Exception:
                pass

        variation = get_variation(scan_num)
        print(f"\n[SCAN] {scan_id} (provider={variation.provider_name}, "
              f"mode={variation.context_mode.value}, temp={variation.temperature})")

        # Get provider
        try:
            provider = self._get_provider(variation.provider_name)
        except Exception as e:
            print(f"  ERROR: Could not initialize provider: {e}")
            self._save_error_record(scan_output_dir, scan_id, principle, scan_num, variation, str(e))
            return

        # Build prompts
        system_prompt = build_system_prompt(principle)

        if variation.context_mode == ContextMode.FULL_REPO:
            # Full repo context — cap at 200K for Gemini free tier (250K/min limit)
            token_budget = min(provider.max_context_tokens() - 5000, 200_000)
            code_context = prepare_full_repo_context(self.files, token_budget)
            user_prompt = build_full_repo_prompt(
                principle, self.config.repo.language, code_context
            )
            self._execute_scan(
                scan_id, principle, scan_num, variation,
                provider, system_prompt, user_prompt, scan_output_dir,
            )
        else:
            # Per-file mode: scan multiple files, aggregate findings
            file_selection = get_file_selection(scan_num)
            file_contexts = prepare_per_file_context(self.files, file_selection)
            all_findings = []
            total_errors = 0

            for file_path, file_content in file_contexts:
                user_prompt = build_per_file_prompt(
                    principle, self.config.repo.language, file_path, file_content
                )
                try:
                    response = provider.complete_with_retry(
                        system_prompt, user_prompt,
                        temperature=variation.temperature,
                        max_tokens=self.config.llm.max_output_tokens,
                    )
                    findings, errors = parse_llm_response(response.raw_text)
                    all_findings.extend(findings)
                    total_errors += errors
                    print(f"  {file_path}: {len(findings)} findings")
                except Exception as e:
                    print(f"  {file_path}: ERROR — {e}")
                    total_errors += 1

                # Small delay between per-file calls
                time.sleep(0.5)

            # Register all findings
            new_count = 0
            for finding in all_findings:
                _, is_new = self.registry.register(finding, scan_id)
                if is_new:
                    new_count += 1

            print(f"  Total: {len(all_findings)} findings, {new_count} new issues")

            # Save scan record
            record = ScanRecord(
                scan_id=scan_id,
                repo_name=self.config.repo.name,
                principle=Principle(principle),
                scan_number=scan_num,
                provider=variation.provider_name,
                model="per-file-aggregate",
                temperature=variation.temperature,
                context_mode=variation.context_mode,
                prompt_text="[per-file mode — multiple prompts]",
                raw_response=json.dumps(
                    [f.model_dump() for f in all_findings], default=str
                ),
                findings=all_findings,
                parse_errors=total_errors,
            )
            self._save_record(scan_output_dir, record)
            self.registry.save()

    def _execute_scan(
        self,
        scan_id: str,
        principle: str,
        scan_num: int,
        variation,
        provider: LLMProvider,
        system_prompt: str,
        user_prompt: str,
        scan_output_dir: Path,
    ):
        """Execute a single LLM call and process results."""
        start = time.time()
        try:
            response = provider.complete_with_retry(
                system_prompt, user_prompt,
                temperature=variation.temperature,
                max_tokens=self.config.llm.max_output_tokens,
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            self._save_error_record(
                scan_output_dir, scan_id, principle, scan_num, variation, str(e)
            )
            return

        duration_ms = (time.time() - start) * 1000

        # Parse findings
        findings, parse_errors = parse_llm_response(response.raw_text)
        print(f"  Found {len(findings)} findings ({parse_errors} parse errors) "
              f"in {duration_ms:.0f}ms")

        # Register findings
        new_count = 0
        for finding in findings:
            issue_id, is_new = self.registry.register(finding, scan_id)
            if is_new:
                new_count += 1
                print(f"    NEW: {issue_id} — {finding.entity_name} ({finding.severity.value})")

        print(f"  {new_count} new issues, {len(findings) - new_count} duplicates")

        # Save scan record
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
        self.registry.save()

    def _save_record(self, scan_output_dir: Path, record: ScanRecord):
        """Save a scan record to disk."""
        scan_output_dir.mkdir(parents=True, exist_ok=True)

        # Save full record
        (scan_output_dir / "raw_response.json").write_text(
            json.dumps(record.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )

        # Save parsed findings separately for easy reading
        (scan_output_dir / "parsed_findings.json").write_text(
            json.dumps(
                [f.model_dump() for f in record.findings],
                indent=2, default=str,
            ),
            encoding="utf-8",
        )

    def _save_error_record(
        self, scan_output_dir: Path, scan_id: str, principle: str,
        scan_num: int, variation, error: str,
    ):
        """Save an error record for a failed scan."""
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
        """Reload findings from a previously completed scan into registry."""
        findings_file = scan_output_dir / "parsed_findings.json"
        if findings_file.exists():
            try:
                from .models import Finding
                data = json.loads(findings_file.read_text(encoding="utf-8"))
                for item in data:
                    finding = Finding(**item)
                    self.registry.register(finding, scan_id)
            except Exception:
                pass
