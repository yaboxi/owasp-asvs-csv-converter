#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Handles cloning and updating external Git repositories."""

import subprocess
import sys
from io import TextIOWrapper
from pathlib import Path
from typing import Optional, Union

from . import config


def _run_command(
    command: list[str],
    cwd: Optional[Path] = None,
    check: bool = True,  # Note: check=True is effectively ignored due to manual check
    output_file: Optional[Path] = None,
) -> bool:
    """Runs a command using subprocess, capturing/redirecting output and handling errors."""
    cwd_str = str(cwd) if cwd else "."
    output_redirect_str = f" > {output_file}" if output_file else ""
    print(f"Running command: {' '.join(command)} in {cwd_str}{output_redirect_str}")

    stdout_dest: Optional[Union[int, TextIOWrapper]] = None
    stderr_dest = subprocess.PIPE  # Always capture stderr
    process_handle = None
    stdout_file_handle: Optional[TextIOWrapper] = None

    try:
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            # Keep track of the file handle separately
            stdout_file_handle = output_file.open("w", encoding="utf-8")
            stdout_dest = stdout_file_handle
        else:
            stdout_dest = subprocess.PIPE

        process_handle = subprocess.run(
            command,
            cwd=cwd,
            check=False,  # Check returncode manually for better error reporting
            stdout=stdout_dest,
            stderr=stderr_dest,
            text=(
                output_file is None
            ),  # Use text=True only when capturing stdout to PIPE
            encoding="utf-8" if output_file is None else None,
        )

        # Log stderr regardless of success/failure if present
        if process_handle.stderr:
            stderr_output = (
                process_handle.stderr.decode("utf-8", errors="replace")
                if isinstance(process_handle.stderr, bytes)
                else process_handle.stderr
            )
            # Avoid printing empty stderr lines
            if stderr_output.strip():
                print(f"Stderr:\n{stderr_output.strip()}", file=sys.stderr)

        # Check return code after handling stderr
        if process_handle.returncode != 0:
            raise subprocess.CalledProcessError(
                process_handle.returncode,
                process_handle.args,
                output=process_handle.stdout,  # May be None if redirected
                stderr=process_handle.stderr,  # Already decoded/printed above
            )

        # If captured stdout, print it
        if output_file is None and process_handle.stdout:
            # Avoid printing empty stdout lines
            if process_handle.stdout.strip():
                print(process_handle.stdout.strip())

        return True  # Command succeeded

    except subprocess.CalledProcessError as e:
        print(
            f"Command '{' '.join(e.cmd)}' failed with exit code {e.returncode}",
            file=sys.stderr,
        )
        # Output was already printed if captured, or redirected
        return False
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}", file=sys.stderr)
        return False
    except Exception as e:
        print(
            f"An unexpected error occurred during command execution: {e}",
            file=sys.stderr,
        )
        return False
    finally:
        # Ensure the file handle is closed if it was opened
        if stdout_file_handle and not stdout_file_handle.closed:
            try:
                stdout_file_handle.close()
            except Exception as e:
                print(f"Error closing output file handle: {e}", file=sys.stderr)


def _clone_or_update(repo_url: str, repo_dir: Path):
    """Clones a repository if it doesn't exist, or updates it if it does."""
    # Use absolute path based on project root defined in config
    repo_path = config.PROJECT_ROOT / repo_dir
    if repo_path.is_dir():
        print(f"Updating repository in {repo_path}...")
        # Use check=False for git pull as it might return non-zero even on some warnings
        if not _run_command(["git", "pull"], cwd=repo_path, check=False):
            # Log warning but continue, assuming repo might still be usable
            print(
                f"Warning: 'git pull' failed or had issues in {repo_path}. Continuing...",
                file=sys.stderr,
            )
    else:
        print(f"Cloning repository {repo_url} into {repo_path}...")
        # Use check=True implicitly (default) or explicitly for clone, as failure is critical
        if not _run_command(["git", "clone", "--depth", "1", repo_url, str(repo_path)]):
            # Raise specific error for cloning failure
            raise RuntimeError(f"Failed to clone repository: {repo_url}")


def prepare_repositories():
    """Prepares both English and Japanese ASVS repositories."""
    print("Preparing repositories...")
    try:
        _clone_or_update(config.ASVS_REPO_EN_URL, config.ASVS_REPO_EN_DIR)
        _clone_or_update(config.ASVS_REPO_JA_URL, config.ASVS_REPO_JA_DIR)
        print("Repositories are ready.")
    except RuntimeError as e:
        # Log the specific error and re-raise to be handled by main
        print(f"Error during repository preparation: {e}", file=sys.stderr)
        raise
