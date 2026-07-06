"""
Clinical-data utilities for glaucoma segmentation experiments.
"""

from glaucoma_segmentation.clinical.datasets import ClinicalDerivedMaskDataset
from glaucoma_segmentation.clinical.evaluation import (
    binary_dice,
    evaluate_model_on_clinical_loader,
    summarize_image_level_clinical_metrics,
    summarize_patient_weighted_clinical_metrics,
    vertical_cdr_from_label_array,
    vertical_extent,
)
from glaucoma_segmentation.clinical.psd_annotations import (
    build_clinical_psd_annotation_dataset,
    build_clean_image,
    make_public_safe_extraction_summary,
    overlay_mask,
    parse_patient_and_eye,
    process_psd_annotation,
    stable_hash,
    strict_annotation_color_masks,
    summarize_extraction_manifest,
)

__all__ = [
    "ClinicalDerivedMaskDataset",
    "binary_dice",
    "build_clinical_psd_annotation_dataset",
    "build_clean_image",
    "evaluate_model_on_clinical_loader",
    "make_public_safe_extraction_summary",
    "overlay_mask",
    "parse_patient_and_eye",
    "process_psd_annotation",
    "stable_hash",
    "strict_annotation_color_masks",
    "summarize_extraction_manifest",
    "summarize_image_level_clinical_metrics",
    "summarize_patient_weighted_clinical_metrics",
    "vertical_cdr_from_label_array",
    "vertical_extent",
]
