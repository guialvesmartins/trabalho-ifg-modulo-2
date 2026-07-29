"""Extract computer vision features from product images."""

import os
import sys

import numpy as np
import pandas as pd
from PIL import Image
from skimage.feature import graycomatrix, graycoprops

import cv2


IMAGES_DIR = "images/products"


def nan_row(product_id):
    return {
        "product_id": product_id,
        "width": np.nan,
        "height": np.nan,
        "aspect_ratio": np.nan,
        "file_size_kb": np.nan,
        "format": None,
        "brightness_mean": np.nan,
        "saturation_mean": np.nan,
        "colorfulness_score": np.nan,
        "dominant_color_1_r": np.nan,
        "dominant_color_1_g": np.nan,
        "dominant_color_1_b": np.nan,
        "dominant_color_2_r": np.nan,
        "dominant_color_2_g": np.nan,
        "dominant_color_2_b": np.nan,
        "dominant_color_3_r": np.nan,
        "dominant_color_3_g": np.nan,
        "dominant_color_3_b": np.nan,
        "blur_score": np.nan,
        "edge_density": np.nan,
        "corner_count": np.nan,
        "entropy": np.nan,
        "contrast": np.nan,
        "hist_r_mean": np.nan,
        "hist_r_std": np.nan,
        "hist_g_mean": np.nan,
        "hist_g_std": np.nan,
        "hist_b_mean": np.nan,
        "hist_b_std": np.nan,
    }


def find_local_image(image_id, product_id, img_link):
    candidates = []

    if img_link and not pd.isna(img_link):
        fname = os.path.basename(str(img_link))
        candidates.append(os.path.join(IMAGES_DIR, fname))

    if product_id:
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            candidates.append(os.path.join(IMAGES_DIR, f"{product_id}{ext}"))
            candidates.append(os.path.join(IMAGES_DIR, f"{image_id}{ext}"))

    for cand in candidates:
        if os.path.isfile(cand):
            return cand

    return None


def extract_dimensions(image_path):
    try:
        pil_img = Image.open(image_path)
        width, height = pil_img.size
        aspect_ratio = width / height if height > 0 else np.nan
        file_size_kb = os.path.getsize(image_path) / 1024.0
        fmt = pil_img.format
        return width, height, aspect_ratio, file_size_kb, fmt
    except Exception:
        return np.nan, np.nan, np.nan, np.nan, None


def extract_color_hsv(cv_img):
    try:
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        brightness_mean = float(np.mean(hsv[:, :, 2]))
        saturation_mean = float(np.mean(hsv[:, :, 1]))
        colorfulness_score = float(np.std(hsv[:, :, 0]) + np.std(hsv[:, :, 1]))
        return brightness_mean, saturation_mean, colorfulness_score
    except Exception:
        return np.nan, np.nan, np.nan


def extract_dominant_colors(cv_img, k=3):
    try:
        pixels = cv_img.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = centers / 255.0
        result = []
        for i in range(k):
            if i < len(centers):
                result.extend([float(centers[i][0]), float(centers[i][1]), float(centers[i][2])])
            else:
                result.extend([np.nan, np.nan, np.nan])
        return tuple(result)
    except Exception:
        return (np.nan,) * (k * 3)


def extract_sharpness(cv_img):
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        return blur_score
    except Exception:
        return np.nan


def extract_complexity(cv_img):
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
        threshold = 0.01 * dst.max()
        corner_count = int(np.sum(dst > threshold))

        return edge_density, corner_count
    except Exception:
        return np.nan, np.nan


def extract_texture_glcm(cv_img):
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        glcm = graycomatrix(gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
        entropy = float(-np.sum(glcm * np.log2(glcm + 1e-10)))
        contrast = float(graycoprops(glcm, "contrast")[0, 0])
        return entropy, contrast
    except Exception:
        return np.nan, np.nan


def extract_histogram(cv_img):
    try:
        result = {}
        for idx, channel in enumerate(["r", "g", "b"]):
            ch = cv_img[:, :, idx].ravel()
            result[f"hist_{channel}_mean"] = float(np.mean(ch))
            result[f"hist_{channel}_std"] = float(np.std(ch))
        return result
    except Exception:
        return {
            "hist_r_mean": np.nan, "hist_r_std": np.nan,
            "hist_g_mean": np.nan, "hist_g_std": np.nan,
            "hist_b_mean": np.nan, "hist_b_std": np.nan,
        }


def process_single_image(image_id, product_id, img_link):
    image_path = find_local_image(image_id, product_id, img_link)
    row = {"product_id": product_id if product_id else image_id}

    if image_path is None:
        nan_values = nan_row(product_id)
        nan_values.pop("product_id")
        row.update(nan_values)
        return row

    width, height, aspect_ratio, file_size_kb, fmt = extract_dimensions(image_path)

    cv_img = cv2.imread(image_path)
    if cv_img is None:
        nan_values = nan_row(product_id)
        nan_values.pop("product_id")
        row.update(nan_values)
        return row

    bm, sm, cs = extract_color_hsv(cv_img)
    dc = extract_dominant_colors(cv_img, k=3)
    blur = extract_sharpness(cv_img)
    edge_density, corner_count = extract_complexity(cv_img)
    entropy, contrast = extract_texture_glcm(cv_img)
    hist = extract_histogram(cv_img)

    row.update(
        {
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "file_size_kb": file_size_kb,
            "format": fmt,
            "brightness_mean": bm,
            "saturation_mean": sm,
            "colorfulness_score": cs,
            "dominant_color_1_r": dc[0],
            "dominant_color_1_g": dc[1],
            "dominant_color_1_b": dc[2],
            "dominant_color_2_r": dc[3],
            "dominant_color_2_g": dc[4],
            "dominant_color_2_b": dc[5],
            "dominant_color_3_r": dc[6],
            "dominant_color_3_g": dc[7],
            "dominant_color_3_b": dc[8],
            "blur_score": blur,
            "edge_density": edge_density,
            "corner_count": corner_count,
            "entropy": entropy,
            "contrast": contrast,
            **hist,
        }
    )

    return row


def main():
    input_path = os.path.join("data", "processed", "products_clean.csv")
    output_path = os.path.join("data", "processed", "images_features.csv")

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    df = pd.read_csv(input_path)

    has_product_id = "product_id" in df.columns
    has_img_link = "img_link" in df.columns

    rows = []
    for i, row_data in df.iterrows():
        image_id = str(i)
        product_id = row_data.get("product_id", image_id) if has_product_id else image_id
        img_link = row_data.get("img_link", None) if has_img_link else None

        row = process_single_image(image_id, product_id, img_link)
        rows.append(row)

        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(df)} images...")

    result = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.to_csv(output_path, index=False)

    total_features = result.shape[1] - 1

    print(f"=== Image Feature Extraction Summary ===")
    print(f"Images processed: {len(result)}")
    print(f"Total features generated: {total_features}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
