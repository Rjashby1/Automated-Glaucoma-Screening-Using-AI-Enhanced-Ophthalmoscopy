"""
Augmentation utilities for glaucoma segmentation experiments.
"""

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
    "build_online_augmentation_pipeline",
    "build_online_augmentation_preset",
    "describe_online_augmentation_presets",
    "supported_online_augmentation_presets",
]
