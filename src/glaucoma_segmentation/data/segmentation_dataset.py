"""
Manifest-driven PyTorch dataset for glaucoma segmentation.

Expected manifest columns:
- image_path
- mask_path
- split

Optional but supported columns:
- dataset_key
- source_dataset
- file_id
- split_group_id

Mask convention:
0 = background
1 = optic disc
2 = optic cup
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


EXPECTED_MASK_VALUES = {0, 1, 2}

Sample = dict[str, Any]
SampleTransform = Callable[[Sample], Sample]


def find_project_root(start: Path | None = None) -> Path:
    """
    Find the project root by walking upward until .git is found.
    """
    current = (start or Path.cwd()).resolve()

    for path in [current, *current.parents]:
        if (path / ".git").exists():
            return path

    raise RuntimeError(
        "Could not find project root. Run this from inside the Git repository."
    )


def resolve_project_path(path_value: str | Path, project_root: Path | None = None) -> Path:
    """
    Resolve a path that may be absolute or relative to the project root.
    """
    path = Path(path_value)

    if path.is_absolute():
        return path

    root = project_root or find_project_root()
    return root / path


def load_rgb_image(path: str | Path, image_size: tuple[int, int] | None = None) -> torch.Tensor:
    """
    Load an RGB image as a float tensor with shape (3, H, W), scaled to [0, 1].
    """
    with Image.open(path) as image:
        image = image.convert("RGB")

        if image_size is not None:
            image = image.resize(image_size, resample=Image.BILINEAR)

        array = np.asarray(image, dtype=np.float32) / 255.0

    tensor = torch.from_numpy(array).permute(2, 0, 1)

    return tensor


def load_mask(
    path: str | Path,
    image_size: tuple[int, int] | None = None,
    expected_values: set[int] | None = EXPECTED_MASK_VALUES,
) -> torch.Tensor:
    """
    Load an integer segmentation mask with shape (H, W).

    The mask is expected to already use:
    0 = background
    1 = optic disc
    2 = optic cup
    """
    with Image.open(path) as mask:
        mask = mask.convert("L")

        if image_size is not None:
            mask = mask.resize(image_size, resample=Image.NEAREST)

        array = np.asarray(mask, dtype=np.int64)

    unique_values = set(np.unique(array).tolist())

    if expected_values is not None and not unique_values.issubset(expected_values):
        raise ValueError(
            f"Unexpected mask values in {path}: {sorted(unique_values)}. "
            f"Expected values to be subset of {sorted(expected_values)}."
        )

    return torch.from_numpy(array).long()


class GlaucomaSegmentationDataset(Dataset):
    """
    PyTorch Dataset for manifest-driven optic disc/cup segmentation.

    Parameters
    ----------
    manifest_path:
        Path to a CSV manifest with image_path, mask_path, and split columns.

    split:
        Optional split filter, such as "train", "val", or "test".

    dataset_key:
        Optional dataset_key filter.

    source_dataset:
        Optional source_dataset filter.

    image_size:
        Optional resize size as (width, height). PIL uses this order.

    validate_paths:
        If True, verify all image and mask paths exist during initialization.

    validate_masks:
        If True, verify mask values are in {0, 1, 2} when each item is loaded
        and after optional transforms are applied.

    transform:
        Optional callable that receives and returns a sample dictionary. For
        segmentation augmentation, paired spatial transforms must apply the same
        geometry to image and mask, while photometric transforms should only
        modify the image.
    """

    required_columns = {"image_path", "mask_path"}

    def __init__(
        self,
        manifest_path: str | Path,
        split: str | None = None,
        dataset_key: str | None = None,
        source_dataset: str | None = None,
        image_size: tuple[int, int] | None = None,
        validate_paths: bool = True,
        validate_masks: bool = True,
        transform: SampleTransform | None = None,
    ) -> None:
        self.project_root = find_project_root()
        self.manifest_path = resolve_project_path(manifest_path, self.project_root)
        self.split = split
        self.dataset_key = dataset_key
        self.source_dataset = source_dataset
        self.image_size = image_size
        self.validate_paths = validate_paths
        self.validate_masks = validate_masks
        self.transform = transform

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        self.manifest = pd.read_csv(self.manifest_path)
        self._validate_manifest_columns()
        self.manifest = self._filter_manifest(self.manifest).reset_index(drop=True)

        if len(self.manifest) == 0:
            raise ValueError(
                "No rows remain after filtering manifest. "
                f"split={split!r}, dataset_key={dataset_key!r}, "
                f"source_dataset={source_dataset!r}"
            )

        if self.validate_paths:
            self._validate_paths_exist()

    def _validate_manifest_columns(self) -> None:
        missing = self.required_columns - set(self.manifest.columns)
        if missing:
            raise ValueError(
                f"Manifest {self.manifest_path} is missing required columns: "
                f"{sorted(missing)}"
            )

    def _filter_manifest(self, manifest: pd.DataFrame) -> pd.DataFrame:
        filtered = manifest.copy()

        if self.split is not None:
            if "split" not in filtered.columns:
                raise ValueError("Cannot filter by split because manifest has no split column.")
            filtered = filtered[filtered["split"] == self.split]

        if self.dataset_key is not None:
            if "dataset_key" not in filtered.columns:
                raise ValueError(
                    "Cannot filter by dataset_key because manifest has no dataset_key column."
                )
            filtered = filtered[filtered["dataset_key"] == self.dataset_key]

        if self.source_dataset is not None:
            if "source_dataset" not in filtered.columns:
                raise ValueError(
                    "Cannot filter by source_dataset because manifest has no source_dataset column."
                )
            filtered = filtered[filtered["source_dataset"] == self.source_dataset]

        return filtered

    def _validate_paths_exist(self) -> None:
        missing_paths: list[Path] = []

        for row in self.manifest.itertuples(index=False):
            image_path = resolve_project_path(row.image_path, self.project_root)
            mask_path = resolve_project_path(row.mask_path, self.project_root)

            if not image_path.exists():
                missing_paths.append(image_path)
            if not mask_path.exists():
                missing_paths.append(mask_path)

            if len(missing_paths) >= 10:
                break

        if missing_paths:
            preview = "\n".join(str(path) for path in missing_paths)
            raise FileNotFoundError(
                "Some image/mask paths listed in the manifest do not exist. "
                "First missing paths:\n"
                f"{preview}"
            )

    def _validate_sample_tensors(self, sample: Sample, context: str) -> None:
        if "image" not in sample or "mask" not in sample:
            raise KeyError(f"{context} sample must contain 'image' and 'mask' keys.")

        image = sample["image"]
        mask = sample["mask"]

        if not torch.is_tensor(image):
            raise TypeError(f"{context} image must be a torch.Tensor, got {type(image)!r}.")
        if not torch.is_tensor(mask):
            raise TypeError(f"{context} mask must be a torch.Tensor, got {type(mask)!r}.")

        if image.ndim != 3:
            raise ValueError(
                f"{context} image must have shape (C, H, W), got {tuple(image.shape)}."
            )
        if mask.ndim != 2:
            raise ValueError(
                f"{context} mask must have shape (H, W), got {tuple(mask.shape)}."
            )
        if image.shape[1:] != mask.shape:
            raise ValueError(
                f"{context} image and mask spatial dimensions do not match. "
                f"image={tuple(image.shape)}, mask={tuple(mask.shape)}."
            )

        if self.validate_masks:
            unique_values = set(torch.unique(mask.detach().cpu()).tolist())
            unique_values = {int(value) for value in unique_values}
            if not unique_values.issubset(EXPECTED_MASK_VALUES):
                raise ValueError(
                    f"{context} mask has unexpected values: {sorted(unique_values)}. "
                    f"Expected values to be subset of {sorted(EXPECTED_MASK_VALUES)}."
                )

    def __len__(self) -> int:
        return len(self.manifest)

    def __getitem__(self, index: int) -> Sample:
        row = self.manifest.iloc[index]

        image_path = resolve_project_path(row["image_path"], self.project_root)
        mask_path = resolve_project_path(row["mask_path"], self.project_root)

        image = load_rgb_image(image_path, image_size=self.image_size)
        mask = load_mask(
            mask_path,
            image_size=self.image_size,
            expected_values=EXPECTED_MASK_VALUES if self.validate_masks else None,
        )

        sample: Sample = {
            "image": image,
            "mask": mask,
            "image_path": str(image_path),
            "mask_path": str(mask_path),
        }

        for column in ["dataset_key", "source_dataset", "file_id", "split_group_id", "split"]:
            if column in row:
                sample[column] = row[column]

        self._validate_sample_tensors(sample, context="Loaded")

        if self.transform is not None:
            transformed = self.transform(sample)

            if transformed is None:
                raise ValueError("Dataset transform returned None; expected a sample dictionary.")
            if not isinstance(transformed, dict):
                raise TypeError(
                    "Dataset transform must return a sample dictionary, "
                    f"got {type(transformed)!r}."
                )

            sample = transformed

        sample["image"] = sample["image"].float()
        sample["mask"] = sample["mask"].long()

        self._validate_sample_tensors(sample, context="Transformed")

        return sample


__all__ = [
    "EXPECTED_MASK_VALUES",
    "GlaucomaSegmentationDataset",
    "Sample",
    "SampleTransform",
    "find_project_root",
    "load_mask",
    "load_rgb_image",
    "resolve_project_path",
]
