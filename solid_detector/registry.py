"""Issue registry with deduplication."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Finding, Issue, Principle


class IssueRegistry:
    """Stores detected issues and handles deduplication."""

    def __init__(self, registry_path: str):
        self._path = Path(registry_path)
        self._issues: list[Issue] = []
        self._counters: dict[str, int] = {p.value: 0 for p in Principle}
        self._load()

    def _load(self):
        """Load existing registry from disk."""
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                self._issues = [Issue(**item) for item in data.get("issues", [])]
                self._counters = data.get("counters", self._counters)
            except Exception:
                self._issues = []

    def save(self, extra: dict | None = None):
        """Persist registry to disk. `extra` is merged into the top-level JSON."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {}
        if extra:
            data.update(extra)
        data["issues"] = [issue.model_dump() for issue in self._issues]
        data["counters"] = self._counters
        self._path.write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )

    def register(self, finding: Finding, scan_id: str) -> tuple[str, bool]:
        """Register a finding. Returns (issue_id, is_new).

        If the finding is a duplicate of an existing issue, the existing
        issue is updated and is_new=False. Otherwise a new issue is created.
        """
        # Check for duplicates
        for issue in self._issues:
            if self._is_duplicate(finding, issue):
                if scan_id not in issue.duplicate_scan_ids:
                    issue.duplicate_scan_ids.append(scan_id)
                    issue.scan_count += 1
                return issue.issue_id, False

        # Create new issue
        principle = finding.principle.value
        self._counters[principle] = self._counters.get(principle, 0) + 1
        issue_id = f"{principle}-{self._counters[principle]:03d}"

        issue = Issue(
            issue_id=issue_id,
            principle=finding.principle,
            canonical_finding=finding,
            duplicate_scan_ids=[scan_id],
            first_detected_scan=scan_id,
            scan_count=1,
        )
        self._issues.append(issue)
        return issue_id, True

    def _is_duplicate(self, finding: Finding, issue: Issue) -> bool:
        """Check if a finding is a duplicate of an existing issue."""
        existing = issue.canonical_finding

        # Must be same principle
        if finding.principle != existing.principle:
            return False

        # Must be same file
        if finding.file_path != existing.file_path:
            return False

        # Check entity name overlap (fuzzy)
        if not self._entity_overlap(finding.entity_name, existing.entity_name):
            return False

        # Check line range overlap (>50%)
        if finding.line_start > 0 and existing.line_start > 0:
            if not self._line_overlap(
                finding.line_start, finding.line_end,
                existing.line_start, existing.line_end,
            ):
                return False

        return True

    @staticmethod
    def _entity_overlap(name1: str, name2: str) -> bool:
        """Check if two entity names refer to the same or related entities."""
        # Exact match
        if name1 == name2:
            return True

        # One is a method of the other's class (e.g., "Foo" and "Foo.bar")
        parts1 = name1.split(".")
        parts2 = name2.split(".")
        if parts1[0] == parts2[0]:
            return True

        return False

    @staticmethod
    def _line_overlap(
        start1: int, end1: int, start2: int, end2: int
    ) -> bool:
        """Check if two line ranges overlap by more than 50%."""
        if end1 == 0 or end2 == 0:
            return True  # If we don't have line info, assume overlap

        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        overlap = max(0, overlap_end - overlap_start)

        min_range = min(end1 - start1, end2 - start2)
        if min_range <= 0:
            return True

        return overlap / min_range > 0.5

    def clear(self):
        """Drop all in-memory issues and reset counters (registry not saved)."""
        self._issues = []
        self._counters = {p.value: 0 for p in Principle}

    @property
    def issues(self) -> list[Issue]:
        return self._issues

    def get_issues_by_principle(self, principle: str) -> list[Issue]:
        return [i for i in self._issues if i.principle.value == principle]

    def summary(self) -> dict:
        """Return a summary of the registry."""
        total = len(self._issues)
        by_principle = {}
        for p in Principle:
            issues = self.get_issues_by_principle(p.value)
            by_principle[p.value] = {
                "total": len(issues),
                "multi_scan": sum(1 for i in issues if i.scan_count > 1),
            }
        return {"total_issues": total, "by_principle": by_principle}
