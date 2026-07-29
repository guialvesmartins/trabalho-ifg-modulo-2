import os
import time
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix as sklearn_confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from ml.hard_code.naive_bayes_hardcode import (
    HardCodedNaiveBayes,
    compute_confusion_matrix,
    compute_precision_recall_f1,
)

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

    feature_cols = [c for c in df.columns if c.startswith("tfidf_")]
    X = (df[feature_cols] > 0).astype(int)
    y = df["rating"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    most_common_class = Counter(y_train).most_common(1)[0][0]
    y_baseline = np.full_like(y_test, most_common_class)

    baseline_acc = accuracy_score(y_test, y_baseline)
    bp_macro, br_macro, bf_macro, _ = precision_recall_fscore_support(
        y_test, y_baseline, average="macro", zero_division=0
    )

    hard_model = HardCodedNaiveBayes(alpha=1.0)
    start = time.time()
    hard_model.fit(X_train, y_train)
    hard_train_time = (time.time() - start) * 1000

    start = time.time()
    y_pred_hard = hard_model.predict(X_test)
    hard_pred_time = (time.time() - start) * 1000

    hard_acc = accuracy_score(y_test, y_pred_hard)
    cm_hard = compute_confusion_matrix(y_test, y_pred_hard, hard_model.classes_)
    _, _, _, hp_macro, hr_macro, hf_macro = compute_precision_recall_f1(
        cm_hard, hard_model.classes_
    )

    sk_model = MultinomialNB(alpha=1.0)
    start = time.time()
    sk_model.fit(X_train, y_train)
    sk_train_time = (time.time() - start) * 1000

    start = time.time()
    y_pred_sk = sk_model.predict(X_test)
    sk_pred_time = (time.time() - start) * 1000

    sk_acc = accuracy_score(y_test, y_pred_sk)
    sp_macro, sr_macro, sf_macro, _ = precision_recall_fscore_support(
        y_test, y_pred_sk, average="macro", zero_division=0
    )
    cm_sk = sklearn_confusion_matrix(y_test, y_pred_sk)

    print("=" * 80)
    print("COMPARACAO: HARD-CODE vs SCIKIT-LEARN vs BASELINE")
    print("=" * 80)

    print(f"\n{'Metrica':<25} {'Hard-Code':<14} {'Sklearn':<14} {'Baseline':<14}")
    print("-" * 67)
    print(
        f"{'Acuracia':<25} {hard_acc:<14.4f} {sk_acc:<14.4f} {baseline_acc:<14.4f}"
    )
    print(
        f"{'Precision (macro)':<25} {hp_macro:<14.4f} {sp_macro:<14.4f} "
        f"{bp_macro:<14.4f}"
    )
    print(
        f"{'Recall (macro)':<25} {hr_macro:<14.4f} {sr_macro:<14.4f} "
        f"{br_macro:<14.4f}"
    )
    print(
        f"{'F1-Score (macro)':<25} {hf_macro:<14.4f} {sf_macro:<14.4f} "
        f"{bf_macro:<14.4f}"
    )
    print(
        f"{'Tempo Treino (ms)':<25} {hard_train_time:<14.2f} "
        f"{sk_train_time:<14.2f} {'N/A':<14}"
    )
    print(
        f"{'Tempo Predicao (ms)':<25} {hard_pred_time:<14.2f} "
        f"{sk_pred_time:<14.2f} {'N/A':<14}"
    )

    comparison = {
        "Metrica": [
            "Acuracia",
            "Precision (macro)",
            "Recall (macro)",
            "F1-Score (macro)",
            "Tempo Treino (ms)",
            "Tempo Predicao (ms)",
        ],
        "Hard-Code": [
            hard_acc,
            hp_macro,
            hr_macro,
            hf_macro,
            hard_train_time,
            hard_pred_time,
        ],
        "Sklearn": [sk_acc, sp_macro, sr_macro, sf_macro, sk_train_time, sk_pred_time],
        "Baseline": [baseline_acc, bp_macro, br_macro, bf_macro, None, None],
    }
    pd.DataFrame(comparison).to_csv(
        "data/processed/model_comparison.csv", index=False
    )
    print("\nComparacao salva em: data/processed/model_comparison.csv")

    classes = sorted(set(y_test))

    plot_confusion_matrix(
        cm_hard,
        classes,
        "Matriz de Confusao — Hard-Code Naive Bayes",
        "data/processed/hardcode_confusion.png",
    )
    print("Matriz de confusao salva em: data/processed/hardcode_confusion.png")

    plot_confusion_matrix(
        cm_sk,
        classes,
        "Matriz de Confusao — Scikit-Learn Naive Bayes",
        "data/processed/sklearn_confusion.png",
    )
    print("Matriz de confusao salva em: data/processed/sklearn_confusion.png")

    print("\n" + "=" * 80)
    print("DISCUSSAO")
    print("=" * 80)

    print(
        """
1. ACURACIA E METRICAS:
   - O modelo hard-code deve apresentar metricas muito proximas do sklearn,
     pois ambos implementam o mesmo algoritmo (Multinomial Naive Bayes)
     com o mesmo alpha de Laplace smoothing (1.0).
   - Pequenas diferencas podem surgir de implementacoes internas distintas,
     como a ordem de operacoes em ponto flutuante.

2. TEMPO DE EXECUCAO:
   - O scikit-learn e altamente otimizado com codigo compilado (Cython/C),
     enquanto a versao hard-code usa apenas Python puro com NumPy.
   - Espera-se que o sklearn seja significativamente mais rapido,
     especialmente no treinamento com muitos features.

3. BASELINE:
   - O baseline representa a estrategia mais simples: prever sempre
     a classe mais frequente.
   - Se o modelo tem acuracia pouco acima do baseline, isso pode indicar
     que as features TF-IDF tem baixo poder preditivo para as classes.
   - Um ganho significativo sobre o baseline indica que o modelo
     esta capturando padroes reais nos dados textuais.
"""
    )

    if np.isclose(hard_acc, sk_acc, atol=0.01):
        print(
            ">> VERIFICACAO: As acuracias dos modelos hard-code e sklearn "
            "sao consistentes (OK)"
        )
    else:
        print(
            f">> ATENCAO: Diferenca nas acuracias "
            f"({abs(hard_acc - sk_acc):.6f}). Verificar implementacao."
        )


if __name__ == "__main__":
    main()
