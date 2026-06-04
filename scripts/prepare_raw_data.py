"""
prepare_raw_data.py

Prepare local raw capstone data without committing raw files to GitHub.

This script is designed for the project structure where raw_from_Tien/ may
contain both original zip archives and previously extracted folders.

Core idea:
    raw_from_Tien/ is treated as the messy intake/source dump.
    data/raw/ is treated as the clean, generated raw-data workspace.

What this script does:
    1. Scans raw_from_Tien/ recursively for source zip files.
    2. Skips already-extracted sibling folders in raw_from_Tien/.
    3. Extracts source zip files into data/raw/extracted_zips/.
    4. Recursively scans data/raw/extracted_zips/ for nested zip files.
    5. Extracts nested zip files inside the clean data/raw workspace.
    6. Copies loose non-zip files into data/raw/loose_files/.
    7. Writes inventory, tree, extraction, and extension-summary logs.

Important:
    Original .zip archives are preserved after extraction.
    Seeing .zip files under data/raw/ does not necessarily mean they were not
    opened. It means the archive was preserved alongside its extracted contents.

Expected repo layout:

repo_root/
    raw_from_Tien/              # ignored by Git
    data/raw/                   # ignored by Git
    scripts/prepare_raw_data.py # tracked by Git
"""

from __future__ import annotations

import argparse
import csv
import shutil
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    """
    Infer repo root from this script location.

    Expected:
        repo_root/scripts/prepare_raw_data.py
    """
    return Path(__file__).resolve().parents[1]


def ensure_dir(path: Path) -> None:
    """Create directory if needed."""
    path.mkdir(parents=True, exist_ok=True)


def size_mb(path: Path) -> float:
    """Return file size in megabytes."""
    return path.stat().st_size / (1024 * 1024)


def is_relative_to(path: Path, parent: Path) -> bool:
    """
    Return True if path is inside parent.

    This helper keeps behavior explicit and works cleanly across Python versions.
    """
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def should_skip_path(path: Path, skip_dirs: set[Path]) -> bool:
    """Return True if path is inside one of the skip directories."""
    path_resolved = path.resolve()

    for skip_dir in skip_dirs:
        if is_relative_to(path_resolved, skip_dir):
            return True

    return False


def find_existing_extraction_dirs(zip_files: list[Path]) -> set[Path]:
    """
    Identify folders that appear to be existing extractions of zip files.

    Example:
        raw_from_Tien/convert_psd_to_label.zip
        raw_from_Tien/convert_psd_to_label/

    In this case, the folder is probably an old extraction of the zip archive.
    We skip crawling/copying from those folders when deciding what belongs in
    the clean data/raw workspace.
    """
    extraction_dirs = set()

    for zip_path in zip_files:
        likely_dir = zip_path.with_suffix("")
        if likely_dir.exists() and likely_dir.is_dir():
            extraction_dirs.add(likely_dir.resolve())

    return extraction_dirs


def get_source_zip_files(source_root: Path) -> tuple[list[Path], list[Path], set[Path]]:
    """
    Find zip files in raw_from_Tien/ and separate true source zips from zips
    buried inside already-extracted folders.

    Returns:
        raw_zip_candidates:
            Every zip file found under raw_from_Tien/.

        source_zip_files:
            Zip files that should be treated as source archives.

        skip_dirs:
            Existing extracted sibling folders that should be skipped.
    """
    raw_zip_candidates = sorted(source_root.rglob("*.zip"))
    skip_dirs = find_existing_extraction_dirs(raw_zip_candidates)

    source_zip_files = [
        zip_path
        for zip_path in raw_zip_candidates
        if not should_skip_path(zip_path, skip_dirs)
        and "extraction_logs" not in zip_path.parts
        and "__pycache__" not in zip_path.parts
    ]

    return raw_zip_candidates, source_zip_files, skip_dirs


def safe_extract_zip(zip_path: Path, destination: Path, overwrite: bool = False) -> int:
    """
    Extract a zip file safely while preventing path traversal.

    Args:
        zip_path:
            Zip file to extract.

        destination:
            Destination folder.

        overwrite:
            Whether to overwrite existing extracted files.

    Returns:
        Number of files extracted.
    """
    ensure_dir(destination)

    destination_resolved = destination.resolve()
    extracted_count = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target = destination / member.filename
            target_resolved = target.resolve()

            if not is_relative_to(target_resolved, destination_resolved):
                print(f"WARNING: skipped unsafe zip path: {member.filename}")
                continue

            if member.is_dir():
                ensure_dir(target)
                continue

            ensure_dir(target.parent)

            if target.exists() and not overwrite:
                continue

            with zf.open(member, "r") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)

            extracted_count += 1

    return extracted_count


def extract_zip_with_log(
    zip_path: Path,
    destination: Path,
    repo_root: Path,
    extraction_type: str,
    overwrite: bool = False,
) -> dict[str, object]:
    """
    Extract a zip file and return a log row.
    """
    print(f"Extracting {extraction_type} zip: {zip_path.relative_to(repo_root)}")
    print(f"                    to: {destination.relative_to(repo_root)}")

    try:
        extracted_count = safe_extract_zip(
            zip_path=zip_path,
            destination=destination,
            overwrite=overwrite,
        )
        status = "ok"

    except zipfile.BadZipFile:
        extracted_count = 0
        status = "bad_zip"
        print(f"WARNING: bad zip file skipped: {zip_path}")

    except Exception as exc:
        extracted_count = 0
        status = f"error: {repr(exc)}"
        print(f"WARNING: error extracting {zip_path}: {repr(exc)}")

    return {
        "extraction_type": extraction_type,
        "zip_path": str(zip_path.relative_to(repo_root)),
        "zip_size_mb": round(size_mb(zip_path), 6),
        "output_directory": str(destination.relative_to(repo_root)),
        "extracted_file_count": extracted_count,
        "status": status,
    }


def extract_source_zips(
    source_zip_files: list[Path],
    source_root: Path,
    extracted_root: Path,
    repo_root: Path,
    overwrite: bool = False,
) -> list[dict[str, object]]:
    """
    Extract source zip files from raw_from_Tien/ into data/raw/extracted_zips/.
    """
    extraction_log = []

    for zip_path in source_zip_files:
        rel_zip = zip_path.relative_to(source_root)
        output_dir = extracted_root / rel_zip.parent / zip_path.stem

        log_row = extract_zip_with_log(
            zip_path=zip_path,
            destination=output_dir,
            repo_root=repo_root,
            extraction_type="source",
            overwrite=overwrite,
        )
        extraction_log.append(log_row)

    return extraction_log


def extract_nested_zips(
    extracted_root: Path,
    repo_root: Path,
    overwrite: bool = False,
    max_rounds: int = 10,
) -> list[dict[str, object]]:
    """
    Recursively extract nested zip files found inside data/raw/extracted_zips/.

    The original nested .zip archives are preserved. Extracted contents are
    written to a sibling folder with the same stem.

    Example:
        some_folder/Predictions.zip
            -> some_folder/Predictions/

    Args:
        extracted_root:
            Root of clean extracted zip workspace.

        repo_root:
            Repo root for readable relative paths.

        overwrite:
            Whether to overwrite existing extracted files.

        max_rounds:
            Safety limit to prevent infinite recursive extraction loops.

    Returns:
        Extraction log rows.
    """
    extraction_log = []
    processed_zips: set[Path] = set()

    for round_idx in range(1, max_rounds + 1):
        nested_zip_files = sorted(
            zip_path
            for zip_path in extracted_root.rglob("*.zip")
            if zip_path.resolve() not in processed_zips
            and "extraction_logs" not in zip_path.parts
            and "__pycache__" not in zip_path.parts
        )

        if not nested_zip_files:
            if round_idx == 1:
                print("No nested zip files found in extracted workspace.")
            else:
                print("No additional nested zip files found.")
            break

        print()
        print(f"Nested zip extraction pass {round_idx}:")
        print(f"Found {len(nested_zip_files)} nested zip file(s).")

        for zip_path in nested_zip_files:
            output_dir = zip_path.with_suffix("")

            log_row = extract_zip_with_log(
                zip_path=zip_path,
                destination=output_dir,
                repo_root=repo_root,
                extraction_type="nested",
                overwrite=overwrite,
            )
            extraction_log.append(log_row)
            processed_zips.add(zip_path.resolve())

    else:
        print()
        print(
            f"WARNING: reached max nested extraction rounds ({max_rounds}). "
            "There may still be nested zip files remaining."
        )

    return extraction_log


def copy_loose_non_zip_files(
    source_root: Path,
    destination_root: Path,
    skip_dirs: set[Path],
    overwrite: bool = False,
) -> int:
    """
    Copy loose non-zip files from raw_from_Tien/ into data/raw/loose_files/.

    This skips:
        - zip files
        - previously extracted sibling folders
        - extraction_logs folders
        - __pycache__ folders
    """
    copied_count = 0

    for src in sorted(source_root.rglob("*")):
        if not src.is_file():
            continue

        if src.suffix.lower() == ".zip":
            continue

        if should_skip_path(src, skip_dirs):
            continue

        if "extraction_logs" in src.parts:
            continue

        if "__pycache__" in src.parts:
            continue

        rel = src.relative_to(source_root)
        dst = destination_root / rel

        ensure_dir(dst.parent)

        if dst.exists() and not overwrite:
            continue

        shutil.copy2(src, dst)
        copied_count += 1

    return copied_count


def write_tree_log(
    root: Path,
    output_file: Path,
    skip_dirs: set[Path] | None = None,
    max_depth: int | None = 5,
) -> None:
    """
    Write a readable file hierarchy log.

    Args:
        root:
            Folder to scan.

        output_file:
            Text file to write.

        skip_dirs:
            Directories to skip.

        max_depth:
            Maximum depth to include. Use None for full recursive tree.
    """
    ensure_dir(output_file.parent)
    skip_dirs = skip_dirs or set()

    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"File hierarchy for: {root}\n")
        f.write(f"Created: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"Max depth: {max_depth if max_depth is not None else 'full'}\n")
        f.write("=" * 80 + "\n\n")

        if not root.exists():
            f.write("Path does not exist.\n")
            return

        for path in sorted(root.rglob("*")):
            if should_skip_path(path, skip_dirs):
                continue

            rel = path.relative_to(root)
            depth = len(rel.parts)

            if max_depth is not None and depth > max_depth:
                continue

            indent = "  " * (depth - 1)
            marker = "[D]" if path.is_dir() else "[F]"

            if path.is_file():
                f.write(f"{indent}{marker} {path.name} ({size_mb(path):.3f} MB)\n")
            else:
                f.write(f"{indent}{marker} {path.name}\n")


def write_inventory_csv(
    root: Path,
    output_file: Path,
    skip_dirs: set[Path] | None = None,
) -> None:
    """
    Write a CSV inventory of all files under a folder.
    """
    ensure_dir(output_file.parent)
    skip_dirs = skip_dirs or set()

    fieldnames = [
        "relative_path",
        "file_name",
        "extension",
        "size_bytes",
        "size_mb",
        "modified_time",
    ]

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        if not root.exists():
            return

        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue

            if should_skip_path(path, skip_dirs):
                continue

            writer.writerow(
                {
                    "relative_path": str(path.relative_to(root)),
                    "file_name": path.name,
                    "extension": path.suffix.lower() if path.suffix else "[no extension]",
                    "size_bytes": path.stat().st_size,
                    "size_mb": round(size_mb(path), 6),
                    "modified_time": datetime.fromtimestamp(
                        path.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                }
            )


def write_extension_summary_csv(
    root: Path,
    output_file: Path,
    skip_dirs: set[Path] | None = None,
) -> None:
    """
    Write a summary of file counts by extension.
    """
    ensure_dir(output_file.parent)
    skip_dirs = skip_dirs or set()

    extension_counts: Counter[str] = Counter()
    extension_sizes: Counter[str] = Counter()

    if root.exists():
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue

            if should_skip_path(path, skip_dirs):
                continue

            extension = path.suffix.lower() if path.suffix else "[no extension]"
            extension_counts[extension] += 1
            extension_sizes[extension] += path.stat().st_size

    with output_file.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["extension", "file_count", "total_size_mb"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for extension, count in extension_counts.most_common():
            writer.writerow(
                {
                    "extension": extension,
                    "file_count": count,
                    "total_size_mb": round(extension_sizes[extension] / (1024 * 1024), 6),
                }
            )


def write_zip_candidate_log(
    raw_zip_candidates: list[Path],
    source_zip_files: list[Path],
    source_root: Path,
    output_file: Path,
) -> None:
    """
    Write a log showing all zip files found in raw_from_Tien/ and whether each
    was treated as a source zip.
    """
    ensure_dir(output_file.parent)

    source_zip_set = {path.resolve() for path in source_zip_files}

    with output_file.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "zip_relative_path",
            "zip_size_mb",
            "used_as_source_zip",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for zip_path in raw_zip_candidates:
            writer.writerow(
                {
                    "zip_relative_path": str(zip_path.relative_to(source_root)),
                    "zip_size_mb": round(size_mb(zip_path), 6),
                    "used_as_source_zip": zip_path.resolve() in source_zip_set,
                }
            )


def write_extraction_log(
    extraction_rows: list[dict[str, object]],
    output_file: Path,
) -> None:
    """
    Write zip extraction log.
    """
    ensure_dir(output_file.parent)

    fieldnames = [
        "extraction_type",
        "zip_path",
        "zip_size_mb",
        "output_directory",
        "extracted_file_count",
        "status",
    ]

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extraction_rows)


def write_skipped_dirs_log(
    skip_dirs: set[Path],
    source_root: Path,
    output_file: Path,
) -> None:
    """
    Write a text log of skipped existing extraction folders.
    """
    ensure_dir(output_file.parent)

    with output_file.open("w", encoding="utf-8") as f:
        f.write("Existing extracted folders skipped by prepare_raw_data.py\n")
        f.write("=" * 80 + "\n\n")

        for path in sorted(skip_dirs):
            try:
                f.write(str(path.relative_to(source_root.resolve())) + "\n")
            except ValueError:
                f.write(str(path) + "\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare raw capstone data locally."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing extracted/copied files.",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete data/raw before rebuilding it.",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum depth for tree logs. Default: 5.",
    )

    parser.add_argument(
        "--full-tree",
        action="store_true",
        help="Write full recursive tree logs. This can create very large text files.",
    )

    parser.add_argument(
        "--max-nested-rounds",
        type=int,
        default=10,
        help="Maximum recursive nested zip extraction rounds. Default: 10.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repo_root = get_repo_root()

    source_root = repo_root / "raw_from_Tien"
    data_raw = repo_root / "data" / "raw"

    extracted_root = data_raw / "extracted_zips"
    loose_root = data_raw / "loose_files"
    inventory_root = data_raw / "_inventory"

    tree_max_depth = None if args.full_tree else args.max_depth

    print("=" * 80)
    print("Preparing raw data")
    print("=" * 80)
    print(f"Repo root:       {repo_root}")
    print(f"Source folder:   {source_root}")
    print(f"Output folder:   {data_raw}")
    print()

    if not source_root.exists():
        raise FileNotFoundError(f"Source folder not found: {source_root}")

    if args.clean and data_raw.exists():
        print(f"Cleaning existing generated raw folder: {data_raw}")
        shutil.rmtree(data_raw)

    ensure_dir(extracted_root)
    ensure_dir(loose_root)
    ensure_dir(inventory_root)

    raw_zip_candidates, source_zip_files, skip_dirs = get_source_zip_files(source_root)

    print(f"Found {len(raw_zip_candidates)} total zip candidate(s) under raw_from_Tien/.")
    print(f"Found {len(skip_dirs)} existing extracted folder(s) to skip in raw_from_Tien/.")
    print(f"Will extract {len(source_zip_files)} source zip file(s).")
    print()

    source_extraction_log = extract_source_zips(
        source_zip_files=source_zip_files,
        source_root=source_root,
        extracted_root=extracted_root,
        repo_root=repo_root,
        overwrite=args.overwrite,
    )

    nested_extraction_log = extract_nested_zips(
        extracted_root=extracted_root,
        repo_root=repo_root,
        overwrite=args.overwrite,
        max_rounds=args.max_nested_rounds,
    )

    extraction_log = source_extraction_log + nested_extraction_log

    print()
    print("Copying loose non-zip files...")
    copied_count = copy_loose_non_zip_files(
        source_root=source_root,
        destination_root=loose_root,
        skip_dirs=skip_dirs,
        overwrite=args.overwrite,
    )
    print(f"Copied {copied_count} loose non-zip file(s).")

    print()
    print("Writing inventory logs...")

    inventory_skip_dirs = {inventory_root.resolve()}

    write_extraction_log(
        extraction_rows=extraction_log,
        output_file=inventory_root / "zip_extraction_log.csv",
    )

    write_zip_candidate_log(
        raw_zip_candidates=raw_zip_candidates,
        source_zip_files=source_zip_files,
        source_root=source_root,
        output_file=inventory_root / "source_zip_candidates.csv",
    )

    write_skipped_dirs_log(
        skip_dirs=skip_dirs,
        source_root=source_root,
        output_file=inventory_root / "skipped_existing_extraction_dirs.txt",
    )

    write_tree_log(
        root=source_root,
        output_file=inventory_root / "source_raw_from_Tien_tree_source_only.txt",
        skip_dirs=skip_dirs,
        max_depth=tree_max_depth,
    )

    write_inventory_csv(
        root=source_root,
        output_file=inventory_root / "source_raw_from_Tien_inventory_source_only.csv",
        skip_dirs=skip_dirs,
    )

    write_tree_log(
        root=data_raw,
        output_file=inventory_root / "data_raw_tree.txt",
        skip_dirs=inventory_skip_dirs,
        max_depth=tree_max_depth,
    )

    write_inventory_csv(
        root=data_raw,
        output_file=inventory_root / "data_raw_inventory.csv",
        skip_dirs=inventory_skip_dirs,
    )

    write_extension_summary_csv(
        root=data_raw,
        output_file=inventory_root / "data_raw_extension_summary.csv",
        skip_dirs=inventory_skip_dirs,
    )

    remaining_zips = sorted(data_raw.rglob("*.zip"))
    source_count = len(source_extraction_log)
    nested_count = len(nested_extraction_log)

    print()
    print("=" * 80)
    print("Done.")
    print("=" * 80)
    print(f"Source zips extracted:  {source_count}")
    print(f"Nested zips extracted:  {nested_count}")
    print(f"Remaining zip archives: {len(remaining_zips)}")
    print(f"Copied loose files:     {copied_count}")
    print()
    print(f"Extracted zip contents: {extracted_root}")
    print(f"Loose files:            {loose_root}")
    print(f"Inventory logs:         {inventory_root}")
    print()
    print("Note:")
    print("  Remaining .zip files are preserved archives. They may already have")
    print("  corresponding extracted folders next to them.")
    print()
    print("Suggested next checks:")
    print("  find data/raw -type f | wc -l")
    print("  find data/raw -type f -name '*.zip' -print -exec du -h {} \\;")
    print("  git status --short")


if __name__ == "__main__":
    main()