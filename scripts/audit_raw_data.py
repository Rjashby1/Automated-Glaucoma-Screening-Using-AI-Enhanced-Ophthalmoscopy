"""
audit_raw_data.py

Project-aware raw data audit for the UVA MSDS capstone:

    Automated Glaucoma Screening Using AI-Enhanced Ophthalmoscopy

This script assumes scripts/prepare_raw_data.py has already been run and that
the local generated raw-data workspace exists here:

    data/raw/

The audit is intentionally aligned to the project objective:

    Identify and organize the data needed to improve optic cup and optic disc
    segmentation on low-quality head-mounted ophthalmoscopy frames, while also
    preserving public fundus datasets, prior baseline artifacts, masks, labels,
    metadata, and model checkpoints for reproducible experimentation.

Primary questions this audit tries to answer:
    1. Where are likely public/reference fundus datasets such as ORIGA?
    2. Where are likely sponsor/clinic/head-mounted camera frames?
    3. Where are masks, labels, predictions, PSDs, bounding boxes, and metadata?
    4. Where are prior baseline model artifacts, including U-Net/SAM code?
    5. What directories may support grouped splitting by patient/video/eye?
    6. What folders should be manually verified before building train/val/test splits?
    7. What is the evidence map for the project plan:
        - public clean data
        - sponsor low-quality data
        - labeled masks / ground truth
        - prior model outputs
        - candidate holdout data
        - augmentation / synthetic data experiments

Outputs are written by default to:

    reports/data_audit/

These are summary-level reports. They do not copy raw image data or model files.

Expected repo layout:

repo_root/
    data/raw/                  # ignored by Git
    reports/data_audit/        # summary reports, possibly tracked by Git
    scripts/audit_raw_data.py  # tracked by Git
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Project-specific constants
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp",
}

MASK_LABEL_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".mat",
    ".psd",
    ".csv",
    ".txt",
}

MODEL_EXTENSIONS = {
    ".ckpt",
    ".pth",
    ".pt",
    ".onnx",
    ".h5",
    ".pkl",
    ".joblib",
}

CODE_EXTENSIONS = {
    ".py",
    ".ipynb",
    ".sh",
    ".bat",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
}

DOCUMENT_EXTENSIONS = {
    ".docx",
    ".pdf",
    ".pptx",
    ".xlsx",
    ".txt",
    ".md",
    ".log",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".m4v",
}

METADATA_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".mat",
}

PUBLIC_DATASET_KEYWORDS = {
    "origa",
    "refuge",
    "drishti",
    "rim-one",
    "rimone",
    "fundus",
    "kaggle",
    "oct",
}

SPONSOR_DATASET_KEYWORDS = {
    "clinic",
    "subject",
    "patient",
    "head",
    "mounted",
    "discview",
    "disc_view",
    "dr_d",
    "dirghangi",
    "psd_clinic",
    "uva",
    "video",
    "frame",
    "frames",
}

MASK_LABEL_KEYWORDS = {
    "mask",
    "masks",
    "label",
    "labels",
    "cup",
    "disc",
    "disk",
    "oc",
    "od",
    "prediction",
    "predictions",
    "pred",
    "threshold",
    "thresholded",
    "segmentation",
    "ground",
    "truth",
    "bbox",
    "bounding",
    "box",
    "annotation",
    "annotations",
    "psd",
}

PRIOR_BASELINE_KEYWORDS = {
    "unet",
    "u-net",
    "sam",
    "medsam",
    "medical-sam",
    "checkpoint",
    "checkpoints",
    "model",
    "models",
    "state_dict",
    "training_logs",
    "lightning",
}

SPLIT_RELEVANT_KEYWORDS = {
    "train",
    "training",
    "test",
    "testing",
    "val",
    "validation",
    "holdout",
    "split",
    "splits",
}

QUALITY_DOMAIN_KEYWORDS = {
    "blur",
    "glare",
    "low",
    "contrast",
    "compressed",
    "processed",
    "preprocessed",
    "non_processed",
    "non-processed",
    "threshold",
    "thresholded",
}

RAW_INVENTORY_FOLDERS_TO_SKIP = {
    "_inventory",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FileRecord:
    """Metadata for one file in data/raw."""

    path: Path
    relative_path: Path
    parent_relative_path: Path
    name: str
    extension: str
    size_bytes: int
    size_mb: float
    modified_time: str


@dataclass
class DirectorySummary:
    """Summary statistics for one directory."""

    relative_path: Path
    file_count: int
    total_size_bytes: int
    total_size_mb: float
    extension_counts: Counter[str]
    image_file_count: int
    mask_label_file_count: int
    model_file_count: int
    code_file_count: int
    document_file_count: int
    video_file_count: int
    metadata_file_count: int
    public_keyword_hits: int
    sponsor_keyword_hits: int
    mask_label_keyword_hits: int
    baseline_keyword_hits: int
    split_keyword_hits: int
    quality_domain_keyword_hits: int


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def get_repo_root() -> Path:
    """
    Infer repo root from this script location.

    Expected:
        repo_root/scripts/audit_raw_data.py
    """
    return Path(__file__).resolve().parents[1]


def ensure_dir(path: Path) -> None:
    """Create directory if needed."""
    path.mkdir(parents=True, exist_ok=True)


def bytes_to_mb(size_bytes: int) -> float:
    """Convert bytes to megabytes."""
    return size_bytes / (1024 * 1024)


def normalize_extension(path: Path) -> str:
    """Return lowercase extension, or [no extension]."""
    suffix = path.suffix.lower()
    return suffix if suffix else "[no extension]"


def path_text(path: Path) -> str:
    """Return normalized lowercase path text for keyword matching."""
    return str(path).replace("\\", "/").lower()


def count_keyword_hits(path: Path, keywords: set[str]) -> int:
    """Count distinct keyword hits in a path."""
    text = path_text(path)
    return sum(1 for keyword in keywords if keyword.lower() in text)


def matched_keywords(path: Path, keywords: set[str]) -> list[str]:
    """Return sorted keywords found in a path."""
    text = path_text(path)
    return sorted(keyword for keyword in keywords if keyword.lower() in text)


def format_counter(counter: Counter[str]) -> str:
    """Format Counter as compact semicolon-separated text."""
    return "; ".join(f"{key}:{value}" for key, value in counter.most_common())


def should_skip_file(relative_path: Path) -> bool:
    """
    Skip generated inventory files inside data/raw/_inventory.

    The audit should describe raw-data contents, not previous logs.
    """
    parts_lower = {part.lower() for part in relative_path.parts}
    return bool(parts_lower.intersection(RAW_INVENTORY_FOLDERS_TO_SKIP))


def safe_slug(text: str) -> str:
    """Create a safe-ish identifier from path text."""
    text = text.replace("\\", "/")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:120] if len(text) > 120 else text


# ---------------------------------------------------------------------------
# Scanning and summaries
# ---------------------------------------------------------------------------

def scan_files(data_raw: Path) -> list[FileRecord]:
    """
    Scan data/raw and return file records.
    """
    records: list[FileRecord] = []

    for path in sorted(data_raw.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(data_raw)

        if should_skip_file(relative_path):
            continue

        stat = path.stat()
        extension = normalize_extension(path)

        records.append(
            FileRecord(
                path=path,
                relative_path=relative_path,
                parent_relative_path=relative_path.parent,
                name=path.name,
                extension=extension,
                size_bytes=stat.st_size,
                size_mb=round(bytes_to_mb(stat.st_size), 6),
                modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat(
                    timespec="seconds"
                ),
            )
        )

    return records


def summarize_extensions(records: list[FileRecord]) -> list[dict[str, object]]:
    """
    Summarize files by extension.
    """
    count_by_ext: Counter[str] = Counter()
    size_by_ext: Counter[str] = Counter()

    for record in records:
        count_by_ext[record.extension] += 1
        size_by_ext[record.extension] += record.size_bytes

    rows = []

    for extension, count in count_by_ext.most_common():
        rows.append(
            {
                "extension": extension,
                "file_count": count,
                "total_size_mb": round(bytes_to_mb(size_by_ext[extension]), 6),
            }
        )

    return rows


def summarize_top_level_sources(records: list[FileRecord]) -> list[dict[str, object]]:
    """
    Summarize files by top-level area under data/raw.

    Example:
        extracted_zips/
        loose_files/
    """
    count_by_source: Counter[str] = Counter()
    size_by_source: Counter[str] = Counter()

    for record in records:
        source = record.relative_path.parts[0] if record.relative_path.parts else "."
        count_by_source[source] += 1
        size_by_source[source] += record.size_bytes

    rows = []

    for source, count in count_by_source.most_common():
        rows.append(
            {
                "source_area": source,
                "file_count": count,
                "total_size_mb": round(bytes_to_mb(size_by_source[source]), 6),
            }
        )

    return rows


def summarize_source_packages(records: list[FileRecord]) -> list[dict[str, object]]:
    """
    Summarize practical source package areas.

    Examples:
        extracted_zips/convert_psd_to_label
        extracted_zips/rivanna_train_discview
        extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive
    """
    count_by_package: Counter[str] = Counter()
    size_by_package: Counter[str] = Counter()

    for record in records:
        parts = record.relative_path.parts

        if len(parts) >= 2 and parts[0] == "extracted_zips":
            if len(parts) >= 3 and parts[1] == "Tien_DiscView":
                package = "/".join(parts[:3])
            else:
                package = "/".join(parts[:2])
        else:
            package = parts[0] if parts else "."

        count_by_package[package] += 1
        size_by_package[package] += record.size_bytes

    rows = []

    for package, count in count_by_package.most_common():
        rows.append(
            {
                "package_area": package,
                "file_count": count,
                "total_size_mb": round(bytes_to_mb(size_by_package[package]), 6),
                "public_keyword_hits": count_keyword_hits(Path(package), PUBLIC_DATASET_KEYWORDS),
                "sponsor_keyword_hits": count_keyword_hits(Path(package), SPONSOR_DATASET_KEYWORDS),
                "baseline_keyword_hits": count_keyword_hits(Path(package), PRIOR_BASELINE_KEYWORDS),
            }
        )

    return rows


def summarize_directories(records: list[FileRecord]) -> list[DirectorySummary]:
    """
    Summarize files by immediate parent directory.
    """
    grouped: dict[Path, list[FileRecord]] = defaultdict(list)

    for record in records:
        grouped[record.parent_relative_path].append(record)

    summaries: list[DirectorySummary] = []

    for directory, directory_records in grouped.items():
        extension_counts: Counter[str] = Counter(
            record.extension for record in directory_records
        )
        total_size_bytes = sum(record.size_bytes for record in directory_records)

        image_file_count = sum(
            1 for record in directory_records if record.extension in IMAGE_EXTENSIONS
        )
        mask_label_file_count = sum(
            1
            for record in directory_records
            if record.extension in MASK_LABEL_EXTENSIONS
            and count_keyword_hits(record.relative_path, MASK_LABEL_KEYWORDS) > 0
        )
        model_file_count = sum(
            1 for record in directory_records if record.extension in MODEL_EXTENSIONS
        )
        code_file_count = sum(
            1 for record in directory_records if record.extension in CODE_EXTENSIONS
        )
        document_file_count = sum(
            1 for record in directory_records if record.extension in DOCUMENT_EXTENSIONS
        )
        video_file_count = sum(
            1 for record in directory_records if record.extension in VIDEO_EXTENSIONS
        )
        metadata_file_count = sum(
            1 for record in directory_records if record.extension in METADATA_EXTENSIONS
        )

        summaries.append(
            DirectorySummary(
                relative_path=directory,
                file_count=len(directory_records),
                total_size_bytes=total_size_bytes,
                total_size_mb=round(bytes_to_mb(total_size_bytes), 6),
                extension_counts=extension_counts,
                image_file_count=image_file_count,
                mask_label_file_count=mask_label_file_count,
                model_file_count=model_file_count,
                code_file_count=code_file_count,
                document_file_count=document_file_count,
                video_file_count=video_file_count,
                metadata_file_count=metadata_file_count,
                public_keyword_hits=count_keyword_hits(directory, PUBLIC_DATASET_KEYWORDS),
                sponsor_keyword_hits=count_keyword_hits(directory, SPONSOR_DATASET_KEYWORDS),
                mask_label_keyword_hits=count_keyword_hits(directory, MASK_LABEL_KEYWORDS),
                baseline_keyword_hits=count_keyword_hits(directory, PRIOR_BASELINE_KEYWORDS),
                split_keyword_hits=count_keyword_hits(directory, SPLIT_RELEVANT_KEYWORDS),
                quality_domain_keyword_hits=count_keyword_hits(directory, QUALITY_DOMAIN_KEYWORDS),
            )
        )

    return sorted(summaries, key=lambda row: row.total_size_bytes, reverse=True)


def directory_summary_to_rows(
    summaries: list[DirectorySummary],
    limit: int | None = None,
) -> list[dict[str, object]]:
    """
    Convert directory summaries to CSV rows.
    """
    selected = summaries[:limit] if limit is not None else summaries
    rows = []

    for summary in selected:
        rows.append(
            {
                "directory": str(summary.relative_path),
                "file_count": summary.file_count,
                "total_size_mb": summary.total_size_mb,
                "image_file_count": summary.image_file_count,
                "mask_label_file_count": summary.mask_label_file_count,
                "model_file_count": summary.model_file_count,
                "code_file_count": summary.code_file_count,
                "document_file_count": summary.document_file_count,
                "video_file_count": summary.video_file_count,
                "metadata_file_count": summary.metadata_file_count,
                "public_keyword_hits": summary.public_keyword_hits,
                "sponsor_keyword_hits": summary.sponsor_keyword_hits,
                "mask_label_keyword_hits": summary.mask_label_keyword_hits,
                "baseline_keyword_hits": summary.baseline_keyword_hits,
                "split_keyword_hits": summary.split_keyword_hits,
                "quality_domain_keyword_hits": summary.quality_domain_keyword_hits,
                "extension_counts": format_counter(summary.extension_counts),
            }
        )

    return rows


# ---------------------------------------------------------------------------
# Project-aware candidate identification
# ---------------------------------------------------------------------------

def identify_candidate_image_dirs(
    summaries: list[DirectorySummary],
    min_images: int,
) -> list[dict[str, object]]:
    """
    Identify directories likely to contain image datasets.
    """
    rows = []

    for summary in summaries:
        if summary.image_file_count < min_images:
            continue

        if summary.sponsor_keyword_hits > summary.public_keyword_hits:
            likely_source = "sponsor_or_clinic"
        elif summary.public_keyword_hits > summary.sponsor_keyword_hits:
            likely_source = "public_or_reference"
        else:
            likely_source = "uncertain"

        rows.append(
            {
                "directory": str(summary.relative_path),
                "file_count": summary.file_count,
                "image_file_count": summary.image_file_count,
                "total_size_mb": summary.total_size_mb,
                "likely_source": likely_source,
                "public_keyword_hits": summary.public_keyword_hits,
                "sponsor_keyword_hits": summary.sponsor_keyword_hits,
                "mask_label_keyword_hits": summary.mask_label_keyword_hits,
                "quality_domain_keyword_hits": summary.quality_domain_keyword_hits,
                "extension_counts": format_counter(summary.extension_counts),
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            str(row["likely_source"]) == "sponsor_or_clinic",
            int(row["image_file_count"]),
            float(row["total_size_mb"]),
        ),
        reverse=True,
    )


def identify_candidate_mask_label_dirs(
    summaries: list[DirectorySummary],
    min_files: int,
) -> list[dict[str, object]]:
    """
    Identify directories likely to contain masks, labels, predictions,
    segmentation outputs, PSD annotations, or bounding boxes.
    """
    rows = []

    for summary in summaries:
        if summary.file_count < min_files:
            continue

        if summary.mask_label_keyword_hits == 0 and summary.mask_label_file_count == 0:
            continue

        rows.append(
            {
                "directory": str(summary.relative_path),
                "file_count": summary.file_count,
                "image_file_count": summary.image_file_count,
                "mask_label_file_count": summary.mask_label_file_count,
                "metadata_file_count": summary.metadata_file_count,
                "total_size_mb": summary.total_size_mb,
                "mask_label_keyword_hits": summary.mask_label_keyword_hits,
                "public_keyword_hits": summary.public_keyword_hits,
                "sponsor_keyword_hits": summary.sponsor_keyword_hits,
                "extension_counts": format_counter(summary.extension_counts),
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            int(row["mask_label_keyword_hits"]),
            int(row["mask_label_file_count"]),
            int(row["image_file_count"]),
            int(row["file_count"]),
        ),
        reverse=True,
    )


def identify_public_reference_dirs(
    summaries: list[DirectorySummary],
    min_images: int,
) -> list[dict[str, object]]:
    """
    Identify likely public/reference fundus dataset folders, especially ORIGA.
    """
    rows = []

    for summary in summaries:
        if summary.public_keyword_hits == 0:
            continue

        if summary.image_file_count < min_images and summary.metadata_file_count == 0:
            continue

        rows.append(
            {
                "directory": str(summary.relative_path),
                "file_count": summary.file_count,
                "image_file_count": summary.image_file_count,
                "metadata_file_count": summary.metadata_file_count,
                "total_size_mb": summary.total_size_mb,
                "matched_public_keywords": "; ".join(
                    matched_keywords(summary.relative_path, PUBLIC_DATASET_KEYWORDS)
                ),
                "mask_label_keyword_hits": summary.mask_label_keyword_hits,
                "extension_counts": format_counter(summary.extension_counts),
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            "origa" in str(row["matched_public_keywords"]).lower(),
            int(row["image_file_count"]),
            float(row["total_size_mb"]),
        ),
        reverse=True,
    )


def identify_sponsor_clinic_dirs(
    summaries: list[DirectorySummary],
    min_files: int,
) -> list[dict[str, object]]:
    """
    Identify likely sponsor/clinic/head-mounted camera data folders.
    """
    rows = []

    for summary in summaries:
        if summary.sponsor_keyword_hits == 0:
            continue

        if summary.file_count < min_files:
            continue

        rows.append(
            {
                "directory": str(summary.relative_path),
                "file_count": summary.file_count,
                "image_file_count": summary.image_file_count,
                "video_file_count": summary.video_file_count,
                "metadata_file_count": summary.metadata_file_count,
                "mask_label_file_count": summary.mask_label_file_count,
                "total_size_mb": summary.total_size_mb,
                "matched_sponsor_keywords": "; ".join(
                    matched_keywords(summary.relative_path, SPONSOR_DATASET_KEYWORDS)
                ),
                "mask_label_keyword_hits": summary.mask_label_keyword_hits,
                "quality_domain_keyword_hits": summary.quality_domain_keyword_hits,
                "extension_counts": format_counter(summary.extension_counts),
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            int(row["image_file_count"]) + int(row["video_file_count"]),
            float(row["total_size_mb"]),
        ),
        reverse=True,
    )


def identify_group_split_clues(records: list[FileRecord]) -> list[dict[str, object]]:
    """
    Identify file paths and names that may contain patient/video/eye/frame clues.

    This is heuristic. It helps decide whether grouped splitting by
    patient/video/eye is possible.
    """
    patterns = {
        "patient_like_P_number": re.compile(r"\bP\d+", re.IGNORECASE),
        "subject_number": re.compile(r"\bSubject[-_ ]?\d+", re.IGNORECASE),
        "eye_OD": re.compile(r"(^|[^A-Za-z])OD([^A-Za-z]|$)", re.IGNORECASE),
        "eye_OS": re.compile(r"(^|[^A-Za-z])OS([^A-Za-z]|$)", re.IGNORECASE),
        "cd_number": re.compile(r"\bCD[-_ ]?\d+", re.IGNORECASE),
        "frame_number": re.compile(r"\bframe[-_ ]?\d+", re.IGNORECASE),
        "image_id_number": re.compile(r"\b\d{3,4}\b"),
    }

    rows = []

    for record in records:
        text = str(record.relative_path)

        matched = [
            label
            for label, pattern in patterns.items()
            if pattern.search(text)
        ]

        if not matched:
            continue

        rows.append(
            {
                "relative_path": str(record.relative_path),
                "file_name": record.name,
                "extension": record.extension,
                "size_mb": record.size_mb,
                "matched_grouping_clues": "; ".join(matched),
            }
        )

    return rows


def identify_prior_baseline_artifacts(
    records: list[FileRecord],
    summaries: list[DirectorySummary],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """
    Identify likely prior U-Net/SAM/checkpoint artifacts.

    Returns:
        baseline_file_rows, baseline_directory_rows
    """
    baseline_file_rows = []

    for record in records:
        hit_count = count_keyword_hits(record.relative_path, PRIOR_BASELINE_KEYWORDS)
        is_model = record.extension in MODEL_EXTENSIONS
        is_code = record.extension in CODE_EXTENSIONS

        if hit_count == 0 and not is_model:
            continue

        baseline_file_rows.append(
            {
                "relative_path": str(record.relative_path),
                "file_name": record.name,
                "extension": record.extension,
                "size_mb": record.size_mb,
                "keyword_hits": hit_count,
                "artifact_type": classify_artifact_type(record),
            }
        )

    baseline_directory_rows = []

    for summary in summaries:
        if summary.baseline_keyword_hits == 0 and summary.model_file_count == 0:
            continue

        baseline_directory_rows.append(
            {
                "directory": str(summary.relative_path),
                "file_count": summary.file_count,
                "model_file_count": summary.model_file_count,
                "code_file_count": summary.code_file_count,
                "total_size_mb": summary.total_size_mb,
                "baseline_keyword_hits": summary.baseline_keyword_hits,
                "extension_counts": format_counter(summary.extension_counts),
            }
        )

    baseline_file_rows = sorted(
        baseline_file_rows,
        key=lambda row: (
            str(row["artifact_type"]) == "model_artifact",
            int(row["keyword_hits"]),
            float(row["size_mb"]),
        ),
        reverse=True,
    )

    baseline_directory_rows = sorted(
        baseline_directory_rows,
        key=lambda row: (
            int(row["model_file_count"]),
            int(row["code_file_count"]),
            int(row["baseline_keyword_hits"]),
            float(row["total_size_mb"]),
        ),
        reverse=True,
    )

    return baseline_file_rows, baseline_directory_rows


def classify_artifact_type(record: FileRecord) -> str:
    """Classify a file into a project-relevant artifact type."""
    if record.extension in MODEL_EXTENSIONS:
        return "model_artifact"
    if record.extension in CODE_EXTENSIONS:
        return "code_or_config"
    if record.extension in VIDEO_EXTENSIONS:
        return "video"
    if record.extension in IMAGE_EXTENSIONS:
        if count_keyword_hits(record.relative_path, MASK_LABEL_KEYWORDS) > 0:
            return "mask_label_prediction_image"
        return "image"
    if record.extension in METADATA_EXTENSIONS:
        return "metadata_or_annotation"
    if record.extension in DOCUMENT_EXTENSIONS:
        return "document_or_log"
    return "other"


def identify_artifacts(
    records: list[FileRecord],
    extensions: set[str],
) -> list[dict[str, object]]:
    """
    Identify files matching a set of extensions.
    """
    rows = []

    for record in records:
        if record.extension not in extensions:
            continue

        rows.append(
            {
                "relative_path": str(record.relative_path),
                "file_name": record.name,
                "extension": record.extension,
                "size_mb": record.size_mb,
                "artifact_type": classify_artifact_type(record),
                "modified_time": record.modified_time,
            }
        )

    return sorted(rows, key=lambda row: float(row["size_mb"]), reverse=True)


def identify_manual_review_targets(
    candidate_image_rows: list[dict[str, object]],
    candidate_mask_rows: list[dict[str, object]],
    public_reference_rows: list[dict[str, object]],
    sponsor_clinic_rows: list[dict[str, object]],
    baseline_directory_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Build a prioritized manual review list.
    """
    rows = []

    def add_rows(source_rows: list[dict[str, object]], review_type: str, priority: int) -> None:
        for row in source_rows:
            rows.append(
                {
                    "priority": priority,
                    "review_type": review_type,
                    "directory": row.get("directory", ""),
                    "file_count": row.get("file_count", ""),
                    "image_file_count": row.get("image_file_count", ""),
                    "total_size_mb": row.get("total_size_mb", ""),
                    "why_review": review_reason(review_type),
                }
            )

    add_rows(sponsor_clinic_rows[:30], "sponsor_clinic_candidate", 1)
    add_rows(candidate_mask_rows[:30], "mask_label_candidate", 2)
    add_rows(public_reference_rows[:30], "public_reference_candidate", 3)
    add_rows(candidate_image_rows[:30], "image_dataset_candidate", 4)
    add_rows(baseline_directory_rows[:30], "prior_baseline_candidate", 5)

    deduped = []
    seen = set()

    for row in rows:
        key = (row["review_type"], row["directory"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    return sorted(
        deduped,
        key=lambda row: (
            int(row["priority"]),
            -float(row["total_size_mb"] or 0),
        ),
    )


def review_reason(review_type: str) -> str:
    """Human-readable reason for manual review."""
    reasons = {
        "sponsor_clinic_candidate": (
            "Potential Dr. Dirghangi / clinic / head-mounted frame data. "
            "Needed for sponsor holdout and grouped splitting."
        ),
        "mask_label_candidate": (
            "Potential cup/disc masks, predictions, PSD labels, or bounding boxes. "
            "Needed to pair images with ground truth."
        ),
        "public_reference_candidate": (
            "Potential public clean fundus data such as ORIGA. "
            "Needed for public train/validation/holdout."
        ),
        "image_dataset_candidate": (
            "Large image directory. Verify whether images are raw inputs, processed inputs, "
            "or derived artifacts."
        ),
        "prior_baseline_candidate": (
            "Potential prior U-Net/SAM/checkpoint artifacts. "
            "Useful for baseline reproduction or comparison."
        ),
    }
    return reasons.get(review_type, "Manual verification recommended.")


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """
    Write list of dictionaries to CSV.

    If rows is empty, write a one-column placeholder.
    """
    ensure_dir(path.parent)

    if not rows:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["message"])
            writer.writeheader()
            writer.writerow({"message": "No rows found."})
        return

    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, object]], columns: list[str], limit: int = 20) -> str:
    """
    Create a simple Markdown table.
    """
    if not rows:
        return "_No rows found._\n"

    selected = rows[:limit]

    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")

    for row in selected:
        values = [str(row.get(column, "")) for column in columns]
        values = [value.replace("\n", " ").replace("|", "\\|") for value in values]
        lines.append("| " + " | ".join(values) + " |")

    if len(rows) > limit:
        lines.append("")
        lines.append(f"_Showing top {limit} of {len(rows)} rows._")

    return "\n".join(lines) + "\n"


def write_markdown_report(
    output_file: Path,
    data_raw: Path,
    records: list[FileRecord],
    extension_rows: list[dict[str, object]],
    source_area_rows: list[dict[str, object]],
    package_rows: list[dict[str, object]],
    top_directory_rows: list[dict[str, object]],
    candidate_image_rows: list[dict[str, object]],
    candidate_mask_rows: list[dict[str, object]],
    public_reference_rows: list[dict[str, object]],
    sponsor_clinic_rows: list[dict[str, object]],
    baseline_file_rows: list[dict[str, object]],
    baseline_directory_rows: list[dict[str, object]],
    model_artifact_rows: list[dict[str, object]],
    code_artifact_rows: list[dict[str, object]],
    document_artifact_rows: list[dict[str, object]],
    video_artifact_rows: list[dict[str, object]],
    metadata_artifact_rows: list[dict[str, object]],
    group_split_rows: list[dict[str, object]],
    manual_review_rows: list[dict[str, object]],
) -> None:
    """
    Write a project-aware Markdown summary.
    """
    ensure_dir(output_file.parent)

    total_size_bytes = sum(record.size_bytes for record in records)
    total_images = sum(1 for record in records if record.extension in IMAGE_EXTENSIONS)
    total_masks_or_labels = sum(
        1
        for record in records
        if record.extension in MASK_LABEL_EXTENSIONS
        and count_keyword_hits(record.relative_path, MASK_LABEL_KEYWORDS) > 0
    )
    total_models = sum(1 for record in records if record.extension in MODEL_EXTENSIONS)
    total_code = sum(1 for record in records if record.extension in CODE_EXTENSIONS)
    total_docs = sum(1 for record in records if record.extension in DOCUMENT_EXTENSIONS)
    total_videos = sum(1 for record in records if record.extension in VIDEO_EXTENSIONS)
    total_metadata = sum(1 for record in records if record.extension in METADATA_EXTENSIONS)

    with output_file.open("w", encoding="utf-8") as f:
        f.write("# Raw Data Audit Summary\n\n")
        f.write(f"Created: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write(f"Audited folder: `{data_raw}`\n\n")

        f.write("## Project Objective Context\n\n")
        f.write(
            "This audit supports a data-centric segmentation and generalization study for "
            "optic cup and optic disc segmentation. The core project question is whether "
            "targeted augmentation, synthetic data expansion, and careful held-out evaluation "
            "can improve segmentation on low-quality head-mounted ophthalmoscopy frames while "
            "maintaining performance on clean public fundus data.\n\n"
        )
        f.write(
            "The most important audit task is to separate public/reference data from "
            "sponsor/clinic data, identify cup/disc labels or masks, and determine whether "
            "patient/video/eye grouping information exists for leakage-safe train/validation/test splits.\n\n"
        )

        f.write("## High-Level Counts\n\n")
        f.write(f"- Total files audited: **{len(records):,}**\n")
        f.write(f"- Total audited size: **{round(bytes_to_mb(total_size_bytes), 3):,} MB**\n")
        f.write(f"- Image files: **{total_images:,}**\n")
        f.write(f"- Possible mask/label/prediction files: **{total_masks_or_labels:,}**\n")
        f.write(f"- Metadata/annotation-like files: **{total_metadata:,}**\n")
        f.write(f"- Video files: **{total_videos:,}**\n")
        f.write(f"- Model artifacts: **{total_models:,}**\n")
        f.write(f"- Code/config artifacts: **{total_code:,}**\n")
        f.write(f"- Document/log artifacts: **{total_docs:,}**\n\n")

        f.write("## Immediate Interpretation\n\n")
        f.write(
            "- Review `manual_review_targets.csv` first. It is the triage list for finding "
            "sponsor data, masks, public data, and prior baseline artifacts.\n"
        )
        f.write(
            "- Review `sponsor_clinic_candidate_dirs.csv` to locate Dr. D / Tien clinic data "
            "and possible grouped split clues.\n"
        )
        f.write(
            "- Review `public_reference_candidate_dirs.csv` to confirm ORIGA or other public "
            "fundus data provided in the handoff.\n"
        )
        f.write(
            "- Review `candidate_mask_label_directories.csv` to pair input images with optic "
            "cup/disc masks, predictions, PSD labels, bounding boxes, or MATLAB annotations.\n"
        )
        f.write(
            "- Review `group_split_clues.csv` before any train/validation/test split. Frames "
            "from the same patient, video, or eye should not be split across train and holdout.\n\n"
        )

        f.write("## File Types\n\n")
        f.write(
            markdown_table(
                extension_rows,
                columns=["extension", "file_count", "total_size_mb"],
                limit=25,
            )
        )
        f.write("\n")

        f.write("## Top-Level Source Areas\n\n")
        f.write(
            markdown_table(
                source_area_rows,
                columns=["source_area", "file_count", "total_size_mb"],
                limit=20,
            )
        )
        f.write("\n")

        f.write("## Source Package Areas\n\n")
        f.write(
            markdown_table(
                package_rows,
                columns=[
                    "package_area",
                    "file_count",
                    "total_size_mb",
                    "public_keyword_hits",
                    "sponsor_keyword_hits",
                    "baseline_keyword_hits",
                ],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Manual Review Targets\n\n")
        f.write(
            markdown_table(
                manual_review_rows,
                columns=[
                    "priority",
                    "review_type",
                    "directory",
                    "file_count",
                    "image_file_count",
                    "total_size_mb",
                    "why_review",
                ],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Public / Reference Dataset Candidates\n\n")
        f.write(
            markdown_table(
                public_reference_rows,
                columns=[
                    "directory",
                    "image_file_count",
                    "metadata_file_count",
                    "total_size_mb",
                    "matched_public_keywords",
                    "extension_counts",
                ],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Sponsor / Clinic / Head-Mounted Data Candidates\n\n")
        f.write(
            markdown_table(
                sponsor_clinic_rows,
                columns=[
                    "directory",
                    "image_file_count",
                    "video_file_count",
                    "metadata_file_count",
                    "mask_label_file_count",
                    "total_size_mb",
                    "matched_sponsor_keywords",
                    "extension_counts",
                ],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Candidate Image Directories\n\n")
        f.write(
            markdown_table(
                candidate_image_rows,
                columns=[
                    "directory",
                    "image_file_count",
                    "total_size_mb",
                    "likely_source",
                    "public_keyword_hits",
                    "sponsor_keyword_hits",
                    "extension_counts",
                ],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Candidate Mask / Label / Prediction Directories\n\n")
        f.write(
            markdown_table(
                candidate_mask_rows,
                columns=[
                    "directory",
                    "file_count",
                    "image_file_count",
                    "mask_label_file_count",
                    "metadata_file_count",
                    "total_size_mb",
                    "mask_label_keyword_hits",
                    "extension_counts",
                ],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Group Split Clues\n\n")
        f.write(
            markdown_table(
                group_split_rows,
                columns=[
                    "relative_path",
                    "extension",
                    "matched_grouping_clues",
                ],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Prior Baseline Directories\n\n")
        f.write(
            markdown_table(
                baseline_directory_rows,
                columns=[
                    "directory",
                    "file_count",
                    "model_file_count",
                    "code_file_count",
                    "total_size_mb",
                    "baseline_keyword_hits",
                    "extension_counts",
                ],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Prior Baseline / Model Files\n\n")
        f.write(
            markdown_table(
                baseline_file_rows,
                columns=[
                    "relative_path",
                    "extension",
                    "size_mb",
                    "artifact_type",
                    "keyword_hits",
                ],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Model Artifacts\n\n")
        f.write(
            markdown_table(
                model_artifact_rows,
                columns=["relative_path", "extension", "size_mb", "artifact_type"],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Code / Config Artifacts\n\n")
        f.write(
            markdown_table(
                code_artifact_rows,
                columns=["relative_path", "extension", "size_mb", "artifact_type"],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Video Artifacts\n\n")
        f.write(
            markdown_table(
                video_artifact_rows,
                columns=["relative_path", "extension", "size_mb", "artifact_type"],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Metadata / Annotation-Like Artifacts\n\n")
        f.write(
            markdown_table(
                metadata_artifact_rows,
                columns=["relative_path", "extension", "size_mb", "artifact_type"],
                limit=60,
            )
        )
        f.write("\n")

        f.write("## Document / Log Artifacts\n\n")
        f.write(
            markdown_table(
                document_artifact_rows,
                columns=["relative_path", "extension", "size_mb", "artifact_type"],
                limit=50,
            )
        )
        f.write("\n")

        f.write("## Largest Directories\n\n")
        f.write(
            markdown_table(
                top_directory_rows,
                columns=[
                    "directory",
                    "file_count",
                    "total_size_mb",
                    "image_file_count",
                    "extension_counts",
                ],
                limit=40,
            )
        )
        f.write("\n")

        f.write("## Recommended Next Manual Steps\n\n")
        f.write("1. Confirm which ORIGA/public folders contain raw images and ground-truth masks.\n")
        f.write("2. Confirm which clinic folders contain Dr. D / Tien head-mounted frames.\n")
        f.write("3. Pair sponsor images with masks, PSD-derived labels, bounding boxes, or clinician labels.\n")
        f.write("4. Decide grouping variables for sponsor splits: patient, video, eye, and/or frame sequence.\n")
        f.write("5. Create a cleaned manifest under `data/processed/manifests/`, not by moving raw files.\n")
        f.write("6. Reproduce or evaluate prior U-Net checkpoints only after the image/mask map is verified.\n")
        f.write("7. Use public and sponsor holdouts separately; sponsor holdout should be the headline generalization metric.\n\n")

        f.write("## Notes\n\n")
        f.write(
            "- This audit is heuristic. It narrows the manual search space but does not prove label correctness.\n"
        )
        f.write(
            "- `data/raw/` should remain ignored by Git. Review summary reports before committing them.\n"
        )
        f.write(
            "- Do not create train/validation/test splits by random frame alone if patient/video/eye grouping is recoverable.\n"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Project-aware audit of generated raw data for glaucoma capstone."
    )

    parser.add_argument(
        "--data-raw",
        type=Path,
        default=None,
        help="Path to generated raw data. Default: repo_root/data/raw",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output folder for audit reports. Default: repo_root/reports/data_audit",
    )

    parser.add_argument(
        "--min-images",
        type=int,
        default=10,
        help="Minimum images required for candidate image directory. Default: 10.",
    )

    parser.add_argument(
        "--min-mask-files",
        type=int,
        default=1,
        help="Minimum files required for candidate mask/label directory. Default: 1.",
    )

    parser.add_argument(
        "--top-n-dirs",
        type=int,
        default=150,
        help="Number of largest directories to write. Default: 150.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repo_root = get_repo_root()
    data_raw = args.data_raw if args.data_raw else repo_root / "data" / "raw"
    output_root = args.output if args.output else repo_root / "reports" / "data_audit"

    print("=" * 80)
    print("Auditing raw data")
    print("=" * 80)
    print(f"Repo root:      {repo_root}")
    print(f"Data raw:       {data_raw}")
    print(f"Output folder:  {output_root}")
    print()

    if not data_raw.exists():
        raise FileNotFoundError(
            f"Raw data folder not found: {data_raw}\n"
            "Run scripts/prepare_raw_data.py first."
        )

    ensure_dir(output_root)

    records = scan_files(data_raw)
    summaries = summarize_directories(records)

    extension_rows = summarize_extensions(records)
    source_area_rows = summarize_top_level_sources(records)
    package_rows = summarize_source_packages(records)
    top_directory_rows = directory_summary_to_rows(
        summaries,
        limit=args.top_n_dirs,
    )

    candidate_image_rows = identify_candidate_image_dirs(
        summaries,
        min_images=args.min_images,
    )
    candidate_mask_rows = identify_candidate_mask_label_dirs(
        summaries,
        min_files=args.min_mask_files,
    )
    public_reference_rows = identify_public_reference_dirs(
        summaries,
        min_images=args.min_images,
    )
    sponsor_clinic_rows = identify_sponsor_clinic_dirs(
        summaries,
        min_files=args.min_mask_files,
    )

    baseline_file_rows, baseline_directory_rows = identify_prior_baseline_artifacts(
        records=records,
        summaries=summaries,
    )

    model_artifact_rows = identify_artifacts(records, MODEL_EXTENSIONS)
    code_artifact_rows = identify_artifacts(records, CODE_EXTENSIONS)
    document_artifact_rows = identify_artifacts(records, DOCUMENT_EXTENSIONS)
    video_artifact_rows = identify_artifacts(records, VIDEO_EXTENSIONS)
    metadata_artifact_rows = identify_artifacts(records, METADATA_EXTENSIONS)
    group_split_rows = identify_group_split_clues(records)

    manual_review_rows = identify_manual_review_targets(
        candidate_image_rows=candidate_image_rows,
        candidate_mask_rows=candidate_mask_rows,
        public_reference_rows=public_reference_rows,
        sponsor_clinic_rows=sponsor_clinic_rows,
        baseline_directory_rows=baseline_directory_rows,
    )

    print(f"Files audited: {len(records):,}")
    print(f"Directory summaries: {len(summaries):,}")
    print(f"Candidate image directories: {len(candidate_image_rows):,}")
    print(f"Candidate mask/label directories: {len(candidate_mask_rows):,}")
    print(f"Public/reference candidate directories: {len(public_reference_rows):,}")
    print(f"Sponsor/clinic candidate directories: {len(sponsor_clinic_rows):,}")
    print(f"Group split clue files: {len(group_split_rows):,}")
    print(f"Prior baseline file artifacts: {len(baseline_file_rows):,}")
    print(f"Model artifacts: {len(model_artifact_rows):,}")
    print(f"Code/config artifacts: {len(code_artifact_rows):,}")
    print()

    write_csv(output_root / "file_type_summary.csv", extension_rows)
    write_csv(output_root / "top_level_source_summary.csv", source_area_rows)
    write_csv(output_root / "source_package_summary.csv", package_rows)
    write_csv(output_root / "largest_directories.csv", top_directory_rows)
    write_csv(output_root / "candidate_image_directories.csv", candidate_image_rows)
    write_csv(output_root / "candidate_mask_label_directories.csv", candidate_mask_rows)
    write_csv(output_root / "public_reference_candidate_dirs.csv", public_reference_rows)
    write_csv(output_root / "sponsor_clinic_candidate_dirs.csv", sponsor_clinic_rows)
    write_csv(output_root / "prior_baseline_files.csv", baseline_file_rows)
    write_csv(output_root / "prior_baseline_directories.csv", baseline_directory_rows)
    write_csv(output_root / "model_artifacts.csv", model_artifact_rows)
    write_csv(output_root / "code_artifacts.csv", code_artifact_rows)
    write_csv(output_root / "document_artifacts.csv", document_artifact_rows)
    write_csv(output_root / "video_artifacts.csv", video_artifact_rows)
    write_csv(output_root / "metadata_annotation_artifacts.csv", metadata_artifact_rows)
    write_csv(output_root / "group_split_clues.csv", group_split_rows)
    write_csv(output_root / "manual_review_targets.csv", manual_review_rows)

    write_markdown_report(
        output_file=output_root / "raw_data_audit_summary.md",
        data_raw=data_raw,
        records=records,
        extension_rows=extension_rows,
        source_area_rows=source_area_rows,
        package_rows=package_rows,
        top_directory_rows=top_directory_rows,
        candidate_image_rows=candidate_image_rows,
        candidate_mask_rows=candidate_mask_rows,
        public_reference_rows=public_reference_rows,
        sponsor_clinic_rows=sponsor_clinic_rows,
        baseline_file_rows=baseline_file_rows,
        baseline_directory_rows=baseline_directory_rows,
        model_artifact_rows=model_artifact_rows,
        code_artifact_rows=code_artifact_rows,
        document_artifact_rows=document_artifact_rows,
        video_artifact_rows=video_artifact_rows,
        metadata_artifact_rows=metadata_artifact_rows,
        group_split_rows=group_split_rows,
        manual_review_rows=manual_review_rows,
    )

    print("=" * 80)
    print("Done.")
    print("=" * 80)
    print(f"Audit reports written to: {output_root}")
    print()
    print("Suggested next checks:")
    print("  ls -lh reports/data_audit")
    print("  sed -n '1,180p' reports/data_audit/raw_data_audit_summary.md")
    print("  git status --short")


if __name__ == "__main__":
    main()