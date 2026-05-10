"""C/C++ adapter: source discovery + unverified patch mode.

The project does not try to build or test C/C++ repositories automatically.
This adapter gives the refactoring pipeline the language plumbing it needs
for prompt context and path classification, while applied patches are marked
`applied_unverified` for manual review.
"""

from __future__ import annotations

from pathlib import Path

from ..models import TestResult
from .base import list_siblings_by_extension


class CCppAdapter:
    name = "c-cpp"
    source_extensions = (
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".h",
        ".hh",
        ".hpp",
        ".hxx",
        ".ipp",
    )
    supports_testing = False

    def setup_environment(self, workspace_root: Path) -> None:
        return None

    def syntax_check(
        self, workspace_root: Path, rel_paths: list[str],
    ) -> str | None:
        for rel in rel_paths:
            if Path(rel).suffix.lower() not in self.source_extensions:
                continue
            path = workspace_root / rel
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as e:
                return f"could not read {rel}: {e}"
            for marker in ("<<<<<<<", "=======", ">>>>>>>"):
                if marker in text:
                    return f"unresolved patch/conflict marker {marker!r} in {rel}"
        return None

    def run_tests(
        self,
        workspace_root: Path,
        timeout_sec: float,
        fail_fast: bool = True,
        deselect_node_ids: list[str] | None = None,
    ) -> TestResult:
        return TestResult(
            passed=True,
            command="not run: C/C++ adapter is patch-only",
            total=0,
            passed_count=0,
            failed_count=0,
            skipped_count=0,
            error_count=0,
            duration_ms=0.0,
            output_tail="",
            timed_out=False,
        )

    def is_test_path(self, rel_path: str) -> bool:
        norm = rel_path.replace("\\", "/").lower()
        parts = norm.split("/")
        if any(part in {"test", "tests", "testing", "fuzzing", "benchmarks"} for part in parts):
            return True
        name = Path(norm).name
        return name.startswith("test_") or name.endswith("_test.cpp") or name.endswith("_tests.cpp")

    def list_sibling_sources(
        self, workspace_root: Path, file_path: str, max_count: int = 30,
    ) -> list[str]:
        return list_siblings_by_extension(
            workspace_root, file_path, self.source_extensions, max_count,
        )
