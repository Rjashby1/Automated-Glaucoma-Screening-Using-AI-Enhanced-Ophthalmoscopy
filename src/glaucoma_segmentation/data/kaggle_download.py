"""
Kaggle dataset download utilities.

This module uses the Kaggle CLI, not the old Kaggle Python API import.

Notebook usage example:

    from glaucoma_segmentation.data.kaggle_download import download_kaggle_datasets

    download_kaggle_datasets(["origa_prior_group"], unzip=True)
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from glaucoma_segmentation.data.dataset_registry import (
    find_project_root,
    select_datasets,
)


def resolve_local_dir(local_dir: str | Path) -> Path:
    """Resolve a registry local_dir relative to the project root."""
    path = Path(local_dir)

    if path.is_absolute():
        return path

    return find_project_root() / path


def check_kaggle_cli() -> None:
    """Confirm that the Kaggle CLI is available."""
    result = subprocess.run(
        ["kaggle", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Kaggle CLI is not available in this environment.\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a shell command and raise a readable error if it fails."""
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


def download_kaggle_dataset(
    dataset_key: str,
    dataset_metadata: dict[str, Any],
    unzip: bool = True,
    force: bool = False,
) -> dict[str, Any]:
    """Download one Kaggle dataset using the Kaggle CLI."""
    check_kaggle_cli()

    kaggle_slug = dataset_metadata["kaggle_slug"]
    local_dir = resolve_local_dir(dataset_metadata["local_dir"])
    local_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "kaggle",
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
    """Download selected Kaggle datasets by registry key."""
    selected = select_datasets(
        dataset_keys=dataset_keys,
        registry_path=registry_path,
    )

    results = []

    for dataset_key, metadata in selected.items():
        results.append(
            download_kaggle_dataset(
                dataset_key=dataset_key,
                dataset_metadata=metadata,
                unzip=unzip,
                force=force,
            )
        )

    return results


def download_default_kaggle_datasets(
    unzip: bool = True,
    force: bool = False,
    registry_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Download all datasets marked download_now: true in the registry."""
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