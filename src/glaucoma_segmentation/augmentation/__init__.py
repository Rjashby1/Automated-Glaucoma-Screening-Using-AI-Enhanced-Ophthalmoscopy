"""
Augmentation utilities for glaucoma segmentation experiments.
"""

from glaucoma_segmentation.augmentation.offline_synthetic import (
    SyntheticExpansionSpec,
    VirtualSyntheticExpansionDataset,
    VirtualSyntheticExpansionSummary,
    VirtualSyntheticIndex,
    build_virtual_synthetic_expansion_dataset,
    deterministic_synthetic_seed,
    summarize_virtual_synthetic_expansion,
    temporary_rng_seed,
)
from glaucoma_segmentation.augmentation.online_presets import (
    ClampImageSample,
    ComposeSampleTransforms,
    RandomDefocusBlurSample,
    RandomGlobalPhotometricSample,
    RandomHorizontalFlipSample,
    RandomJPEGCompressionSample,
    RandomLowResolutionSample,
    RandomSmallAffineSample,
    RandomVignetteIlluminationSample,
    build_online_augmentation_pipeline,
    build_online_augmentation_preset,
    describe_online_augmentation_presets,
    supported_online_augmentation_presets,
)

__all__ = [
    "ClampImageSample",
    "ComposeSampleTransforms",
    "RandomDefocusBlurSample",
    "RandomGlobalPhotometricSample",
    "RandomHorizontalFlipSample",
    "RandomJPEGCompressionSample",
    "RandomLowResolutionSample",
    "RandomSmallAffineSample",
    "RandomVignetteIlluminationSample",
    "SyntheticExpansionSpec",
    "VirtualSyntheticExpansionDataset",
    "VirtualSyntheticExpansionSummary",
    "VirtualSyntheticIndex",
    "build_online_augmentation_pipeline",
    "build_online_augmentation_preset",
    "build_virtual_synthetic_expansion_dataset",
    "describe_online_augmentation_presets",
    "deterministic_synthetic_seed",
    "summarize_virtual_synthetic_expansion",
    "supported_online_augmentation_presets",
    "temporary_rng_seed",
]
