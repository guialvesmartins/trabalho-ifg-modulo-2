"""Upload MIMII pump WAV files to S3/MinIO."""

import os
from pathlib import Path

import boto3
from botocore.config import Config
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
BUCKET_NAME = "raw"
DATA_DIR = Path("data/raw/pump")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(s3={"addressing_style": "path"}),
    )


def ensure_bucket(s3_client):
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{BUCKET_NAME}' already exists.")
    except Exception as e:
        print(f"Bucket creation skipped or failed: {e}")


def upload_wavs(s3_client):
    if not DATA_DIR.exists():
        print(f"Data directory {DATA_DIR} not found. Run download_dataset.py first.")
        return

    wav_files = list(DATA_DIR.rglob("*.wav"))
    if not wav_files:
        print("No .wav files found.")
        return

    total = len(wav_files)
    print(f"Uploading {total} .wav files to S3 bucket '{BUCKET_NAME}'...")

    for idx, wav_file in enumerate(wav_files):
        relative_path = str(wav_file.relative_to(DATA_DIR))
        s3_key = f"pump/{relative_path}"

        try:
            s3_client.upload_file(
                str(wav_file),
                BUCKET_NAME,
                s3_key,
            )
        except Exception as e:
            print(f"  [{idx}/{total}] Error uploading {relative_path}: {e}")
            continue

        if (idx + 1) % 1000 == 0:
            print(f"  Progress: {idx + 1}/{total} files uploaded.")

    print(f"Upload complete. {total} files uploaded to '{BUCKET_NAME}/pump/'.")


def main():
    s3_client = get_s3_client()
    ensure_bucket(s3_client)
    upload_wavs(s3_client)
    print("Done.")


if __name__ == "__main__":
    main()
