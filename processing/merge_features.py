"""Merge structured metadata and audio features into final ML-ready dataset."""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def load_table(path, label):
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"  [{label}] Loaded {path} ({len(df)} rows, {len(df.columns)} cols)")
        return df
    print(f"  [{label}] NOT FOUND: {path}")
    return None


def main():
    base_dir = Path("data/processed")
    output_path = base_dir / "ml_features.csv"

    print("=== Merging Feature Tables ===")
    print()

    metadata = load_table(base_dir / "pump_metadata.csv", "metadata")
    audio = load_table(base_dir / "audio_features.csv", "audio")

    if metadata is None:
        print("ERROR: pump_metadata.csv is required for merge.")
        sys.exit(1)

    if audio is None:
        print("ERROR: audio_features.csv is required for merge.")
        sys.exit(1)

    merged = metadata.merge(audio, on="file_id", how="left", suffixes=("", "_audio"))

    drop_cols = ["file_path_audio"] if "file_path_audio" in merged.columns else []
    merged = merged.drop(columns=drop_cols, errors="ignore")

    feature_cols = [c for c in merged.columns if c not in ("file_id", "filename", "file_path", "condition")]
    merged[feature_cols] = merged[feature_cols].fillna(0)

    merged = merged.reset_index(drop=True)

    base_dir.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)

    numeric_cols = len(merged.select_dtypes(include=[np.number]).columns)
    categorical_cols = len(merged.select_dtypes(include=["object"]).columns)

    print()
    print("=== Merge Summary ===")
    print(f"Total rows:      {len(merged)}")
    print(f"Total columns:   {len(merged.columns)}")
    print(f"  - Numeric:     {numeric_cols}")
    print(f"  - Text/ID:     {categorical_cols}")
    print(f"Conditions:")
    for cond, count in merged["condition"].value_counts().items():
        print(f"  - {cond}: {count}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
