"""
Kaggle dataset download utilities.

This module downloads public Kaggle datasets defined in:

    configs/data/kaggle_datasets.yaml

Design intent
-------------
The notebooks should choose *which* datasets to download, while this module
does the actual work.

Example notebook usage:

    from glaucoma_segmentation.data.kaggle_download import download_kaggle_datasets

    download_results = download_kaggle_datasets(
        dataset_keys=["glaucoma_fundus_imaging_bundle", "papila"],
        unzip=True,
        force=False,
    )

This implementation uses the Kaggle CLI through subprocess instead of importing
the Kaggle Python API. That is intentional because the current Kaggle package
on Rivanna exposes a working CLI, while the old Python import path may not be
available.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from glaucoma_segmentation.data.dataset_registry import (
    find_project_root,
    select_datasets,
)


def get_kaggle_executable() -> str:
    """
    Find the Kaggle CLI executable.

    The usual path is discovered from PATH. If PATH is odd, which can happen
    in Rivanna / VS Code / Jupyter sessions, this function also checks beside
    the active Python executable.

    Returns
    -------
    str
        Path to the Kaggle CLI executable.

    Raises
    ------
    RuntimeError
        If the Kaggle CLI cannot be found.
    """
    kaggle_path = shutil.which("kaggle")

    if kaggle_path:
        return kaggle_path

    env_kaggle_path = Path(sys.executable).parent / "kaggle"

    if env_kaggle_path.exists():
        return str(env_kaggle_path)

    raise RuntimeError(
        "Could not find the Kaggle CLI. Confirm that the notebook kernel or "
        "terminal is using the glaucoma-capstone environment and that the "
        "kaggle package is installed."
    )


def resolve_local_dir(local_dir: str | Path) -> Path:
    """
    Resolve a dataset local_dir from the YAML registry.

    Relative paths are interpreted relative to the project root.

    Parameters
    ----------
    local_dir:
        Local dataset directory from the registry.

    Returns
    -------
    Path
        Absolute path to the local dataset directory.
    """
    path = Path(local_dir)

    if path.is_absolute():
        return path

    return find_project_root() / path


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    """
    Run a command and raise a readable error if it fails.

    Parameters
    ----------
    command:
        Command represented as a list of arguments.

    Returns
    -------
    subprocess.CompletedProcess[str]
        Completed process result.

    Raises
    ------
    RuntimeError
        If the command exits with a non-zero return code.
    """
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Command failed.\n\n"
            f"Command:\n{' '.join(command)}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    return result


def check_kaggle_cli() -> None:
    """
    Confirm that the Kaggle CLI is available.
    """
    command = [get_kaggle_executable(), "--help"]
    run_command(command)


def check_kaggle_auth() -> dict[str, str]:
    """
    Check whether Kaggle authentication is available.

    This uses:

        kaggle auth print-access-token

    It does not print the token value in the returned dictionary.

    Returns
    -------
    dict[str, str]
        Small status dictionary.

    Raises
    ------
    RuntimeError
        If Kaggle auth is not configured.
    """
    command = [get_kaggle_executable(), "auth", "print-access-token"]
    result = run_command(command)

    token_preview = result.stdout.strip()

    if not token_preview:
        raise RuntimeError(
            "Kaggle auth command succeeded but did not return a token."
        )

    return {
        "status": "authenticated",
        "token_detected": "true",
    }


def download_kaggle_dataset(
    dataset_key: str,
    dataset_metadata: dict[str, Any],
    unzip: bool = True,
    force: bool = False,
) -> dict[str, Any]:
    """
    Download one Kaggle dataset using the Kaggle CLI.

    Parameters
    ----------
    dataset_key:
        Dataset key from configs/data/kaggle_datasets.yaml.
    dataset_metadata:
        Metadata dictionary for the dataset.
    unzip:
        Whether to unzip the dataset after download.
    force:
        Whether to force re-download if files already exist.

    Returns
    -------
    dict[str, Any]
        Download result summary.
    """
    check_kaggle_cli()

    kaggle_slug = dataset_metadata["kaggle_slug"]
    local_dir = resolve_local_dir(dataset_metadata["local_dir"])
    local_dir.mkdir(parents=True, exist_ok=True)

    command = [
        get_kaggle_executable(),
        "datasets",
        "download",
        "-d",
        kaggle_slug,
        "-p",
        str(local_dir),
    ]

    if unzip:
        command.append("--unzip")

    if force:
        command.append("--force")

    result = run_command(command)

    return {
        "dataset_key": dataset_key,
        "display_name": dataset_metadata.get("display_name"),
        "kaggle_slug": kaggle_slug,
        "local_dir": str(local_dir),
        "unzip": unzip,
        "force": force,
        "stdout": result.stdout,
    }


def download_kaggle_datasets(
    dataset_keys: list[str],
    unzip: bool = True,
    force: bool = False,
    registry_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Download selected Kaggle datasets by registry key.

    Parameters
    ----------
    dataset_keys:
        Dataset keys from configs/data/kaggle_datasets.yaml.
    unzip:
        Whether to unzip downloads.
    force:
        Whether to force re-download.
    registry_path:
        Optional custom path to a dataset registry YAML file.

    Returns
    -------
    list[dict[str, Any]]
        Download summaries.
    """
    selected = select_datasets(
        dataset_keys=dataset_keys,
        registry_path=registry_path,
    )

    results: list[dict[str, Any]] = []

    for dataset_key, metadata in selected.items():
        result = download_kaggle_dataset(
            dataset_key=dataset_key,
            dataset_metadata=metadata,
            unzip=unzip,
            force=force,
        )
        results.append(result)

    return results


def download_default_kaggle_datasets(
    unzip: bool = True,
    force: bool = False,
    registry_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Download all datasets marked download_now: true in the registry.

    Parameters
    ----------
    unzip:
        Whether to unzip downloads.
    force:
        Whether to force re-download.
    registry_path:
        Optional custom path to a dataset registry YAML file.

    Returns
    -------
    list[dict[str, Any]]
        Download summaries.
    """
    selected = select_datasets(
        dataset_keys=None,
        download_now_only=True,
        registry_path=registry_path,
    )

    return download_kaggle_datasets(
        dataset_keys=list(selected.keys()),
        unzip=unzip,
        force=force,
        registry_path=registry_path,
    )