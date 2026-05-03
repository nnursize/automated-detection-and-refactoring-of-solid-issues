"""Java Maven adapter: mvnw/mvn + Surefire XML reports."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from ..models import TestResult
from . import junit_xml
from .base import list_siblings_by_extension


class JavaMavenAdapter:
    name = "java-maven"
    source_extensions = (".java",)
    # Java/Maven test runs are slow + brittle to set up across OS/JDK combos.
    # The orchestrator will skip baseline + run_tests entirely; attempts get
    # the `applied_unverified` status and humans review the diff/PR by hand.
    supports_testing = False

    def __init__(
        self,
        maven_command: list[str] | None = None,
        skip_setup: bool = False,
        full_suite_command: list[str] | None = None,
        extra_test_args: list[str] | None = None,
    ):
        # Resolved at first use against the workspace (mvnw lives there)
        self._maven_override = maven_command
        self.skip_setup = skip_setup
        self._full_suite_override = full_suite_command
        self.extra_test_args = list(extra_test_args or [])

    def _maven(self, workspace_root: Path) -> list[str]:
        if self._maven_override:
            return list(self._maven_override)
        if sys.platform == "win32":
            wrapper = workspace_root / "mvnw.cmd"
        else:
            wrapper = workspace_root / "mvnw"
        if wrapper.exists():
            return [str(wrapper)]
        # Fall back to system mvn on PATH
        mvn = shutil.which("mvn") or shutil.which("mvn.cmd")
        if not mvn:
            raise RuntimeError(
                "No Maven available: workspace lacks mvnw/mvnw.cmd and "
                "`mvn` is not on PATH."
            )
        return [mvn]

    def setup_environment(self, workspace_root: Path) -> None:
        if self.skip_setup:
            return
        marker = workspace_root / ".refactor_maven_ready"
        if marker.exists():
            return
        cmd = self._maven(workspace_root) + [
            "-q", "-B", "-DskipTests", "test-compile",
        ]
        print(f"[maven-adapter] {' '.join(cmd)}")
        proc = subprocess.run(
            cmd, cwd=str(workspace_root),
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-50:])
            raise RuntimeError(
                f"Maven setup failed (exit {proc.returncode}):\n{tail}"
            )
        marker.write_text("ok", encoding="utf-8")

    def syntax_check(
        self, workspace_root: Path, rel_paths: list[str],
    ) -> str | None:
        # Don't run a separate javac; let `mvn test-compile` (next step)
        # surface compile errors. The framework runs that as part of
        # `mvn test`, which is the actual test invocation.
        return None

    def _surefire_report_dirs(self, workspace_root: Path) -> list[Path]:
        roots = [workspace_root / "target" / "surefire-reports"]
        for child in workspace_root.iterdir() if workspace_root.is_dir() else []:
            sub = child / "target" / "surefire-reports"
            if sub.is_dir():
                roots.append(sub)
        return roots

    def run_tests(
        self,
        workspace_root: Path,
        timeout_sec: float,
        fail_fast: bool = True,
        deselect_node_ids: list[str] | None = None,
    ) -> TestResult:
        if self._full_suite_override:
            cmd = list(self._full_suite_override)
        else:
            for d in self._surefire_report_dirs(workspace_root):
                for old in d.glob("TEST-*.xml") if d.exists() else []:
                    try:
                        old.unlink()
                    except OSError:
                        pass
            cmd = self._maven(workspace_root) + ["-q", "-B", "test"]
            if fail_fast:
                # Surefire stops on first failing test; reactor stops on first failing module.
                cmd += [
                    "-Dsurefire.skipAfterFailureCount=1",
                    "-Dfailsafe.skipAfterFailureCount=1",
                    "--fail-fast",
                ]
            cmd += list(self.extra_test_args)
        return self._run_with_command(cmd, workspace_root, timeout_sec)

    def _run_with_command(
        self,
        cmd: list[str],
        workspace_root: Path,
        timeout_sec: float,
    ) -> TestResult:
        cmd_str = " ".join(cmd)
        started = time.time()
        timed_out = False
        try:
            proc = subprocess.run(
                cmd, cwd=str(workspace_root),
                capture_output=True, text=True,
                timeout=timeout_sec,
            )
            stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as e:
            stdout = _decode(e.stdout)
            stderr = _decode(e.stderr)
            rc = -1
            timed_out = True
        duration_ms = (time.time() - started) * 1000.0
        output = (stdout or "") + ("\n[stderr]\n" + stderr if stderr else "")

        report_files = junit_xml.discover_reports(
            *self._surefire_report_dirs(workspace_root)
        )
        counts = junit_xml.parse_reports(report_files)

        passed = (
            rc == 0 and not timed_out
            and counts.failed_count == 0 and counts.error_count == 0
        )
        return TestResult(
            passed=passed,
            command=cmd_str,
            total=counts.total,
            passed_count=counts.passed_count,
            failed_count=counts.failed_count,
            skipped_count=counts.skipped_count,
            error_count=counts.error_count,
            duration_ms=duration_ms,
            output_tail=_tail(output, 200),
            timed_out=timed_out,
            failed_node_ids=counts.failed_node_ids,
            error_node_ids=counts.error_node_ids,
        )

    def is_test_path(self, rel_path: str) -> bool:
        norm = rel_path.replace("\\", "/")
        if "/src/test/java/" in norm or norm.startswith("src/test/java/"):
            return True
        return False

    def list_sibling_sources(
        self, workspace_root: Path, file_path: str, max_count: int = 30,
    ) -> list[str]:
        return list_siblings_by_extension(
            workspace_root, file_path, self.source_extensions, max_count,
        )


def _decode(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value or ""


def _tail(text: str, lines: int) -> str:
    parts = text.splitlines()
    return "\n".join(parts[-lines:]) if len(parts) > lines else text
