"""Clean structured data from raw CSV and save processed version."""

import os

import numpy as np
import pandas as pd


def clean_currency(value):
    if pd.isna(value):
        return np.nan
    return float(str(value).replace("₹", "").replace(",", "").strip())


def clean_percentage(value):
    if pd.isna(value):
        return np.nan
    return float(str(value).replace("%", "").strip()) / 100


def clean_rating_count(value):
    if pd.isna(value):
        return np.nan
    return int(str(value).replace(",", "").strip())


def load_raw_data(path):
    return pd.read_csv(path)


def clean_data(df):
    df = df.copy()

    if "discounted_price" in df.columns:
        df["discounted_price"] = df["discounted_price"].apply(clean_currency)

    if "actual_price" in df.columns:
        df["actual_price"] = df["actual_price"].apply(clean_currency)

    if "discount_percentage" in df.columns:
        df["discount_percentage"] = df["discount_percentage"].apply(clean_percentage)

    if "rating_count" in df.columns:
        df["rating_count"] = df["rating_count"].apply(clean_rating_count)

    if "product_id" not in df.columns:
        df["product_id"] = df.index.astype(str)
        df["product_id"] = "prod_" + df["product_id"]
    else:
        df["product_id"] = df["product_id"].astype(str)

    df = df.drop_duplicates(subset=["product_name", "product_id"], keep="first")

    if "rating" in df.columns:
        before_drop = len(df)
        df = df.dropna(subset=["rating"])
        df["rating"] = df["rating"].astype(int)
        nulls_removed = before_drop - len(df)
    else:
        nulls_removed = 0

    return df, nulls_removed


def add_derived_features(df):
    df = df.copy()

    if "actual_price" in df.columns:
        df["log_price"] = np.log1p(df["actual_price"])

    if "rating_count" in df.columns:
        df["log_rating_count"] = np.log1p(df["rating_count"])

    if "actual_price" in df.columns and "discounted_price" in df.columns:
        df["price_difference"] = df["actual_price"] - df["discounted_price"]

    if "discount_percentage" in df.columns:

        def bucketize(pct):
            if pd.isna(pct):
                return "unknown"
            if pct < 0.20:
                return "low"
            if pct <= 0.50:
                return "medium"
            return "high"

        df["discount_bucket"] = df["discount_percentage"].apply(bucketize)

    return df


def encode_categorical(df):
    if "category" in df.columns:
        cat_dummies = pd.get_dummies(df["category"], prefix="cat_", dtype=int)
        df = pd.concat([df, cat_dummies], axis=1)
    return df


def save_processed(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def main():
    raw_path = os.path.join("data", "raw", "amazon_sales.csv")
    processed_path = os.path.join("data", "processed", "products_clean.csv")

    original_cols = None

    if not os.path.exists(raw_path):
        alt_paths = [
            "data/amazon_sales.csv",
            "data/amazon.csv",
            "data/products.csv",
        ]
        for alt in alt_paths:
            if os.path.exists(alt):
                raw_path = alt
                break

    df_raw = load_raw_data(raw_path)
    original_rows = len(df_raw)
    original_cols = df_raw.columns.tolist()

    df_clean, nulls_removed = clean_data(df_raw)
    df_featured = add_derived_features(df_clean)
    df_encoded = encode_categorical(df_featured)

    final_rows = len(df_encoded)
    final_cols = df_encoded.columns.tolist()
    columns_added = [c for c in final_cols if c not in original_cols]

    save_processed(df_encoded, processed_path)

    print("=== Structured Data Processing Summary ===")
    print(f"Original rows: {original_rows}")
    print(f"Final rows:    {final_rows}")
    print(f"Nulls removed: {nulls_removed}")
    print(f"Columns added: {len(columns_added)}")
    for col in columns_added:
        print(f"  - {col}")
    print(f"Output saved to: {processed_path}")


if __name__ == "__main__":
    main()
