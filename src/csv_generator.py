#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Handles generating CSV files from ASVS source repositories."""

import sys
from pathlib import Path

from .repo_fetcher import _run_command
from . import config  # Import the whole module


def generate_english_csv() -> bool:
    """Generates the English CSV file using the tools in the ASVS repo."""
    print("Generating English CSV...")
    # Define paths relative to project root
    # Use config module attributes
    repo_en_dir = config.PROJECT_ROOT / config.ASVS_REPO_EN_DIR
    tools_dir = repo_en_dir / config.ASVS_VERSION / "tools"
    export_script = tools_dir / "export.py"
    # Use the Python interpreter from the current activated environment
    python_executable = sys.executable
    output_csv_path = config.CSV_EN_FINAL
    # Command working directory needs to be ASVS/<version>
    run_cwd = repo_en_dir / config.ASVS_VERSION

    if not run_cwd.is_dir():
        print(f"Error: English ASVS directory not found: {run_cwd}", file=sys.stderr)
        return False
    if not export_script.is_file():
        print(f"Error: Export script not found: {export_script}", file=sys.stderr)
        return False

    # 1. Install Python dependencies for the export tool
    print("Installing Python dependencies (dicttoxml, dicttoxml2) using uv...")
    uv_executable = "uv"
    dependencies = ["dicttoxml", "dicttoxml2"]
    install_cmd = [uv_executable, "pip", "install"] + dependencies
    # Run install command from the tools directory where scripts might expect it
    if not _run_command(install_cmd, cwd=tools_dir, check=False):
        print(
            "Warning: Failed to install Python dependencies using uv pip install. CSV generation might fail.",
            file=sys.stderr,
        )
        # Continue, the export script might still work if deps are already present

    # 2. Run the export script to generate CSV
    print(f"Running export script to generate {output_csv_path.name}...")
    export_cmd = [
        python_executable,
        str(
            export_script.relative_to(run_cwd)
        ),  # Path relative to CWD: "tools/export.py"
        "--format",
        "csv",
    ]

    # Execute the command, redirecting stdout to the output file
    if not _run_command(export_cmd, cwd=run_cwd, output_file=output_csv_path):
        print(
            "Error: Failed to generate English CSV using export script.",
            file=sys.stderr,
        )
        _try_remove_file(output_csv_path, "incomplete")
        return False

    # 3. Check if the CSV was generated and is not empty
    if output_csv_path.is_file() and output_csv_path.stat().st_size > 0:
        print("English CSV generated successfully.")
        return True
    else:
        print(
            f"Error: Generated English CSV not found or empty at: {output_csv_path}",
            file=sys.stderr,
        )
        _try_remove_file(output_csv_path, "empty")
        return False


def generate_japanese_csv() -> bool:
    """Attempts to generate the Japanese CSV using the export tool."""
    print("Attempting to generate Japanese CSV...")
    # Define paths relative to project root
    # Use config module attributes
    repo_en_dir = config.PROJECT_ROOT / config.ASVS_REPO_EN_DIR
    repo_ja_dir = config.PROJECT_ROOT / config.ASVS_REPO_JA_DIR
    tools_dir = repo_en_dir / config.ASVS_VERSION / "tools"
    export_script = tools_dir / "export.py"
    python_executable = sys.executable
    output_csv_path = config.CSV_JA_FINAL
    # Command working directory needs to be owasp-asvs-ja/<version>
    run_cwd = repo_ja_dir / config.ASVS_VERSION

    # 1. Check directories and script existence
    if not run_cwd.is_dir():
        print(
            f"Warning: Japanese source directory for ASVS {config.ASVS_VERSION} not found: {run_cwd}. Skipping generation.",
            file=sys.stderr,
        )
        _create_empty_ja_csv()
        return False  # Indicate skipped/failed
    if not export_script.is_file():
        # This should not happen if English generation succeeded
        print(f"Error: Export script not found: {export_script}", file=sys.stderr)
        _create_empty_ja_csv()
        return False

    # No separate dependency install needed, assuming English step succeeded

    # 2. Run the export script with language flag
    print(f"Running export script to generate {output_csv_path.name}...")
    export_cmd = [
        python_executable,
        str(export_script),  # Use absolute path to script
        "--format",
        "csv",
        "--language",
        "ja",
    ]

    # Execute the command, redirecting stdout to the output file
    # Run from the Japanese directory context
    if not _run_command(export_cmd, cwd=run_cwd, output_file=output_csv_path):
        print(
            "Error: Failed to generate Japanese CSV using export script.",
            file=sys.stderr,
        )
        _try_remove_file(output_csv_path, "incomplete")
        _create_empty_ja_csv()  # Ensure placeholder exists
        return False

    # 3. Check if the CSV was generated and is not empty
    if output_csv_path.is_file() and output_csv_path.stat().st_size > 0:
        print("Japanese CSV generated successfully.")
        return True
    else:
        print(
            f"Error: Generated Japanese CSV not found or empty at: {output_csv_path}",
            file=sys.stderr,
        )
        _try_remove_file(output_csv_path, "empty")
        _create_empty_ja_csv()
        return False


def _create_empty_ja_csv():
    """Creates an empty placeholder file for the Japanese CSV if generation fails."""
    print(
        f"Creating empty placeholder file: {config.CSV_JA_FINAL}"
    )  # Use config attribute
    try:
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Use config attribute
        config.CSV_JA_FINAL.touch()  # Use config attribute
    except Exception as e:
        print(
            f"Error creating empty Japanese CSV placeholder {config.CSV_JA_FINAL}: {e}",  # Use config attribute
            file=sys.stderr,
        )


def _try_remove_file(file_path: Path, reason: str):
    """Attempts to remove a file, logging errors but not crashing."""
    if file_path.exists():
        try:
            file_path.unlink()
            print(f"Removed {reason} file: {file_path}")
        except OSError as e:
            print(f"Error removing {reason} file {file_path}: {e}", file=sys.stderr)
