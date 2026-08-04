"""Train and evaluate sklearn MLPClassifier for binary classification."""

import time

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


def main():
    print("=== MLP Sklearn — Classificacao Binaria (Normal vs Anomalia) ===\n")

    df = pd.read_csv("data/processed/ml_features.csv")

    exclude_cols = [
        "file_id", "filename", "file_path", "condition",
        "condition_binary", "machine_type", "model_id",
    ]
    id_cols = [c for c in df.columns if c.endswith("_id") and c != "file_id"]
    exclude_cols.extend(id_cols)

    feature_cols = [c for c in df.columns if c not in exclude_cols]
    numeric_df = df[feature_cols].select_dtypes(include=["number"])
    X = numeric_df.fillna(0).values
    y = df["condition_binary"].values.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
    )

    inicio = time.time()
    model.fit(X_train, y_train)
    fim = time.time()
    tempo_ms = (fim - inicio) * 1000

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("=" * 50)
    print("RESULTADOS — Sklearn MLPClassifier Binario")
    print("=" * 50)
    print(f"Acuracia:        {acc:.4f}")
    print(f"Precisao:        {prec:.4f}")
    print(f"Recall:          {rec:.4f}")
    print(f"F1-Score:        {f1:.4f}")
    print(f"Tempo de treino: {tempo_ms:,.2f} ms")
    print(f"Iteracoes:       {model.n_iter_}")
    print(f"Layers:          {model.hidden_layer_sizes}")
    print()
    print("Matriz de Confusao (Linha=Real, Coluna=Predito):")
    print(f"  [[TN={cm[0,0]:>6}  FP={cm[0,1]:>6}]")
    print(f"   [FN={cm[1,0]:>6}  TP={cm[1,1]:>6}]]")
    print("=" * 50)


if __name__ == "__main__":
    main()
