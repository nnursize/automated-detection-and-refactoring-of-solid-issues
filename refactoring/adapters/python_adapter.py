"""Python adapter: pip + pytest + pytest-json-report (full suite + fail-fast)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ..models import TestResult
from ..test_runner import run_pytest
from .base import list_siblings_by_extension


class PythonAdapter:
    name = "python"
    source_extensions = (".py",)
    supports_testing = True

    def __init__(
        self,
        python_executable: str | None = None,
        install_extras: str = ".[dev,stats]",
    ):
        self.python_executable = python_executable or sys.executable
        self.install_extras = install_extras

    def venv_python(self, workspace_root: Path) -> Path:
        venv_dir = workspace_root / ".venv"
        if sys.platform == "win32":
            return venv_dir / "Scripts" / "python.exe"
        return venv_dir / "bin" / "python"

    def setup_environment(self, workspace_root: Path) -> None:
        venv_dir = workspace_root / ".venv"
        if not venv_dir.exists():
            print(f"[python-adapter] creating venv at {venv_dir} using {self.python_executable}")
            subprocess.run(
                [self.python_executable, "-m", "venv", str(venv_dir)],
                check=True,
            )
        if self._already_installed(workspace_root):
            return
        py = self.venv_python(workspace_root)
        print(f"[python-adapter] pip install -e {self.install_extras}")
        subprocess.run(
            [str(py), "-m", "pip", "install", "-e", self.install_extras],
            cwd=str(workspace_root),
            check=True,
        )
        subprocess.run(
            [str(py), "-m", "pip", "install", "pytest", "pytest-json-report"],
            check=True,
        )

    def _already_installed(self, workspace_root: Path) -> bool:
        py = self.venv_python(workspace_root)
        if not py.exists():
            return False
        check = subprocess.run(
            [str(py), "-c",
             "import importlib.util, sys; "
             "sys.exit(0 if importlib.util.find_spec('pytest') and "
             "importlib.util.find_spec('pytest_jsonreport') else 1)"],
            capture_output=True,
        )
        return check.returncode == 0

    def syntax_check(
        self, workspace_root: Path, rel_paths: list[str],
    ) -> str | None:
        for rel in rel_paths:
            if not rel.endswith(".py"):
                continue
            path = workspace_root / rel
            try:
                source = path.read_text(encoding="utf-8")
            except OSError as e:
                return f"could not read {rel}: {e}"
            try:
                compile(source, rel, "exec")
            except SyntaxError as e:
                return f"syntax error in {rel}:{e.lineno}: {e.msg}"
        return None

    def run_tests(
        self,
        workspace_root: Path,
        timeout_sec: float,
        fail_fast: bool = True,
        deselect_node_ids: list[str] | None = None,
    ) -> TestResult:
        return run_pytest(
            python_exe=self.venv_python(workspace_root),
            workspace_root=workspace_root,
            paths=[],
            timeout_sec=timeout_sec,
            fail_fast=fail_fast,
            deselect_node_ids=deselect_node_ids,
        )

    def is_test_path(self, rel_path: str) -> bool:
        norm = rel_path.replace("\\", "/")
        if norm.startswith("tests/") or "/tests/" in norm:
            return True
        if Path(norm).name.startswith("test_"):
            return True
        return False

    def list_sibling_sources(
        self, workspace_root: Path, file_path: str, max_count: int = 30,
    ) -> list[str]:
        return list_siblings_by_extension(
            workspace_root, file_path, self.source_extensions, max_count,
        )
