"""Cloned-repo workspace management: clone, checkpoint, revert, baseline.

Language-agnostic. Per-language environment setup (venv + pip, mvn compile,
gradle compileTestJava, etc.) is delegated to the LanguageAdapter and called
by the orchestrator after `prepare()`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class WorkspaceError(RuntimeError):
    pass


class Workspace:
    """Owns one cloned copy of a target repo and runs git operations against it."""

    def __init__(
        self,
        source_repo: Path,
        clone_dir: Path,
    ):
        self.source_repo = Path(source_repo).resolve()
        self.clone_dir = Path(clone_dir).resolve()

    def prepare(self) -> None:
        """One-shot setup: clone (or copy + git init) the source repo."""
        if not self.source_repo.exists():
            raise WorkspaceError(f"Source repo missing: {self.source_repo}")
        if not self.clone_dir.exists():
            self.clone_dir.parent.mkdir(parents=True, exist_ok=True)
            source_is_git = (self.source_repo / ".git").exists()
            if source_is_git:
                print(f"[workspace] git clone {self.source_repo} -> {self.clone_dir}")
                self._git("clone", str(self.source_repo), str(self.clone_dir), cwd=None)
            else:
                print(f"[workspace] copying {self.source_repo} -> {self.clone_dir} (source has no .git)")
                shutil.copytree(
                    self.source_repo, self.clone_dir,
                    ignore=shutil.ignore_patterns(
                        ".venv", "venv", "__pycache__",
                        ".pytest_cache", ".tox", "*.egg-info",
                        "build", "dist", "target", ".gradle",
                    ),
                )
                self._init_git_in_clone()
        self._ensure_git_identity()
        self._ensure_framework_gitignore()

    def _init_git_in_clone(self) -> None:
        self._git("init", cwd=self.clone_dir)
        self._git("config", "user.email", "refactor@local", cwd=self.clone_dir)
        self._git("config", "user.name", "Refactor Framework", cwd=self.clone_dir)
        self._git("add", "-A", cwd=self.clone_dir)
        self._git("commit", "-m", "baseline", cwd=self.clone_dir)

    _FRAMEWORK_IGNORES = (
        ".venv/",
        "venv/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        ".pytest_report.json",
        ".refactor_baseline.json",
        ".refactor_maven_ready",
        ".refactor_gradle_ready",
        "*.egg-info/",
        "target/",
        ".gradle/",
        "build/",
    )

    def _ensure_framework_gitignore(self) -> None:
        gitignore_path = self.clone_dir / ".gitignore"
        existing = ""
        if gitignore_path.exists():
            existing = gitignore_path.read_text(encoding="utf-8")
        existing_lines = {line.strip() for line in existing.splitlines()}
        missing = [p for p in self._FRAMEWORK_IGNORES if p not in existing_lines]
        if not missing:
            return
        prefix = existing if existing.endswith("\n") or not existing else existing + "\n"
        new_text = prefix + "# Added by refactoring framework\n" + "\n".join(missing) + "\n"
        gitignore_path.write_text(new_text, encoding="utf-8")
        try:
            self._git("add", ".gitignore", cwd=self.clone_dir)
            self._git("commit", "-m",
                      "refactor framework: ignore .venv and runtime artifacts",
                      cwd=self.clone_dir)
        except WorkspaceError as e:
            if "nothing to commit" not in str(e):
                raise

    def _ensure_git_identity(self) -> None:
        try:
            subprocess.run(
                ["git", "config", "user.email"],
                cwd=str(self.clone_dir), check=True,
                capture_output=True, text=True,
            )
        except subprocess.CalledProcessError:
            self._git("config", "user.email", "refactor@local", cwd=self.clone_dir)
            self._git("config", "user.name", "Refactor Framework", cwd=self.clone_dir)

    def _git(self, *args: str, cwd: Path | None = None) -> str:
        cmd = ["git"]
        if cwd is not None:
            try:
                safe_dir = str(Path(cwd).resolve())
                cmd += ["-c", f"safe.directory={safe_dir}"]
            except OSError:
                pass
        elif self.clone_dir.exists():
            cmd += ["-c", f"safe.directory={self.clone_dir}"]
        result = subprocess.run(
            [*cmd, *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            detail = "\n".join(
                part for part in (result.stdout.strip(), result.stderr.strip())
                if part
            )
            raise WorkspaceError(
                f"git {' '.join(args)} failed:\n{detail}"
            )
        return result.stdout

    def baseline_ref(self) -> str:
        return self._git("rev-parse", "HEAD", cwd=self.clone_dir).strip()

    def head_commit(self) -> str:
        return self._git("rev-parse", "HEAD", cwd=self.clone_dir).strip()

    def is_clean(self) -> bool:
        out = self._git("status", "--porcelain", cwd=self.clone_dir)
        return out.strip() == ""

    def revert(self) -> None:
        self._git("reset", "--hard", "HEAD", cwd=self.clone_dir)
        self._git("clean", "-fd",
                  "-e", ".venv", "-e", "venv",
                  "-e", ".refactor_baseline.json",
                  "-e", ".refactor_maven_ready",
                  "-e", ".refactor_gradle_ready",
                  cwd=self.clone_dir)

    def checkpoint(self, message: str) -> str:
        self._git("add", "-A", cwd=self.clone_dir)
        try:
            self._git("commit", "-m", message, cwd=self.clone_dir)
        except WorkspaceError as e:
            if "nothing to commit" in str(e):
                return self.head_commit()
            raise
        return self.head_commit()

    def diff_since(self, ref: str) -> str:
        return self._git("diff", f"{ref}..HEAD", cwd=self.clone_dir)

    def diff_between(self, base_ref: str, head_ref: str) -> str:
        return self._git("diff", f"{base_ref}..{head_ref}", cwd=self.clone_dir)

    def diff_working_tree(self) -> str:
        return self._git("diff", cwd=self.clone_dir)

    def diff_working_tree_for_paths(self, rel_paths: list[str]) -> str:
        """Return a working-tree diff for known touched paths, including
        untracked CREATE-block files.
        """
        paths = _dedupe_paths(rel_paths)
        if not paths:
            return ""
        tracked = []
        untracked = []
        for rel in paths:
            if self._is_tracked(rel):
                tracked.append(rel)
            else:
                target = self.clone_dir / rel
                if target.is_file():
                    untracked.append(rel)

        parts = []
        if tracked:
            parts.append(self._git("diff", "--", *tracked, cwd=self.clone_dir))
        for rel in untracked:
            parts.append(self._diff_new_file(rel))
        return "".join(part for part in parts if part)

    def _is_tracked(self, rel_path: str) -> bool:
        try:
            self._git("ls-files", "--error-unmatch", rel_path, cwd=self.clone_dir)
            return True
        except WorkspaceError as e:
            if "did not match any file" in str(e) or "pathspec" in str(e):
                return False
            raise

    def _diff_new_file(self, rel_path: str) -> str:
        path = self.clone_dir / rel_path
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return (
                f"diff --git a/{rel_path} b/{rel_path}\n"
                "new file mode 100644\n"
                "index 0000000..0000000\n"
                "--- /dev/null\n"
                f"+++ b/{rel_path}\n"
                "@@ -0,0 +1 @@\n"
                "+(binary file omitted)\n"
            )
        lines = content.splitlines()
        old_count = 0
        new_count = len(lines)
        header_count = new_count if new_count > 0 else 0
        out = [
            f"diff --git a/{rel_path} b/{rel_path}\n",
            "new file mode 100644\n",
            "index 0000000..0000000\n",
            "--- /dev/null\n",
            f"+++ b/{rel_path}\n",
            f"@@ -0,0 +1,{header_count} @@\n" if header_count else "@@ -0,0 +0,0 @@\n",
        ]
        out.extend(f"+{line}\n" for line in lines)
        if content and not content.endswith("\n"):
            out.append("\\ No newline at end of file\n")
        return "".join(out)

    def file_at_commit(self, ref: str, rel_path: str) -> str | None:
        """Return file content at commit `ref`, or None if not present.

        Uses `git show <ref>:<path>`. Raises only on non-"file not found" errors.
        """
        try:
            return self._git("show", f"{ref}:{rel_path}", cwd=self.clone_dir)
        except WorkspaceError as e:
            msg = str(e)
            # Path doesn't exist at that ref (e.g. CREATE block — file is new).
            if "exists on disk, but not in" in msg or "does not exist" in msg \
                    or "fatal: path " in msg or "exists on disk" in msg:
                return None
            raise

    def read_file(self, rel_path: str) -> str:
        return (self.clone_dir / rel_path).read_text(encoding="utf-8")

    def write_file(self, rel_path: str, content: str) -> None:
        path = self.clone_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    @property
    def baseline_path(self) -> Path:
        return self.clone_dir / ".refactor_baseline.json"

    def load_baseline(self) -> dict:
        if not self.baseline_path.exists():
            return {}
        try:
            return json.loads(self.baseline_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def save_baseline(self, data: dict) -> None:
        self.baseline_path.write_text(
            json.dumps(data, indent=2, default=str, sort_keys=True),
            encoding="utf-8",
        )


def _dedupe_paths(paths: list[str]) -> list[str]:
    out = []
    seen = set()
    for path in paths:
        norm = str(path).replace("\\", "/")
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out
