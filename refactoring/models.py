"""Pydantic models for refactor attempts, patches, test results, and metrics."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from solid_detector.models import Principle


class PatchKind(str, Enum):
    SEARCH_REPLACE = "search_replace"
    CREATE = "create"


class AttemptStatus(str, Enum):
    APPLIED_PASSED = "applied_passed"            # patch applied + tests passed
    APPLIED_FAILED = "applied_failed"            # patch applied but tests regressed
    APPLIED_UNVERIFIED = "applied_unverified"    # patch applied + committed; no test run (non-testing adapter)
    PATCH_FAILED = "patch_failed"
    DETECTION_REJECTED = "detection_rejected"    # detection label is false; refactor intentionally skipped
    OBSOLETE = "obsolete"
    LLM_ERROR = "llm_error"


class PatchBlock(BaseModel):
    kind: PatchKind
    file_path: str
    search_text: Optional[str] = None
    replace_text: str


class TestResult(BaseModel):
    passed: bool
    command: str
    return_code: int = 0
    total: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    duration_ms: float = 0.0
    output_tail: str = ""
    timed_out: bool = False
    failed_node_ids: list[str] = Field(default_factory=list)
    error_node_ids: list[str] = Field(default_factory=list)
    new_failures: list[str] = Field(default_factory=list)
    pre_existing_failures: list[str] = Field(default_factory=list)


class FileMetrics(BaseModel):
    file: str
    # Size — computed for every supported language
    loc: int = 0                 # code lines (excluding blank + comment lines)
    blank_lines: int = 0
    comment_lines: int = 0
    function_count: int = 0      # detected function/method definitions
    # Complexity
    avg_cc: float = 0.0          # Python: radon per-block average. Other langs: 1 + branches/funcs.
    max_cc: float = 0.0          # Python: radon per-block max. Other langs: upper bound = 1 + branches.
    mi: float = 0.0              # Maintainability index — Python only (radon). 0 elsewhere.


class MetricsSnapshot(BaseModel):
    files: list[FileMetrics] = Field(default_factory=list)


class IssueRef(BaseModel):
    """Subset of a refactor-shortlist entry — what the orchestrator actually consumes."""

    issue_id: str
    principle: Principle
    rank: int
    scan_count: int
    severity: str
    file_path: str
    entity_name: str
    entity_type: str
    line_start: int
    line_end: int
    description: str
    reasoning: str


class RefactorAttempt(BaseModel):
    """Persisted record of one refactor attempt."""

    issue_id: str
    principle: Principle
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    model: str = ""
    temperature: float = 0.2
    status: AttemptStatus
    obsolete_reason: Optional[str] = None
    apply_error: Optional[str] = None
    error: Optional[str] = None
    detection_label: Optional[bool] = None
    detection_label_explanation: Optional[str] = None
    prompt_text: str = ""
    response_text: str = ""
    llm_finish_reason: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    patch_blocks: list[PatchBlock] = Field(default_factory=list)
    files_touched: list[str] = Field(default_factory=list)
    test_result: Optional[TestResult] = None
    metrics_before: Optional[MetricsSnapshot] = None
    metrics_after: Optional[MetricsSnapshot] = None
    head_commit: Optional[str] = None
    duration_ms: float = 0.0
