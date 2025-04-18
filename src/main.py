#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main script to generate and merge OWASP ASVS checklists."""

import sys
import logging

from src import config, csv_generator, csv_merger, repo_fetcher


def main():
    """Orchestrates the checklist generation and merge process."""
    print("Starting OWASP ASVS checklist generation and merge process...")

    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # 0. Ensure output directory exists
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Using output directory: {config.OUTPUT_DIR}")

        # 1. Clone or update repositories
        print("\n[Step 1/4] Preparing external repositories...")
        repo_fetcher.prepare_repositories()

        # 2. Generate English CSV
        print("\n[Step 2/4] Generating English CSV...")
        success_en = csv_generator.generate_english_csv()
        if not success_en:
            # Error is logged within the function, exit here
            print(
                "Stopping script due to English CSV generation failure.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 3. Attempt to Generate Japanese CSV
        print("\n[Step 3/4] Attempting to generate Japanese CSV...")
        # Failure here is not critical, warnings are logged within the function
        csv_generator.generate_japanese_csv()

        # 4. Merge CSV files
        print("\n[Step 4/4] Merging CSV files...")
        # Merge function handles missing/empty files
        csv_merger.merge_csv_files()

        print("\nScript finished successfully.")

    except Exception as e:
        # Catch any unexpected errors during the main flow
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        print("Script finished with errors.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
