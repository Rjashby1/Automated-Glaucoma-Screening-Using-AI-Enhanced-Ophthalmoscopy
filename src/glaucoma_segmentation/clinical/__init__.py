"""Clinical data utilities for glaucoma segmentation generalization experiments."""

from glaucoma_segmentation.clinical.datasets import (
    ClinicalDerivedMaskDataset,
    filter_manifest_for_clinical_split,
    make_grouped_clinical_adaptation_splits,
    summarize_clinical_adaptation_splits,
)
from glaucoma_segmentation.clinical.evaluation import (
    binary_dice,
    evaluate_model_on_clinical_loader,
    summarize_image_level_clinical_metrics,
    summarize_patient_weighted_clinical_metrics,
    vertical_cdr_from_label_array,
    vertical_extent,
)
from glaucoma_segmentation.clinical.psd_annotations import (
    build_clean_image,
    build_clinical_psd_annotation_dataset,
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
    "build_clean_image",
    "build_clinical_psd_annotation_dataset",
    "evaluate_model_on_clinical_loader",
    "filter_manifest_for_clinical_split",
    "make_grouped_clinical_adaptation_splits",
    "make_public_safe_extraction_summary",
    "overlay_mask",
    "parse_patient_and_eye",
    "process_psd_annotation",
    "stable_hash",
    "strict_annotation_color_masks",
    "summarize_clinical_adaptation_splits",
    "summarize_extraction_manifest",
    "summarize_image_level_clinical_metrics",
    "summarize_patient_weighted_clinical_metrics",
    "vertical_cdr_from_label_array",
    "vertical_extent",
]
