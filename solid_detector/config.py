"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, model_validator


class RepoConfig(BaseModel):
    name: str
    path: str
    language: str
    source_root: str
    file_extensions: list[str]
    exclude_patterns: list[str] = Field(default_factory=list)
    max_file_lines: int = 500
    min_file_lines: int = 10


class LLMConfig(BaseModel):
    primary_provider: str = "gemini"
    secondary_provider: str = "gemini"
    temperature_range: list[float] = Field(default_factory=lambda: [0.2, 0.8])
    max_output_tokens: int = 16384
    model: Optional[str] = None  # None -> GeminiProvider default (gemini-2.5-flash)


class ScanConfig(BaseModel):
    scans_per_principle: int = 12
    principles: list[str] = Field(
        default_factory=lambda: ["SRP", "OCP", "LSP", "ISP", "DIP"]
    )
    output_dir: str = "scans"
    reports_dir: str = "reports"


class ProjectConfig(BaseModel):
    repo: RepoConfig
    llm: LLMConfig = Field(default_factory=LLMConfig)
    scan: ScanConfig = Field(default_factory=ScanConfig)

    # Resolved paths (set after loading)
    base_dir: Optional[str] = None  # directory containing the config file
    repo_abs_path: Optional[str] = None
    source_abs_path: Optional[str] = None

    @model_validator(mode="after")
    def resolve_paths(self) -> "ProjectConfig":
        if self.base_dir:
            base = Path(self.base_dir)
            repo_path = Path(self.repo.path)
            if not repo_path.is_absolute():
                repo_path = (base / repo_path).resolve()
            self.repo_abs_path = str(repo_path)
            self.source_abs_path = str(repo_path / self.repo.source_root)
        return self


def load_config(config_path: str) -> ProjectConfig:
    """Load and validate a YAML config file."""
    config_path = Path(config_path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    config = ProjectConfig(**raw, base_dir=str(config_path.parent))

    # Validate that repo path exists
    if not Path(config.repo_abs_path).exists():
        raise FileNotFoundError(f"Repository not found: {config.repo_abs_path}")
    if not Path(config.source_abs_path).exists():
        raise FileNotFoundError(f"Source root not found: {config.source_abs_path}")

    return config


def get_api_key(provider: str) -> str:
    """Get API key from environment variable."""
    env_var = f"{provider.upper()}_API_KEY"
    key = os.environ.get(env_var, "")
    if not key:
        raise EnvironmentError(
            f"API key not found. Set the {env_var} environment variable.\n"
            f"See the plan for setup instructions."
        )
    return key
