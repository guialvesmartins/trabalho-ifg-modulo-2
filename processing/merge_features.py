"""Merge all feature tables into final ML-ready dataset."""

import os
import sys

import numpy as np
import pandas as pd


def load_table(path, label):
    if os.path.exists(path):
        print(f"  [{label}] Loaded {path}")
        return pd.read_csv(path)
    print(f"  [{label}] NOT FOUND: {path}")
    return None


def drop_unused_columns(df):
    cols_to_drop = []
    for col in df.columns:
        if col.startswith("http") or col.startswith("www"):
            cols_to_drop.append(col)
            continue
        name_lower = col.lower()
        if any(
            keyword in name_lower
            for keyword in [
                "img_link",
                "product_link",
                "review_link",
                "image_url",
                "imageurl",
            ]
        ):
            cols_to_drop.append(col)
            continue
        if any(
            keyword in name_lower
            for keyword in [
                "review_content",
                "review_title",
                "review_text",
                "description",
                "about_product",
                "product_specification",
                "product_description",
            ]
        ):
            cols_to_drop.append(col)
            continue

    df = df.drop(columns=cols_to_drop, errors="ignore")
    return df


def classify_feature_types(df):
    numeric_count = 0
    categorical_count = 0
    boolean_count = 0
    text_count = 0

    for col in df.columns:
        dtype = df[col].dtype
        if col == "product_id":
            text_count += 1
        elif col == "format":
            categorical_count += 1
        elif dtype == "bool":
            boolean_count += 1
        elif dtype == "object":
            categorical_count += 1
        elif dtype == "int64":
            if set(df[col].dropna().unique()).issubset({0, 1}):
                boolean_count += 1
            else:
                numeric_count += 1
        elif dtype == "float64":
            numeric_count += 1
        else:
            numeric_count += 1

    return numeric_count, categorical_count, boolean_count, text_count


def main():
    base_dir = os.path.join("data", "processed")
    output_path = os.path.join(base_dir, "ml_features.csv")

    print("=== Merging Feature Tables ===")
    print()

    products = load_table(os.path.join(base_dir, "products_clean.csv"), "products")
    reviews = load_table(os.path.join(base_dir, "reviews_features.csv"), "reviews")
    images = load_table(os.path.join(base_dir, "images_features.csv"), "images")

    if products is None:
        print("ERROR: products_clean.csv is required for merge.")
        sys.exit(1)

    merged = products.copy()

    if "product_id" not in merged.columns:
        print("WARNING: no product_id column found in products. Using index.")
        merged["product_id"] = "prod_" + merged.index.astype(str)

    merge_keys = ["product_id"]

    if reviews is not None:
        if "product_id" in reviews.columns:
            reviews_cols = ["product_id"] + [c for c in reviews.columns if c != "product_id"]
            reviews = reviews[reviews_cols]
            merged = merged.merge(reviews, on="product_id", how="left", suffixes=("", "_review"))
        else:
            print("WARNING: reviews_features.csv has no product_id; merging by index.")
            reviews = reviews.reset_index(drop=True)
            merged = merged.reset_index(drop=True)
            merged = pd.concat([merged, reviews], axis=1)

    if images is not None:
        if "product_id" in images.columns:
            images_cols = ["product_id"] + [c for c in images.columns if c != "product_id"]
            images = images[images_cols]
            merged = merged.merge(images, on="product_id", how="left", suffixes=("", "_image"))
        else:
            print("WARNING: images_features.csv has no product_id; merging by index.")
            images = images.reset_index(drop=True)
            merged = merged.reset_index(drop=True)
            merged = pd.concat([merged, images], axis=1)

    for col_suffix in ["_review", "_image"]:
        dup_cols = [c for c in merged.columns if c.endswith(col_suffix)]
        for dc in dup_cols:
            base = dc[: -len(col_suffix)]
            if base in merged.columns:
                merged[base] = merged[base].fillna(merged[dc])
                merged = merged.drop(columns=[dc])

    merged = merged.dropna(axis=1, how="all")

    feature_cols = [c for c in merged.columns if c != "product_id"]
    merged[feature_cols] = merged[feature_cols].fillna(0)

    merged = drop_unused_columns(merged)

    merged = merged.reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    merged.to_csv(output_path, index=False)

    numeric, categorical, boolean, text = classify_feature_types(merged)

    print()
    print("=== Merge Summary ===")
    print(f"Total rows:      {len(merged)}")
    print(f"Total columns:   {len(merged.columns)}")
    print(f"  - Numeric:     {numeric}")
    print(f"  - Categorical: {categorical}")
    print(f"  - Boolean:     {boolean}")
    print(f"  - Text/ID:     {text}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
