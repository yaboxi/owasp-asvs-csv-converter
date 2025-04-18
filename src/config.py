#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration settings for the ASVS checklist generation."""

from pathlib import Path

# --- Repository Settings ---
ASVS_REPO_EN_URL = "https://github.com/OWASP/ASVS.git"
ASVS_REPO_JA_URL = "https://github.com/coky-t/owasp-asvs-ja.git"
ASVS_REPO_EN_DIR = Path("ASVS")
ASVS_REPO_JA_DIR = Path("owasp-asvs-ja")

# --- ASVS Version ---
ASVS_VERSION = "5.0"

# --- Output Settings ---
# Assuming script runs from the project root
PROJECT_ROOT = Path(__file__).parent.parent  # srcの親 = プロジェクトルート
OUTPUT_DIR = PROJECT_ROOT / "output"
CSV_EN_FINAL = OUTPUT_DIR / f"asvs_{ASVS_VERSION}_en.csv"
CSV_JA_FINAL = OUTPUT_DIR / f"asvs_{ASVS_VERSION}_ja.csv"
CSV_MERGED = OUTPUT_DIR / f"asvs_{ASVS_VERSION}_merged.csv"

# --- Tool Paths (Relative to project root) ---
# These might need adjustment depending on where the script is run from
# Or determined dynamically in the generator module
# GENERATE_CSV_SCRIPT_REL_PATH = f"{ASVS_REPO_EN_DIR}/{ASVS_VERSION}/tools/generate-csv"
