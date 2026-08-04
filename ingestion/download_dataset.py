"""Download MIMII Pump dataset from Zenodo (com suporte a resume).

Estrutura real do zip: pump/id_XX/{normal,abnormal}/*.wav
Dados sinteticos legados usavam pump/model_id_XX/{normal,anomaly}/ — se
detectados, sao removidos antes da extracao do dataset real.
"""

import shutil
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

MIMII_URL = "https://zenodo.org/records/3384388/files/0_dB_pump.zip"
CHUNK_SIZE = 1024 * 1024


def remote_size(url):
    response = requests.head(url, allow_redirects=True, timeout=30)
    response.raise_for_status()
    return int(response.headers.get("content-length", 0))


def download_with_resume(url, dest_path):
    total_size = remote_size(url)
    local_size = dest_path.stat().st_size if dest_path.exists() else 0

    if local_size == total_size:
        print(f"ZIP completo ja existe: {dest_path}")
        return

    headers = {}
    mode = "wb"
    if 0 < local_size < total_size:
        print(f"Retomando download a partir de {local_size / 1e9:.2f} GB...")
        headers["Range"] = f"bytes={local_size}-"
        mode = "ab"
    else:
        print("Baixando MIMII Pump dataset...")

    print(f"URL: {url}")
    response = requests.get(url, stream=True, headers=headers, timeout=60)
    response.raise_for_status()

    if headers and response.status_code != 206:
        # Servidor ignorou o Range: recomeca do zero
        local_size = 0
        mode = "wb"

    with open(dest_path, mode) as f:
        with tqdm(
            total=total_size,
            initial=local_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Download",
        ) as pbar:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
                pbar.update(len(chunk))

    print(f"Download concluido: {dest_path}")


def has_real_dataset(extract_dir):
    return any(extract_dir.glob("pump/id_*/normal"))


def remove_synthetic_data(extract_dir):
    synthetic_dirs = list(extract_dir.glob("pump/model_id_*"))
    if synthetic_dirs:
        print(f"Removendo {len(synthetic_dirs)} diretorios de dados sinteticos...")
        for d in synthetic_dirs:
            shutil.rmtree(d)


def main():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    zip_path = raw_dir / "0_dB_pump.zip"
    extract_dir = raw_dir / "pump"

    if has_real_dataset(extract_dir):
        print(f"Dataset real ja extraido em {extract_dir}")
        return

    download_with_resume(MIMII_URL, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.testzip()
        members = zf.namelist()

        remove_synthetic_data(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        print(f"Extraindo {zip_path}...")
        for member in tqdm(members, desc="Extraindo"):
            zf.extract(member, extract_dir)

    print(f"Extracao concluida em {extract_dir}")

    wav_count = sum(1 for _ in extract_dir.rglob("*.wav"))
    print(f"Total de arquivos .wav: {wav_count}")

    print("Done.")


if __name__ == "__main__":
    main()
