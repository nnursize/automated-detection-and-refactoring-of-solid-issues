"""CLI entry point for SOLID violation detection."""

import argparse
import sys
from pathlib import Path

from solid_detector.config import load_config
from solid_detector.orchestrator import ScanOrchestrator
from solid_detector.reporting import generate_all_reports


def main():
    parser = argparse.ArgumentParser(
        description="SOLID Violation Detection Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run — see what would be scanned
  python run_detection.py --config configs/seaborn.yaml --dry-run

  # Run a single scan
  python run_detection.py --config configs/seaborn.yaml --principle SRP --scan 1

  # Run all 12 scans for SRP
  python run_detection.py --config configs/seaborn.yaml --principle SRP

  # Run all 60 scans
  python run_detection.py --config configs/seaborn.yaml

  # Generate reports from existing scan data
  python run_detection.py --config configs/seaborn.yaml --report-only
        """,
    )
    parser.add_argument(
        "--config", required=True, help="Path to repo YAML config file"
    )
    parser.add_argument(
        "--principle",
        choices=["SRP", "OCP", "LSP", "ISP", "DIP"],
        help="Run only scans for this principle if wanted",
    )
    parser.add_argument(
        "--scan", type=int, choices=range(1, 13),
        help="Run only this scan number (1-12)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be scanned without calling LLMs",
    )
    parser.add_argument(
        "--report-only", action="store_true",
        help="Generate reports from existing scan data",
    )
    parser.add_argument(
        "--model",
        help="Override the Gemini model ID (e.g. gemini-2.5-flash-lite, "
             "gemini-2.0-flash, gemma-3-27b-it). Defaults to gemini-2.5-flash. "
             "Useful for switching to a fresh per-model free-tier quota bucket. "
             "Run --list-models to see valid IDs for your API key.",
    )
    parser.add_argument(
        "--list-models", action="store_true",
        help="Print the Gemini model IDs available to your API key and exit.",
    )
    parser.add_argument(
        "--sleep", type=float, default=60.0,
        help="Seconds to wait between scans that actually call the API. "
             "Default 60s to respect Gemini's free-tier per-minute quota. "
             "Skipped scans (already completed) don't trigger the wait. "
             "Set to 0 to disable.",
    )
    parser.add_argument(
        "--rebuild-registry", action="store_true",
        help="Clear the registry and rebuild it from scans/ on disk. "
             "Run this after deleting a scan folder so its findings are "
             "dropped; then re-run the scan with a different --model.",
    )
    parser.add_argument(
        "--continue-on-error", action="store_true",
        help="Keep running after a scan fails (e.g. 429 / 503 / 404). "
             "Default is to halt so quota isn't wasted while the model is busy.",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Print a table of every scan (ok / failed / missing) with "
             "the model used and any error message, then exit.",
    )

    args = parser.parse_args()

    if args.list_models:
        from solid_detector.config import get_api_key
        from solid_detector.llm.gemini import GeminiProvider
        provider = GeminiProvider(get_api_key("gemini"))
        models = provider.list_models()

        families = {"gemini-3": [], "gemini-2.5": [], "gemini-2.0": [],
                    "gemma": [], "other": []}
        for mid in models:
            tag = " (preview)" if "preview" in mid else ""
            line = f"  {mid}{tag}"
            if mid.startswith("gemini-3"):
                families["gemini-3"].append(line)
            elif mid.startswith("gemini-2.5"):
                families["gemini-2.5"].append(line)
            elif mid.startswith("gemini-2.0"):
                families["gemini-2.0"].append(line)
            elif mid.startswith("gemma"):
                families["gemma"].append(line)
            else:
                families["other"].append(line)

        labels = {
            "gemini-2.5": "Gemini 2.5 (recommended — stable, free-tier friendly)",
            "gemini-2.0": "Gemini 2.0 (stable, separate quota bucket)",
            "gemini-3":   "Gemini 3 (preview — newer, separate quota bucket)",
            "gemma":      "Gemma (open models, separate quota family)",
            "other":      "Other",
        }
        print("Text-generation models available to your API key:\n")
        for key in ["gemini-2.5", "gemini-2.0", "gemini-3", "gemma", "other"]:
            if families[key]:
                print(f"{labels[key]}:")
                for line in families[key]:
                    print(line)
                print()
        return

    # Load config
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    # CLI --model overrides whatever the YAML config says
    if args.model:
        config.llm.model = args.model

    print(f"=== SOLID Violation Detector ===")
    print(f"Repository: {config.repo.name} ({config.repo.language})")
    print(f"Source: {config.source_abs_path}")
    print(f"Model: {config.llm.model or 'gemini-2.5-flash (default)'}")

    # Create orchestrator
    orchestrator = ScanOrchestrator(config)

    if args.status:
        orchestrator.print_status()
        return

    if args.rebuild_registry:
        orchestrator.rebuild_registry()
        return

    if args.dry_run:
        orchestrator.dry_run()
        return

    if args.report_only:
        # Just generate reports from existing data
        orchestrator.discover()
        # Reload all existing scans into registry
        scan_dir = Path(config.scan.output_dir) / config.repo.name
        for principle_dir in sorted(scan_dir.iterdir()):
            if not principle_dir.is_dir():
                continue
            for scan_subdir in sorted(principle_dir.iterdir()):
                if not scan_subdir.is_dir():
                    continue
                scan_id = f"{config.repo.name}_{principle_dir.name}_scan_{scan_subdir.name.split('_')[-1]}"
                orchestrator._reload_scan(scan_subdir, scan_id)

        reports_dir = Path(config.scan.reports_dir)
        print(f"\nGenerating reports...")
        generate_all_reports(
            orchestrator.registry, scan_dir, reports_dir, config.repo.name
        )
        return

    # Run scans
    orchestrator.run_all(
        principle=args.principle,
        scan_number=args.scan,
        sleep_seconds=args.sleep,
        stop_on_error=not args.continue_on_error,
    )

    # Generate reports after scanning
    reports_dir = Path(config.scan.reports_dir)
    scan_dir = Path(config.scan.output_dir) / config.repo.name
    print(f"\nGenerating reports...")
    generate_all_reports(
        orchestrator.registry, scan_dir, reports_dir, config.repo.name
    )


if __name__ == "__main__":
    main()
