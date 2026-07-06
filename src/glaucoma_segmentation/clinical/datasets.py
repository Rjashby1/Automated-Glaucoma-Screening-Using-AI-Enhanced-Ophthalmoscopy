"""
Datasets for private clinical generalization evaluation.
"""

from __future__ import annotations

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
            frame = frame.loc[frame["mask_ready"].astype(bool)].copy()

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


__all__ = ["ClinicalDerivedMaskDataset"]
