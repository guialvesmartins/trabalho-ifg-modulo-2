"""Extract NLP features from review text content."""

import os
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import textstat


COMPLAINT_PATTERN = re.compile(
    r"\b(bad|terrible|awful|poor|worst|broke|broken|defect|"
    r"return|refund|disappointed|waste)\b",
    re.IGNORECASE,
)

PRAISE_PATTERN = re.compile(
    r"\b(great|excellent|amazing|love|best|perfect|"
    r"fantastic|wonderful|recommend)\b",
    re.IGNORECASE,
)

PRICE_MENTION_PATTERN = re.compile(
    r"\b(price|cheap|expensive|cost|worth|value|money)\b",
    re.IGNORECASE,
)

DELIVERY_MENTION_PATTERN = re.compile(
    r"\b(delivery|shipping|arrived|package|fast|slow|days|quick)\b",
    re.IGNORECASE,
)


def safe_len(s):
    if pd.isna(s):
        return 0
    return len(str(s))


def safe_split(s):
    if pd.isna(s):
        return []
    return str(s).split()


def build_full_review(title, content):
    ttl = str(title) if not pd.isna(title) else ""
    cnt = str(content) if not pd.isna(content) else ""
    return (ttl + " " + cnt).strip()


def extract_metadata(row):
    full = build_full_review(row.get("review_title"), row.get("review_content"))
    review_length = len(full)
    words = full.split()
    word_count = len(words)
    avg_word_length = review_length / word_count if word_count > 0 else 0.0
    sentence_count = full.count(".") + full.count("!") + full.count("?")
    return review_length, word_count, avg_word_length, sentence_count


def extract_style(full_review):
    total = len(full_review)
    uppercase_count = sum(1 for ch in full_review if ch.isupper())
    uppercase_ratio = uppercase_count / total if total > 0 else 0.0
    exclamation_count = full_review.count("!")
    question_count = full_review.count("?")
    digit_count = sum(1 for ch in full_review if ch.isdigit())
    numeric_ratio = digit_count / total if total > 0 else 0.0
    return uppercase_ratio, exclamation_count, question_count, numeric_ratio


def extract_vader(full_review, analyzer):
    scores = analyzer.polarity_scores(full_review)
    polarity = scores["compound"]
    subjectivity = scores["pos"] + scores["neg"]
    vader_compound = scores["compound"]
    return polarity, subjectivity, vader_compound


def extract_regex(full_review):
    contains_complaint = int(bool(COMPLAINT_PATTERN.search(full_review)))
    contains_praise = int(bool(PRAISE_PATTERN.search(full_review)))
    contains_price_mention = int(bool(PRICE_MENTION_PATTERN.search(full_review)))
    contains_delivery_mention = int(bool(DELIVERY_MENTION_PATTERN.search(full_review)))
    return contains_complaint, contains_praise, contains_price_mention, contains_delivery_mention


def extract_readability(full_review):
    try:
        fk_score = textstat.flesch_reading_ease(full_review)
    except Exception:
        fk_score = np.nan

    words = full_review.split()
    if len(words) == 0:
        complex_word_ratio = 0.0
    else:
        complex_count = sum(
            1 for w in words if textstat.syllable_count(w) >= 3
        )
        complex_word_ratio = complex_count / len(words)

    return fk_score, complex_word_ratio


def extract_tfidf(texts, max_features=200):
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        stop_words="english",
        min_df=2,
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = ["tfidf_" + name.replace(" ", "_") for name in vectorizer.get_feature_names_out()]
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    return tfidf_df


def main():
    input_path = os.path.join("data", "processed", "products_clean.csv")
    output_path = os.path.join("data", "processed", "reviews_features.csv")

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    df = pd.read_csv(input_path)

    text_cols = ["review_title", "review_content"]
    has_title = "review_title" in df.columns
    has_content = "review_content" in df.columns

    if not has_title:
        df["review_title"] = ""
    if not has_content:
        df["review_content"] = ""

    full_reviews = df.apply(
        lambda r: build_full_review(
            r.get("review_title"), r.get("review_content")
        ),
        axis=1,
    )

    analyzer = SentimentIntensityAnalyzer()

    meta = df.apply(extract_metadata, axis=1, result_type="expand")
    meta.columns = ["review_length", "word_count", "avg_word_length", "sentence_count"]

    style = full_reviews.apply(extract_style).apply(pd.Series)
    style.columns = ["uppercase_ratio", "exclamation_count", "question_count", "numeric_ratio"]

    vader = full_reviews.apply(lambda x: extract_vader(x, analyzer)).apply(pd.Series)
    vader.columns = ["polarity", "subjectivity", "vader_compound"]

    regex = full_reviews.apply(extract_regex).apply(pd.Series)
    regex.columns = [
        "contains_complaint",
        "contains_praise",
        "contains_price_mention",
        "contains_delivery_mention",
    ]

    readability = full_reviews.apply(extract_readability).apply(pd.Series)
    readability.columns = ["flesch_reading_ease", "complex_word_ratio"]

    tfidf_df = extract_tfidf(full_reviews.tolist())

    features = pd.concat(
        [meta, style, vader, regex, readability, tfidf_df], axis=1
    )

    if "product_id" in df.columns:
        features.insert(0, "product_id", df["product_id"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False)

    total_features = features.shape[1] - (1 if "product_id" in features.columns else 0)

    print(f"=== Text Feature Extraction Summary ===")
    print(f"Reviews processed: {len(df)}")
    print(f"Total features generated: {total_features}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
