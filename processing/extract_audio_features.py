"""Extract audio features from MIMII Pump .wav files using librosa.

A extracao roda em paralelo (multiprocessing) — no dataset real sao
milhares de arquivos de 10s com 8 canais, e a extracao sequencial
levaria horas.
"""

import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path

import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

DATA_DIR = Path("data/raw/pump")
SAMPLE_RATE = 16000
N_MFCC = 40

# O dataset MIMII real usa "abnormal"; normalizamos para "anomaly" para
# que o file_id case com o gerado em process_structured.py.
CONDITION_MAP = {"abnormal": "anomaly"}


def extract_features(wav_path):
    y, sr = librosa.load(str(wav_path), sr=SAMPLE_RATE, mono=True)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr), axis=1)

    zcr = np.mean(librosa.feature.zero_crossing_rate(y))

    rms = np.mean(librosa.feature.rms(y=y))

    features = {
        "zcr_mean": zcr,
        "rms_mean": rms,
        "spectral_centroid_mean": spectral_centroid,
        "spectral_bandwidth_mean": spectral_bandwidth,
        "spectral_rolloff_mean": spectral_rolloff,
    }

    for i in range(N_MFCC):
        features[f"mfcc_{i + 1}_mean"] = mfcc_mean[i]
        features[f"mfcc_{i + 1}_std"] = mfcc_std[i]

    for i in range(len(spectral_contrast)):
        features[f"spectral_contrast_{i + 1}_mean"] = spectral_contrast[i]

    return features


def make_file_id(relative_path):
    parts = Path(relative_path).parts
    machine_type = parts[0]
    model_id = parts[1]
    condition = CONDITION_MAP.get(parts[2], parts[2])
    filename = parts[3]
    return f"{machine_type}_{model_id}_{condition}_{Path(filename).stem}"


def process_file(wav_path):
    relative = str(wav_path.relative_to(DATA_DIR))
    try:
        features = extract_features(wav_path)
    except Exception as e:
        return ("error", relative, str(e))

    features["file_id"] = make_file_id(relative)
    features["file_path"] = relative
    return ("ok", relative, features)


def main():
    print("=== Audio Feature Extraction ===")

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found. Run download_dataset.py first.")
        return

    wav_files = sorted(DATA_DIR.rglob("*.wav"))
    total = len(wav_files)
    n_workers = max(1, (os.cpu_count() or 2) - 1)

    # Dentro do Airflow (LocalExecutor) a task roda em processo daemonico,
    # que nao pode criar processos filhos — nesse caso usa threads (numpy/
    # BLAS libera o GIL, entao ainda ha paralelismo real na extracao).
    use_threads = multiprocessing.current_process().daemon
    modo = "threads" if use_threads else "processos"
    print(f"Found {total} .wav files. Using {n_workers} workers ({modo}).")

    rows = []
    if use_threads:
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            results = executor.map(process_file, wav_files)
            for status, relative, payload in tqdm(
                results, total=total, desc="Extracting features"
            ):
                if status == "error":
                    print(f"  Error processing {relative}: {payload}")
                    continue
                rows.append(payload)
    else:
        with Pool(processes=n_workers) as pool:
            for status, relative, payload in tqdm(
                pool.imap_unordered(process_file, wav_files, chunksize=8),
                total=total,
                desc="Extracting features",
            ):
                if status == "error":
                    print(f"  Error processing {relative}: {payload}")
                    continue
                rows.append(payload)

    df = pd.DataFrame(rows).sort_values("file_id").reset_index(drop=True)

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "audio_features.csv"
    df.to_csv(output_path, index=False)

    print(f"\n=== Audio Features Summary ===")
    print(f"Files processed:  {len(df)}")
    print(f"Total features:   {len(df.columns)}")
    feature_cols = [c for c in df.columns if c not in ("file_id", "file_path")]
    print(f"Audio features:   {len(feature_cols)}")
    print(f"Output saved to:  {output_path}")


if __name__ == "__main__":
    main()
