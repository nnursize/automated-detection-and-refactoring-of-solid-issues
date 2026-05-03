"""Parse JUnit-format XML reports (Surefire / Gradle) into TestResult counts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET


@dataclass
class JUnitCounts:
    total: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    failed_node_ids: list[str] = field(default_factory=list)
    error_node_ids: list[str] = field(default_factory=list)


def parse_reports(report_files: list[Path]) -> JUnitCounts:
    """Aggregate counts and failed/errored node IDs across multiple XML files."""
    out = JUnitCounts()
    for path in report_files:
        try:
            tree = ET.parse(path)
        except (ET.ParseError, OSError):
            continue
        _consume(tree.getroot(), out)
    out.passed_count = max(
        0, out.total - out.failed_count - out.skipped_count - out.error_count,
    )
    return out


def discover_reports(*roots: Path) -> list[Path]:
    """Walk the given root dirs for `TEST-*.xml` files."""
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("TEST-*.xml"):
            if p.is_file():
                found.append(p)
    return found


def _consume(node: ET.Element, out: JUnitCounts) -> None:
    if node.tag == "testsuites":
        for child in node:
            _consume(child, out)
        return

    if node.tag == "testsuite":
        nested_suite = any(c.tag == "testsuite" for c in node)
        if nested_suite:
            for child in node:
                _consume(child, out)
            return
        for child in node:
            if child.tag == "testcase":
                _consume_testcase(child, out)
        return


def _consume_testcase(case: ET.Element, out: JUnitCounts) -> None:
    classname = case.get("classname", "") or ""
    name = case.get("name", "") or ""
    nodeid = f"{classname}.{name}" if classname else name
    out.total += 1
    has_failure = any(c.tag == "failure" for c in case)
    has_error = any(c.tag == "error" for c in case)
    has_skipped = any(c.tag == "skipped" for c in case)
    if has_error:
        out.error_count += 1
        out.error_node_ids.append(nodeid)
    elif has_failure:
        out.failed_count += 1
        out.failed_node_ids.append(nodeid)
    elif has_skipped:
        out.skipped_count += 1
