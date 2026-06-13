"""
Kaggle dataset download utilities.

This module downloads public Kaggle datasets defined in:
    configs/data/kaggle_datasets.yaml

The notebook should call these functions with dataset keys, for example:

    download_kaggle_datasets(["origa_prior_group", "papila"])

Kaggle credentials should remain local-only and should never be committed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kaggle.api.kaggle_api_extended import KaggleApi

from glaucoma_segmentation.data.dataset_registry import (
    find_project_root,
    select_datasets,
)


def get_kaggle_api() -> KaggleApi:
    """
    Authenticate and return a Kaggle API client.

    This expects Kaggle credentials to already be configured locally.
    Common setup:
        ~/.kaggle/kaggle.json

    Returns
    -------
    KaggleApi
        Authenticated Kaggle API client.
    """
    api = KaggleApi()
    api.authenticate()
    return api


def resolve_local_dir(local_dir: str | Path) -> Path:
    """
    Resolve a dataset local_dir relative to the project root.

    Parameters
    ----------
    local_dir:
        Path from the YAML registry.

    Returns
    -------
    Path
        Absolute local directory path.
    """
    local_dir = Path(local_dir)

    if local_dir.is_absolute():
        return local_dir

    return find_project_root() / local_dir


def download_kaggle_dataset(
    dataset_key: str,
    dataset_metadata: dict[str, Any],
    unzip: bool = True,
    force: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    """
    Download one Kaggle dataset.

    Parameters
    ----------
    dataset_key:
        Registry key for the dataset.
    dataset_metadata:
        Metadata dictionary from the YAML registry.
    unzip:
        Whether Kaggle should unzip the downloaded dataset.
    force:
        Whether to force re-download even if files already exist.
    quiet:
        Whether to reduce Kaggle API output.

    Returns
    -------
    dict
        Download result summary.
    """
    api = get_kaggle_api()

    kaggle_slug = dataset_metadata["kaggle_slug"]
    local_dir = resolve_local_dir(dataset_metadata["local_dir"])
    local_dir.mkdir(parents=True, exist_ok=True)

    api.dataset_download_files(
        dataset=kaggle_slug,
        path=str(local_dir),
        unzip=unzip,
        quiet=quiet,
        force=force,
    )

    return {
        "dataset_key": dataset_key,
        "display_name": dataset_metadata.get("display_name"),
        "kaggle_slug": kaggle_slug,
        "local_dir": str(local_dir),
        "unzip": unzip,
        "force": force,
    }


def download_kaggle_datasets(
    dataset_keys: list[str],
    unzip: bool = True,
    force: bool = False,
    quiet: bool = False,
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
    quiet:
        Whether to reduce Kaggle API output.
    registry_path:
        Optional custom registry path.

    Returns
    -------
    list[dict]
        Download result summaries.
    """
    selected = select_datasets(
        dataset_keys=dataset_keys,
        registry_path=registry_path,
    )

    results = []

    for dataset_key, metadata in selected.items():
        result = download_kaggle_dataset(
            dataset_key=dataset_key,
            dataset_metadata=metadata,
            unzip=unzip,
            force=force,
            quiet=quiet,
        )
        results.append(result)

    return results


def download_default_kaggle_datasets(
    unzip: bool = True,
    force: bool = False,
    quiet: bool = False,
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
    quiet:
        Whether to reduce Kaggle API output.
    registry_path:
        Optional custom registry path.

    Returns
    -------
    list[dict]
        Download result summaries.
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
        quiet=quiet,
        registry_path=registry_path,
    )