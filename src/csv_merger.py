#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Handles merging the English and Japanese CSV files."""

import sys
from pathlib import Path
from typing import Optional
import re  # Import re module

import pandas as pd

# Add project root to sys.path if needed, or ensure running from root
# project_root = Path(__file__).parent.parent
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root)) # Removed sys.path modification

from src import config

# Define the final desired column order
FINAL_COLUMNS_ORDER = [
    "req_id",
    "chapter_id",
    "chapter_name_ja",
    "chapter_name_en",
    "section_id",
    "section_name_ja",
    "section_name_en",
    "req_description_ja",
    "req_description_en",
    "level1",
    "level2",
    "level3",
    "cwe",
    "nist",
]

# Columns expected to be common after loading (before merge)
COMMON_COLS = [
    "req_id",
    "chapter_id",
    "section_id",
    "level1",
    "level2",
    "level3",
    "cwe",
    "nist",
]


def _parse_req_id(req_id: str) -> tuple:
    """Parses 'Vx.y.z' into a tuple of integers (x, y, z) for sorting."""
    if not isinstance(req_id, str):
        # Handle non-string or NaN values, place them at the end
        return (float("inf"), float("inf"), float("inf"))
    match = re.match(r"V(\d+)\.(\d+)\.(\d+)", req_id)
    if match:
        # Convert captured groups to integers
        return tuple(map(int, match.groups()))
    else:
        # Handle unexpected formats, place them at the end
        # Alternatively, raise an error or log a warning
        print(
            f"Warning: Could not parse req_id '{req_id}' for sorting.", file=sys.stderr
        )
        return (float("inf"), float("inf"), float("inf"))


def _load_and_prepare_csv(file_path: Path, lang_suffix: str) -> Optional[pd.DataFrame]:
    """Loads a CSV, cleans column names, checks for req_id, and renames language cols."""
    if not file_path.is_file() or file_path.stat().st_size == 0:
        print(f"Warning: CSV file not found or empty: {file_path}", file=sys.stderr)
        return None

    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        if "req_id" not in df.columns:
            print(f"Error: 'req_id' column missing in {file_path}", file=sys.stderr)
            return None

        cols_to_rename = {
            "chapter_name": f"chapter_name_{lang_suffix}",
            "section_name": f"section_name_{lang_suffix}",
            "req_description": f"req_description_{lang_suffix}",
        }
        # Rename only existing columns
        df = df.rename(
            columns={k: v for k, v in cols_to_rename.items() if k in df.columns}
        )

        print(f"Loaded and prepared {lang_suffix.upper()} CSV: {file_path}")
        return df

    except Exception as e:
        print(f"Error reading or preparing CSV {file_path}: {e}", file=sys.stderr)
        return None


def merge_csv_files():
    """Loads the generated English and Japanese CSVs and merges them based on req_id."""
    print("Merging CSV files...")

    df_ja = _load_and_prepare_csv(config.CSV_JA_FINAL, "ja")
    df_en = _load_and_prepare_csv(config.CSV_EN_FINAL, "en")

    df_merged: Optional[pd.DataFrame] = None

    # --- Merge Logic ---
    if df_ja is not None and df_en is not None:
        print("Performing outer merge on 'req_id'...")
        try:
            # Identify common columns actually present in both dataframes
            common_cols_present_in_both = list(
                set(df_ja.columns) & set(df_en.columns) & set(COMMON_COLS)
            )
            if "req_id" not in common_cols_present_in_both:
                print(
                    "Critical Error: 'req_id' is missing from common columns for merge.",
                    file=sys.stderr,
                )
                return  # Cannot merge without req_id

            df_merged = pd.merge(
                df_ja,
                df_en,
                on=common_cols_present_in_both,  # Merge on all common keys
                how="outer",
                suffixes=(
                    "_ja",
                    "_en",
                ),  # Suffixes apply if non-key cols have same name
            )
            print("Merge complete.")

        except Exception as e:
            print(f"Error during merge operation: {e}", file=sys.stderr)
            # Attempt to proceed with individual files if merge fails
            df_merged = None

    # --- Handle cases where merge didn't happen or only one file exists ---
    if df_merged is None:
        if df_ja is not None:
            print(
                "Merge failed or English CSV missing. Using Japanese CSV data.",
                file=sys.stderr,
            )
            df_merged = df_ja
        elif df_en is not None:
            print(
                "Merge failed or Japanese CSV missing. Using English CSV data.",
                file=sys.stderr,
            )
            df_merged = df_en
        else:
            print(
                "Error: Neither English nor Japanese CSV could be loaded. Cannot create merged file.",
                file=sys.stderr,
            )
            return  # Exit the function

    # --- Sorting by req_id ---
    try:
        print("Sorting merged data by req_id...")
        # Apply the custom sort key function to the 'req_id' column
        df_merged = df_merged.sort_values(
            by="req_id", key=lambda col: col.map(_parse_req_id)
        )
        print("Sorting complete.")
    except Exception as e:
        print(f"Error during sorting by req_id: {e}", file=sys.stderr)
        # Continue even if sorting fails, but log the error

    # --- Final Column Reordering and Saving ---
    try:
        # Ensure all desired columns exist, adding missing ones with NaN
        for col in FINAL_COLUMNS_ORDER:
            if col not in df_merged.columns:
                df_merged[col] = pd.NA  # Or np.nan if preferred

        # Reindex to enforce final order and drop unexpected columns
        df_merged = df_merged.reindex(columns=FINAL_COLUMNS_ORDER)

        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df_merged.to_csv(config.CSV_MERGED, index=False, encoding="utf-8-sig")
        print(f"Merged CSV saved successfully to: {config.CSV_MERGED}")

    except Exception as e:
        print(f"Error reordering columns or saving merged CSV: {e}", file=sys.stderr)


# Example for direct execution (testing purposes)
# if __name__ == "__main__":
#     config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
#     # Create dummy CSVs for testing if needed
#     # pd.DataFrame({"req_id": ["V1.1.1"], "chapter_name": ["Test En"], ...}).to_csv(config.CSV_EN_FINAL, index=False)
#     # pd.DataFrame({"req_id": ["V1.1.1"], "chapter_name": ["Test Ja"], ...}).to_csv(config.CSV_JA_FINAL, index=False)
#     merge_csv_files()
