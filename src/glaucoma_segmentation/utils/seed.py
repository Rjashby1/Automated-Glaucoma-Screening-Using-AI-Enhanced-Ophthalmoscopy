"""
Reproducibility helpers for glaucoma segmentation experiments.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass

import numpy as np
import torch


@dataclass(frozen=True)
class SeedConfig:
    """
    Summary of reproducibility settings applied to the current process.
    """

    seed: int
    deterministic: bool
    cudnn_benchmark: bool | None


def seed_everything(
    seed: int = 42,
    deterministic: bool = False,
    cudnn_benchmark: bool | None = None,
) -> SeedConfig:
    """
    Seed Python, NumPy, and PyTorch RNGs.

    Parameters
    ----------
    seed:
        Integer seed used across supported random-number generators.

    deterministic:
        If True, ask PyTorch to prefer deterministic algorithms when possible.
        This can make training slower and may warn for unsupported operations.

    cudnn_benchmark:
        Optional cuDNN benchmark setting. If None, benchmark is disabled when
        deterministic=True and otherwise left unchanged.

    Returns
    -------
    SeedConfig
        Record of the settings applied.
    """
    if not isinstance(seed, int):
        raise TypeError(f"seed must be an int, got {type(seed)!r}")

    os.environ["PYTHONHASHSEED"] = str(seed)

    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.use_deterministic_algorithms(True, warn_only=True)

    applied_cudnn_benchmark = cudnn_benchmark

    if hasattr(torch.backends, "cudnn"):
        if cudnn_benchmark is None and deterministic:
            torch.backends.cudnn.benchmark = False
            applied_cudnn_benchmark = False
        elif cudnn_benchmark is not None:
            torch.backends.cudnn.benchmark = cudnn_benchmark

        if deterministic:
            torch.backends.cudnn.deterministic = True

    return SeedConfig(
        seed=seed,
        deterministic=deterministic,
        cudnn_benchmark=applied_cudnn_benchmark,
    )


__all__ = ["SeedConfig", "seed_everything"]
