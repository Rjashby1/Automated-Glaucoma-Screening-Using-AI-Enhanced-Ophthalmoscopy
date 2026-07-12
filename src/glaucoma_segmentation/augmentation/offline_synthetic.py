"""
Deterministic virtual synthetic expansion for segmentation training.

This module supports synthetic add-back experiments without materializing
augmented images or masks to disk. Instead, it wraps an existing training
dataset and exposes a larger virtual dataset:

- original samples are returned unchanged
- synthetic samples are generated on demand from original samples
- synthetic transforms are deterministic for a fixed base seed, source index,
  strategy name, and copy index
- validation and test datasets should remain unwrapped

Mask convention:
0 = background
1 = optic disc
2 = optic cup
"""

from __future__ import annotations

import random
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Iterator, Mapping, Sequence

import numpy as np
import torch
from torch.utils.data import Dataset

from glaucoma_segmentation.augmentation.online_presets import (
    build_online_augmentation_preset,
    supported_online_augmentation_presets,
)


Sample = dict[str, Any]


@dataclass(frozen=True)
class SyntheticExpansionSpec:
    """
    Configuration for one virtual synthetic add-back strategy.

    Parameters
    ----------
    strategy_name:
        Name of an augmentation strategy supported by online_presets.py.

    copy_count:
        Number of deterministic synthetic copies to expose per original sample.
    """

    strategy_name: str
    copy_count: int = 1

    def __post_init__(self) -> None:
        supported = set(supported_online_augmentation_presets(include_combinations=True))

        if self.strategy_name not in supported:
            raise ValueError(
                f"Unsupported strategy_name={self.strategy_name!r}. "
                f"Supported strategies: {sorted(supported)}"
            )

        if self.strategy_name == "none":
            raise ValueError(
                "SyntheticExpansionSpec should use an actual augmentation strategy, "
                "not 'none'. Keep original samples through include_original=True."
            )

        if not isinstance(self.copy_count, int):
            raise TypeError(f"copy_count must be an int, got {type(self.copy_count)!r}")

        if self.copy_count < 1:
            raise ValueError("copy_count must be at least 1.")


@dataclass(frozen=True)
class VirtualSyntheticIndex:
    """
    Mapping from a virtual dataset index back to its source sample.
    """

    virtual_index: int
    source_index: int
    is_synthetic: bool
    strategy_name: str
    copy_index: int
    synthetic_seed: int

    def to_dict(self) -> dict[str, int | bool | str]:
        """Return the mapping as a plain dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class VirtualSyntheticExpansionSummary:
    """
    Lightweight summary of a virtual synthetic expansion dataset.
    """

    base_rows: int
    original_rows_exposed: int
    synthetic_rows_exposed: int
    total_rows_exposed: int
    base_seed: int
    include_original: bool
    strategies: str
    copy_counts: str

    def to_dict(self) -> dict[str, int | bool | str]:
        """Return the summary as a plain dictionary."""
        return asdict(self)


class VirtualSyntheticExpansionDataset(Dataset):
    """
    Dataset wrapper for deterministic synthetic add-back training.

    The wrapper does not save augmented files. Synthetic samples are generated
    on demand by applying the requested augmentation strategy to the source
    sample under a deterministic temporary RNG seed.

    This wrapper is intended for training splits only. Validation and test
    datasets should remain original/unaltered.
    """

    def __init__(
        self,
        base_dataset: Dataset,
        specs: Sequence[SyntheticExpansionSpec],
        *,
        base_seed: int = 42,
        include_original: bool = True,
        add_metadata: bool = True,
    ) -> None:
        """
        Build a virtual synthetic expansion wrapper.

        Parameters
        ----------
        base_dataset:
            Original dataset to wrap, normally the training split dataset.

        specs:
            One or more synthetic expansion specifications.

        base_seed:
            Base seed used to derive per-sample deterministic augmentation seeds.

        include_original:
            If True, expose the original samples before synthetic samples.

        add_metadata:
            If True, add simple synthetic-traceability fields to each returned
            sample. These fields are safe for PyTorch default collation.
        """
        if not isinstance(base_seed, int):
            raise TypeError(f"base_seed must be an int, got {type(base_seed)!r}")

        if len(specs) == 0:
            raise ValueError("At least one SyntheticExpansionSpec is required.")

        if len(base_dataset) == 0:
            raise ValueError("base_dataset must contain at least one sample.")

        self.base_dataset = base_dataset
        self.specs = tuple(specs)
        self.base_seed = base_seed
        self.include_original = include_original
        self.add_metadata = add_metadata

        self._base_len = len(base_dataset)
        self._transforms = {
            spec.strategy_name: build_online_augmentation_preset(spec.strategy_name)
            for spec in self.specs
        }

    @property
    def base_len(self) -> int:
        """Number of rows in the wrapped base dataset."""
        return self._base_len

    @property
    def original_rows_exposed(self) -> int:
        """Number of original rows exposed by this wrapper."""
        return self._base_len if self.include_original else 0

    @property
    def synthetic_rows_exposed(self) -> int:
        """Number of synthetic rows exposed by this wrapper."""
        return self._base_len * sum(spec.copy_count for spec in self.specs)

    def __len__(self) -> int:
        """Return total number of virtual rows exposed."""
        return self.original_rows_exposed + self.synthetic_rows_exposed

    def __getitem__(self, index: int) -> Sample:
        """
        Return an original or deterministic synthetic sample.
        """
        mapped = self.map_index(index)
        sample = _clone_sample(self.base_dataset[mapped.source_index])

        if mapped.is_synthetic:
            transform = self._transforms[mapped.strategy_name]
            if transform is None:
                raise RuntimeError(
                    f"Synthetic strategy {mapped.strategy_name!r} unexpectedly "
                    "resolved to None."
                )

            with temporary_rng_seed(mapped.synthetic_seed):
                sample = transform(sample)

        if self.add_metadata:
            sample = _with_virtual_metadata(sample, mapped)

        return sample

    def map_index(self, index: int) -> VirtualSyntheticIndex:
        """
        Map a virtual dataset index to source-row and synthetic metadata.
        """
        if not isinstance(index, int):
            raise TypeError(f"index must be an int, got {type(index)!r}")

        total_len = len(self)
        if index < 0:
            index = total_len + index

        if index < 0 or index >= total_len:
            raise IndexError(f"index {index} out of range for dataset of length {total_len}")

        if self.include_original and index < self._base_len:
            return VirtualSyntheticIndex(
                virtual_index=index,
                source_index=index,
                is_synthetic=False,
                strategy_name="none",
                copy_index=-1,
                synthetic_seed=-1,
            )

        synthetic_offset = index - self.original_rows_exposed

        block_start = 0
        for spec in self.specs:
            block_len = self._base_len * spec.copy_count
            block_end = block_start + block_len

            if block_start <= synthetic_offset < block_end:
                within_block = synthetic_offset - block_start
                copy_index = within_block // self._base_len
                source_index = within_block % self._base_len
                synthetic_seed = deterministic_synthetic_seed(
                    base_seed=self.base_seed,
                    source_index=source_index,
                    strategy_name=spec.strategy_name,
                    copy_index=copy_index,
                )

                return VirtualSyntheticIndex(
                    virtual_index=index,
                    source_index=source_index,
                    is_synthetic=True,
                    strategy_name=spec.strategy_name,
                    copy_index=copy_index,
                    synthetic_seed=synthetic_seed,
                )

            block_start = block_end

        raise RuntimeError("Failed to map virtual index; this should be unreachable.")

    def summary(self) -> VirtualSyntheticExpansionSummary:
        """
        Return a lightweight summary of the virtual expansion plan.
        """
        return VirtualSyntheticExpansionSummary(
            base_rows=self._base_len,
            original_rows_exposed=self.original_rows_exposed,
            synthetic_rows_exposed=self.synthetic_rows_exposed,
            total_rows_exposed=len(self),
            base_seed=self.base_seed,
            include_original=self.include_original,
            strategies=";".join(spec.strategy_name for spec in self.specs),
            copy_counts=";".join(str(spec.copy_count) for spec in self.specs),
        )

    def index_preview(self, n: int = 10) -> list[dict[str, int | bool | str]]:
        """
        Return a small preview of virtual-index mappings.

        This is useful for notebook QA and lightweight CSV summaries.
        """
        if n < 0:
            raise ValueError("n must be non-negative.")

        preview_count = min(n, len(self))
        return [self.map_index(index).to_dict() for index in range(preview_count)]


def build_virtual_synthetic_expansion_dataset(
    base_dataset: Dataset,
    strategy_names: str | Sequence[str],
    *,
    copy_count: int = 1,
    base_seed: int = 42,
    include_original: bool = True,
    add_metadata: bool = True,
) -> VirtualSyntheticExpansionDataset:
    """
    Convenience builder for virtual synthetic expansion datasets.

    Parameters
    ----------
    base_dataset:
        Dataset to wrap.

    strategy_names:
        One strategy name or a sequence of strategy names.

    copy_count:
        Number of deterministic synthetic copies per original sample for each
        strategy.

    base_seed:
        Base seed used for deterministic synthetic generation.

    include_original:
        Whether to include original samples in addition to synthetic samples.

    add_metadata:
        Whether to add simple traceability fields to returned samples.

    Returns
    -------
    VirtualSyntheticExpansionDataset
        Wrapped dataset exposing original plus virtual synthetic samples.
    """
    if isinstance(strategy_names, str):
        normalized_strategy_names = [strategy_names]
    else:
        normalized_strategy_names = list(strategy_names)

    specs = [
        SyntheticExpansionSpec(strategy_name=strategy_name, copy_count=copy_count)
        for strategy_name in normalized_strategy_names
    ]

    return VirtualSyntheticExpansionDataset(
        base_dataset=base_dataset,
        specs=specs,
        base_seed=base_seed,
        include_original=include_original,
        add_metadata=add_metadata,
    )


def deterministic_synthetic_seed(
    *,
    base_seed: int,
    source_index: int,
    strategy_name: str,
    copy_index: int,
) -> int:
    """
    Derive a stable per-synthetic-sample seed.

    Python's built-in hash is intentionally randomized across processes, so this
    function uses a small deterministic character-code sum for the strategy name.
    """
    if source_index < 0:
        raise ValueError("source_index must be non-negative.")

    if copy_index < 0:
        raise ValueError("copy_index must be non-negative for synthetic samples.")

    strategy_code = sum(
        (position + 1) * ord(character)
        for position, character in enumerate(strategy_name)
    )

    modulus = 2_147_483_647
    seed = (
        int(base_seed)
        + (int(source_index) + 1) * 1_000_003
        + (int(copy_index) + 1) * 10_007
        + strategy_code * 101
    ) % modulus

    return int(seed)


@contextmanager
def temporary_rng_seed(seed: int) -> Iterator[None]:
    """
    Temporarily set Python, NumPy, and PyTorch CPU RNG state.

    The previous RNG states are restored after the context exits. This keeps
    deterministic synthetic sample generation from permanently perturbing the
    broader training process RNG state.
    """
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    torch_state = torch.random.get_rng_state()

    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    torch.manual_seed(seed)

    try:
        yield
    finally:
        random.setstate(python_state)
        np.random.set_state(numpy_state)
        torch.random.set_rng_state(torch_state)


def summarize_virtual_synthetic_expansion(
    dataset: VirtualSyntheticExpansionDataset,
) -> dict[str, int | bool | str]:
    """
    Return a plain dictionary summary for notebook display or CSV output.
    """
    return dataset.summary().to_dict()


def _clone_sample(sample: Mapping[str, Any]) -> Sample:
    """
    Clone tensor values in a sample dictionary and shallow-copy other values.
    """
    cloned: Sample = {}

    for key, value in sample.items():
        if torch.is_tensor(value):
            cloned[key] = value.clone()
        else:
            cloned[key] = value

    return cloned


def _with_virtual_metadata(sample: Sample, mapped: VirtualSyntheticIndex) -> Sample:
    """
    Add simple, collate-safe traceability metadata to a returned sample.
    """
    sample["is_synthetic"] = bool(mapped.is_synthetic)
    sample["synthetic_strategy"] = str(mapped.strategy_name)
    sample["synthetic_copy_index"] = int(mapped.copy_index)
    sample["synthetic_seed"] = int(mapped.synthetic_seed)
    sample["synthetic_source_index"] = int(mapped.source_index)
    sample["virtual_index"] = int(mapped.virtual_index)

    return sample


__all__ = [
    "SyntheticExpansionSpec",
    "VirtualSyntheticExpansionDataset",
    "VirtualSyntheticExpansionSummary",
    "VirtualSyntheticIndex",
    "build_virtual_synthetic_expansion_dataset",
    "deterministic_synthetic_seed",
    "summarize_virtual_synthetic_expansion",
    "temporary_rng_seed",
]
