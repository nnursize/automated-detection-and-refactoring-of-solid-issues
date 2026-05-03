"""Refactoring-specific configuration helpers.

Layered on top of `solid_detector.config.ProjectConfig`. We don't modify the
detection config schema; instead, we read the optional `refactor:` block from
the YAML and add framework defaults.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from solid_detector.config import ProjectConfig, load_config as _load_project


class RefactorConfig(BaseModel):
    """Refactor-stage settings (optional `refactor:` YAML block)."""

    workspace_root: str = "refactor_workspaces"
    attempts_root: str = "refactor_attempts"
    reports_dir: str = "refactor_reports"
    install_extras: str = ".[dev,stats]"
    test_timeout_sec: float = 1800.0
    full_suite_timeout_sec: float = 3600.0
    full_suite_command: list[str] = Field(default_factory=list)
    max_full_file_lines: int = 1500
    temperature: float = 0.2
    max_output_tokens: int = 8192
    python_executable: Optional[str] = None  # interpreter to seed the clone's venv (None -> sys.executable)

    # Build-system selection for Java/Kotlin repos. Auto-detected from the
    # workspace (pom.xml / build.gradle) when left empty.
    build_system: Optional[str] = None  # "maven" | "gradle" | None

    # Maven-specific knobs
    maven_command: list[str] = Field(default_factory=list)  # override mvnw / mvn
    maven_extra_args: list[str] = Field(default_factory=list)

    # Gradle-specific knobs
    gradle_command: list[str] = Field(default_factory=list)  # override gradlew / gradle
    gradle_test_task: Optional[str] = None  # default "test"; multi-module: ":logstash-core:test"
    gradle_compile_task: Optional[str] = None  # default "compileTestJava"
    gradle_extra_args: list[str] = Field(default_factory=list)

    # Skip the once-per-clone compile step (mvn test-compile / gradle compileTestJava).
    skip_build_setup: bool = False

    # Back-compat: older YAMLs may set this; we accept it and treat as test_timeout_sec.
    targeted_test_timeout_sec: Optional[float] = None

    def model_post_init(self, _ctx):
        if self.targeted_test_timeout_sec is not None:
            # Honor old field name without breaking existing configs.
            self.test_timeout_sec = max(self.test_timeout_sec, self.targeted_test_timeout_sec)


class RefactorProject(BaseModel):
    """Combined config: detection ProjectConfig + refactor extension."""

    project: ProjectConfig
    refactor: RefactorConfig

    class Config:
        arbitrary_types_allowed = True

    @property
    def repo_name(self) -> str:
        return self.project.repo.name

    @property
    def shortlist_path(self) -> Path:
        return Path(self.project.scan.reports_dir) / f"{self.repo_name}_refactor_shortlist.json"

    @property
    def workspace_dir(self) -> Path:
        return Path(self.refactor.workspace_root) / self.repo_name

    @property
    def attempts_dir(self) -> Path:
        return Path(self.refactor.attempts_root) / self.repo_name

    @property
    def labels_path(self) -> Path:
        return Path("evaluations") / f"{self.repo_name}_labels.json"


def load(config_path: str) -> RefactorProject:
    project = _load_project(config_path)
    raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8")) or {}
    refactor_block = raw.get("refactor", {}) or {}
    refactor = RefactorConfig(**refactor_block)
    return RefactorProject(project=project, refactor=refactor)
