"""LanguageAdapter implementations + factory."""

from __future__ import annotations

from pathlib import Path

from .base import LanguageAdapter
from .c_cpp_adapter import CCppAdapter
from .java_gradle_adapter import JavaGradleAdapter
from .java_maven_adapter import JavaMavenAdapter
from .python_adapter import PythonAdapter


def get_adapter(language: str, refactor_config, workspace_root: Path | None = None):
    """Instantiate the right adapter for a (language, build-system) combination.

    `language` comes from the project YAML (`repo.language`). `refactor_config`
    is the parsed `refactor:` block — we read adapter-specific knobs off it.
    `workspace_root` is optional; if given and `build_system` is not pinned,
    we auto-detect Maven vs Gradle by looking for `pom.xml` / `build.gradle`.
    """
    lang = (language or "").lower()
    if lang in ("python", "py"):
        return PythonAdapter(
            python_executable=refactor_config.python_executable,
            install_extras=refactor_config.install_extras,
        )
    if lang in ("c", "c++", "cpp", "cxx", "cc"):
        return CCppAdapter()
    if lang in ("java", "kotlin", "kt", "jvm"):
        bs = (refactor_config.build_system or "").lower()
        if not bs and workspace_root is not None:
            if (workspace_root / "pom.xml").exists():
                bs = "maven"
            elif (
                (workspace_root / "build.gradle").exists()
                or (workspace_root / "build.gradle.kts").exists()
                or (workspace_root / "settings.gradle").exists()
                or (workspace_root / "settings.gradle.kts").exists()
            ):
                bs = "gradle"
        if bs == "maven":
            return JavaMavenAdapter(
                maven_command=refactor_config.maven_command or None,
                skip_setup=refactor_config.skip_build_setup,
                full_suite_command=refactor_config.full_suite_command or None,
                extra_test_args=list(refactor_config.maven_extra_args or []),
            )
        if bs == "gradle":
            return JavaGradleAdapter(
                gradle_command=refactor_config.gradle_command or None,
                skip_setup=refactor_config.skip_build_setup,
                gradle_test_task=refactor_config.gradle_test_task or "test",
                gradle_compile_task=refactor_config.gradle_compile_task or "compileTestJava",
                gradle_extra_args=list(refactor_config.gradle_extra_args or []),
                full_suite_command=refactor_config.full_suite_command or None,
            )
        raise ValueError(
            f"Could not determine Java build system (set refactor.build_system "
            f"to 'maven' or 'gradle' in your config, or ensure pom.xml / "
            f"build.gradle exists in the workspace). language={language!r}"
        )
    raise ValueError(f"No adapter registered for language={language!r}")


__all__ = [
    "LanguageAdapter",
    "CCppAdapter",
    "PythonAdapter",
    "JavaMavenAdapter",
    "JavaGradleAdapter",
    "get_adapter",
]
