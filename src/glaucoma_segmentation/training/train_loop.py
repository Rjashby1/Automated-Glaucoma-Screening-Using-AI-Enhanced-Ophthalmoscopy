"""
Minimal reusable training loops for segmentation experiments.

These helpers are intentionally lightweight. Notebooks should use them to run
small smoke tests and baseline experiments without defining training logic
inline.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any

import torch
from torch.utils.data import DataLoader

from glaucoma_segmentation.evaluation.metrics import SegMetrics


@dataclass
class EpochResult:
    """
    Summary of one train or evaluation epoch.
    """

    phase: str
    epoch: int
    loss: float
    disc_dice: float
    cup_dice: float
    cdr_mae: float
    n_images: int
    n_batches: int
    elapsed_seconds: float
    max_batches: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the result to a plain dictionary for pandas/CSV output.
        """
        return asdict(self)


def extract_images_and_masks(batch: Any) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Extract image and mask tensors from a dataloader batch.

    Supports the repository's dictionary batch format:
    {"image": tensor, "mask": tensor, ...}

    Also supports simple tuple/list batches:
    (images, masks)
    """
    if isinstance(batch, dict):
        if "image" not in batch or "mask" not in batch:
            raise KeyError("Dictionary batch must contain 'image' and 'mask' keys.")
        return batch["image"], batch["mask"]

    if isinstance(batch, (tuple, list)) and len(batch) >= 2:
        return batch[0], batch[1]

    raise TypeError(
        "Unsupported batch format. Expected dict with image/mask keys or "
        "tuple/list containing image and mask tensors."
    )


def model_forward(model: torch.nn.Module, images: torch.Tensor) -> torch.Tensor:
    """
    Run a model forward pass and normalize common output formats to logits.

    Segmentation Models PyTorch returns a tensor directly. Some torchvision
    segmentation models return {"out": logits}; that format is supported too.
    """
    outputs = model(images)

    if isinstance(outputs, dict):
        if "out" not in outputs:
            raise KeyError("Model returned a dict without an 'out' key.")
        outputs = outputs["out"]

    if not torch.is_tensor(outputs):
        raise TypeError(f"Model output must be a torch.Tensor, got {type(outputs)!r}")

    return outputs


def run_one_epoch(
    model: torch.nn.Module,
    dataloader: DataLoader,
    criterion: torch.nn.Module,
    device: torch.device | str,
    optimizer: torch.optim.Optimizer | None = None,
    epoch: int = 1,
    phase: str = "train",
    max_batches: int | None = None,
) -> EpochResult:
    """
    Run one training or evaluation epoch.

    Parameters
    ----------
    model:
        Segmentation model.

    dataloader:
        PyTorch DataLoader yielding batches with image and mask tensors.

    criterion:
        Loss function taking logits and integer masks.

    device:
        Target PyTorch device.

    optimizer:
        Optimizer. Required when phase='train'.

    epoch:
        Epoch number recorded in the result.

    phase:
        Either 'train', 'val', 'test', or another label. Only 'train' enables
        gradients and optimizer steps.

    max_batches:
        Optional cap for smoke tests. If None, the full dataloader is used.

    Returns
    -------
    EpochResult
        Aggregate loss and metrics for the epoch.
    """
    selected_device = torch.device(device)
    is_train = phase == "train"

    if is_train and optimizer is None:
        raise ValueError("optimizer is required when phase='train'.")

    model.to(selected_device)
    model.train(is_train)

    metrics = SegMetrics()
    total_loss = 0.0
    total_images = 0
    n_batches = 0

    start_time = time.perf_counter()

    grad_context = torch.enable_grad() if is_train else torch.no_grad()

    with grad_context:
        for batch_index, batch in enumerate(dataloader):
            if max_batches is not None and batch_index >= max_batches:
                break

            images, masks = extract_images_and_masks(batch)
            images = images.to(selected_device, non_blocking=True).float()
            masks = masks.to(selected_device, non_blocking=True).long()

            if is_train:
                optimizer.zero_grad(set_to_none=True)

            logits = model_forward(model, images)
            loss = criterion(logits, masks)

            if is_train:
                loss.backward()
                optimizer.step()

            batch_size = int(images.shape[0])
            total_loss += float(loss.detach().cpu().item()) * batch_size
            total_images += batch_size
            n_batches += 1

            metrics.update(logits.detach(), masks.detach())

    elapsed_seconds = time.perf_counter() - start_time
    computed = metrics.compute()

    mean_loss = float("nan")
    if total_images > 0:
        mean_loss = total_loss / total_images

    return EpochResult(
        phase=phase,
        epoch=epoch,
        loss=mean_loss,
        disc_dice=float(computed["disc_dice"]),
        cup_dice=float(computed["cup_dice"]),
        cdr_mae=float(computed["cdr_mae"]),
        n_images=int(computed["n_images"]),
        n_batches=n_batches,
        elapsed_seconds=elapsed_seconds,
        max_batches=max_batches,
    )


def fit_model(
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader | None,
    criterion: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device | str,
    epochs: int = 1,
    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
) -> list[EpochResult]:
    """
    Fit a segmentation model for a small number of epochs.

    This function is suitable for baseline and smoke-test training. More complex
    experiment orchestration can be added later in experiment_runner.py.
    """
    if epochs < 1:
        raise ValueError("epochs must be at least 1.")

    history: list[EpochResult] = []

    for epoch in range(1, epochs + 1):
        train_result = run_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            epoch=epoch,
            phase="train",
            max_batches=max_train_batches,
        )
        history.append(train_result)

        if val_loader is not None:
            val_result = run_one_epoch(
                model=model,
                dataloader=val_loader,
                criterion=criterion,
                optimizer=None,
                device=device,
                epoch=epoch,
                phase="val",
                max_batches=max_val_batches,
            )
            history.append(val_result)

    return history


def history_to_dicts(history: list[EpochResult]) -> list[dict[str, Any]]:
    """
    Convert a list of EpochResult objects to dictionaries.
    """
    return [result.to_dict() for result in history]


__all__ = [
    "EpochResult",
    "extract_images_and_masks",
    "fit_model",
    "history_to_dicts",
    "model_forward",
    "run_one_epoch",
]
