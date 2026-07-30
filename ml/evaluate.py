import os
import time

import matplotlib
import matplotlib.pyplot as plt
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

from ml.hard_code.neural_network_hardcode import HardCodedMLP

matplotlib.use("Agg")


def plot_confusion_matrix(cm, classes, title, filepath):
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(len(classes)),
        yticks=np.arange(len(classes)),
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel="Real",
        xlabel="Predito",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    threshold = cm.max() / 2
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(
                j,
                i,
                cm[i, j],
                ha="center",
                va="center",
                color="white" if cm[i, j] > threshold else "black",
            )

    fig.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    os.makedirs("data/processed", exist_ok=True)

    df = pd.read_csv("data/processed/ml_features.csv")

    exclude_cols = ["rating"]
    id_cols = [c for c in df.columns if c.endswith("_id") or c == "id" or c == "ID"]
    exclude_cols.extend(id_cols)
    exclude_cols.append("product_name")  # coluna de texto
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    # Garantir apenas colunas numericas
    numeric_df = df[feature_cols].select_dtypes(include=['number'])
    X = numeric_df.fillna(0).values
    y = df["rating"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    hard_model = HardCodedMLP()
    start = time.time()
    hard_model.fit(X_train, y_train)
    hard_train_time = (time.time() - start) * 1000

    start = time.time()
    y_pred_hard = hard_model.predict(X_test)
    hard_pred_time = (time.time() - start) * 1000

    hard_acc = accuracy_score(y_test, y_pred_hard)
    hard_prec = precision_score(y_test, y_pred_hard, average="macro", zero_division=0)
    hard_rec = recall_score(y_test, y_pred_hard, average="macro", zero_division=0)
    hard_f1 = f1_score(y_test, y_pred_hard, average="macro", zero_division=0)
    cm_hard = confusion_matrix(y_test, y_pred_hard)

    sk_model = MLPClassifier(
        hidden_layer_sizes=(100,), max_iter=500, random_state=42
    )
    start = time.time()
    sk_model.fit(X_train, y_train)
    sk_train_time = (time.time() - start) * 1000

    start = time.time()
    y_pred_sk = sk_model.predict(X_test)
    sk_pred_time = (time.time() - start) * 1000

    sk_acc = accuracy_score(y_test, y_pred_sk)
    sk_prec = precision_score(y_test, y_pred_sk, average="macro", zero_division=0)
    sk_rec = recall_score(y_test, y_pred_sk, average="macro", zero_division=0)
    sk_f1 = f1_score(y_test, y_pred_sk, average="macro", zero_division=0)
    cm_sk = confusion_matrix(y_test, y_pred_sk)

    print("=" * 60)
    print("         COMPARACAO: Hard-code MLP vs Sklearn MLPClassifier")
    print("=" * 60)
    print(f"{'Metrica':<22} {'Hard-Code':<14} {'Sklearn':<14}")
    print("-" * 50)
    print(f"{'Accuracy':<22} {hard_acc:<14.4f} {sk_acc:<14.4f}")
    print(f"{'Precision (macro)':<22} {hard_prec:<14.4f} {sk_prec:<14.4f}")
    print(f"{'Recall (macro)':<22} {hard_rec:<14.4f} {sk_rec:<14.4f}")
    print(f"{'F1-Score (macro)':<22} {hard_f1:<14.4f} {sk_f1:<14.4f}")
    print(f"{'Tempo Treino (ms)':<22} {hard_train_time:<14.2f} {sk_train_time:<14.2f}")
    print(f"{'Tempo Predicao (ms)':<22} {hard_pred_time:<14.2f} {sk_pred_time:<14.2f}")
    print("-" * 50)

    comparison = {
        "Metrica": [
            "Accuracy",
            "Precision (macro)",
            "Recall (macro)",
            "F1-Score (macro)",
            "Tempo Treino (ms)",
            "Tempo Predicao (ms)",
        ],
        "Hard-Code": [
            hard_acc,
            hard_prec,
            hard_rec,
            hard_f1,
            hard_train_time,
            hard_pred_time,
        ],
        "Sklearn": [
            sk_acc,
            sk_prec,
            sk_rec,
            sk_f1,
            sk_train_time,
            sk_pred_time,
        ],
    }
    pd.DataFrame(comparison).to_csv(
        "data/processed/model_comparison.csv", index=False
    )
    print("\nComparacao salva em: data/processed/model_comparison.csv")

    classes = sorted(set(y_test))

    plot_confusion_matrix(
        cm_hard,
        classes,
        "Matriz de Confusao — Hard-Code MLP",
        "data/processed/hardcode_cm.png",
    )
    print("Matriz de confusao salva em: data/processed/hardcode_cm.png")

    plot_confusion_matrix(
        cm_sk,
        classes,
        "Matriz de Confusao — Scikit-Learn MLPClassifier",
        "data/processed/sklearn_cm.png",
    )
    print("Matriz de confusao salva em: data/processed/sklearn_cm.png")

    print("\n" + "=" * 60)
    print("ANALISE")
    print("=" * 60)

    print(
        """
Os resultados podem diferir devido a varios fatores:

1. ALGORITMO DE OTIMIZACAO:
   - O HardCodedMLP implementa SGD com momento (descida do gradiente
     estocastica classica), enquanto o MLPClassifier do sklearn usa
     Adam por padrao — um otimizador adaptativo que ajusta a taxa de
     aprendizado por parametro e converge mais rapidamente.

2. INICIALIZACAO DOS PESOS:
   - A inicializacao dos pesos pode diferir entre as implementacoes.
     O sklearn usa inicializacao Glorot/Xavier uniforme por padrao,
     enquanto a versao hard-code pode usar uma estrategia diferente
     (ex: valores aleatorios pequenos sem escala).

3. FUNCAO DE ATIVACAO:
   - O sklearn MLPClassifier usa ReLU por padrao. Se o HardCodedMLP
     usa sigmoid ou tanh, surgem diferencas no gradiente (vanishing
     gradient) e na velocidade de convergencia.

4. REGULARIZACAO:
   - O sklearn aplica regularizacao L2 por padrao (alpha=0.0001),
     o que ajuda a prevenir overfitting. A versao hard-code pode
     nao ter regularizacao implementada.

5. TAXA DE APRENDIZADO:
   - O sklearn usa taxa de aprendizado constante por padrao. Se a
     versao hard-code usar uma taxa diferente ou decaimento, os
     resultados podem divergir.

6. IMPLEMENTACAO E PERFORMANCE:
   - O sklearn e altamente otimizado com uso intensivo de NumPy
     vetorizado e codigo compilado, resultando em tempos de
     execucao significativamente menores que uma implementacao
     em Python puro com loops explicitos.
"""
    )


if __name__ == "__main__":
    main()
