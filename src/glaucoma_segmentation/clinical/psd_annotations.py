"""
Utilities for deriving optic disc/cup masks from annotated clinical PSD files.

The clinical PSD files contain visual red/blue annotation overlays rather than
separate mask files. This module extracts those annotation outlines, converts
them into filled integer-label masks, and writes private intermediate images
under ignored local data directories.

Mask convention:
0 = background
1 = optic disc
2 = optic cup

Privacy convention:
- Private manifests may include local paths and hashed sample IDs.
- Public/committed summaries should use only aggregate counts and metrics.
"""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


def stable_hash(value: str, length: int = 16) -> str:
    """Return a stable short hash for private local identifiers."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def parse_patient_and_eye(path: Path) -> dict[str, object]:
    """
    Parse patient/encounter number and eye from a clinical PSD filename.

    The first P-number is treated as the encounter/patient grouping key.
    OD and OS are parsed when present. Files without OD/OS are marked unknown.
    """
    stem = path.stem.strip()
    compact = stem.replace(" ", "")

    patient_match = re.match(r"(?i)^P(?:S)?(?P<patient_number>\d+)", compact)
    patient_number = int(patient_match.group("patient_number")) if patient_match else None

    eye_match = re.search(r"(?i)(OD|OS)", compact)
    eye = eye_match.group(1).upper() if eye_match else "unknown"

    cd_match = re.search(r"(?i)cd(?P<cd_number>\d+)", compact)
    cd_group = f"CD{cd_match.group('cd_number')}" if cd_match else "unknown"

    patient_hash = stable_hash(f"P{patient_number}") if patient_number is not None else stable_hash(compact)

    return {
        "patient_number_private": patient_number,
        "patient_hash": patient_hash,
        "eye": eye,
        "cd_group": cd_group,
    }


def load_psd_composite(path: Path) -> np.ndarray:
    """Load the flattened PSD composite as an RGB numpy array."""
    with Image.open(path) as image:
        return np.array(image.convert("RGB"))


def strict_annotation_color_masks(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Return strict candidate masks for red disc and blue cup annotation lines.

    The thresholds are intentionally conservative. They target annotation colors
    rather than natural fundus colors.
    """
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)

    red = (
        (r > 180)
        & (g < 115)
        & (b < 135)
        & ((r - g) > 70)
        & ((r - b) > 70)
    )

    blue = (
        (b > 145)
        & (r < 135)
        & (g < 185)
        & ((b - r) > 55)
    )

    return red.astype(np.uint8), blue.astype(np.uint8)


def connected_components(mask: np.ndarray, min_area: int = 10) -> list[dict[str, object]]:
    """Return connected components above a minimum pixel area."""
    mask_u8 = (mask > 0).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)

    components: list[dict[str, object]] = []

    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]
        if int(area) < min_area:
            continue

        component_mask = labels == label
        ys, xs = np.where(component_mask)

        components.append(
            {
                "label": int(label),
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area),
                "cx": float(centroids[label][0]),
                "cy": float(centroids[label][1]),
                "mask": component_mask,
                "points": np.column_stack([xs, ys]).astype(np.int32),
            }
        )

    return components


def component_bbox_contains(
    inner: dict[str, object],
    outer: dict[str, object],
    pad: int = 6,
) -> bool:
    """Return whether the inner component centroid falls inside the outer bbox."""
    inner_cx = float(inner["cx"])
    inner_cy = float(inner["cy"])
    x = int(outer["x"]) - pad
    y = int(outer["y"]) - pad
    w = int(outer["w"]) + 2 * pad
    h = int(outer["h"]) + 2 * pad
    return x <= inner_cx <= x + w and y <= inner_cy <= y + h


def select_annotation_pair(
    red_components: list[dict[str, object]],
    blue_components: list[dict[str, object]],
) -> tuple[dict[str, object] | None, dict[str, object] | None, str]:
    """
    Select a red disc component and blue cup component using spatial constraints.
    """
    red_candidates = [
        component
        for component in red_components
        if 8 <= int(component["w"]) <= 180 and 8 <= int(component["h"]) <= 180
    ]

    blue_candidates = [
        component
        for component in blue_components
        if 8 <= int(component["w"]) <= 180 and 8 <= int(component["h"]) <= 180
    ]

    if not red_candidates:
        return None, None, "no_red_component"

    if not blue_candidates:
        red_best = sorted(red_candidates, key=lambda component: int(component["area"]), reverse=True)[0]
        return red_best, None, "no_blue_component"

    scored_pairs: list[tuple[float, dict[str, object], dict[str, object]]] = []

    for red_component in red_candidates:
        for blue_component in blue_candidates:
            dx = float(red_component["cx"]) - float(blue_component["cx"])
            dy = float(red_component["cy"]) - float(blue_component["cy"])
            distance = math.sqrt(dx * dx + dy * dy)

            blue_center_inside_red_bbox = component_bbox_contains(blue_component, red_component, pad=8)
            blue_not_much_larger = (
                int(blue_component["w"]) <= int(red_component["w"]) * 1.45
                and int(blue_component["h"]) <= int(red_component["h"]) * 1.45
            )

            if not blue_center_inside_red_bbox:
                continue

            if not blue_not_much_larger:
                continue

            score = (
                5000.0
                - distance * 30.0
                + min(int(red_component["area"]), 2000) * 0.50
                + min(int(blue_component["area"]), 2000) * 0.50
            )

            scored_pairs.append((score, red_component, blue_component))

    if scored_pairs:
        scored_pairs = sorted(scored_pairs, key=lambda item: item[0], reverse=True)
        _, red_best, blue_best = scored_pairs[0]
        return red_best, blue_best, "ok"

    red_best = sorted(red_candidates, key=lambda component: int(component["area"]), reverse=True)[0]
    blue_best = sorted(
        blue_candidates,
        key=lambda component: (
            (float(component["cx"]) - float(red_best["cx"])) ** 2
            + (float(component["cy"]) - float(red_best["cy"])) ** 2
        ),
    )[0]
    return red_best, blue_best, "fallback_nearest_blue"


def fill_component_as_ellipse(component: dict[str, object], shape: tuple[int, int]) -> np.ndarray:
    """
    Fill an annotation outline component as an ellipse.

    Ellipse filling is appropriate because the source annotations are drawn as
    disc/cup outlines. A contour fallback is retained for very small components.
    """
    filled = np.zeros(shape, dtype=np.uint8)
    points = component["points"].reshape(-1, 1, 2).astype(np.int32)

    if len(points) >= 5:
        ellipse = cv2.fitEllipse(points)
        cv2.ellipse(filled, ellipse, color=1, thickness=-1)
    else:
        cv2.drawContours(filled, [points], contourIdx=-1, color=1, thickness=-1)

    return filled.astype(bool)


def vertical_height(mask: np.ndarray) -> int:
    """Return vertical height of a binary mask."""
    rows = np.where(mask.any(axis=1))[0]
    if len(rows) == 0:
        return 0
    return int(rows[-1] - rows[0] + 1)


def build_clean_image(
    rgb: np.ndarray,
    red_component: dict[str, object] | None,
    blue_component: dict[str, object] | None,
) -> np.ndarray:
    """
    Inpaint selected annotation lines so the model does not see the answer key.
    """
    annotation_mask = np.zeros(rgb.shape[:2], dtype=np.uint8)

    for component in [red_component, blue_component]:
        if component is not None:
            annotation_mask[component["mask"]] = 255

    kernel = np.ones((5, 5), dtype=np.uint8)
    annotation_mask = cv2.dilate(annotation_mask, kernel, iterations=1)

    return cv2.inpaint(rgb, annotation_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)


def overlay_mask(rgb: np.ndarray, label_mask: np.ndarray) -> np.ndarray:
    """Overlay derived disc/cup labels on an RGB image for private QA."""
    overlay = rgb.copy()
    disc = label_mask == 1
    cup = label_mask == 2

    overlay[disc] = (0.60 * overlay[disc] + 0.40 * np.array([255, 0, 0])).astype(np.uint8)
    overlay[cup] = (0.55 * overlay[cup] + 0.45 * np.array([0, 0, 255])).astype(np.uint8)

    return overlay


def process_psd_annotation(
    path: Path,
    *,
    project_root: Path,
    clean_dir: Path,
    mask_dir: Path,
) -> tuple[dict[str, object], np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    """
    Process one annotated PSD into a cleaned clinical image and derived label mask.
    """
    relative_path_private = str(path.resolve().relative_to(project_root))
    sample_hash = stable_hash(relative_path_private)

    base_info: dict[str, object] = {
        "sample_hash": sample_hash,
        "relative_path_private": relative_path_private,
        **parse_patient_and_eye(path),
        "read_ok": False,
        "image_width": None,
        "image_height": None,
        "red_component_count": None,
        "blue_component_count": None,
        "selected_red_pixels": None,
        "selected_blue_pixels": None,
        "disc_area_pixels": None,
        "cup_area_pixels": None,
        "cup_to_disc_area_ratio": None,
        "vertical_cdr_from_derived_mask": None,
        "cup_inside_disc_fraction": None,
        "extraction_status": "not_processed",
        "mask_ready": False,
        "clean_image_private_path": None,
        "derived_mask_private_path": None,
        "error_type": None,
        "error_message_private": None,
    }

    try:
        rgb = load_psd_composite(path)
        height, width = rgb.shape[:2]

        red_raw, blue_raw = strict_annotation_color_masks(rgb)
        red_components = connected_components(red_raw, min_area=8)
        blue_components = connected_components(blue_raw, min_area=8)

        red_component, blue_component, status = select_annotation_pair(red_components, blue_components)

        base_info.update(
            {
                "read_ok": True,
                "image_width": int(width),
                "image_height": int(height),
                "red_component_count": len(red_components),
                "blue_component_count": len(blue_components),
                "extraction_status": status,
            }
        )

        if red_component is None or blue_component is None:
            return base_info, rgb, None, None

        disc_fill = fill_component_as_ellipse(red_component, rgb.shape[:2])
        cup_fill = fill_component_as_ellipse(blue_component, rgb.shape[:2])

        disc_area = int(disc_fill.sum())
        cup_area = int(cup_fill.sum())
        cup_inside_disc = int(np.logical_and(cup_fill, disc_fill).sum())
        cup_inside_disc_fraction = cup_inside_disc / cup_area if cup_area > 0 else float("nan")
        cup_to_disc_area_ratio = cup_area / disc_area if disc_area > 0 else float("nan")

        disc_height = vertical_height(disc_fill)
        cup_height = vertical_height(cup_fill)
        vertical_cdr = cup_height / disc_height if disc_height > 0 else float("nan")

        label_mask = np.zeros(rgb.shape[:2], dtype=np.uint8)
        label_mask[disc_fill] = 1
        label_mask[cup_fill] = 2

        mask_ready = (
            disc_area > 25
            and cup_area > 10
            and cup_inside_disc_fraction >= 0.50
            and 0.01 <= cup_to_disc_area_ratio <= 1.30
            and 0.05 <= vertical_cdr <= 1.50
        )

        clean_rgb = build_clean_image(rgb, red_component, blue_component)

        clean_path = clean_dir / f"{sample_hash}_clean.png"
        mask_path = mask_dir / f"{sample_hash}_mask.png"

        Image.fromarray(clean_rgb).save(clean_path)
        Image.fromarray(label_mask).save(mask_path)

        base_info.update(
            {
                "selected_red_pixels": int(red_component["area"]),
                "selected_blue_pixels": int(blue_component["area"]),
                "disc_area_pixels": disc_area,
                "cup_area_pixels": cup_area,
                "cup_to_disc_area_ratio": cup_to_disc_area_ratio,
                "vertical_cdr_from_derived_mask": vertical_cdr,
                "cup_inside_disc_fraction": cup_inside_disc_fraction,
                "mask_ready": bool(mask_ready),
                "clean_image_private_path": str(clean_path.relative_to(project_root)),
                "derived_mask_private_path": str(mask_path.relative_to(project_root)),
            }
        )

        return base_info, rgb, clean_rgb, label_mask

    except Exception as exc:
        base_info.update(
            {
                "error_type": type(exc).__name__,
                "error_message_private": str(exc)[:300],
                "extraction_status": "error",
            }
        )
        return base_info, None, None, None


def summarize_extraction_manifest(manifest: pd.DataFrame) -> pd.DataFrame:
    """Create aggregate extraction summary from a private manifest."""
    rows: list[dict[str, object]] = []

    rows.append({"metric": "psd_files_processed", "value": int(len(manifest))})

    if manifest.empty:
        rows.append({"metric": "read_ok_count", "value": 0})
        rows.append({"metric": "mask_ready_count", "value": 0})
        rows.append({"metric": "unique_patient_count", "value": 0})
        return pd.DataFrame(rows)

    rows.extend(
        [
            {"metric": "read_ok_count", "value": int(manifest["read_ok"].sum())},
            {"metric": "mask_ready_count", "value": int(manifest["mask_ready"].sum())},
            {"metric": "mask_ready_rate", "value": float(manifest["mask_ready"].mean())},
            {"metric": "unique_patient_count", "value": int(manifest["patient_hash"].nunique())},
            {"metric": "eye_od_count", "value": int((manifest["eye"] == "OD").sum())},
            {"metric": "eye_os_count", "value": int((manifest["eye"] == "OS").sum())},
            {"metric": "eye_unknown_count", "value": int((manifest["eye"] == "unknown").sum())},
        ]
    )

    ready = manifest.loc[manifest["mask_ready"]].copy()

    if not ready.empty:
        rows.extend(
            [
                {"metric": "mask_ready_unique_patient_count", "value": int(ready["patient_hash"].nunique())},
                {"metric": "mask_ready_eye_od_count", "value": int((ready["eye"] == "OD").sum())},
                {"metric": "mask_ready_eye_os_count", "value": int((ready["eye"] == "OS").sum())},
                {"metric": "mask_ready_eye_unknown_count", "value": int((ready["eye"] == "unknown").sum())},
            ]
        )

        for column in [
            "vertical_cdr_from_derived_mask",
            "cup_to_disc_area_ratio",
            "cup_inside_disc_fraction",
            "disc_area_pixels",
            "cup_area_pixels",
        ]:
            rows.append({"metric": f"{column}_mean", "value": float(ready[column].mean())})
            rows.append({"metric": f"{column}_median", "value": float(ready[column].median())})
            rows.append({"metric": f"{column}_min", "value": float(ready[column].min())})
            rows.append({"metric": f"{column}_max", "value": float(ready[column].max())})

    status_counts = (
        manifest
        .groupby(["extraction_status", "mask_ready"], dropna=False)
        .size()
        .rename("count")
        .reset_index()
    )

    for _, row in status_counts.iterrows():
        status = str(row["extraction_status"])
        ready_label = "ready" if bool(row["mask_ready"]) else "not_ready"
        rows.append(
            {
                "metric": f"status_{status}_{ready_label}_count",
                "value": int(row["count"]),
            }
        )

    return pd.DataFrame(rows)


def make_public_safe_extraction_summary(manifest: pd.DataFrame) -> pd.DataFrame:
    """
    Return an aggregate-only extraction summary safe for committed reports.

    This intentionally excludes raw paths, sample hashes, and patient hashes.
    """
    summary = summarize_extraction_manifest(manifest)
    summary.insert(0, "dataset", "clinical_psd_annotations")
    summary.insert(1, "source_type", "annotated_psd_composites")
    summary.insert(2, "mask_source", "red_blue_overlay_extraction")
    summary.insert(3, "contains_private_paths", False)
    summary.insert(4, "contains_patient_hashes", False)
    return summary


def make_qa_contact_sheet(
    qa_tiles: list[dict[str, Any]],
    output_path: Path,
    *,
    tile_width: int = 240,
    tile_height: int = 240,
    label_height: int = 48,
) -> None:
    """Write a private QA contact sheet for visual inspection."""
    if not qa_tiles:
        return

    columns = 3
    rows_count = len(qa_tiles)

    sheet = Image.new(
        "RGB",
        (columns * tile_width, rows_count * (tile_height + label_height)),
        color=(255, 255, 255),
    )
    draw = ImageDraw.Draw(sheet)

    for row_index, tile in enumerate(qa_tiles):
        images = [tile["original"], tile["clean"], tile["overlay"]]
        labels = ["annotated composite", "inpainted input", "derived mask overlay"]

        for col_index, (image_array, label) in enumerate(zip(images, labels)):
            image = Image.fromarray(image_array).convert("RGB")
            image.thumbnail((tile_width, tile_height))
            x = col_index * tile_width + (tile_width - image.width) // 2
            y = row_index * (tile_height + label_height)
            sheet.paste(image, (x, y))

            text = label
            if col_index == 0:
                text = f"{tile['sample_hash']} | eye={tile['eye']} | ready={tile['mask_ready']}"

            draw.text((col_index * tile_width + 8, y + tile_height + 4), text, fill=(0, 0, 0))

    sheet.save(output_path)


def build_clinical_psd_annotation_dataset(
    *,
    psd_root: Path,
    output_dir: Path,
    project_root: Path,
    qa_tile_limit: int = 24,
) -> dict[str, Any]:
    """
    Build private clean images, derived masks, manifest, summary, and QA sheet.
    """
    clean_dir = output_dir / "clean_images"
    mask_dir = output_dir / "derived_masks"
    qa_dir = output_dir / "qa"

    for directory in [clean_dir, mask_dir, qa_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "clinical_psd_derived_mask_manifest_private.csv"
    summary_path = output_dir / "clinical_psd_extraction_summary_private.csv"
    qa_contact_sheet_path = qa_dir / "clinical_psd_extraction_contact_sheet_private.png"

    psd_paths = sorted(Path(psd_root).rglob("*.psd"))

    rows: list[dict[str, object]] = []
    qa_tiles: list[dict[str, Any]] = []

    for path in psd_paths:
        row, rgb, clean_rgb, label_mask = process_psd_annotation(
            path,
            project_root=project_root,
            clean_dir=clean_dir,
            mask_dir=mask_dir,
        )
        rows.append(row)

        if rgb is not None and clean_rgb is not None and label_mask is not None and len(qa_tiles) < qa_tile_limit:
            qa_tiles.append(
                {
                    "sample_hash": row["sample_hash"],
                    "eye": row["eye"],
                    "mask_ready": row["mask_ready"],
                    "original": rgb,
                    "clean": clean_rgb,
                    "overlay": overlay_mask(clean_rgb, label_mask),
                }
            )

    manifest = pd.DataFrame(rows)
    summary = summarize_extraction_manifest(manifest)
    public_summary = make_public_safe_extraction_summary(manifest)

    manifest.to_csv(manifest_path, index=False)
    summary.to_csv(summary_path, index=False)
    make_qa_contact_sheet(qa_tiles, qa_contact_sheet_path)

    return {
        "manifest": manifest,
        "summary": summary,
        "public_summary": public_summary,
        "paths": {
            "manifest_path": manifest_path,
            "summary_path": summary_path,
            "qa_contact_sheet_path": qa_contact_sheet_path,
            "clean_dir": clean_dir,
            "mask_dir": mask_dir,
        },
    }


__all__ = [
    "build_clinical_psd_annotation_dataset",
    "build_clean_image",
    "connected_components",
    "fill_component_as_ellipse",
    "load_psd_composite",
    "make_public_safe_extraction_summary",
    "overlay_mask",
    "parse_patient_and_eye",
    "process_psd_annotation",
    "select_annotation_pair",
    "stable_hash",
    "strict_annotation_color_masks",
    "summarize_extraction_manifest",
    "vertical_height",
]
