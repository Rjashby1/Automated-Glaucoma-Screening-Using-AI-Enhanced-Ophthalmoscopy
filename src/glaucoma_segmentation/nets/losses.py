"""
Loss functions for glaucoma segmentation models.

The current baseline task is multiclass semantic segmentation:

0 = background
1 = optic disc
2 = optic cup

This module keeps loss logic out of notebooks so training scripts and
notebooks can share the same implementation.
"""

from __future__ import annotations

from typing import Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceCELoss(nn.Module):
    """
    Combined Cross-Entropy and soft Dice loss for multiclass segmentation.

    Parameters
    ----------
    dice_weight:
        Weight applied to Dice loss.

    ce_weight:
        Weight applied to Cross-Entropy loss.

    smooth:
        Small smoothing value to avoid divide-by-zero.

    ignore_index:
        Optional target label to ignore. If None, all pixels are used.

    class_weights:
        Optional class weights for CrossEntropyLoss.
    """

    def __init__(
        self,
        dice_weight: float = 1.0,
        ce_weight: float = 1.0,
        smooth: float = 1e-6,
        ignore_index: int | None = None,
        class_weights: Sequence[float] | torch.Tensor | None = None,
    ) -> None:
        super().__init__()

        if dice_weight < 0:
            raise ValueError("dice_weight must be non-negative.")
        if ce_weight < 0:
            raise ValueError("ce_weight must be non-negative.")
        if dice_weight == 0 and ce_weight == 0:
            raise ValueError("At least one of dice_weight or ce_weight must be positive.")

        self.dice_weight = dice_weight
        self.ce_weight = ce_weight
        self.smooth = smooth
        self.ignore_index = ignore_index

        if class_weights is None:
            self.register_buffer("class_weights", None)
        else:
            weights_tensor = torch.as_tensor(class_weights, dtype=torch.float32)
            self.register_buffer("class_weights", weights_tensor)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Compute combined Dice + Cross-Entropy loss.

        Parameters
        ----------
        logits:
            Raw model outputs with shape (batch, classes, height, width).

        targets:
            Integer class-label masks with shape (batch, height, width).

        Returns
        -------
        torch.Tensor
            Scalar loss.
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

        targets = targets.long()
        num_classes = logits.shape[1]

        ce_loss = logits.new_tensor(0.0)
        if self.ce_weight > 0:
            ce_loss = F.cross_entropy(
                logits,
                targets,
                weight=self.class_weights,
                ignore_index=self.ignore_index if self.ignore_index is not None else -100,
            )

        dice_loss = logits.new_tensor(0.0)
        if self.dice_weight > 0:
            dice_loss = self._soft_dice_loss(logits, targets, num_classes)

        return (self.ce_weight * ce_loss) + (self.dice_weight * dice_loss)

    def _soft_dice_loss(
        self,
        logits: torch.Tensor,
        targets: torch.Tensor,
        num_classes: int,
    ) -> torch.Tensor:
        """Compute multiclass soft Dice loss."""
        probs = torch.softmax(logits, dim=1)

        valid_mask = torch.ones_like(targets, dtype=torch.bool)
        safe_targets = targets

        if self.ignore_index is not None:
            valid_mask = targets != self.ignore_index
            safe_targets = targets.clone()
            safe_targets[~valid_mask] = 0

        target_one_hot = F.one_hot(safe_targets, num_classes=num_classes)
        target_one_hot = target_one_hot.permute(0, 3, 1, 2).to(dtype=probs.dtype)

        valid_mask = valid_mask.unsqueeze(1).to(dtype=probs.dtype)
        probs = probs * valid_mask
        target_one_hot = target_one_hot * valid_mask

        dims = (0, 2, 3)
        intersection = torch.sum(probs * target_one_hot, dim=dims)
        cardinality = torch.sum(probs + target_one_hot, dim=dims)

        dice_score = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        return 1.0 - dice_score.mean()


__all__ = ["DiceCELoss"]