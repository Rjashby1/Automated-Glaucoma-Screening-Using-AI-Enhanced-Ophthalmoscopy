"""
Online augmentation strategies for optic disc/cup segmentation.

Transforms operate on sample dictionaries with:
- image: torch.Tensor with shape (3, H, W), float in [0, 1]
- mask: torch.Tensor with shape (H, W), integer labels

Spatial transforms apply the same geometry to image and mask. Masks are always
resampled with nearest-neighbor interpolation to preserve class labels.
Photometric and image-quality transforms modify only the image.

The original atomic presets are preserved for Notebooks 05–07. Combined presets
are added for later public-data robustness experiments without changing the
default list returned by supported_online_augmentation_presets().
"""

from __future__ import annotations

import io
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import torch
from PIL import Image
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as TF

Sample = dict[str, Any]
SampleTransform = Callable[[Sample], Sample]


def _random_probability() -> float:
    """Draw a random probability from the active torch RNG."""
    return float(torch.rand(1).item())


def _random_uniform(low: float, high: float) -> float:
    """Draw a random float from the active torch RNG."""
    return float(torch.empty(1).uniform_(low, high).item())


def _random_int(low: int, high: int) -> int:
    """Draw a random integer from the active torch RNG, inclusive."""
    if low == high:
        return int(low)
    return int(torch.randint(low, high + 1, size=(1,)).item())


def _copy_sample(
    sample: Sample,
    image: torch.Tensor | None = None,
    mask: torch.Tensor | None = None,
) -> Sample:
    """Return a shallow sample copy with optional image/mask replacement."""
    updated = dict(sample)

    if image is not None:
        updated["image"] = image

    if mask is not None:
        updated["mask"] = mask

    return updated


def _require_image_and_mask(sample: Sample) -> tuple[torch.Tensor, torch.Tensor]:
    """Validate and return the image/mask tensors from a sample dictionary."""
    if "image" not in sample or "mask" not in sample:
        raise KeyError("Augmentation sample must contain 'image' and 'mask' keys.")

    image = sample["image"]
    mask = sample["mask"]

    if not torch.is_tensor(image):
        raise TypeError(f"Sample image must be a torch.Tensor, got {type(image)!r}.")
    if not torch.is_tensor(mask):
        raise TypeError(f"Sample mask must be a torch.Tensor, got {type(mask)!r}.")

    if image.ndim != 3:
        raise ValueError(f"Sample image must have shape (C, H, W), got {tuple(image.shape)}.")
    if mask.ndim != 2:
        raise ValueError(f"Sample mask must have shape (H, W), got {tuple(mask.shape)}.")

    if image.shape[1:] != mask.shape:
        raise ValueError(
            "Sample image and mask must have matching spatial dimensions. "
            f"image={tuple(image.shape)}, mask={tuple(mask.shape)}."
        )

    return image.float(), mask.long()


@dataclass(frozen=True)
class ComposeSampleTransforms:
    """Compose several sample-level transforms."""

    transforms: Sequence[SampleTransform]

    def __call__(self, sample: Sample) -> Sample:
        transformed = sample

        for transform in self.transforms:
            transformed = transform(transformed)

        return transformed


@dataclass(frozen=True)
class ClampImageSample:
    """Clamp image intensities to a valid tensor image range."""

    min_value: float = 0.0
    max_value: float = 1.0

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)
        image = torch.clamp(image, min=self.min_value, max=self.max_value)
        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomHorizontalFlipSample:
    """Randomly flip image and mask horizontally."""

    p: float = 0.5

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        image = TF.hflip(image)
        mask = TF.hflip(mask.unsqueeze(0)).squeeze(0).long()

        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomSmallAffineSample:
    """
    Randomly apply mild rotation, translation, and scale changes.

    The image uses bilinear interpolation. The mask uses nearest-neighbor
    interpolation and background fill to preserve class labels.
    """

    degrees: float = 8.0
    translate_fraction: float = 0.04
    scale_min: float = 0.95
    scale_max: float = 1.05
    p: float = 0.75

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        height, width = image.shape[-2:]
        max_dx = max(0, int(round(width * self.translate_fraction)))
        max_dy = max(0, int(round(height * self.translate_fraction)))

        angle = _random_uniform(-self.degrees, self.degrees)
        translate = [
            _random_int(-max_dx, max_dx),
            _random_int(-max_dy, max_dy),
        ]
        scale = _random_uniform(self.scale_min, self.scale_max)
        shear = [0.0, 0.0]

        image = TF.affine(
            image,
            angle=angle,
            translate=translate,
            scale=scale,
            shear=shear,
            interpolation=InterpolationMode.BILINEAR,
            fill=0.0,
        )

        transformed_mask = TF.affine(
            mask.unsqueeze(0).float(),
            angle=angle,
            translate=translate,
            scale=scale,
            shear=shear,
            interpolation=InterpolationMode.NEAREST,
            fill=0.0,
        )
        mask = transformed_mask.squeeze(0).round().long()

        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomGlobalPhotometricSample:
    """
    Randomly perturb global exposure/color properties.

    This combines brightness, contrast, gamma, and mild saturation changes as
    one atomic photometric strategy.
    """

    brightness: float = 0.18
    contrast: float = 0.18
    gamma_min: float = 0.85
    gamma_max: float = 1.15
    saturation: float = 0.08
    p: float = 0.90

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        if self.brightness > 0:
            image = TF.adjust_brightness(
                image,
                brightness_factor=_random_uniform(
                    max(0.0, 1.0 - self.brightness),
                    1.0 + self.brightness,
                ),
            )

        if self.contrast > 0:
            image = TF.adjust_contrast(
                image,
                contrast_factor=_random_uniform(
                    max(0.0, 1.0 - self.contrast),
                    1.0 + self.contrast,
                ),
            )

        if self.saturation > 0:
            image = TF.adjust_saturation(
                image,
                saturation_factor=_random_uniform(
                    max(0.0, 1.0 - self.saturation),
                    1.0 + self.saturation,
                ),
            )

        gamma = _random_uniform(self.gamma_min, self.gamma_max)
        image = TF.adjust_gamma(image.clamp(0.0, 1.0), gamma=gamma, gain=1.0)
        image = image.clamp(0.0, 1.0)

        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomDefocusBlurSample:
    """Randomly apply mild Gaussian blur to approximate defocus."""

    kernel_size: int = 5
    sigma_min: float = 0.3
    sigma_max: float = 1.2
    p: float = 0.50

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        sigma = _random_uniform(self.sigma_min, self.sigma_max)
        image = TF.gaussian_blur(
            image,
            kernel_size=[self.kernel_size, self.kernel_size],
            sigma=[sigma, sigma],
        ).clamp(0.0, 1.0)

        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomLowResolutionSample:
    """
    Randomly degrade and restore image resolution.

    This approximates mild lower-resolution capture without changing the mask.
    """

    scale_min: float = 0.55
    scale_max: float = 0.80
    p: float = 0.50

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        height, width = image.shape[-2:]
        scale = _random_uniform(self.scale_min, self.scale_max)
        degraded_height = max(16, int(round(height * scale)))
        degraded_width = max(16, int(round(width * scale)))

        image = TF.resize(
            image,
            size=[degraded_height, degraded_width],
            interpolation=InterpolationMode.BILINEAR,
            antialias=True,
        )
        image = TF.resize(
            image,
            size=[height, width],
            interpolation=InterpolationMode.BILINEAR,
            antialias=True,
        ).clamp(0.0, 1.0)

        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomJPEGCompressionSample:
    """
    Randomly apply JPEG compression artifacts to the image.

    This approximates screen-recording or video-compression artifacts while
    leaving the segmentation mask unchanged.
    """

    quality_min: int = 35
    quality_max: int = 75
    p: float = 0.50

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        quality = _random_int(self.quality_min, self.quality_max)
        image_cpu = image.detach().cpu().clamp(0.0, 1.0)
        pil_image = TF.to_pil_image(image_cpu)

        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)

        with Image.open(buffer) as compressed_image:
            image = TF.to_tensor(compressed_image.convert("RGB")).to(dtype=torch.float32)

        image = image.clamp(0.0, 1.0)

        return _copy_sample(sample, image=image, mask=mask)


@dataclass(frozen=True)
class RandomVignetteIlluminationSample:
    """
    Randomly apply mild edge darkening / uneven illumination.

    This approximates ophthalmoscopy-style illumination falloff while leaving
    the segmentation mask unchanged.
    """

    strength_min: float = 0.12
    strength_max: float = 0.35
    center_shift_fraction: float = 0.20
    p: float = 0.50

    def __call__(self, sample: Sample) -> Sample:
        image, mask = _require_image_and_mask(sample)

        if _random_probability() >= self.p:
            return _copy_sample(sample, image=image, mask=mask)

        height, width = image.shape[-2:]
        dtype = image.dtype
        device = image.device

        y = torch.linspace(-1.0, 1.0, steps=height, dtype=dtype, device=device)
        x = torch.linspace(-1.0, 1.0, steps=width, dtype=dtype, device=device)
        yy, xx = torch.meshgrid(y, x, indexing="ij")

        center_y = _random_uniform(-self.center_shift_fraction, self.center_shift_fraction)
        center_x = _random_uniform(-self.center_shift_fraction, self.center_shift_fraction)
        strength = _random_uniform(self.strength_min, self.strength_max)

        radius = torch.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
        radius = torch.clamp(radius, min=0.0, max=1.0)

        vignette = 1.0 - strength * (radius**2)
        vignette = torch.clamp(vignette, min=1.0 - strength, max=1.0)

        image = (image * vignette.unsqueeze(0)).clamp(0.0, 1.0)

        return _copy_sample(sample, image=image, mask=mask)


_ATOMIC_STRATEGY_DESCRIPTIONS: dict[str, dict[str, object]] = {
    "none": {
        "strategy_name": "none",
        "preset_name": "none",
        "augmentation_family": "reference",
        "applies_to": "reference only",
        "mask_handling": "mask unchanged",
        "description": "No online augmentation.",
    },
    "horizontal_flip": {
        "strategy_name": "horizontal_flip",
        "preset_name": "horizontal_flip",
        "augmentation_family": "spatial",
        "applies_to": "image and mask",
        "mask_handling": "paired horizontal flip",
        "description": "Left/right flip invariance for local cup-disc anatomy.",
    },
    "small_affine": {
        "strategy_name": "small_affine",
        "preset_name": "small_affine",
        "augmentation_family": "spatial",
        "applies_to": "image and mask",
        "mask_handling": "paired affine transform with nearest-neighbor mask interpolation",
        "description": "Mild rotation, translation, and scale variation.",
    },
    "global_photometric": {
        "strategy_name": "global_photometric",
        "preset_name": "global_photometric",
        "augmentation_family": "photometric",
        "applies_to": "image only",
        "mask_handling": "mask unchanged",
        "description": "Brightness, contrast, gamma, and mild saturation changes.",
    },
    "defocus_blur": {
        "strategy_name": "defocus_blur",
        "preset_name": "defocus_blur",
        "augmentation_family": "image_quality",
        "applies_to": "image only",
        "mask_handling": "mask unchanged",
        "description": "Mild blur to approximate imperfect focus.",
    },
    "low_resolution": {
        "strategy_name": "low_resolution",
        "preset_name": "low_resolution",
        "augmentation_family": "image_quality",
        "applies_to": "image only",
        "mask_handling": "mask unchanged",
        "description": "Downsample and restore resolution to approximate lower-resolution capture.",
    },
    "jpeg_compression": {
        "strategy_name": "jpeg_compression",
        "preset_name": "jpeg_compression",
        "augmentation_family": "image_quality",
        "applies_to": "image only",
        "mask_handling": "mask unchanged",
        "description": "JPEG compression artifacts to approximate screen/video compression.",
    },
    "vignette_illumination": {
        "strategy_name": "vignette_illumination",
        "preset_name": "vignette_illumination",
        "augmentation_family": "illumination",
        "applies_to": "image only",
        "mask_handling": "mask unchanged",
        "description": "Mild uneven illumination / edge darkening.",
    },
}


_COMBINED_STRATEGY_COMPONENTS: dict[str, tuple[str, ...]] = {
    "combo_small_affine_photometric": (
        "small_affine",
        "global_photometric",
    ),
    "combo_small_affine_blur": (
        "small_affine",
        "defocus_blur",
    ),
    "combo_small_affine_vignette": (
        "small_affine",
        "vignette_illumination",
    ),
    "combo_affine_photometric_blur": (
        "small_affine",
        "global_photometric",
        "defocus_blur",
    ),
    "combo_affine_vignette_blur": (
        "small_affine",
        "vignette_illumination",
        "defocus_blur",
    ),
    "combo_full_robustness": (
        "small_affine",
        "global_photometric",
        "defocus_blur",
        "low_resolution",
        "jpeg_compression",
        "vignette_illumination",
    ),
}


_COMBINED_STRATEGY_DESCRIPTIONS: dict[str, dict[str, object]] = {
    "combo_small_affine_photometric": {
        "strategy_name": "combo_small_affine_photometric",
        "preset_name": "combo_small_affine_photometric",
        "augmentation_family": "combined_spatial_photometric",
        "applies_to": "image and mask for spatial components; image only for photometric components",
        "mask_handling": "paired affine transform for masks; mask unchanged for photometric components",
        "description": "Mild affine variation followed by global brightness/contrast/gamma/color perturbation.",
        "component_strategies": "small_affine;global_photometric",
    },
    "combo_small_affine_blur": {
        "strategy_name": "combo_small_affine_blur",
        "preset_name": "combo_small_affine_blur",
        "augmentation_family": "combined_spatial_quality",
        "applies_to": "image and mask for spatial components; image only for blur",
        "mask_handling": "paired affine transform for masks; mask unchanged for blur",
        "description": "Mild affine variation followed by defocus blur.",
        "component_strategies": "small_affine;defocus_blur",
    },
    "combo_small_affine_vignette": {
        "strategy_name": "combo_small_affine_vignette",
        "preset_name": "combo_small_affine_vignette",
        "augmentation_family": "combined_spatial_illumination",
        "applies_to": "image and mask for spatial components; image only for illumination",
        "mask_handling": "paired affine transform for masks; mask unchanged for vignette",
        "description": "Mild affine variation followed by uneven illumination / edge darkening.",
        "component_strategies": "small_affine;vignette_illumination",
    },
    "combo_affine_photometric_blur": {
        "strategy_name": "combo_affine_photometric_blur",
        "preset_name": "combo_affine_photometric_blur",
        "augmentation_family": "combined_spatial_photometric_quality",
        "applies_to": "image and mask for spatial components; image only for photometric/blur components",
        "mask_handling": "paired affine transform for masks; mask unchanged for image-quality components",
        "description": "Mild affine variation, global photometric perturbation, and defocus blur.",
        "component_strategies": "small_affine;global_photometric;defocus_blur",
    },
    "combo_affine_vignette_blur": {
        "strategy_name": "combo_affine_vignette_blur",
        "preset_name": "combo_affine_vignette_blur",
        "augmentation_family": "combined_spatial_illumination_quality",
        "applies_to": "image and mask for spatial components; image only for illumination/blur components",
        "mask_handling": "paired affine transform for masks; mask unchanged for image-quality components",
        "description": "Mild affine variation, uneven illumination, and defocus blur.",
        "component_strategies": "small_affine;vignette_illumination;defocus_blur",
    },
    "combo_full_robustness": {
        "strategy_name": "combo_full_robustness",
        "preset_name": "combo_full_robustness",
        "augmentation_family": "combined_spatial_photometric_quality_illumination",
        "applies_to": "image and mask for spatial components; image only for quality/illumination components",
        "mask_handling": "paired affine transform for masks; mask unchanged for image-only components",
        "description": (
            "Full public-data robustness recipe combining affine variation, photometric changes, "
            "blur, low-resolution degradation, JPEG artifacts, and uneven illumination."
        ),
        "component_strategies": (
            "small_affine;global_photometric;defocus_blur;"
            "low_resolution;jpeg_compression;vignette_illumination"
        ),
    },
}


def _all_strategy_descriptions(include_combinations: bool = False) -> dict[str, dict[str, object]]:
    """Return strategy descriptions, optionally including combined presets."""
    descriptions = dict(_ATOMIC_STRATEGY_DESCRIPTIONS)

    if include_combinations:
        descriptions.update(_COMBINED_STRATEGY_DESCRIPTIONS)

    return descriptions


def supported_online_augmentation_presets(
    include_combinations: bool = False,
) -> tuple[str, ...]:
    """
    Return supported online augmentation preset names.

    By default, only the original atomic presets are returned. This preserves
    the behavior of earlier notebooks that screen all supported presets. Pass
    include_combinations=True to include combined Notebook 09 robustness presets.
    """
    return tuple(_all_strategy_descriptions(include_combinations=include_combinations))


def supported_combined_online_augmentation_presets() -> tuple[str, ...]:
    """Return only the combined augmentation preset names."""
    return tuple(_COMBINED_STRATEGY_DESCRIPTIONS)


def describe_online_augmentation_presets(
    include_combinations: bool = False,
) -> list[dict[str, object]]:
    """
    Return human-readable descriptions for available augmentation strategies.

    By default, only original atomic presets are described. Pass
    include_combinations=True to include later combined robustness presets.
    """
    descriptions = _all_strategy_descriptions(include_combinations=include_combinations)
    return [dict(value) for value in descriptions.values()]


def describe_combined_online_augmentation_presets() -> list[dict[str, object]]:
    """Return human-readable descriptions for combined augmentation presets."""
    return [dict(value) for value in _COMBINED_STRATEGY_DESCRIPTIONS.values()]


def combined_online_augmentation_components(preset_name: str) -> tuple[str, ...]:
    """Return the atomic component strategies for a combined preset."""
    normalized_name = preset_name.strip().lower()

    if normalized_name not in _COMBINED_STRATEGY_COMPONENTS:
        supported = ", ".join(supported_combined_online_augmentation_presets())
        raise ValueError(
            f"Unknown combined online augmentation preset: {preset_name!r}. "
            f"Supported combined presets: {supported}."
        )

    return _COMBINED_STRATEGY_COMPONENTS[normalized_name]


def _build_atomic_online_augmentation_preset(preset_name: str | None) -> SampleTransform | None:
    """Build one original atomic online augmentation strategy."""
    normalized_name = "none" if preset_name is None else preset_name.strip().lower()

    if normalized_name == "none":
        return None

    if normalized_name == "horizontal_flip":
        return RandomHorizontalFlipSample(p=0.5)

    if normalized_name == "small_affine":
        return RandomSmallAffineSample(
            degrees=8.0,
            translate_fraction=0.04,
            scale_min=0.95,
            scale_max=1.05,
            p=0.75,
        )

    if normalized_name == "global_photometric":
        return RandomGlobalPhotometricSample(
            brightness=0.18,
            contrast=0.18,
            gamma_min=0.85,
            gamma_max=1.15,
            saturation=0.08,
            p=0.90,
        )

    if normalized_name == "defocus_blur":
        return RandomDefocusBlurSample(
            kernel_size=5,
            sigma_min=0.3,
            sigma_max=1.2,
            p=0.50,
        )

    if normalized_name == "low_resolution":
        return RandomLowResolutionSample(
            scale_min=0.55,
            scale_max=0.80,
            p=0.50,
        )

    if normalized_name == "jpeg_compression":
        return RandomJPEGCompressionSample(
            quality_min=35,
            quality_max=75,
            p=0.50,
        )

    if normalized_name == "vignette_illumination":
        return RandomVignetteIlluminationSample(
            strength_min=0.12,
            strength_max=0.35,
            center_shift_fraction=0.20,
            p=0.50,
        )

    supported = ", ".join(supported_online_augmentation_presets())
    raise ValueError(
        f"Unknown atomic online augmentation preset: {preset_name!r}. "
        f"Supported atomic presets: {supported}."
    )


def build_online_augmentation_preset(preset_name: str | None) -> SampleTransform | None:
    """
    Build one online augmentation preset.

    Supported atomic presets:
    - none
    - horizontal_flip
    - small_affine
    - global_photometric
    - defocus_blur
    - low_resolution
    - jpeg_compression
    - vignette_illumination

    Supported combined presets:
    - combo_small_affine_photometric
    - combo_small_affine_blur
    - combo_small_affine_vignette
    - combo_affine_photometric_blur
    - combo_affine_vignette_blur
    - combo_full_robustness

    The "none" preset returns None.
    """
    normalized_name = "none" if preset_name is None else preset_name.strip().lower()

    if normalized_name == "none":
        return None

    if normalized_name in _COMBINED_STRATEGY_COMPONENTS:
        component_transforms = [
            _build_atomic_online_augmentation_preset(component_name)
            for component_name in _COMBINED_STRATEGY_COMPONENTS[normalized_name]
        ]
        transforms = [transform for transform in component_transforms if transform is not None]
        return ComposeSampleTransforms(transforms)

    try:
        return _build_atomic_online_augmentation_preset(normalized_name)
    except ValueError as exc:
        supported = ", ".join(supported_online_augmentation_presets(include_combinations=True))
        raise ValueError(
            f"Unknown online augmentation preset: {preset_name!r}. "
            f"Supported presets: {supported}."
        ) from exc

def build_online_augmentation_pipeline(
    strategy_names: Sequence[str],
) -> SampleTransform | None:
    """
    Build a composed online augmentation pipeline from several strategies.

    The "none" strategy is ignored inside composed pipelines. Strategy names may
    be atomic or combined, though Notebook 09 should usually prefer one combined
    preset name to keep virtual synthetic row counts controlled.
    """
    transforms: list[SampleTransform] = []

    for strategy_name in strategy_names:
        transform = build_online_augmentation_preset(strategy_name)
        if transform is not None:
            transforms.append(transform)

    if not transforms:
        return None

    return ComposeSampleTransforms(transforms)


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
    "Sample",
    "SampleTransform",
    "build_online_augmentation_pipeline",
    "build_online_augmentation_preset",
    "combined_online_augmentation_components",
    "describe_combined_online_augmentation_presets",
    "describe_online_augmentation_presets",
    "supported_combined_online_augmentation_presets",
    "supported_online_augmentation_presets",
]
