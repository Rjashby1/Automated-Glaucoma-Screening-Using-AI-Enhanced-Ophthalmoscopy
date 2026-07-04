"""
Device-selection helpers for training and inference.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import torch


@dataclass(frozen=True)
class DeviceInfo:
    """
    Human-readable summary of the selected torch device.
    """

    device: str
    device_type: str
    name: str
    cuda_available: bool
    cuda_device_count: int
    mps_available: bool


def get_device(
    prefer_cuda: bool = True,
    prefer_mps: bool = True,
) -> torch.device:
    """
    Select a PyTorch device.

    Priority:
    1. CUDA, when available and preferred
    2. Apple MPS, when available and preferred
    3. CPU
    """
    if prefer_cuda and torch.cuda.is_available():
        return torch.device("cuda")

    mps_backend = getattr(torch.backends, "mps", None)
    if prefer_mps and mps_backend is not None and mps_backend.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def describe_device(device: torch.device | str | None = None) -> DeviceInfo:
    """
    Return a small summary of the active compute device.
    """
    selected = torch.device(device) if device is not None else get_device()

    cuda_available = torch.cuda.is_available()
    cuda_device_count = torch.cuda.device_count() if cuda_available else 0

    mps_backend = getattr(torch.backends, "mps", None)
    mps_available = bool(mps_backend is not None and mps_backend.is_available())

    if selected.type == "cuda" and cuda_available:
        index = selected.index if selected.index is not None else torch.cuda.current_device()
        name = torch.cuda.get_device_name(index)
    elif selected.type == "mps":
        name = "Apple Metal Performance Shaders"
    else:
        name = "CPU"

    return DeviceInfo(
        device=str(selected),
        device_type=selected.type,
        name=name,
        cuda_available=cuda_available,
        cuda_device_count=cuda_device_count,
        mps_available=mps_available,
    )


def device_summary_dict(device: torch.device | str | None = None) -> dict[str, object]:
    """
    Return device information as a dictionary for notebook display/reporting.
    """
    return asdict(describe_device(device))


__all__ = ["DeviceInfo", "describe_device", "device_summary_dict", "get_device"]
