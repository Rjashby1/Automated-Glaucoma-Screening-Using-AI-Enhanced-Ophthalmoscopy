"""
prepare_raw_data.py

Prepare local raw capstone data without committing raw files to GitHub.

This script:
1. Scans raw_from_Tien/ for zip files.
2. Extracts zip files into data/raw/extracted_from_zips/.
3. Copies already-unzipped non-zip files into data/raw/from_raw_folder/.
4. Creates inventory logs under data/raw/_inventory/.

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
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    """
    Infer repo root from this file location.

    Expected:
        repo_root/scripts/prepare_raw_data.py
    """
    return Path(__file__).resolve().parents[1]


def ensure_dir(path: Path) -> None:
    """Create a directory if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)


def size_mb(path: Path) -> float:
    """Return file size in megabytes."""
    return path.stat().st_size / (1024 * 1024)


def safe_extract_zip(zip_path: Path, destination: Path, overwrite: bool = False) -> int:
    """
    Extract a zip file safely while preventing path traversal.

    Args:
        zip_path: Path to the zip file.
        destination: Folder where zip contents should be extracted.
        overwrite: Whether to overwrite existing files.

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

            if not str(target_resolved).startswith(str(destination_resolved)):
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


def copy_non_zip_material(
    source_root: Path,
    destination_root: Path,
    overwrite: bool = False,
) -> int:
    """
    Copy all non-zip files from raw_from_Tien/ into data/raw/from_raw_folder/,
    preserving relative paths.

    This catches already-unzipped folders and loose files that came from Tien.
    """
    copied_count = 0

    for src in sorted(source_root.rglob("*")):
        if not src.is_file():
            continue

        if src.suffix.lower() == ".zip":
            continue

        rel = src.relative_to(source_root)
        dst = destination_root / rel

        ensure_dir(dst.parent)

        if dst.exists() and not overwrite:
            continue

        shutil.copy2(src, dst)
        copied_count += 1

    return copied_count


def write_tree_log(root: Path, output_file: Path) -> None:
    """
    Write a readable file hierarchy log.
    """
    ensure_dir(output_file.parent)

    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"File hierarchy for: {root}\n")
        f.write(f"Created: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")

        if not root.exists():
            f.write("Path does not exist.\n")
            return

        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root)
            depth = len(rel.parts)
            indent = "  " * (depth - 1)
            marker = "[D]" if path.is_dir() else "[F]"

            if path.is_file():
                f.write(f"{indent}{marker} {path.name} ({size_mb(path):.3f} MB)\n")
            else:
                f.write(f"{indent}{marker} {path.name}\n")


def write_inventory_csv(root: Path, output_file: Path) -> None:
    """
    Write a CSV inventory of all files under a folder.
    """
    ensure_dir(output_file.parent)

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

            writer.writerow(
                {
                    "relative_path": str(path.relative_to(root)),
                    "file_name": path.name,
                    "extension": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                    "size_mb": round(size_mb(path), 6),
                    "modified_time": datetime.fromtimestamp(
                        path.stat().st_mtime
                    ).isoformat(timespec="seconds"),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare raw capstone data locally."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in data/raw/.",
    )

    args = parser.parse_args()

    repo_root = get_repo_root()

    source_root = repo_root / "raw_from_Tien"
    data_raw = repo_root / "data" / "raw"

    extracted_root = data_raw / "extracted_from_zips"
    copied_root = data_raw / "from_raw_folder"
    inventory_root = data_raw / "_inventory"

    ensure_dir(extracted_root)
    ensure_dir(copied_root)
    ensure_dir(inventory_root)

    print("=" * 80)
    print("Preparing raw data")
    print("=" * 80)
    print(f"Repo root:       {repo_root}")
    print(f"Source folder:   {source_root}")
    print(f"Output folder:   {data_raw}")
    print()

    if not source_root.exists():
        raise FileNotFoundError(f"Source folder not found: {source_root}")

    zip_files = sorted(source_root.rglob("*.zip"))
    extraction_log = []

    print(f"Found {len(zip_files)} zip file(s).")
    print()

    for zip_path in zip_files:
        rel_zip = zip_path.relative_to(source_root)
        output_dir = extracted_root / rel_zip.parent / zip_path.stem

        print(f"Extracting: {rel_zip}")
        print(f"        to: {output_dir}")

        try:
            extracted_count = safe_extract_zip(
                zip_path=zip_path,
                destination=output_dir,
                overwrite=args.overwrite,
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

        extraction_log.append(
            {
                "zip_relative_path": str(rel_zip),
                "zip_size_mb": round(size_mb(zip_path), 6),
                "output_directory": str(output_dir.relative_to(repo_root)),
                "extracted_file_count": extracted_count,
                "status": status,
            }
        )

    print()
    print("Copying non-zip material from raw_from_Tien/...")
    copied_count = copy_non_zip_material(
        source_root=source_root,
        destination_root=copied_root,
        overwrite=args.overwrite,
    )
    print(f"Copied {copied_count} non-zip file(s).")

    print()
    print("Writing inventory logs...")

    zip_log_file = inventory_root / "zip_extraction_log.csv"

    with zip_log_file.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "zip_relative_path",
            "zip_size_mb",
            "output_directory",
            "extracted_file_count",
            "status",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extraction_log)

    write_tree_log(source_root, inventory_root / "source_raw_from_Tien_tree.txt")
    write_tree_log(data_raw, inventory_root / "data_raw_tree.txt")

    write_inventory_csv(
        source_root,
        inventory_root / "source_raw_from_Tien_inventory.csv",
    )
    write_inventory_csv(
        data_raw,
        inventory_root / "data_raw_inventory.csv",
    )

    print()
    print("=" * 80)
    print("Done.")
    print("=" * 80)
    print(f"Extracted zip contents: {extracted_root}")
    print(f"Copied loose material:  {copied_root}")
    print(f"Inventory logs:         {inventory_root}")


if __name__ == "__main__":
    main()