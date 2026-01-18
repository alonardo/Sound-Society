#!/usr/bin/env python3
"""
Main orchestrator script for the Music Sociology Dashboard pipeline.

Usage:
    python run_pipeline.py                     # Run full pipeline
    python run_pipeline.py --test              # Test run (1990s only)
    python run_pipeline.py --years 1980-1989   # Process year range
    python run_pipeline.py --serve             # Launch dashboard server
"""

import argparse
import subprocess
import sys
from datetime import datetime

import config
from fetch_pipeline import run_fetch_pipeline
from analyze_pipeline import run_analysis_pipeline


def print_banner():
    """Print startup banner."""
    print()
    print("=" * 60)
    print("  Sound & Society - Music Sociology Dashboard")
    print("  Billboard Year-End Hot 100 (1959-2023)")
    print("=" * 60)
    print()


def run_test():
    """Run a test on a single decade (1990s)."""
    print("Running test for 1990s...")
    print("-" * 40)

    songs = run_fetch_pipeline(start_year=1990, end_year=1999)
    run_analysis_pipeline(songs=songs)

    print("\nVerifying outputs...")

    if config.DATA_JSON.exists():
        import json
        with open(config.DATA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"  data.json: OK ({len(data['songs'])} songs)")

        if data["songs"]:
            sample = data["songs"][0]
            print(f"  Sample: '{sample['title']}' by {sample['artist']} ({sample['year']})")
            print(f"    - Lyrics: {sample.get('lyrics_available', False)}")
            if sample.get("sentiment"):
                print(f"    - Sentiment: {sample['sentiment']['compound']}")
            if sample.get("lexical_diversity"):
                print(f"    - Lexical diversity: {sample['lexical_diversity']}")
    else:
        print("  data.json: NOT FOUND")

    print("\nTest complete!")


def serve_dashboard():
    """Launch the dashboard server."""
    serve_script = config.BASE_DIR / "serve.py"
    subprocess.run([sys.executable, str(serve_script)])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sound & Society - Music Sociology Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                     Run full pipeline (all years)
  python run_pipeline.py --test              Test run (1990s only)
  python run_pipeline.py --years 1970-1989   Process specific years
  python run_pipeline.py --serve             Launch dashboard in browser
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test on 1990s data"
    )
    parser.add_argument(
        "--years",
        type=str,
        help="Year range to process (e.g., 1980-1989)"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the dashboard server"
    )

    args = parser.parse_args()

    # Handle serve command separately
    if args.serve:
        serve_dashboard()
        return

    print_banner()

    if not config.check_source_data():
        sys.exit(1)

    # Parse year range
    start_year = config.START_YEAR
    end_year = config.END_YEAR

    if args.years:
        try:
            parts = args.years.split("-")
            start_year = int(parts[0])
            end_year = int(parts[1])
        except (ValueError, IndexError):
            print(f"Invalid year range: {args.years}")
            print("Use format: YYYY-YYYY (e.g., 1980-1989)")
            sys.exit(1)

    start_time = datetime.now()

    if args.test:
        run_test()
    else:
        print(f"Running pipeline ({start_year}-{end_year})...")
        print()
        songs = run_fetch_pipeline(start_year=start_year, end_year=end_year)
        run_analysis_pipeline(songs=songs)

    elapsed = datetime.now() - start_time
    print()
    print("=" * 60)
    print(f"Pipeline finished in {elapsed}")
    print()
    print("To view the dashboard, run:")
    print("  python run_pipeline.py --serve")
    print("=" * 60)


if __name__ == "__main__":
    main()
