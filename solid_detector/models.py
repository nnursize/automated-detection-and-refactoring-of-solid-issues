"""Data models for the SOLID violation detection framework."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Principle(str, Enum):
    SRP = "SRP"
    OCP = "OCP"
    LSP = "LSP"
    ISP = "ISP"
    DIP = "DIP"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EntityType(str, Enum):
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"


class ContextMode(str, Enum):
    FULL_REPO = "full-repo"
    PER_FILE = "per-file"


class Finding(BaseModel):
    """A single SOLID violation finding from an LLM scan."""

    file_path: str
    entity_name: str
    entity_type: EntityType
    line_start: int
    line_end: int
    principle: Principle
    severity: Severity
    description: str
    reasoning: str


class Issue(BaseModel):
    """A deduplicated issue in the registry, possibly found by multiple scans."""

    issue_id: str  # e.g., "SRP-001"
    principle: Principle
    canonical_finding: Finding
    duplicate_scan_ids: list[str] = Field(default_factory=list)
    first_detected_scan: str
    scan_count: int = 1  # how many scans found this
    status: str = "detected"


class LLMResponse(BaseModel):
    """Response from an LLM API call."""

    raw_text: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    finish_reason: str = ""


class ScanVariation(BaseModel):
    """Parameters for a single scan variation."""

    scan_number: int
    context_mode: ContextMode
    temperature: float
    provider_name: str  # "gemini" or "groq"


class ScanRecord(BaseModel):
    """Full record of a completed scan."""

    scan_id: str  # e.g., "seaborn-master_SRP_scan_01"
    repo_name: str
    principle: Principle
    scan_number: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    provider: str
    model: str
    temperature: float
    context_mode: ContextMode
    prompt_text: str
    raw_response: str
    findings: list[Finding] = Field(default_factory=list)
    parse_errors: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None


class FileInfo(BaseModel):
    """Metadata about a discovered source file."""

    path: str  # relative to repo root
    absolute_path: str
    line_count: int
    char_count: int
    estimated_tokens: int  # char_count // 4
    classes: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)
