"""
Dataset registry utilities.

This module reads the project YAML registry for public datasets and exposes
small helper functions that notebooks and scripts can use.

The YAML file is expected at:
    configs/data/kaggle_datasets.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_DATASET_FIELDS = {
    "display_name",
    "kaggle_slug",
    "local_dir",
    "source_url",
    "source_role",
    "task_type",
    "priority",
    "download_now",
}


def find_project_root(start: Path | None = None) -> Path:
    """
    Find the project root by walking upward until README.md and configs/ exist.

    Parameters
    ----------
    start:
        Optional starting path. Defaults to this file's location.

    Returns
    -------
    Path
        Project root directory.

    Raises
    ------
    FileNotFoundError
        If the project root cannot be found.
    """
    current = Path(start or __file__).resolve()

    if current.is_file():
        current = current.parent

    for parent in [current, *current.parents]:
        if (parent / "README.md").exists() and (parent / "configs").exists():
            return parent

    raise FileNotFoundError(
        "Could not find project root. Expected to find README.md and configs/."
    )


def default_registry_path() -> Path:
    """Return the default Kaggle dataset registry path."""
    return find_project_root() / "configs" / "data" / "kaggle_datasets.yaml"


def load_dataset_registry(registry_path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """
    Load the Kaggle dataset registry from YAML.

    Parameters
    ----------
    registry_path:
        Optional path to the YAML registry. If omitted, the default project
        registry is used.

    Returns
    -------
    dict
        Mapping from dataset key to dataset metadata.
    """
    path = Path(registry_path) if registry_path else default_registry_path()

    if not path.exists():
        raise FileNotFoundError(f"Dataset registry not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict) or "datasets" not in raw:
        raise ValueError(f"Registry must contain a top-level 'datasets' key: {path}")

    datasets = raw["datasets"]

    if not isinstance(datasets, dict):
        raise ValueError("'datasets' must be a mapping of dataset keys to metadata.")

    validate_dataset_registry(datasets)

    return datasets


def validate_dataset_registry(datasets: dict[str, dict[str, Any]]) -> None:
    """
    Validate that each dataset entry has the required fields.

    Parameters
    ----------
    datasets:
        Dataset registry mapping.

    Raises
    ------
    ValueError
        If a dataset entry is missing required fields.
    """
    for dataset_key, metadata in datasets.items():
        if not isinstance(metadata, dict):
            raise ValueError(f"Dataset entry must be a mapping: {dataset_key}")

        missing = REQUIRED_DATASET_FIELDS - set(metadata.keys())

        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(
                f"Dataset '{dataset_key}' is missing required fields: {missing_fields}"
            )


def list_dataset_keys(
    registry_path: str | Path | None = None,
    download_now_only: bool = False,
) -> list[str]:
    """
    List dataset keys from the registry.

    Parameters
    ----------
    registry_path:
        Optional path to registry YAML.
    download_now_only:
        If True, return only datasets marked download_now: true.

    Returns
    -------
    list[str]
        Dataset keys sorted by priority.
    """
    datasets = load_dataset_registry(registry_path)

    if download_now_only:
        datasets = {
            key: value
            for key, value in datasets.items()
            if bool(value.get("download_now", False))
        }

    return sorted(datasets.keys(), key=lambda key: datasets[key].get("priority", 999))


def get_dataset(
    dataset_key: str,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Get metadata for one dataset.

    Parameters
    ----------
    dataset_key:
        Dataset key from the YAML registry.
    registry_path:
        Optional path to registry YAML.

    Returns
    -------
    dict
        Dataset metadata.

    Raises
    ------
    KeyError
        If the dataset key is not found.
    """
    datasets = load_dataset_registry(registry_path)

    if dataset_key not in datasets:
        available = ", ".join(list_dataset_keys(registry_path))
        raise KeyError(
            f"Dataset key '{dataset_key}' not found. Available datasets: {available}"
        )

    return datasets[dataset_key]


def select_datasets(
    dataset_keys: list[str] | None = None,
    download_now_only: bool = False,
    registry_path: str | Path | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Select datasets by explicit keys or by download_now flag.

    Parameters
    ----------
    dataset_keys:
        Explicit dataset keys to select. If provided, this overrides
        download_now_only.
    download_now_only:
        If True and dataset_keys is None, select datasets marked download_now: true.
    registry_path:
        Optional path to registry YAML.

    Returns
    -------
    dict
        Selected dataset registry entries.
    """
    datasets = load_dataset_registry(registry_path)

    if dataset_keys is None:
        keys = list_dataset_keys(
            registry_path=registry_path,
            download_now_only=download_now_only,
        )
    else:
        keys = dataset_keys

    selected = {}

    for key in keys:
        if key not in datasets:
            available = ", ".join(list_dataset_keys(registry_path))
            raise KeyError(f"Dataset key '{key}' not found. Available datasets: {available}")

        selected[key] = datasets[key]

    return selected