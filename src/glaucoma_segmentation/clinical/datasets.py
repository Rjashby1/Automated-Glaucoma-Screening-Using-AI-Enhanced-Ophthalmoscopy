"""Datasets and split helpers for private clinical generalization evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


def _pil_resampling(name: str) -> int:
    """Return a Pillow resampling constant compatible across Pillow versions."""
    if hasattr(Image, "Resampling"):
        return getattr(Image.Resampling, name)

    return getattr(Image, name)


def _as_bool_series(values: pd.Series) -> pd.Series:
    """Convert a pandas Series to boolean values in a tolerant way."""
    if pd.api.types.is_bool_dtype(values):
        return values.astype(bool)

    if pd.api.types.is_numeric_dtype(values):
        return values.fillna(0).astype(int).astype(bool)

    normalized = values.astype(str).str.strip().str.lower()
    return normalized.isin({"1", "true", "t", "yes", "y"})


def _normalize_eye_value(value: object) -> str:
    """Normalize clinical eye labels for aggregate summaries."""
    normalized = str(value).strip().upper()

    if normalized in {"OD", "RIGHT", "R"}:
        return "OD"

    if normalized in {"OS", "LEFT", "L"}:
        return "OS"

    return "unknown"


def _validate_fraction_values(train_fractions: Iterable[float]) -> tuple[float, ...]:
    """Validate and normalize clinical adaptation train fractions."""
    fractions = tuple(float(value) for value in train_fractions)

    if not fractions:
        raise ValueError("At least one clinical train fraction is required.")

    for fraction in fractions:
        if not 0.0 < fraction < 1.0:
            raise ValueError(
                "Clinical train fractions must be strictly between 0 and 1. "
                f"Received {fraction!r}."
            )

    return fractions


class ClinicalDerivedMaskDataset(Dataset):
    """
    Dataset for PSD-derived clinical clean images and label masks.

    Expected mask convention:
    0 = background
    1 = optic disc
    2 = optic cup
    """

    required_columns = {
        "sample_hash",
        "patient_hash",
        "eye",
        "mask_ready",
        "clean_image_private_path",
        "derived_mask_private_path",
    }

    def __init__(
        self,
        manifest: pd.DataFrame,
        *,
        project_root: Path,
        image_size: tuple[int, int] = (256, 256),
        require_mask_ready: bool = True,
        validate_paths: bool = True,
    ) -> None:
        missing_columns = sorted(self.required_columns - set(manifest.columns))
        if missing_columns:
            raise ValueError(f"Clinical manifest is missing required columns: {missing_columns}")

        self.project_root = Path(project_root).resolve()
        self.image_size = tuple(image_size)

        frame = manifest.copy()

        if require_mask_ready:
            frame = frame.loc[_as_bool_series(frame["mask_ready"])].copy()

        frame = frame.reset_index(drop=True)

        if frame.empty:
            raise ValueError("ClinicalDerivedMaskDataset received zero rows after filtering.")

        if validate_paths:
            missing_paths: list[str] = []

            for _, row in frame.iterrows():
                for column in ["clean_image_private_path", "derived_mask_private_path"]:
                    path = self.project_root / str(row[column])

                    if not path.exists():
                        missing_paths.append(str(path.relative_to(self.project_root)))

            if missing_paths:
                preview = missing_paths[:10]
                raise FileNotFoundError(
                    "Missing clinical derived dataset paths. "
                    f"Preview={preview}; total_missing={len(missing_paths)}"
                )

        self.frame = frame

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> dict[str, Any]:
        row = self.frame.iloc[index]

        image_path = self.project_root / str(row["clean_image_private_path"])
        mask_path = self.project_root / str(row["derived_mask_private_path"])

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize(self.image_size, resample=_pil_resampling("BILINEAR"))
            image_array = np.asarray(image, dtype=np.float32) / 255.0

        with Image.open(mask_path) as mask:
            mask = mask.convert("L")
            mask = mask.resize(self.image_size, resample=_pil_resampling("NEAREST"))
            mask_array = np.asarray(mask, dtype=np.int64)
            mask_array = np.clip(mask_array, 0, 2)

        image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).contiguous().float()
        mask_tensor = torch.from_numpy(mask_array).contiguous().long()

        return {
            "image": image_tensor,
            "mask": mask_tensor,
            "sample_hash": str(row["sample_hash"]),
            "patient_hash": str(row["patient_hash"]),
            "eye": str(row["eye"]),
        }


def make_grouped_clinical_adaptation_splits(
    manifest: pd.DataFrame,
    *,
    group_column: str = "patient_hash",
    train_fractions: Iterable[float] = (0.25, 0.50, 0.75),
    seed: int = 42,
    mask_ready_only: bool = True,
) -> pd.DataFrame:
    """
    Create deterministic row-level clinical adaptation splits by patient/encounter group.

    The returned frame is intended to remain private because it may contain
    patient/group hashes and sample hashes. Use summarize_clinical_adaptation_splits
    to produce public-safe aggregate split summaries.

    Parameters
    ----------
    manifest:
        Clinical manifest containing at least group_column, sample_hash, eye, and
        mask_ready.
    group_column:
        Column used to prevent leakage between clinical adaptation training and
        held-out clinical evaluation. The default is patient_hash.
    train_fractions:
        Fractions of unique patient/encounter groups assigned to clinical
        adaptation training. The remaining groups are held out for evaluation.
    seed:
        Deterministic random seed used to shuffle groups.
    mask_ready_only:
        If True, create splits only from rows with mask_ready == True.
    """
    required_columns = {group_column, "sample_hash", "eye", "mask_ready"}
    missing_columns = sorted(required_columns - set(manifest.columns))
    if missing_columns:
        raise ValueError(f"Clinical split manifest is missing required columns: {missing_columns}")

    fractions = _validate_fraction_values(train_fractions)

    frame = manifest.copy()
    frame["source_row_index"] = np.arange(len(frame), dtype=int)

    if mask_ready_only:
        frame = frame.loc[_as_bool_series(frame["mask_ready"])].copy()

    frame[group_column] = frame[group_column].astype(str)
    frame["sample_hash"] = frame["sample_hash"].astype(str)
    frame["eye"] = frame["eye"].map(_normalize_eye_value)

    if frame.empty:
        raise ValueError("No clinical rows available for adaptation split creation.")

    group_values = np.array(sorted(frame[group_column].dropna().astype(str).unique()))

    if len(group_values) < 2:
        raise ValueError(
            "At least two unique clinical patient/encounter groups are required "
            "to create train/evaluation splits."
        )

    rng = np.random.default_rng(seed)
    shuffled_groups = group_values.copy()
    rng.shuffle(shuffled_groups)

    records: list[dict[str, object]] = []

    for fraction in fractions:
        train_group_count = int(round(len(shuffled_groups) * fraction))
        train_group_count = max(1, min(train_group_count, len(shuffled_groups) - 1))

        train_groups = set(shuffled_groups[:train_group_count].tolist())
        experiment_name = f"clinical_train_{int(round(fraction * 100)):02d}pct"

        assigned = frame.copy()
        assigned["experiment_name"] = experiment_name
        assigned["clinical_train_fraction"] = fraction
        assigned["clinical_eval_fraction"] = 1.0 - fraction
        assigned["split"] = np.where(
            assigned[group_column].isin(train_groups),
            "clinical_train",
            "clinical_eval",
        )
        assigned["group_column"] = group_column
        assigned["group_id"] = assigned[group_column].astype(str)

        for _, row in assigned.iterrows():
            records.append(
                {
                    "experiment_name": str(row["experiment_name"]),
                    "clinical_train_fraction": float(row["clinical_train_fraction"]),
                    "clinical_eval_fraction": float(row["clinical_eval_fraction"]),
                    "split": str(row["split"]),
                    "source_row_index": int(row["source_row_index"]),
                    "sample_hash": str(row["sample_hash"]),
                    "group_column": str(row["group_column"]),
                    "group_id": str(row["group_id"]),
                    "eye": str(row["eye"]),
                }
            )

    split_frame = pd.DataFrame.from_records(records)

    expected_splits = {"clinical_train", "clinical_eval"}
    observed_splits = set(split_frame["split"].unique())
    if observed_splits != expected_splits:
        raise RuntimeError(
            "Clinical adaptation split creation failed to produce both train and "
            f"evaluation rows. Observed splits={sorted(observed_splits)}."
        )

    return split_frame.sort_values(
        ["clinical_train_fraction", "split", "group_id", "source_row_index"]
    ).reset_index(drop=True)


def summarize_clinical_adaptation_splits(split_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize clinical adaptation splits without exposing patient/group hashes.

    The returned frame is public-safe as long as the input split names and
    aggregate counts are acceptable to disclose. It does not include sample
    hashes, patient hashes, group IDs, or raw paths.
    """
    required_columns = {
        "experiment_name",
        "clinical_train_fraction",
        "clinical_eval_fraction",
        "split",
        "group_id",
        "eye",
    }
    missing_columns = sorted(required_columns - set(split_frame.columns))
    if missing_columns:
        raise ValueError(f"Clinical adaptation split frame is missing columns: {missing_columns}")

    records: list[dict[str, object]] = []

    for experiment_name, experiment_frame in split_frame.groupby("experiment_name", sort=True):
        train_fraction = float(experiment_frame["clinical_train_fraction"].iloc[0])
        eval_fraction = float(experiment_frame["clinical_eval_fraction"].iloc[0])

        train_frame = experiment_frame.loc[experiment_frame["split"] == "clinical_train"].copy()
        eval_frame = experiment_frame.loc[experiment_frame["split"] == "clinical_eval"].copy()

        def eye_count(frame: pd.DataFrame, eye_value: str) -> int:
            return int((frame["eye"].map(_normalize_eye_value) == eye_value).sum())

        total_rows = int(len(experiment_frame))
        total_groups = int(experiment_frame["group_id"].nunique())
        train_rows = int(len(train_frame))
        eval_rows = int(len(eval_frame))
        train_groups = int(train_frame["group_id"].nunique())
        eval_groups = int(eval_frame["group_id"].nunique())

        records.append(
            {
                "experiment_name": str(experiment_name),
                "clinical_train_fraction_requested": train_fraction,
                "clinical_eval_fraction_requested": eval_fraction,
                "total_rows": total_rows,
                "total_groups": total_groups,
                "clinical_train_rows": train_rows,
                "clinical_eval_rows": eval_rows,
                "clinical_train_groups": train_groups,
                "clinical_eval_groups": eval_groups,
                "clinical_train_row_fraction_actual": train_rows / total_rows if total_rows else np.nan,
                "clinical_eval_row_fraction_actual": eval_rows / total_rows if total_rows else np.nan,
                "clinical_train_group_fraction_actual": (
                    train_groups / total_groups if total_groups else np.nan
                ),
                "clinical_eval_group_fraction_actual": (
                    eval_groups / total_groups if total_groups else np.nan
                ),
                "clinical_train_od_rows": eye_count(train_frame, "OD"),
                "clinical_train_os_rows": eye_count(train_frame, "OS"),
                "clinical_train_unknown_eye_rows": eye_count(train_frame, "unknown"),
                "clinical_eval_od_rows": eye_count(eval_frame, "OD"),
                "clinical_eval_os_rows": eye_count(eval_frame, "OS"),
                "clinical_eval_unknown_eye_rows": eye_count(eval_frame, "unknown"),
                "contains_sample_hashes": False,
                "contains_patient_hashes": False,
                "contains_group_ids": False,
                "contains_raw_paths": False,
            }
        )

    return pd.DataFrame.from_records(records).sort_values(
        "clinical_train_fraction_requested"
    ).reset_index(drop=True)


def filter_manifest_for_clinical_split(
    manifest: pd.DataFrame,
    split_frame: pd.DataFrame,
    *,
    experiment_name: str,
    split_name: str,
) -> pd.DataFrame:
    """
    Return manifest rows assigned to one clinical adaptation split.

    This helper is intended for private notebook use. The returned frame may
    still contain patient hashes and private derived image/mask paths inherited
    from the clinical manifest.
    """
    valid_split_names = {"clinical_train", "clinical_eval"}
    if split_name not in valid_split_names:
        raise ValueError(
            f"split_name must be one of {sorted(valid_split_names)}, got {split_name!r}."
        )

    required_split_columns = {"experiment_name", "split", "source_row_index"}
    missing_split_columns = sorted(required_split_columns - set(split_frame.columns))
    if missing_split_columns:
        raise ValueError(
            f"Clinical split frame is missing required columns: {missing_split_columns}"
        )

    indexed_manifest = manifest.copy()
    indexed_manifest["source_row_index"] = np.arange(len(indexed_manifest), dtype=int)

    selected = split_frame.loc[
        (split_frame["experiment_name"] == experiment_name)
        & (split_frame["split"] == split_name),
        ["source_row_index", "experiment_name", "clinical_train_fraction", "clinical_eval_fraction", "split"],
    ].copy()

    if selected.empty:
        raise ValueError(
            f"No rows found for experiment_name={experiment_name!r}, split_name={split_name!r}."
        )

    filtered = indexed_manifest.merge(
        selected,
        on="source_row_index",
        how="inner",
        validate="one_to_one",
    )

    return filtered.reset_index(drop=True)


__all__ = [
    "ClinicalDerivedMaskDataset",
    "filter_manifest_for_clinical_split",
    "make_grouped_clinical_adaptation_splits",
    "summarize_clinical_adaptation_splits",
]
