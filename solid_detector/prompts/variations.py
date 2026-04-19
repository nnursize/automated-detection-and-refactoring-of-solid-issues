"""Scan variation schedule — 4 strategies x 3 temperatures = 12 scans per principle.

All scans use Gemini (1M context window).

Scans 1-3:  full_repo       — whole-repo context, baseline
Scans 4-6:  smell_two_step  — CoT: smells first, map to SOLID
Scans 7-9:  class_centric   — target class + base classes + imports
Scans 10-12: skeleton       — signatures-only repo-wide view
"""

from __future__ import annotations

from ..models import ContextMode, ScanVariation

SCAN_SCHEDULE: list[ScanVariation] = [
    # Gemini — full-repo baseline
    ScanVariation(scan_number=1,  context_mode=ContextMode.FULL_REPO,    temperature=0.2, provider_name="gemini", strategy="full_repo"),
    ScanVariation(scan_number=2,  context_mode=ContextMode.FULL_REPO,    temperature=0.5, provider_name="gemini", strategy="full_repo"),
    ScanVariation(scan_number=3,  context_mode=ContextMode.FULL_REPO,    temperature=0.8, provider_name="gemini", strategy="full_repo"),
    # Gemini — SMELL two-step CoT
    ScanVariation(scan_number=4,  context_mode=ContextMode.SMELL,        temperature=0.2, provider_name="gemini", strategy="smell_two_step"),
    ScanVariation(scan_number=5,  context_mode=ContextMode.SMELL,        temperature=0.5, provider_name="gemini", strategy="smell_two_step"),
    ScanVariation(scan_number=6,  context_mode=ContextMode.SMELL,        temperature=0.8, provider_name="gemini", strategy="smell_two_step"),
    # Gemini — class-centric
    ScanVariation(scan_number=7,  context_mode=ContextMode.CLASS_CENTRIC, temperature=0.2, provider_name="gemini", strategy="class_centric"),
    ScanVariation(scan_number=8,  context_mode=ContextMode.CLASS_CENTRIC, temperature=0.5, provider_name="gemini", strategy="class_centric"),
    ScanVariation(scan_number=9,  context_mode=ContextMode.CLASS_CENTRIC, temperature=0.8, provider_name="gemini", strategy="class_centric"),
    # Gemini — skeleton (signatures only)
    ScanVariation(scan_number=10, context_mode=ContextMode.SKELETON,     temperature=0.2, provider_name="gemini", strategy="skeleton"),
    ScanVariation(scan_number=11, context_mode=ContextMode.SKELETON,     temperature=0.5, provider_name="gemini", strategy="skeleton"),
    ScanVariation(scan_number=12, context_mode=ContextMode.SKELETON,     temperature=0.8, provider_name="gemini", strategy="skeleton"),
]


def get_variation(scan_number: int) -> ScanVariation:
    """Get the variation parameters for a specific scan number (1-12)."""
    for v in SCAN_SCHEDULE:
        if v.scan_number == scan_number:
            return v
    raise ValueError(f"Invalid scan number: {scan_number}. Must be 1-12.")
