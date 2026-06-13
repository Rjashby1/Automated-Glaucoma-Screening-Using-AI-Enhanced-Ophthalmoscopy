"""
File discovery and dataset inventory utilities.

These functions inspect downloaded datasets without assuming their internal
structure. This is important because Kaggle dataset names are not enough:
we need to verify whether each dataset actually contains segmentation masks,
annotations, metadata, and image files.

Typical notebook usage:

    from glaucoma_segmentation.data.discover_files import inventory_registry_datasets

    inventory_df, summary_df, candidate_df = inventory_registry_datasets(
        dataset_keys=["glaucoma_fundus_imaging_bundle", "papila"],
        save_reports=True,
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from glaucoma_segmentation.data.dataset_registry import (
    find_project_root,
    select_datasets,
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp",
}

ANNOTATION_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".xml",
    ".mat",
    ".txt",
}

MASK_KEYWORDS = {
    "mask",
    "masks",
    "label",
    "labels",
    "cup",
    "disc",
    "disk",
    "seg",
    "segmentation",
    "annotation",
    "annotations",
    "ground",
    "truth",
    "gt",
}


def resolve_local_dir(local_dir: str | Path) -> Path:
    """
    Resolve a local directory relative to the project root.

    Parameters
    ----------
    local_dir:
        Local directory from the dataset registry.

    Returns
    -------
    Path
        Absolute path to the local directory.
    """
    path = Path(local_dir)

    if path.is_absolute():
        return path

    return find_project_root() / path


def file_has_mask_keyword(path: Path) -> bool:
    """
    Return True if the file path suggests it may be a mask or annotation.

    Parameters
    ----------
    path:
        File path to inspect.

    Returns
    -------
    bool
        Whether the path contains mask/annotation-related keywords.
    """
    lower_parts = [part.lower() for part in path.parts]
    lower_name = path.name.lower()

    if any(keyword in lower_name for keyword in MASK_KEYWORDS):
        return True

    return any(
        any(keyword in part for keyword in MASK_KEYWORDS)
        for part in lower_parts
    )


def classify_file(path: Path) -> str:
    """
    Classify a file based on extension and path/name hints.

    Parameters
    ----------
    path:
        File path to classify.

    Returns
    -------
    str
        One of: image, possible_mask_image, possible_annotation, other.
    """
    suffix = path.suffix.lower()

    if suffix in IMAGE_EXTENSIONS and file_has_mask_keyword(path):
        return "possible_mask_image"

    if suffix in IMAGE_EXTENSIONS:
        return "image"

    if suffix in ANNOTATION_EXTENSIONS:
        return "possible_annotation"

    return "other"


def inventory_dataset(
    dataset_key: str,
    local_dir: str | Path,
) -> pd.DataFrame:
    """
    Inventory all files for one downloaded dataset.

    Parameters
    ----------
    dataset_key:
        Dataset registry key.
    local_dir:
        Local downloaded dataset directory.

    Returns
    -------
    pd.DataFrame
        One row per file.

    Raises
    ------
    FileNotFoundError
        If the dataset directory does not exist.
    """
    root = resolve_local_dir(local_dir)

    if not root.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist for '{dataset_key}': {root}"
        )

    rows: list[dict[str, Any]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)

        rows.append(
            {
                "dataset_key": dataset_key,
                "dataset_root": str(root),
                "relative_path": str(relative_path),
                "file_name": path.name,
                "extension": path.suffix.lower(),
                "file_size_bytes": path.stat().st_size,
                "file_class": classify_file(path),
                "has_mask_keyword": file_has_mask_keyword(path),
            }
        )

    return pd.DataFrame(rows)


def summarize_inventory(inventory_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize inventory counts by dataset, extension, and file class.

    Parameters
    ----------
    inventory_df:
        File-level inventory.

    Returns
    -------
    pd.DataFrame
        Summary table.
    """
    if inventory_df.empty:
        return pd.DataFrame(
            columns=[
                "dataset_key",
                "extension",
                "file_class",
                "file_count",
                "total_size_bytes",
            ]
        )

    summary_df = (
        inventory_df
        .groupby(["dataset_key", "extension", "file_class"], dropna=False)
        .agg(
            file_count=("relative_path", "count"),
            total_size_bytes=("file_size_bytes", "sum"),
        )
        .reset_index()
        .sort_values(
            ["dataset_key", "file_count"],
            ascending=[True, False],
        )
    )

    return summary_df


def summarize_by_dataset_and_class(inventory_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a dataset-level summary by file class.

    Parameters
    ----------
    inventory_df:
        File-level inventory.

    Returns
    -------
    pd.DataFrame
        Dataset-by-file-class count table.
    """
    if inventory_df.empty:
        return pd.DataFrame()

    summary_df = (
        inventory_df
        .groupby(["dataset_key", "file_class"])
        .size()
        .reset_index(name="file_count")
        .pivot(index="dataset_key", columns="file_class", values="file_count")
        .fillna(0)
        .astype(int)
        .reset_index()
    )

    return summary_df


def get_candidate_mask_or_annotation_files(
    inventory_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return files that may be masks, segmentation labels, or annotations.

    Parameters
    ----------
    inventory_df:
        File-level inventory.

    Returns
    -------
    pd.DataFrame
        Candidate mask/annotation files.
    """
    if inventory_df.empty:
        return inventory_df.copy()

    candidate_mask = (
        inventory_df["file_class"].isin(
            ["possible_mask_image", "possible_annotation"]
        )
        | inventory_df["has_mask_keyword"]
    )

    return inventory_df.loc[candidate_mask].copy()


def inventory_registry_datasets(
    dataset_keys: list[str],
    registry_path: str | Path | None = None,
    save_reports: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Inventory selected datasets from the registry.

    Parameters
    ----------
    dataset_keys:
        Dataset keys from configs/data/kaggle_datasets.yaml.
    registry_path:
        Optional custom registry path.
    save_reports:
        If True, save CSV reports under reports/data_audit/.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        inventory_df, summary_df, candidate_df.
    """
    selected = select_datasets(
        dataset_keys=dataset_keys,
        registry_path=registry_path,
    )

    inventory_frames: list[pd.DataFrame] = []

    for dataset_key, metadata in selected.items():
        inventory_frames.append(
            inventory_dataset(
                dataset_key=dataset_key,
                local_dir=metadata["local_dir"],
            )
        )

    if inventory_frames:
        inventory_df = pd.concat(inventory_frames, ignore_index=True)
    else:
        inventory_df = pd.DataFrame()

    summary_df = summarize_inventory(inventory_df)
    candidate_df = get_candidate_mask_or_annotation_files(inventory_df)

    if save_reports:
        reports_dir = find_project_root() / "reports" / "data_audit"
        reports_dir.mkdir(parents=True, exist_ok=True)

        inventory_df.to_csv(
            reports_dir / "public_dataset_file_inventory.csv",
            index=False,
        )
        summary_df.to_csv(
            reports_dir / "public_dataset_file_summary.csv",
            index=False,
        )
        candidate_df.to_csv(
            reports_dir / "public_dataset_candidate_masks_annotations.csv",
            index=False,
        )

        dataset_class_summary_df = summarize_by_dataset_and_class(inventory_df)
        dataset_class_summary_df.to_csv(
            reports_dir / "public_dataset_class_summary.csv",
            index=False,
        )

    return inventory_df, summary_df, candidate_df