"""Utilities for leakage-aware train/validation/test split assignment.

This module keeps split logic out of notebooks so the same split strategy can be
reused by later training, evaluation, and reporting workflows.

The primary design goal is group-level splitting: all records with the same
``split_group_id`` must remain in the same split to avoid leakage between train,
validation, and test sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_SPLIT_ORDER: tuple[str, str, str] = ("train", "val", "test")


@dataclass(frozen=True)
class SplitConfig:
    """Configuration for grouped train/validation/test split assignment.

    Parameters
    ----------
    train_size:
        Proportion of groups assigned to the training split.
    val_size:
        Proportion of groups assigned to the validation split.
    test_size:
        Proportion of groups assigned to the test split.
    group_col:
        Column used to prevent leakage. Each unique group is assigned to exactly
        one split.
    split_col:
        Name of the output split column.
    seed:
        Random seed used for deterministic group shuffling.
    """

    train_size: float = 0.70
    val_size: float = 0.15
    test_size: float = 0.15
    group_col: str = "split_group_id"
    split_col: str = "split"
    seed: int = 42

    def __post_init__(self) -> None:
        sizes = [self.train_size, self.val_size, self.test_size]

        if any(size < 0 for size in sizes):
            raise ValueError("Split sizes must be nonnegative.")

        total = sum(sizes)
        if not np.isclose(total, 1.0):
            raise ValueError(
                f"Split sizes must sum to 1.0. Received {total:.6f}."
            )

        if not self.group_col:
            raise ValueError("group_col must be a non-empty string.")

        if not self.split_col:
            raise ValueError("split_col must be a non-empty string.")


def _validate_manifest_for_grouped_split(
    manifest_df: pd.DataFrame,
    *,
    group_col: str,
) -> None:
    """Validate that a manifest can be split by group."""

    if not isinstance(manifest_df, pd.DataFrame):
        raise TypeError("manifest_df must be a pandas DataFrame.")

    if group_col not in manifest_df.columns:
        raise ValueError(
            f"Grouped split requires column '{group_col}', but it was not found."
        )

    missing_groups = manifest_df[group_col].isna().sum()
    if missing_groups:
        raise ValueError(
            f"Grouped split requires non-missing group IDs. "
            f"Found {missing_groups} missing values in '{group_col}'."
        )


def _calculate_group_split_counts(
    n_groups: int,
    *,
    train_size: float,
    val_size: float,
    test_size: float,
) -> dict[str, int]:
    """Calculate integer group counts for train/val/test splits.

    The function keeps the requested proportions as closely as possible while
    ensuring that every split receives at least one group when there are enough
    groups to do so.
    """

    if n_groups < 0:
        raise ValueError("n_groups must be nonnegative.")

    if n_groups == 0:
        return {"train": 0, "val": 0, "test": 0}

    if n_groups == 1:
        return {"train": 1, "val": 0, "test": 0}

    if n_groups == 2:
        return {"train": 1, "val": 0, "test": 1}

    n_train = int(round(train_size * n_groups))
    n_val = int(round(val_size * n_groups))
    n_test = n_groups - n_train - n_val

    counts = {"train": n_train, "val": n_val, "test": n_test}

    # With at least three groups, keep all three splits represented.
    for split_name in DEFAULT_SPLIT_ORDER:
        if counts[split_name] < 1:
            counts[split_name] = 1

    # If rounding/minimum enforcement over-allocated groups, remove from the
    # largest split until the total is valid.
    while sum(counts.values()) > n_groups:
        largest_split = max(counts, key=counts.get)
        if counts[largest_split] <= 1:
            break
        counts[largest_split] -= 1

    # If rounding under-allocated groups, add remaining groups to train first.
    while sum(counts.values()) < n_groups:
        counts["train"] += 1

    # The test count is the balancing count after train/val adjustments.
    counts["test"] = n_groups - counts["train"] - counts["val"]

    if counts["test"] < 1:
        if counts["train"] >= counts["val"] and counts["train"] > 1:
            counts["train"] -= 1
        elif counts["val"] > 1:
            counts["val"] -= 1
        counts["test"] = n_groups - counts["train"] - counts["val"]

    return counts


def assign_grouped_splits(
    manifest_df: pd.DataFrame,
    *,
    config: SplitConfig | None = None,
    group_col: str | None = None,
    split_col: str | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """Assign leakage-aware train/validation/test splits by group.

    Parameters
    ----------
    manifest_df:
        Manifest with one row per segmentation record.
    config:
        SplitConfig controlling proportions, group column, split column, and seed.
    group_col:
        Optional override for the grouping column.
    split_col:
        Optional override for the output split column.
    seed:
        Optional override for the deterministic shuffle seed.

    Returns
    -------
    pandas.DataFrame
        Copy of ``manifest_df`` with a split column added.
    """

    config = config or SplitConfig()
    group_col = group_col or config.group_col
    split_col = split_col or config.split_col
    seed = config.seed if seed is None else seed

    _validate_manifest_for_grouped_split(manifest_df, group_col=group_col)

    output_df = manifest_df.copy()

    if output_df.empty:
        output_df[split_col] = pd.Series(dtype=str)
        return output_df

    group_df = (
        output_df[[group_col]]
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(columns={group_col: "group_id"})
    )

    rng = np.random.default_rng(seed)
    shuffled_positions = rng.permutation(len(group_df))
    group_df = group_df.iloc[shuffled_positions].reset_index(drop=True)

    counts = _calculate_group_split_counts(
        len(group_df),
        train_size=config.train_size,
        val_size=config.val_size,
        test_size=config.test_size,
    )

    split_labels = (
        ["train"] * counts["train"]
        + ["val"] * counts["val"]
        + ["test"] * counts["test"]
    )

    if len(split_labels) != len(group_df):
        raise RuntimeError(
            "Internal split assignment error: split label count does not match "
            "number of groups."
        )

    group_df[split_col] = split_labels

    split_map = dict(zip(group_df["group_id"], group_df[split_col], strict=True))
    output_df[split_col] = output_df[group_col].map(split_map)

    missing_splits = output_df[split_col].isna().sum()
    if missing_splits:
        raise RuntimeError(
            f"Internal split assignment error: {missing_splits} records did not "
            "receive a split."
        )

    return output_df


def check_group_leakage(
    manifest_df: pd.DataFrame,
    *,
    group_col: str = "split_group_id",
    split_col: str = "split",
) -> pd.DataFrame:
    """Return groups that appear in more than one split.

    An empty returned DataFrame means no group-level leakage was found.
    """

    if group_col not in manifest_df.columns:
        raise ValueError(f"Column '{group_col}' was not found.")

    if split_col not in manifest_df.columns:
        raise ValueError(f"Column '{split_col}' was not found.")

    leakage_df = (
        manifest_df.groupby(group_col, dropna=False)[split_col]
        .agg(
            n_splits=lambda values: values.dropna().nunique(),
            splits=lambda values: ", ".join(sorted(values.dropna().astype(str).unique())),
            n_records="size",
        )
        .reset_index()
    )

    leakage_df = leakage_df[leakage_df["n_splits"] > 1].reset_index(drop=True)

    return leakage_df


def split_summary(
    manifest_df: pd.DataFrame,
    *,
    split_col: str = "split",
    group_col: str | None = "split_group_id",
    split_order: Iterable[str] = DEFAULT_SPLIT_ORDER,
) -> pd.DataFrame:
    """Summarize records and groups by split."""

    if split_col not in manifest_df.columns:
        raise ValueError(f"Column '{split_col}' was not found.")

    if group_col is not None and group_col not in manifest_df.columns:
        raise ValueError(f"Column '{group_col}' was not found.")

    summary_df = (
        manifest_df.groupby(split_col, dropna=False)
        .size()
        .reset_index(name="n_records")
    )

    if group_col is not None:
        group_counts = (
            manifest_df.groupby(split_col, dropna=False)[group_col]
            .nunique()
            .reset_index(name="n_groups")
        )
        summary_df = summary_df.merge(group_counts, on=split_col, how="left")
    else:
        summary_df["n_groups"] = pd.NA

    total_records = int(summary_df["n_records"].sum())
    summary_df["record_fraction"] = (
        summary_df["n_records"] / total_records if total_records else 0.0
    )

    ordered_splits = list(split_order)
    summary_df[split_col] = pd.Categorical(
        summary_df[split_col],
        categories=ordered_splits,
        ordered=True,
    )

    summary_df = (
        summary_df.sort_values(split_col)
        .reset_index(drop=True)
    )

    summary_df[split_col] = summary_df[split_col].astype(str)

    return summary_df


__all__ = [
    "SplitConfig",
    "assign_grouped_splits",
    "check_group_leakage",
    "split_summary",
]