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

    args = parser.parse_args()

    # Load config
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    print(f"=== SOLID Violation Detector ===")
    print(f"Repository: {config.repo.name} ({config.repo.language})")
    print(f"Source: {config.source_abs_path}")

    # Create orchestrator
    orchestrator = ScanOrchestrator(config)

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
