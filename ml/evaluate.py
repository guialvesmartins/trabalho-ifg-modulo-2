"""Treinamento e avaliacao: Baselines vs Hard-Code MLP vs Sklearn MLPClassifier.

Saidas (data/processed/):
    model_comparison.csv   — metricas de todos os modelos
    predictions.csv        — predicao por amostra do conjunto de teste
    hardcode_cm.png / sklearn_cm.png — matrizes de confusao
    models/*.pkl           — modelos exportados via pickle
    report_analys.md (raiz do projeto) — relatorio completo do treinamento

Se o PostgreSQL estiver acessivel (env vars DB_*), as metricas e predicoes
tambem sao carregadas nas tabelas model_metrics e model_predictions para
consumo no Metabase.
"""

import os
import pickle
import time
from datetime import datetime
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.hard_code.neural_network_hardcode import (
    prever,
    prever_probabilidade,
    salvar_modelo,
    treinar,
)

matplotlib.use("Agg")

PROCESSED_DIR = Path("data/processed")
MODELS_DIR = PROCESSED_DIR / "models"
REPORT_PATH = Path("report_analys.md")


def plot_confusion_matrix(cm, title, filepath):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(im, ax=ax)

    classes = ["Normal", "Anomalia"]
    ax.set(
        xticks=np.arange(2),
        yticks=np.arange(2),
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel="Real",
        xlabel="Predito",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    threshold = cm.max() / 2
    for i in range(2):
        for j in range(2):
            ax.text(
                j, i, cm[i, j],
                ha="center", va="center",
                color="white" if cm[i, j] > threshold else "black",
            )

    fig.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()


def compute_metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "cm": confusion_matrix(y_true, y_pred, labels=[0, 1]),
    }


def train_and_eval(model, X_train, y_train, X_test, y_test):
    start = time.time()
    model.fit(X_train, y_train)
    train_ms = (time.time() - start) * 1000

    start = time.time()
    y_pred = model.predict(X_test)
    pred_ms = (time.time() - start) * 1000

    metrics = compute_metrics(y_test, y_pred)
    metrics["train_ms"] = train_ms
    metrics["pred_ms"] = pred_ms
    metrics["y_pred"] = np.asarray(y_pred).astype(int).flatten()
    return metrics


def analyze_errors(df_test, y_true, y_pred, proba, X_test_scaled, feature_names, max_examples=5):
    """Para cada erro, aponta as features que mais desviam da media da classe real."""
    errors = []
    error_idx = np.where(y_true != y_pred)[0]

    for idx in error_idx[:max_examples]:
        true_class = int(y_true[idx])
        class_mask = y_true == true_class
        class_mean = X_test_scaled[class_mask].mean(axis=0)
        deviation = np.abs(X_test_scaled[idx] - class_mean)
        top_features = np.argsort(deviation)[::-1][:3]

        errors.append({
            "file_id": df_test.iloc[idx]["file_id"],
            "model_id": df_test.iloc[idx]["model_id"],
            "real": "anomaly" if true_class == 1 else "normal",
            "predito": "anomaly" if y_pred[idx] == 1 else "normal",
            "proba": float(proba[idx]),
            "top_desvios": [
                f"{feature_names[f]} ({deviation[f]:.1f} desvios-padrao da media da classe real)"
                for f in top_features
            ],
        })
    return errors, len(error_idx)


def sample_hits(df_test, y_true, y_pred, proba, max_examples=3):
    hits = []
    hit_idx = np.where(y_true == y_pred)[0]
    # Prioriza acertos de anomalia (classe de interesse), depois normais
    ordered = sorted(hit_idx, key=lambda i: -y_true[i])
    for idx in ordered[:max_examples]:
        hits.append({
            "file_id": df_test.iloc[idx]["file_id"],
            "real": "anomaly" if y_true[idx] == 1 else "normal",
            "proba": float(proba[idx]),
        })
    return hits


def top_divergent_features(df, feature_names):
    """Features com maior diferenca relativa entre classes (dados nao escalados)."""
    normal = df[df["condition_binary"] == 0]
    anomaly = df[df["condition_binary"] == 1]
    rows = []
    for feat in feature_names:
        mean_n = normal[feat].mean()
        mean_a = anomaly[feat].mean()
        if abs(mean_n) > 1e-9:
            pct = 100.0 * (mean_a - mean_n) / abs(mean_n)
            rows.append((feat, mean_n, mean_a, pct))
    rows.sort(key=lambda r: -abs(r[3]))
    return rows[:10]


def cm_to_markdown(cm):
    return (
        "| | Predito Normal | Predito Anomalia |\n"
        "|---|---|---|\n"
        f"| **Real Normal** | {cm[0, 0]} | {cm[0, 1]} |\n"
        f"| **Real Anomalia** | {cm[1, 0]} | {cm[1, 1]} |\n"
    )


def write_report(context):
    r = context
    lines = []
    add = lines.append

    add("# Relatório de Análise do Treinamento — Manutenção Preditiva Industrial")
    add("")
    add(f"_Gerado automaticamente por `ml/evaluate.py` em {r['timestamp']}._")
    add("")
    add("## 1. Dataset")
    add("")
    add(f"- **Fonte:** MIMII Dataset (Pump, 0 dB SNR) — Zenodo")
    add(f"- **Amostras:** {r['n_samples']} arquivos de áudio")
    add(f"- **Features numéricas:** {r['n_features']} (MFCC, espectrais, ZCR, RMS, duração)")
    add(f"- **Distribuição:** {r['n_normal']} normal ({100 * r['n_normal'] / r['n_samples']:.1f}%) | "
        f"{r['n_anomaly']} anomalia ({100 * r['n_anomaly'] / r['n_samples']:.1f}%)")
    add(f"- **Split:** 80% treino / 20% teste, estratificado por classe (random_state=42)")
    add(f"- **Teste:** {r['n_test']} amostras ({r['n_test_normal']} normal, {r['n_test_anomaly']} anomalia)")
    add(f"- **Escalonamento:** StandardScaler ajustado apenas no treino")
    add("")
    add("## 2. Modelos Comparados")
    add("")
    add("| Modelo | Tipo | Papel |")
    add("|---|---|---|")
    add("| Classe Majoritária (Dummy) | Baseline | Piso de referência — sempre prediz 'normal' |")
    add("| Regressão Logística | Baseline | Modelo linear simples |")
    add("| MLP Hard-Code (NumPy) | Modelo principal | Forward/backprop implementados do zero |")
    add("| MLP Sklearn | Modelo principal | MLPClassifier(64, 32) com Adam |")
    add("")
    add("## 3. Métricas no Conjunto de Teste")
    add("")
    add("| Métrica | Majoritária | Reg. Logística | MLP Hard-Code | MLP Sklearn |")
    add("|---|---|---|---|---|")
    for metric_key, label, fmt in [
        ("accuracy", "Accuracy", "{:.4f}"),
        ("precision", "Precision", "{:.4f}"),
        ("recall", "Recall", "{:.4f}"),
        ("f1", "F1-Score", "{:.4f}"),
        ("train_ms", "Tempo Treino (ms)", "{:.1f}"),
        ("pred_ms", "Tempo Predição (ms)", "{:.2f}"),
    ]:
        row = [fmt.format(r["results"][m][metric_key])
               for m in ["dummy", "logreg", "hardcode", "sklearn"]]
        add(f"| {label} | " + " | ".join(row) + " |")
    add("")
    add(f"O baseline de classe majoritária atinge {r['results']['dummy']['accuracy']:.1%} de accuracy "
        f"apenas por causa do desbalanceamento — mas tem recall 0 (não detecta nenhuma anomalia), "
        f"o que o torna inútil para o problema. Todo modelo precisa superá-lo em recall/F1.")
    add("")
    add("### Matriz de Confusão — MLP Hard-Code")
    add("")
    add(cm_to_markdown(r["results"]["hardcode"]["cm"]))
    add("### Matriz de Confusão — MLP Sklearn")
    add("")
    add(cm_to_markdown(r["results"]["sklearn"]["cm"]))
    add("Imagens: `data/processed/hardcode_cm.png` e `data/processed/sklearn_cm.png`.")
    add("")
    add("## 4. Análise Qualitativa")
    add("")
    add("### Exemplos de acertos (MLP Sklearn)")
    add("")
    for h in r["hits"]:
        add(f"- `{h['file_id']}` — real: **{h['real']}**, P(anomalia)={h['proba']:.3f}")
    add("")
    add(f"### Exemplos de erros (MLP Sklearn — {r['n_errors_sklearn']} erros no teste)")
    add("")
    if r["errors"]:
        for e in r["errors"]:
            add(f"- `{e['file_id']}` ({e['model_id']}) — real: **{e['real']}**, "
                f"predito: **{e['predito']}**, P(anomalia)={e['proba']:.3f}")
            add(f"  - Possível causa: amostra atípica dentro da própria classe; "
                f"features que mais desviam da média da classe real: {'; '.join(e['top_desvios'])}")
        add("")
        add("**Interpretação:** erros concentram-se em amostras cujo perfil espectral foge do "
            "padrão da própria classe — ex.: anomalias sutis (vazamento leve) que soam próximas "
            "do funcionamento normal, ou máquinas normais com ruído de fábrica atipicamente alto.")
    else:
        add("Nenhum erro no conjunto de teste — separação perfeita entre as classes. "
            "Isso é esperado em dados sintéticos; com o dataset real, erros aparecem "
            "principalmente em anomalias sutis mascaradas pelo ruído de fábrica (0 dB SNR).")
    add("")
    add("### Features mais discriminativas (média por classe)")
    add("")
    add("| Feature | Média Normal | Média Anomalia | Diferença |")
    add("|---|---|---|---|")
    for feat, mean_n, mean_a, pct in r["divergent"]:
        add(f"| `{feat}` | {mean_n:.4f} | {mean_a:.4f} | {pct:+.1f}% |")
    add("")
    add("## 5. Modelos Exportados (pickle)")
    add("")
    add("| Arquivo | Conteúdo |")
    add("|---|---|")
    add("| `data/processed/models/mlp_sklearn_pipeline.pkl` | Pipeline sklearn (StandardScaler + MLPClassifier) pronto para inferência |")
    add("| `data/processed/models/mlp_hardcode.pkl` | Pesos e hiperparâmetros do hard-code (`carregar_modelo()`) |")
    add("| `data/processed/models/scaler.pkl` | StandardScaler ajustado no treino (para o hard-code) |")
    add("| `data/processed/models/feature_names.pkl` | Ordem das features esperada pelos modelos |")
    add("")
    add("Exemplo de inferência:")
    add("")
    add("```python")
    add("import pickle")
    add("with open('data/processed/models/mlp_sklearn_pipeline.pkl', 'rb') as f:")
    add("    pipeline = pickle.load(f)")
    add("proba = pipeline.predict_proba(X_novo)[:, 1]  # P(anomalia)")
    add("```")
    add("")
    add("## 6. Limitações e Riscos")
    add("")
    add("- Dataset desbalanceado (~5:1 normal:anomalia) — accuracy isolada engana; "
        "priorizar recall/F1 da classe anomalia.")
    add("- Modelo treinado com bombas específicas (id_00/02/04/06) e ruído de fábrica a 0 dB SNR — "
        "generalização para outras bombas/ambientes não é garantida.")
    add("- Threshold de decisão fixo em 0.5 — em produção, ajustar conforme o custo relativo "
        "de falso positivo (parada desnecessária) vs falso negativo (falha não detectada).")
    add("- Features agregadas por clip (médias) descartam a dinâmica temporal do som.")
    add("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Relatorio salvo em: {REPORT_PATH}")


def load_results_to_postgres(comparison_df, predictions_df):
    """Best-effort: carrega resultados no Postgres para o dashboard do Metabase."""
    try:
        from dotenv import find_dotenv, load_dotenv
        from sqlalchemy import create_engine

        load_dotenv(find_dotenv())
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "airflow")
        password = os.getenv("DB_PASS", "airflow")
        dbname = os.getenv("DB_NAME", "airflow")

        engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{dbname}",
            connect_args={"connect_timeout": 5},
        )
        comparison_df.to_sql("model_metrics", engine, schema="public",
                             if_exists="replace", index=False)
        predictions_df.to_sql("model_predictions", engine, schema="public",
                              if_exists="replace", index=False)
        print("Metricas e predicoes carregadas no PostgreSQL (model_metrics, model_predictions).")
    except Exception as e:
        print(f"Aviso: nao foi possivel carregar resultados no PostgreSQL ({e}). "
              "Rode novamente com os containers ativos para alimentar o dashboard.")


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  AVALIACAO: Baselines vs Hard-Code MLP vs Sklearn MLP")
    print("  Classificacao Binaria — Normal vs Anomalia")
    print("=" * 60)

    df = pd.read_csv(PROCESSED_DIR / "ml_features.csv")

    exclude_cols = [
        "file_id", "filename", "file_path", "condition",
        "condition_binary", "machine_type", "model_id",
    ]
    id_cols = [c for c in df.columns if c.endswith("_id") and c != "file_id"]
    exclude_cols.extend(id_cols)

    feature_cols = [c for c in df.columns if c not in exclude_cols]
    numeric_df = df[feature_cols].select_dtypes(include=["number"])
    feature_names = list(numeric_df.columns)
    X = numeric_df.fillna(0).values
    y = df["condition_binary"].values.astype(int)

    print(f"\nFeatures: {X.shape[1]}  |  Samples: {X.shape[0]}")
    print(f"Normal: {int(np.sum(y == 0))}  |  Anomalia: {int(np.sum(y == 1))}")

    indices = np.arange(len(df))
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, indices, test_size=0.2, random_state=42, stratify=y
    )
    df_test = df.iloc[idx_test].reset_index(drop=True)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    results = {}

    print("\n[1/4] Baseline — Classe Majoritaria (Dummy)...")
    results["dummy"] = train_and_eval(
        DummyClassifier(strategy="most_frequent"),
        X_train_s, y_train, X_test_s, y_test,
    )

    print("[2/4] Baseline — Regressao Logistica...")
    logreg = LogisticRegression(max_iter=1000, random_state=42)
    results["logreg"] = train_and_eval(logreg, X_train_s, y_train, X_test_s, y_test)

    print("[3/4] MLP Hard-Code (NumPy)...")
    start = time.time()
    hard_model = treinar(X_train_s, y_train)
    train_ms = (time.time() - start) * 1000

    start = time.time()
    y_pred_hard = prever(hard_model, X_test_s)
    pred_ms = (time.time() - start) * 1000

    metrics_hard = compute_metrics(y_test, y_pred_hard)
    metrics_hard["train_ms"] = train_ms
    metrics_hard["pred_ms"] = pred_ms
    metrics_hard["y_pred"] = np.asarray(y_pred_hard).astype(int).flatten()
    results["hardcode"] = metrics_hard

    print("[4/4] MLP Sklearn...")
    sk_model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
    )
    results["sklearn"] = train_and_eval(sk_model, X_train_s, y_train, X_test_s, y_test)

    model_labels = {
        "dummy": "Baseline Majoritaria",
        "logreg": "Baseline Reg. Logistica",
        "hardcode": "MLP Hard-Code",
        "sklearn": "MLP Sklearn",
    }

    print()
    header = f"{'Metrica':<22}" + "".join(f"{model_labels[m]:<26}" for m in results)
    print(header)
    print("-" * len(header))
    for key, label in [("accuracy", "Accuracy"), ("precision", "Precision"),
                       ("recall", "Recall"), ("f1", "F1-Score"),
                       ("train_ms", "Tempo Treino (ms)")]:
        row = f"{label:<22}" + "".join(f"{results[m][key]:<26.4f}" for m in results)
        print(row)

    comparison = {"Metrica": ["Accuracy", "Precision", "Recall", "F1-Score",
                              "Tempo Treino (ms)", "Tempo Predicao (ms)"]}
    for m in results:
        comparison[model_labels[m]] = [
            results[m]["accuracy"], results[m]["precision"],
            results[m]["recall"], results[m]["f1"],
            results[m]["train_ms"], results[m]["pred_ms"],
        ]
    comparison_df = pd.DataFrame(comparison)
    comparison_df.to_csv(PROCESSED_DIR / "model_comparison.csv", index=False)
    print(f"\nComparacao salva em: {PROCESSED_DIR / 'model_comparison.csv'}")

    plot_confusion_matrix(
        results["hardcode"]["cm"],
        "Matriz de Confusao — Hard-Code MLP",
        PROCESSED_DIR / "hardcode_cm.png",
    )
    plot_confusion_matrix(
        results["sklearn"]["cm"],
        "Matriz de Confusao — Scikit-Learn MLPClassifier",
        PROCESSED_DIR / "sklearn_cm.png",
    )
    print("Matrizes de confusao salvas (hardcode_cm.png, sklearn_cm.png).")

    # ------------------------------------------------------------------
    # Registro das predicoes por amostra (rastreabilidade dado -> predicao)
    # ------------------------------------------------------------------
    proba_hard = prever_probabilidade(hard_model, X_test_s)
    proba_sk = sk_model.predict_proba(X_test_s)[:, 1]

    predictions_df = pd.DataFrame({
        "file_id": df_test["file_id"],
        "model_id": df_test["model_id"],
        "condition_real": df_test["condition"],
        "y_true": y_test,
        "pred_hardcode": results["hardcode"]["y_pred"],
        "proba_hardcode": np.round(proba_hard, 6),
        "pred_sklearn": results["sklearn"]["y_pred"],
        "proba_sklearn": np.round(proba_sk, 6),
    })
    predictions_df["erro_sklearn"] = (
        predictions_df["y_true"] != predictions_df["pred_sklearn"]
    ).astype(int)
    predictions_df.to_csv(PROCESSED_DIR / "predictions.csv", index=False)
    print(f"Predicoes do teste salvas em: {PROCESSED_DIR / 'predictions.csv'}")

    # ------------------------------------------------------------------
    # Export dos modelos treinados (pickle)
    # ------------------------------------------------------------------
    sk_pipeline = Pipeline([("scaler", scaler), ("mlp", sk_model)])
    with open(MODELS_DIR / "mlp_sklearn_pipeline.pkl", "wb") as f:
        pickle.dump(sk_pipeline, f)

    salvar_modelo(hard_model, MODELS_DIR / "mlp_hardcode.pkl")

    with open(MODELS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(MODELS_DIR / "feature_names.pkl", "wb") as f:
        pickle.dump(feature_names, f)

    print(f"Modelos exportados em: {MODELS_DIR}/")
    for p in sorted(MODELS_DIR.glob("*.pkl")):
        print(f"  - {p.name} ({p.stat().st_size / 1024:.1f} KB)")

    # ------------------------------------------------------------------
    # Relatorio de analise (report_analys.md)
    # ------------------------------------------------------------------
    errors, n_errors = analyze_errors(
        df_test, y_test, results["sklearn"]["y_pred"], proba_sk,
        X_test_s, feature_names,
    )
    hits = sample_hits(df_test, y_test, results["sklearn"]["y_pred"], proba_sk)
    divergent = top_divergent_features(df, feature_names)

    write_report({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "n_samples": len(df),
        "n_features": X.shape[1],
        "n_normal": int(np.sum(y == 0)),
        "n_anomaly": int(np.sum(y == 1)),
        "n_test": len(y_test),
        "n_test_normal": int(np.sum(y_test == 0)),
        "n_test_anomaly": int(np.sum(y_test == 1)),
        "results": results,
        "errors": errors,
        "n_errors_sklearn": n_errors,
        "hits": hits,
        "divergent": divergent,
    })

    # ------------------------------------------------------------------
    # Resultados para o dashboard (Metabase)
    # ------------------------------------------------------------------
    load_results_to_postgres(comparison_df, predictions_df)

    print("\nAvaliacao concluida.")


if __name__ == "__main__":
    main()
