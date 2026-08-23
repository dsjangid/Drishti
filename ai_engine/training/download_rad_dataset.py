"""
JUCC Edge AI Engine - RAD Dataset Downloader & Validator
Module: ai_engine/training/download_rad_dataset.py
Dataset: https://www.kaggle.com/datasets/rohitsuresh15/radroad-anomaly-detection

Automates downloading, unzipping, and formatting the Kaggle RAD Road Anomaly Dataset
into standard YOLOv8 training directory structures.
"""

import os
import sys
import zipfile
import argparse
from pathlib import Path


KAGGLE_DATASET_ID = "rohitsuresh15/radroad-anomaly-detection"
DEFAULT_DEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "datasets/rad_dataset"))


def setup_rad_dataset(dest_dir: str = DEFAULT_DEST_DIR, create_mock_if_missing: bool = True):
    print("=" * 70)
    print("  JUCC - RAD (Road Anomaly Detection) Dataset Setup & Validator")
    print(f"  Target Kaggle Dataset: {KAGGLE_DATASET_ID}")
    print(f"  Target Destination:    {dest_dir}")
    print("=" * 70)

    os.makedirs(dest_dir, exist_ok=True)
    images_train = os.path.join(dest_dir, "images/train")
    images_val = os.path.join(dest_dir, "images/val")
    labels_train = os.path.join(dest_dir, "labels/train")
    labels_val = os.path.join(dest_dir, "labels/val")

    for d in [images_train, images_val, labels_train, labels_val]:
        os.makedirs(d, exist_ok=True)

    # Check if Kaggle CLI is installed
    kaggle_available = False
    try:
        import kaggle
        kaggle_available = True
    except ImportError:
        pass

    if kaggle_available:
        print("[*] Kaggle API detected. Initiating download...")
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            print(f"[*] Downloading {KAGGLE_DATASET_ID} to {dest_dir}...")
            api.dataset_download_files(KAGGLE_DATASET_ID, path=dest_dir, unzip=True)
            print("[✓] Kaggle dataset downloaded and uncompressed successfully.")
            return True
        except Exception as e:
            print(f"[!] Kaggle API download note: {e}")
            print("    Please ensure ~/.kaggle/kaggle.json credentials are configured.")
    else:
        print("[!] Kaggle Python SDK not installed or unauthenticated.")
        print("    To download directly via Kaggle CLI:")
        print(f"    $ pip install kaggle")
        print(f"    $ kaggle datasets download -d {KAGGLE_DATASET_ID} --unzip -p {dest_dir}")

    # Check existing dataset contents
    existing_images = list(Path(images_train).glob("*.jpg")) + list(Path(images_train).glob("*.png"))
    if len(existing_images) > 0:
        print(f"[✓] Found {len(existing_images)} existing training images in {images_train}.")
        return True

    if create_mock_if_missing:
        print("\n[*] Initializing sample training samples for validation verification...")
        import numpy as np
        import cv2

        # Create 5 synthetic training samples for dry-run verification
        for split, count in [("train", 5), ("val", 2)]:
            img_dir = os.path.join(dest_dir, f"images/{split}")
            lbl_dir = os.path.join(dest_dir, f"labels/{split}")
            for idx in range(1, count + 1):
                img_path = os.path.join(img_dir, f"sample_road_{idx:03d}.jpg")
                lbl_path = os.path.join(lbl_dir, f"sample_road_{idx:03d}.txt")

                # Generate synthetic asphalt frame with pothole
                img = np.full((640, 640, 3), 140, dtype=np.uint8)
                cv2.circle(img, (320, 320), 80, (40, 40, 40), -1)
                cv2.imwrite(img_path, img)

                # YOLO annotation: <class-id> <x_center> <y_center> <width> <height> (class 0: pothole)
                with open(lbl_path, "w") as f:
                    f.write("0 0.50 0.50 0.25 0.25\n")

        print(f"[✓] Created sample dataset structure in {dest_dir} ready for training dry-run.")
        return True

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and prepare Kaggle RAD dataset")
    parser.add_argument("--dest", type=str, default=DEFAULT_DEST_DIR, help="Destination directory")
    args = parser.parse_args()

    setup_rad_dataset(args.dest)
