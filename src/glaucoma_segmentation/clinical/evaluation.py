"""
Clinical generalization evaluation helpers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
import torch


def binary_dice(
    pred_binary: np.ndarray,
    target_binary: np.ndarray,
    *,
    empty_score: float = 1.0,
) -> float:
    """Compute binary Sørensen-Dice for one predicted/target mask pair."""
    pred = np.asarray(pred_binary).astype(bool)
    target = np.asarray(target_binary).astype(bool)

    pred_sum = int(pred.sum())
    target_sum = int(target.sum())

    if pred_sum == 0 and target_sum == 0:
        return float(empty_score)

    denominator = pred_sum + target_sum
    if denominator == 0:
        return float(empty_score)

    intersection = int(np.logical_and(pred, target).sum())
    return float((2.0 * intersection) / denominator)


def vertical_extent(mask: np.ndarray) -> int:
    """Return the vertical pixel extent of a binary mask."""
    binary = np.asarray(mask).astype(bool)
    rows = np.where(binary.any(axis=1))[0]

    if len(rows) == 0:
        return 0

    return int(rows[-1] - rows[0] + 1)


def vertical_cdr_from_label_array(label_mask: np.ndarray) -> float:
    """
    Compute vertical cup-to-disc ratio from an integer label mask.

    Disc is interpreted inclusively as labels > 0.
    Cup is interpreted as label == 2.
    """
    mask = np.asarray(label_mask)
    disc_height = vertical_extent(mask > 0)
    cup_height = vertical_extent(mask == 2)

    if disc_height <= 0:
        return float("nan")

    return float(cup_height / disc_height)


def _batch_value(batch: dict[str, Any], key: str, index: int) -> Any:
    value = batch.get(key)

    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        return value[index]

    if torch.is_tensor(value):
        item = value[index]
        if item.ndim == 0:
            return item.item()
        return item.detach().cpu().numpy()

    return value


def evaluate_model_on_clinical_loader(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    *,
    device: torch.device,
    model_forward_fn: Callable[[torch.nn.Module, torch.Tensor], torch.Tensor] | None = None,
) -> pd.DataFrame:
    """
    Evaluate a segmentation model on a clinical DataLoader and return private
    image-level metrics.

    The returned dataframe contains sample and patient hashes. Save it only under
    ignored/private paths.
    """
    rows: list[dict[str, Any]] = []
    forward = model_forward_fn if model_forward_fn is not None else lambda model_obj, images: model_obj(images)

    model.eval()

    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device, non_blocking=True).float()
            masks = batch["mask"].to(device, non_blocking=True).long()

            logits = forward(model, images)
            predictions = torch.argmax(logits, dim=1)

            predictions_np = predictions.detach().cpu().numpy()
            targets_np = masks.detach().cpu().numpy()

            for i in range(predictions_np.shape[0]):
                pred_mask = predictions_np[i]
                target_mask = targets_np[i]

                disc_dice = binary_dice(pred_mask > 0, target_mask > 0)
                cup_dice = binary_dice(pred_mask == 2, target_mask == 2)
                mean_foreground_dice = float((disc_dice + cup_dice) / 2.0)

                pred_vertical_cdr = vertical_cdr_from_label_array(pred_mask)
                target_vertical_cdr = vertical_cdr_from_label_array(target_mask)
                cdr_abs_error = (
                    float(abs(pred_vertical_cdr - target_vertical_cdr))
                    if np.isfinite(pred_vertical_cdr) and np.isfinite(target_vertical_cdr)
                    else float("nan")
                )

                rows.append(
                    {
                        "sample_hash": str(_batch_value(batch, "sample_hash", i)),
                        "patient_hash": str(_batch_value(batch, "patient_hash", i)),
                        "eye": str(_batch_value(batch, "eye", i)),
                        "disc_dice": disc_dice,
                        "cup_dice": cup_dice,
                        "mean_foreground_dice": mean_foreground_dice,
                        "pred_vertical_cdr": pred_vertical_cdr,
                        "target_vertical_cdr": target_vertical_cdr,
                        "cdr_abs_error": cdr_abs_error,
                    }
                )

    return pd.DataFrame(rows)


def summarize_image_level_clinical_metrics(image_metrics: pd.DataFrame) -> pd.DataFrame:
    """Create aggregate-only image-weighted clinical metrics."""
    if image_metrics.empty:
        raise ValueError("Cannot summarize empty clinical image-level metrics.")

    rows = {
        "clinical_rows": int(len(image_metrics)),
        "clinical_patient_groups": int(image_metrics["patient_hash"].nunique()),
        "clinical_eye_od_rows": int((image_metrics["eye"] == "OD").sum()),
        "clinical_eye_os_rows": int((image_metrics["eye"] == "OS").sum()),
        "clinical_eye_unknown_rows": int((image_metrics["eye"] == "unknown").sum()),
    }

    for metric in ["disc_dice", "cup_dice", "mean_foreground_dice", "cdr_abs_error"]:
        values = image_metrics[metric].astype(float)
        rows[f"image_weighted_{metric}_mean"] = float(values.mean())
        rows[f"image_weighted_{metric}_median"] = float(values.median())
        rows[f"image_weighted_{metric}_std"] = float(values.std(ddof=0))
        rows[f"image_weighted_{metric}_min"] = float(values.min())
        rows[f"image_weighted_{metric}_max"] = float(values.max())

    return pd.DataFrame([rows])


def summarize_patient_weighted_clinical_metrics(image_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Create aggregate-only patient-weighted clinical metrics.

    Patient hashes are used for grouping but are not returned.
    """
    if image_metrics.empty:
        raise ValueError("Cannot summarize empty clinical image-level metrics.")

    patient_metrics = (
        image_metrics
        .groupby("patient_hash", dropna=False)
        .agg(
            files=("sample_hash", "count"),
            disc_dice=("disc_dice", "mean"),
            cup_dice=("cup_dice", "mean"),
            mean_foreground_dice=("mean_foreground_dice", "mean"),
            cdr_abs_error=("cdr_abs_error", "mean"),
        )
        .reset_index()
    )

    rows = {
        "clinical_patient_groups": int(len(patient_metrics)),
        "patient_files_mean": float(patient_metrics["files"].mean()),
        "patient_files_median": float(patient_metrics["files"].median()),
        "patient_files_min": int(patient_metrics["files"].min()),
        "patient_files_max": int(patient_metrics["files"].max()),
    }

    for metric in ["disc_dice", "cup_dice", "mean_foreground_dice", "cdr_abs_error"]:
        values = patient_metrics[metric].astype(float)
        rows[f"patient_weighted_{metric}_mean"] = float(values.mean())
        rows[f"patient_weighted_{metric}_median"] = float(values.median())
        rows[f"patient_weighted_{metric}_std"] = float(values.std(ddof=0))
        rows[f"patient_weighted_{metric}_min"] = float(values.min())
        rows[f"patient_weighted_{metric}_max"] = float(values.max())

    return pd.DataFrame([rows])


__all__ = [
    "binary_dice",
    "evaluate_model_on_clinical_loader",
    "summarize_image_level_clinical_metrics",
    "summarize_patient_weighted_clinical_metrics",
    "vertical_cdr_from_label_array",
    "vertical_extent",
]
