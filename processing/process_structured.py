"""Parse MIMII Pump file structure into structured CSV metadata."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

DATA_DIR = Path("data/raw/pump")

# O dataset MIMII real usa "abnormal"; normalizamos para "anomaly",
# valor esperado pelo restante do pipeline (dbt, ML, Metabase).
CONDITION_MAP = {"abnormal": "anomaly"}


def normalize_condition(condition):
    return CONDITION_MAP.get(condition, condition)


def parse_mimii_structure(data_dir):
    rows = []
    wav_files = sorted(data_dir.rglob("*.wav"))

    for wav_path in wav_files:
        relative = str(wav_path.relative_to(data_dir))

        try:
            parts = Path(relative).parts
            machine_type = parts[0]
            model_id = parts[1]
            condition = normalize_condition(parts[2])  # "normal" ou "anomaly"
            filename = parts[3]
        except IndexError:
            print(f"  WARNING: Unexpected path structure: {relative}")
            continue

        info = sf.info(str(wav_path))
        duration = info.duration
        sample_rate = info.samplerate
        channels = info.channels

        file_id = f"{machine_type}_{model_id}_{condition}_{Path(filename).stem}"

        rows.append(
            {
                "file_id": file_id,
                "machine_type": machine_type,
                "model_id": model_id,
                "condition": condition,
                "filename": filename,
                "file_path": relative,
                "duration_sec": round(duration, 4),
                "sample_rate": sample_rate,
                "channels": channels,
            }
        )

    return rows


def main():
    print("=== MIMII Pump Structured Data Extraction ===")

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found. Run download_dataset.py first.")
        return

    rows = parse_mimii_structure(DATA_DIR)
    print(f"Parsed {len(rows)} audio files.")

    df = pd.DataFrame(rows)

    df["condition_binary"] = np.where(df["condition"] == "anomaly", 1, 0)
    df["model_id_encoded"] = df["model_id"].str.extract(r"(\d+)").astype(int)

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "pump_metadata.csv"
    df.to_csv(output_path, index=False)

    print(f"\n=== Structured Data Summary ===")
    print(f"Total files:     {len(df)}")
    print(f"Machine types:   {df['machine_type'].unique().tolist()}")
    print(f"Models:          {sorted(df['model_id'].unique())}")
    print(f"Conditions:      {df['condition'].value_counts().to_dict()}")
    print(f"Mean duration:   {df['duration_sec'].mean():.2f}s")
    print(f"Sample rate:     {df['sample_rate'].iloc[0]} Hz")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
