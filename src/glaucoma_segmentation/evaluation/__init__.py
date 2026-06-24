"""
Evaluation utilities for glaucoma segmentation.
"""

from glaucoma_segmentation.evaluation.metrics import (
    SegMetrics,
    dice_one,
    vertical_cdr_from_mask,
)

__all__ = [
    "SegMetrics",
    "dice_one",
    "vertical_cdr_from_mask",
]