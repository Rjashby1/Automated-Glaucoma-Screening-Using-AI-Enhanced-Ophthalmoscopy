"""
DataLoader utilities for glaucoma segmentation.

This module builds train/validation/test PyTorch DataLoaders from the
manifest-driven GlaucomaSegmentationDataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from glaucoma_segmentation.data.segmentation_dataset import GlaucomaSegmentationDataset


DEFAULT_MANIFEST_PATH = (
    "data/processed/manifests/combined_segmentation_manifest_with_splits.csv"
)


@dataclass
class SegmentationDataLoaders:
    """
    Container for train/validation/test DataLoaders.
    """

    train: DataLoader | None = None
    val: DataLoader | None = None
    test: DataLoader | None = None


@dataclass
class SegmentationDatasets:
    """
    Container for train/validation/test Datasets.
    """

    train: GlaucomaSegmentationDataset | None = None
    val: GlaucomaSegmentationDataset | None = None
    test: GlaucomaSegmentationDataset | None = None


def make_segmentation_dataset(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    split: str = "train",
    dataset_key: str | None = None,
    source_dataset: str | None = None,
    image_size: tuple[int, int] | None = None,
    validate_paths: bool = True,
    validate_masks: bool = True,
) -> GlaucomaSegmentationDataset:
    """
    Create one segmentation dataset for a requested split.
    """
    return GlaucomaSegmentationDataset(
        manifest_path=manifest_path,
        split=split,
        dataset_key=dataset_key,
        source_dataset=source_dataset,
        image_size=image_size,
        validate_paths=validate_paths,
        validate_masks=validate_masks,
    )


def make_segmentation_datasets(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    splits: tuple[str, ...] = ("train", "val", "test"),
    dataset_key: str | None = None,
    source_dataset: str | None = None,
    image_size: tuple[int, int] | None = None,
    validate_paths: bool = True,
    validate_masks: bool = True,
) -> SegmentationDatasets:
    """
    Create train/validation/test segmentation datasets.
    """
    datasets: dict[str, GlaucomaSegmentationDataset] = {}

    for split in splits:
        datasets[split] = make_segmentation_dataset(
            manifest_path=manifest_path,
            split=split,
            dataset_key=dataset_key,
            source_dataset=source_dataset,
            image_size=image_size,
            validate_paths=validate_paths,
            validate_masks=validate_masks,
        )

    return SegmentationDatasets(
        train=datasets.get("train"),
        val=datasets.get("val"),
        test=datasets.get("test"),
    )


def make_segmentation_dataloader(
    dataset: GlaucomaSegmentationDataset,
    batch_size: int = 4,
    shuffle: bool = False,
    num_workers: int = 0,
    pin_memory: bool | None = None,
    drop_last: bool = False,
) -> DataLoader:
    """
    Create one PyTorch DataLoader from a segmentation dataset.
    """
    if pin_memory is None:
        pin_memory = torch.cuda.is_available()

    persistent_workers = num_workers > 0

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
        persistent_workers=persistent_workers,
    )


def make_segmentation_dataloaders(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    batch_size: int = 4,
    image_size: tuple[int, int] | None = None,
    dataset_key: str | None = None,
    source_dataset: str | None = None,
    num_workers: int = 0,
    validate_paths: bool = True,
    validate_masks: bool = True,
    pin_memory: bool | None = None,
) -> SegmentationDataLoaders:
    """
    Create train/validation/test DataLoaders from a manifest.

    The train loader shuffles. Validation and test loaders do not.
    """
    datasets = make_segmentation_datasets(
        manifest_path=manifest_path,
        splits=("train", "val", "test"),
        dataset_key=dataset_key,
        source_dataset=source_dataset,
        image_size=image_size,
        validate_paths=validate_paths,
        validate_masks=validate_masks,
    )

    train_loader = None
    val_loader = None
    test_loader = None

    if datasets.train is not None:
        train_loader = make_segmentation_dataloader(
            datasets.train,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=False,
        )

    if datasets.val is not None:
        val_loader = make_segmentation_dataloader(
            datasets.val,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=False,
        )

    if datasets.test is not None:
        test_loader = make_segmentation_dataloader(
            datasets.test,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=False,
        )

    return SegmentationDataLoaders(
        train=train_loader,
        val=val_loader,
        test=test_loader,
    )


__all__ = [
    "DEFAULT_MANIFEST_PATH",
    "SegmentationDataLoaders",
    "SegmentationDatasets",
    "make_segmentation_dataloader",
    "make_segmentation_dataloaders",
    "make_segmentation_dataset",
    "make_segmentation_datasets",
]