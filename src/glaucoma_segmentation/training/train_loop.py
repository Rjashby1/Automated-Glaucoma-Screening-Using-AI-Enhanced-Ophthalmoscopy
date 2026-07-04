"""
Reusable training loops for glaucoma segmentation experiments.

The plain training helpers are suitable for scripted runs and automated tests.
The progress-enabled helpers are intended for interactive notebooks where
batch-level feedback, elapsed time, and running metrics are useful.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any

import torch
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

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


def _dataloader_length(dataloader: DataLoader) -> int | None:
    """
    Best-effort dataloader length helper.

    Most PyTorch DataLoaders implement len(), but this keeps progress helpers
    robust if a future iterable loader does not.
    """
    try:
        return len(dataloader)
    except TypeError:
        return None


def _progress_total(
    dataloader: DataLoader,
    max_batches: int | None,
) -> int | None:
    """
    Determine the total number of batches shown in a progress bar.
    """
    loader_length = _dataloader_length(dataloader)

    if loader_length is None:
        return max_batches

    if max_batches is None:
        return loader_length

    return min(loader_length, max_batches)


def _run_one_epoch_impl(
    model: torch.nn.Module,
    dataloader: DataLoader,
    criterion: torch.nn.Module,
    device: torch.device | str,
    optimizer: torch.optim.Optimizer | None = None,
    epoch: int = 1,
    phase: str = "train",
    max_batches: int | None = None,
    use_progress: bool = False,
    total_epochs: int | None = None,
    leave_progress: bool = True,
) -> EpochResult:
    """
    Shared implementation for one train/eval epoch.
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

    iterator = dataloader

    progress_bar = None
    if use_progress:
        if total_epochs is None:
            desc = f"{phase} epoch {epoch:02d}"
        else:
            desc = f"{phase} epoch {epoch:02d}/{total_epochs:02d}"

        progress_bar = tqdm(
            dataloader,
            desc=desc,
            total=_progress_total(dataloader, max_batches),
            leave=leave_progress,
        )
        iterator = progress_bar

    grad_context = torch.enable_grad() if is_train else torch.no_grad()

    with grad_context:
        for batch_index, batch in enumerate(iterator):
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

            if progress_bar is not None:
                running_loss = total_loss / max(total_images, 1)
                running_metrics = metrics.compute()

                progress_bar.set_postfix(
                    {
                        "loss": f"{running_loss:.4f}",
                        "disc": f"{running_metrics['disc_dice']:.3f}",
                        "cup": f"{running_metrics['cup_dice']:.3f}",
                        "cdr_mae": f"{running_metrics['cdr_mae']:.3f}",
                    }
                )

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
    Run one training or evaluation epoch without progress display.

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
    return _run_one_epoch_impl(
        model=model,
        dataloader=dataloader,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        epoch=epoch,
        phase=phase,
        max_batches=max_batches,
        use_progress=False,
    )


def run_one_epoch_with_progress(
    model: torch.nn.Module,
    dataloader: DataLoader,
    criterion: torch.nn.Module,
    device: torch.device | str,
    optimizer: torch.optim.Optimizer | None = None,
    epoch: int = 1,
    phase: str = "train",
    max_batches: int | None = None,
    total_epochs: int | None = None,
    leave_progress: bool = True,
) -> EpochResult:
    """
    Run one training or evaluation epoch with a notebook-friendly progress bar.

    The progress bar reports batch progress plus running loss, disc Dice, cup
    Dice, and CDR MAE.
    """
    return _run_one_epoch_impl(
        model=model,
        dataloader=dataloader,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        epoch=epoch,
        phase=phase,
        max_batches=max_batches,
        use_progress=True,
        total_epochs=total_epochs,
        leave_progress=leave_progress,
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
    Fit a segmentation model for a small number of epochs without progress bars.

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


def fit_model_with_progress(
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader | None,
    criterion: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device | str,
    epochs: int = 1,
    max_train_batches: int | None = None,
    max_val_batches: int | None = None,
    run_name: str = "segmentation_training",
    image_size: tuple[int, int] | None = None,
    batch_size: int | None = None,
    print_epoch_summary: bool = True,
    leave_progress: bool = True,
) -> list[EpochResult]:
    """
    Fit a segmentation model with notebook-visible progress bars.

    This is intended for interactive notebook runs where seeing batch progress,
    elapsed time, and running metrics is useful.
    """
    if epochs < 1:
        raise ValueError("epochs must be at least 1.")

    history: list[EpochResult] = []

    for epoch in range(1, epochs + 1):
        if print_epoch_summary:
            header_parts = [
                f"Running {run_name}",
                f"epoch {epoch:02d}/{epochs:02d}",
            ]

            if image_size is not None:
                header_parts.append(f"image_size={image_size}")

            if batch_size is not None:
                header_parts.append(f"batch_size={batch_size}")

            print("=" * 90)
            print(" | ".join(header_parts))
            print("=" * 90)

        train_result = run_one_epoch_with_progress(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            epoch=epoch,
            phase="train",
            max_batches=max_train_batches,
            total_epochs=epochs,
            leave_progress=leave_progress,
        )
        history.append(train_result)

        val_result = None
        if val_loader is not None:
            val_result = run_one_epoch_with_progress(
                model=model,
                dataloader=val_loader,
                criterion=criterion,
                optimizer=None,
                device=device,
                epoch=epoch,
                phase="val",
                max_batches=max_val_batches,
                total_epochs=epochs,
                leave_progress=leave_progress,
            )
            history.append(val_result)

        if print_epoch_summary and val_result is not None:
            epoch_minutes = (
                train_result.elapsed_seconds + val_result.elapsed_seconds
            ) / 60.0

            print(
                f"Epoch {epoch:02d}/{epochs:02d} complete | "
                f"train_loss={train_result.loss:.4f} | "
                f"val_loss={val_result.loss:.4f} | "
                f"val_disc_dice={val_result.disc_dice:.4f} | "
                f"val_cup_dice={val_result.cup_dice:.4f} | "
                f"val_cdr_mae={val_result.cdr_mae:.4f} | "
                f"epoch_time={epoch_minutes:.2f} min"
            )
        elif print_epoch_summary:
            epoch_minutes = train_result.elapsed_seconds / 60.0

            print(
                f"Epoch {epoch:02d}/{epochs:02d} complete | "
                f"train_loss={train_result.loss:.4f} | "
                f"epoch_time={epoch_minutes:.2f} min"
            )

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
    "fit_model_with_progress",
    "history_to_dicts",
    "model_forward",
    "run_one_epoch",
    "run_one_epoch_with_progress",
]
