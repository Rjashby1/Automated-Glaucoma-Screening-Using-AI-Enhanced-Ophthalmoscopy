"""
Model factory for segmentation baselines.

This module centralizes creation of segmentation models so notebooks and
training scripts do not define neural-network architectures inline.

Supported models:
- U-Net
- U-Net++
- DeepLabV3+
"""

from __future__ import annotations

from typing import Any

import segmentation_models_pytorch as smp


MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "unet": {
        "class": smp.Unet,
        "default_encoder": "resnet50",
    },
    "unetplusplus": {
        "class": smp.UnetPlusPlus,
        "default_encoder": "resnet50",
    },
    "deeplabv3plus": {
        "class": smp.DeepLabV3Plus,
        "default_encoder": "resnet50",
    },
}


MODEL_ALIASES: dict[str, str] = {
    "unet": "unet",
    "unetplusplus": "unetplusplus",
    "unet++": "unetplusplus",
    "deeplabv3plus": "deeplabv3plus",
    "deeplabv3+": "deeplabv3plus",
}


def normalize_model_name(model_name: str) -> str:
    """
    Normalize common model-name variants to canonical registry keys.

    Examples
    --------
    "U-Net" -> "unet"
    "U-Net++" -> "unetplusplus"
    "DeepLabV3+" -> "deeplabv3plus"
    """
    cleaned = model_name.strip().lower()
    cleaned = cleaned.replace("_", "")
    cleaned = cleaned.replace("-", "")

    if cleaned not in MODEL_ALIASES:
        valid = ", ".join(sorted(MODEL_ALIASES))
        raise ValueError(
            f"Unknown model_name={model_name!r}. "
            f"Valid options are: {valid}"
        )

    return MODEL_ALIASES[cleaned]


def build_model(
    model_name: str,
    in_channels: int = 3,
    classes: int = 3,
    encoder_name: str | None = None,
    encoder_weights: str | None = "imagenet",
    activation: str | None = None,
    **kwargs: Any,
):
    """
    Build a segmentation model.

    Parameters
    ----------
    model_name:
        Name of model architecture. Supported values include:
        "unet", "unetplusplus", "unet++", "deeplabv3plus", "deeplabv3+".

    in_channels:
        Number of image channels. RGB images use 3.

    classes:
        Number of output segmentation classes.
        For our current masks:
        0 = background
        1 = optic disc
        2 = optic cup

    encoder_name:
        Encoder backbone name. If None, uses the model default.

    encoder_weights:
        Encoder initialization weights. Use "imagenet" for pretrained
        encoders or None for random initialization.

    activation:
        Optional final activation. For training with CrossEntropyLoss-style
        losses, keep this as None.

    **kwargs:
        Additional keyword arguments passed to the SMP model constructor.

    Returns
    -------
    torch.nn.Module
        Instantiated segmentation model.
    """
    key = normalize_model_name(model_name)
    spec = MODEL_REGISTRY[key]

    model_class = spec["class"]
    selected_encoder = encoder_name or spec["default_encoder"]

    return model_class(
        encoder_name=selected_encoder,
        encoder_weights=encoder_weights,
        in_channels=in_channels,
        classes=classes,
        activation=activation,
        **kwargs,
    )