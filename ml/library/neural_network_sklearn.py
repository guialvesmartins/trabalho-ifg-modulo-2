import time

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


def main():
    df = pd.read_csv("data/processed/ml_features.csv")

    exclude_cols = ["product_id", "product_name", "review_id", "rating"]
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    X = df[feature_cols].fillna(0)
    y = df["rating"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=300,
        batch_size=32,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
    )

    start = time.time()
    model.fit(X_train, y_train)
    train_time = (time.time() - start) * 1000

    y_pred = model.predict(X_test)

    print("=" * 70)
    print("MLP CLASSIFIER — SCIKIT-LEARN (REDE NEURAL)")
    print("=" * 70)

    print(f"\nAcuracia: {accuracy_score(y_test, y_pred):.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    cm = confusion_matrix(y_test, y_pred)
    print("Matriz de Confusao:")
    print(cm)

    print(f"\nTempo de Treinamento: {train_time:.2f} ms")

    if hasattr(model, "loss_curve_"):
        print(f"\nFinal Loss: {model.loss_curve_[-1]:.4f}")
        print(f"Numero de Iteracoes: {model.n_iter_}")
        print(f"Loss Curve (primeiras 5): {model.loss_curve_[:5]}")
        print(f"Loss Curve (ultimas 5):  {model.loss_curve_[-5:]}")
    else:
        print("\nLoss curve nao disponivel.")


if __name__ == "__main__":
    main()
