"""
Evaluation metrics for glaucoma segmentation.

Mask convention:
0 = background
1 = optic disc
2 = optic cup

For cup-to-disc ratio, the disc region is treated as all optic-nerve-head
foreground pixels: labels > 0. The cup region is labels == 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch


def dice_one(
    pred_mask: torch.Tensor,
    target_mask: torch.Tensor,
    class_index: int,
    eps: float = 1e-6,
) -> float:
    """
    Compute Dice score for one class from integer-label masks.

    Parameters
    ----------
    pred_mask:
        Predicted integer mask with shape (H, W).

    target_mask:
        Ground-truth integer mask with shape (H, W).

    class_index:
        Class label to evaluate.

    eps:
        Small smoothing value to avoid divide-by-zero.

    Returns
    -------
    float
        Dice score for the requested class.
    """
    pred_binary = pred_mask == class_index
    target_binary = target_mask == class_index

    intersection = torch.logical_and(pred_binary, target_binary).sum().float()
    denominator = pred_binary.sum().float() + target_binary.sum().float()

    if denominator.item() == 0:
        return 1.0

    return float((2.0 * intersection + eps) / (denominator + eps))


def vertical_cdr_from_mask(mask: torch.Tensor) -> float:
    """
    Compute vertical cup-to-disc ratio from an integer-label mask.

    The disc is treated as all foreground optic-nerve-head pixels, labels > 0.
    The cup is treated as label == 2.

    Parameters
    ----------
    mask:
        Integer-label mask with shape (H, W).

    Returns
    -------
    float
        Vertical cup-to-disc ratio. Returns NaN if disc height is zero.
    """
    if mask.ndim != 2:
        raise ValueError(f"mask must have shape (H, W), got {tuple(mask.shape)}")

    disc = mask > 0
    cup = mask == 2

    disc_rows = torch.where(disc.any(dim=1))[0]
    cup_rows = torch.where(cup.any(dim=1))[0]

    if len(disc_rows) == 0:
        return float("nan")

    disc_height = int(disc_rows[-1] - disc_rows[0] + 1)

    if len(cup_rows) == 0:
        cup_height = 0
    else:
        cup_height = int(cup_rows[-1] - cup_rows[0] + 1)

    if disc_height == 0:
        return float("nan")

    return cup_height / disc_height


@dataclass
class SegMetrics:
    """
    Accumulator for segmentation metrics over batches.

    Tracks:
    - Disc Dice
    - Cup Dice
    - Cup-to-disc ratio MAE
    """

    disc_class: int = 1
    cup_class: int = 2
    disc_dice_values: list[float] = field(default_factory=list)
    cup_dice_values: list[float] = field(default_factory=list)
    cdr_abs_errors: list[float] = field(default_factory=list)

    def update(self, logits: torch.Tensor, targets: torch.Tensor) -> None:
        """
        Update metrics from model logits and target masks.

        Parameters
        ----------
        logits:
            Raw model outputs with shape (B, C, H, W).

        targets:
            Integer-label target masks with shape (B, H, W).
        """
        if logits.ndim != 4:
            raise ValueError(
                f"logits must have shape (B, C, H, W), got {tuple(logits.shape)}"
            )

        if targets.ndim != 3:
            raise ValueError(
                f"targets must have shape (B, H, W), got {tuple(targets.shape)}"
            )

        if logits.shape[0] != targets.shape[0]:
            raise ValueError("logits and targets must have the same batch size.")

        if logits.shape[2:] != targets.shape[1:]:
            raise ValueError(
                "logits and targets must have matching spatial dimensions. "
                f"Got logits {tuple(logits.shape[2:])}, targets {tuple(targets.shape[1:])}."
            )

        preds = torch.argmax(logits, dim=1).detach().cpu()
        targets = targets.detach().cpu().long()

        for pred_mask, target_mask in zip(preds, targets):
            self.update_masks(pred_mask, target_mask)

    def update_masks(self, pred_mask: torch.Tensor, target_mask: torch.Tensor) -> None:
        """
        Update metrics from predicted and target integer-label masks.

        Parameters
        ----------
        pred_mask:
            Predicted integer-label mask with shape (H, W).

        target_mask:
            Ground-truth integer-label mask with shape (H, W).
        """
        if pred_mask.shape != target_mask.shape:
            raise ValueError(
                f"pred_mask and target_mask must have same shape. "
                f"Got {tuple(pred_mask.shape)} and {tuple(target_mask.shape)}."
            )

        pred_mask = pred_mask.detach().cpu().long()
        target_mask = target_mask.detach().cpu().long()

        self.disc_dice_values.append(
            dice_one(pred_mask, target_mask, class_index=self.disc_class)
        )
        self.cup_dice_values.append(
            dice_one(pred_mask, target_mask, class_index=self.cup_class)
        )

        pred_cdr = vertical_cdr_from_mask(pred_mask)
        target_cdr = vertical_cdr_from_mask(target_mask)

        if not torch.isnan(torch.tensor(pred_cdr)) and not torch.isnan(torch.tensor(target_cdr)):
            self.cdr_abs_errors.append(abs(pred_cdr - target_cdr))

    def compute(self) -> dict[str, float]:
        """
        Return mean metrics.

        Returns
        -------
        dict[str, float]
            Dictionary with disc_dice, cup_dice, cdr_mae, and n_images.
        """
        return {
            "disc_dice": _mean_or_nan(self.disc_dice_values),
            "cup_dice": _mean_or_nan(self.cup_dice_values),
            "cdr_mae": _mean_or_nan(self.cdr_abs_errors),
            "n_images": float(len(self.disc_dice_values)),
        }

    def reset(self) -> None:
        """Clear accumulated metric values."""
        self.disc_dice_values.clear()
        self.cup_dice_values.clear()
        self.cdr_abs_errors.clear()


def _mean_or_nan(values: list[float]) -> float:
    """Return mean of a list or NaN if the list is empty."""
    if not values:
        return float("nan")
    return float(sum(values) / len(values))


__all__ = [
    "SegMetrics",
    "dice_one",
    "vertical_cdr_from_mask",
]