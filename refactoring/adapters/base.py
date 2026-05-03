"""LanguageAdapter protocol — per-language plumbing for build, test, syntax check."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..models import TestResult


class LanguageAdapter(Protocol):
    """A pluggable per-language strategy for the refactor pipeline.

    Adapters own everything the orchestrator can't do generically: how to set
    up the cloned project, how to run the full test suite (with optional
    fail-fast), and how to syntax-check edited files before testing.

    Test scoping is intentionally NOT an adapter responsibility — the
    orchestrator always asks the adapter to run the whole suite. Fail-fast
    keeps cost down on bad patches; baseline-failure subtraction (computed
    once globally) keeps pre-existing flaky tests from polluting the result.

    `supports_testing` controls whether the orchestrator runs tests for this
    adapter at all. Set to False for adapters where automated test
    verification is impractical (long Java/Kotlin build setup, brittle
    cross-platform toolchains, etc.) — the orchestrator will then apply the
    LLM patch, commit it, and mark the attempt `applied_unverified`. Manual
    review of `pull_request.md` is the verification step in that mode.
    """

    name: str
    source_extensions: tuple[str, ...]
    supports_testing: bool

    def setup_environment(self, workspace_root: Path) -> None:
        """Prepare the clone so tests can run.

        Run once per workspace. Idempotent — should detect "already set up"
        cheaply and short-circuit. Raises if setup fails.
        """
        ...

    def syntax_check(
        self, workspace_root: Path, rel_paths: list[str],
    ) -> str | None:
        """Best-effort syntax check on changed source files.

        Returns an error message string if any file fails, else None.
        Implementations may skip files of the wrong extension (return None).
        """
        ...

    def run_tests(
        self,
        workspace_root: Path,
        timeout_sec: float,
        fail_fast: bool = True,
        deselect_node_ids: list[str] | None = None,
    ) -> TestResult:
        """Run the full test suite.

        `fail_fast=True` asks the adapter to stop at the first failing test
        (pytest `-x`, surefire `skipAfterFailureCount=1`, gradle `--fail-fast`).
        `fail_fast=False` runs the entire suite — used for baseline capture
        and the end-of-run regression gate.
        `deselect_node_ids` is used by pytest adapters to skip known baseline
        failures during per-attempt regression checks.
        """
        ...

    def is_test_path(self, rel_path: str) -> bool:
        """True if `rel_path` refers to a test file (not production source).

        Used by the patcher to optionally refuse blocks that target tests.
        """
        ...

    def list_sibling_sources(
        self, workspace_root: Path, file_path: str, max_count: int = 30,
    ) -> list[str]:
        """List source files in the same directory as `file_path`.

        Used by the prompt builder to suggest plausible new-module paths.
        Default behaviour can be shared via the helper in this module.
        """
        ...


def list_siblings_by_extension(
    workspace_root: Path,
    file_path: str,
    extensions: tuple[str, ...],
    max_count: int = 30,
) -> list[str]:
    """Default sibling listing: same directory, matching extensions, capped."""
    path = workspace_root / file_path
    parent = path.parent
    if not parent.exists():
        return []
    out: list[str] = []
    for p in sorted(parent.iterdir()):
        if (
            p.is_file()
            and p.suffix in extensions
            and p.name != path.name
        ):
            rel = p.relative_to(workspace_root)
            out.append(str(rel).replace("\\", "/"))
        if len(out) >= max_count:
            break
    return out
