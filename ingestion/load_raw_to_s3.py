import os
from pathlib import Path

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
BUCKET_NAME = "raw"
MAX_IMAGES = 1000
PROGRESS_INTERVAL = 50


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        use_path_style_endpoint=True,
    )


def ensure_bucket(s3_client):
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{BUCKET_NAME}' already exists.")
    except Exception as e:
        print(f"Bucket creation skipped or failed: {e}")


def upload_csvs(s3_client, raw_dir):
    csv_files = list(raw_dir.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in data/raw/")
        return

    for csv_file in csv_files:
        print(f"Uploading {csv_file.name}...")
        try:
            s3_client.upload_file(
                str(csv_file),
                BUCKET_NAME,
                csv_file.name,
            )
            print(f"  {csv_file.name} uploaded successfully.")
        except Exception as e:
            print(f"  Error uploading {csv_file.name}: {e}")


def download_image(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception:
        return None


def process_images(s3_client, raw_dir):
    sales_file = raw_dir / "amazon_sales.csv"
    if not sales_file.exists():
        print(f"{sales_file} not found. Skipping image upload.")
        return

    print(f"Reading {sales_file}...")
    df = pd.read_csv(sales_file)

    if "img_link" not in df.columns:
        print("Column 'img_link' not found. Skipping image upload.")
        return

    urls = df["img_link"].dropna().unique()
    urls = urls[:MAX_IMAGES]

    print(f"Processing up to {len(urls)} images...")

    for idx, url in enumerate(urls):
        image_data = download_image(url)
        if image_data is None:
            print(f"  [{idx}] Failed to download: {url}")
            continue

        s3_key = f"images/{idx}.jpg"

        try:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=image_data,
                ContentType="image/jpeg",
            )
        except Exception as e:
            print(f"  [{idx}] Error uploading {s3_key}: {e}")
            continue

        if (idx + 1) % PROGRESS_INTERVAL == 0:
            print(f"  Progress: {idx + 1}/{len(urls)} images processed.")

    print(f"Image upload complete. Processed {len(urls)} images.")


def main():
    s3_client = get_s3_client()
    ensure_bucket(s3_client)

    raw_dir = Path("data/raw")
    upload_csvs(s3_client, raw_dir)
    process_images(s3_client, raw_dir)

    print("Done.")


if __name__ == "__main__":
    main()
