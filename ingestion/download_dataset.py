import shutil
from pathlib import Path

import kagglehub


def main():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        "karkavelrajaj/amazon-sales-dataset": "amazon_sales.csv",
        "arhamrumi/amazon-product-reviews": "amazon_reviews.csv",
    }

    for dataset_path, output_name in datasets.items():
        try:
            print(f"Downloading {dataset_path}...")
            dataset_dir = Path(kagglehub.dataset_download(dataset_path))
            csv_files = list(dataset_dir.glob("*.csv"))
            if not csv_files:
                print(f"  No CSV files found in {dataset_dir}")
                continue

            source_file = csv_files[0]
            dest_file = raw_dir / output_name
            shutil.copy(source_file, dest_file)
            print(f"  Saved to {dest_file}")

        except Exception as e:
            print(f"  Error downloading {dataset_path}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
