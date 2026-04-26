"""Setup proper YOLO dataset layout for Ultralytics training.

Ultralytics expects:
  yolo_dataset/
    images/
      train/  *.png
      val/    *.png
    labels/
      train/  *.txt
      val/    *.txt
    data.yaml

This script copies images and renames label dirs to match.
"""

import shutil
from pathlib import Path

import yaml


def setup_yolo_dataset():
    base = Path("yolo_dataset")
    ds_root = Path("dataset_ds2_dense")

    # Create directory structure
    (base / "images" / "train").mkdir(parents=True, exist_ok=True)
    (base / "images" / "val").mkdir(parents=True, exist_ok=True)
    (base / "labels" / "val").mkdir(parents=True, exist_ok=True)

    # Copy train images
    train_manifest = base / "train.txt"
    if train_manifest.exists():
        paths = train_manifest.read_text().strip().split("\n")
        copied = 0
        for p in paths:
            src = Path(p)
            dst = base / "images" / "train" / src.name
            if not dst.exists() and src.exists():
                shutil.copy2(src, dst)
                copied += 1
        print(f"Train images: {copied} copied, {len(paths)} total in manifest")

    # Copy val images
    val_manifest = base / "test.txt"
    if val_manifest.exists():
        paths = val_manifest.read_text().strip().split("\n")
        copied = 0
        for p in paths:
            src = Path(p)
            dst = base / "images" / "val" / src.name
            if not dst.exists() and src.exists():
                shutil.copy2(src, dst)
                copied += 1
        print(f"Val images: {copied} copied, {len(paths)} total in manifest")

    # Rename labels/test -> labels/val if needed
    old_test = base / "labels" / "test"
    new_val = base / "labels" / "val"
    if old_test.exists():
        for f in old_test.glob("*.txt"):
            dst = new_val / f.name
            if not dst.exists():
                shutil.copy2(f, dst)
        print(f"Val labels: {len(list(new_val.glob('*.txt')))} files")

    # Verify counts
    train_imgs = len(list((base / "images" / "train").glob("*.png")))
    val_imgs = len(list((base / "images" / "val").glob("*.png")))
    train_labels = len(list((base / "labels" / "train").glob("*.txt")))
    val_labels = len(list((base / "labels" / "val").glob("*.txt")))
    print(f"\nDataset summary:")
    print(f"  Train: {train_imgs} images, {train_labels} labels")
    print(f"  Val:   {val_imgs} images, {val_labels} labels")

    # Write proper data.yaml
    data_config = {
        "path": str(base.resolve()),
        "train": "images/train",
        "val": "images/val",
        "nc": 15,
        "names": {
            0: "notehead-full",
            1: "notehead-half",
            2: "notehead-whole",
            3: "clefG",
            4: "clefF",
            5: "clefC",
            6: "rest-8th",
            7: "rest-quarter",
            8: "rest-half",
            9: "rest-whole",
            10: "accidentalSharp",
            11: "accidentalFlat",
            12: "accidentalNatural",
            13: "beam",
            14: "stem",
        },
    }
    yaml_path = base / "data.yaml"
    yaml_path.write_text(yaml.safe_dump(data_config, sort_keys=False), encoding="utf-8")
    print(f"\nWrote {yaml_path}")

    # Clean up bad label cache from previous run
    for cache in ds_root.rglob("labels.cache"):
        cache.unlink()
        print(f"Removed stale cache: {cache}")
    for cache in base.rglob("labels.cache"):
        cache.unlink()
        print(f"Removed stale cache: {cache}")


if __name__ == "__main__":
    setup_yolo_dataset()
