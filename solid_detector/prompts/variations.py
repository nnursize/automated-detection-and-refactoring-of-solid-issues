"""Scan variation schedule — defines how the 12 scans per principle differ."""

from __future__ import annotations

from ..models import ContextMode, ScanVariation

# 12-scan schedule per principle.
# Scans 1-6: Gemini (full-repo, large context)
# Scans 7-12: Groq (per-file, fast)
SCAN_SCHEDULE: list[ScanVariation] = [
    # Full-repo scans with Gemini at varying temperatures
    ScanVariation(scan_number=1, context_mode=ContextMode.FULL_REPO, temperature=0.2, provider_name="gemini"),
    ScanVariation(scan_number=2, context_mode=ContextMode.FULL_REPO, temperature=0.4, provider_name="gemini"),
    ScanVariation(scan_number=3, context_mode=ContextMode.FULL_REPO, temperature=0.6, provider_name="gemini"),
    ScanVariation(scan_number=4, context_mode=ContextMode.FULL_REPO, temperature=0.8, provider_name="gemini"),
    ScanVariation(scan_number=5, context_mode=ContextMode.FULL_REPO, temperature=0.3, provider_name="gemini"),
    ScanVariation(scan_number=6, context_mode=ContextMode.FULL_REPO, temperature=0.5, provider_name="gemini"),
    # Per-file scans with Groq (largest files)
    ScanVariation(scan_number=7, context_mode=ContextMode.PER_FILE, temperature=0.2, provider_name="groq"),
    ScanVariation(scan_number=8, context_mode=ContextMode.PER_FILE, temperature=0.4, provider_name="groq"),
    ScanVariation(scan_number=9, context_mode=ContextMode.PER_FILE, temperature=0.6, provider_name="groq"),
    ScanVariation(scan_number=10, context_mode=ContextMode.PER_FILE, temperature=0.8, provider_name="groq"),
    # Per-file scans with Groq (medium files)
    ScanVariation(scan_number=11, context_mode=ContextMode.PER_FILE, temperature=0.3, provider_name="groq"),
    ScanVariation(scan_number=12, context_mode=ContextMode.PER_FILE, temperature=0.5, provider_name="groq"),
]


def get_variation(scan_number: int) -> ScanVariation:
    """Get the variation parameters for a specific scan number (1-12)."""
    for v in SCAN_SCHEDULE:
        if v.scan_number == scan_number:
            return v
    raise ValueError(f"Invalid scan number: {scan_number}. Must be 1-12.")


def get_file_selection(scan_number: int) -> str:
    """Determine which files to select for per-file scans."""
    if scan_number <= 10:
        return "largest"
    return "medium"
