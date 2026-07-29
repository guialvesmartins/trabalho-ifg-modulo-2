import numpy as np
import pandas as pd
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support,
)


def main():
    df = pd.read_csv("data/processed/ml_features.csv")

    feature_cols = [c for c in df.columns if c.startswith("tfidf_")]
    X = df[feature_cols]
    X_bin = (X > 0).astype(int)
    y = df["rating"]

    X_train, X_test, y_train, y_test = train_test_split(
        X_bin, y, test_size=0.2, random_state=42
    )

    most_common_class = Counter(y_train).most_common(1)[0][0]
    y_baseline = np.full_like(y_test, most_common_class)

    model = MultinomialNB(alpha=1.0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("=" * 70)
    print("MULTINOMIAL NAIVE BAYES — SCIKIT-LEARN")
    print("=" * 70)

    print(f"\nAcuracia: {accuracy_score(y_test, y_pred):.4f}")
    print(
        f"Acuracia Baseline (classe {most_common_class}): "
        f"{accuracy_score(y_test, y_baseline):.4f}"
    )

    print("\nClassification Report (Scikit-Learn):")
    print(classification_report(y_test, y_pred, zero_division=0))

    cm = confusion_matrix(y_test, y_pred)
    print("Matriz de Confusao:")
    print(cm)

    p_macro, r_macro, f_macro, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0
    )
    print(f"\nPrecision (macro): {p_macro:.4f}")
    print(f"Recall (macro):    {r_macro:.4f}")
    print(f"F1-Score (macro):  {f_macro:.4f}")

    bp, br, bf, _ = precision_recall_fscore_support(
        y_test, y_baseline, average="macro", zero_division=0
    )
    acc_baseline = accuracy_score(y_test, y_baseline)

    print(f"\n{'Metrica':<25} {'Baseline':<12} {'Sklearn NB':<12}")
    print("-" * 49)
    print(
        f"{'Acuracia':<25} {acc_baseline:<12.4f} "
        f"{accuracy_score(y_test, y_pred):<12.4f}"
    )
    print(f"{'Precision (macro)':<25} {bp:<12.4f} {p_macro:<12.4f}")
    print(f"{'Recall (macro)':<25} {br:<12.4f} {r_macro:<12.4f}")
    print(f"{'F1-Score (macro)':<25} {bf:<12.4f} {f_macro:<12.4f}")


if __name__ == "__main__":
    main()
