---
title: Machine Learning
date: 2025-07-03
tags:
  - ml
  - machine-learning
  - mlp
  - sklearn
  - features
aliases:
  - ML
  - Aprendizagem de Máquina
  - Modelo
---

# Machine Learning

[[Home|Voltar ao índice]]

---

## Tarefa

**Classificação binária** — prever se a bomba está com anomalia ("Esta bomba está com anomalia?")

| Atributo | Valor |
|----------|-------|
| **Tipo** | Classificação binária (2 classes) |
| **Target** | `condition_binary` ∈ {0 = normal, 1 = anomaly} |
| **Features de entrada** | 96 features numéricas (de áudio + metadados) |
| **Algoritmo** | MLP binário (hard-code NumPy + sklearn MLPClassifier) |

---

## Features

Total após merge: **103 colunas × 4.205 linhas** (96 features numéricas usadas no ML).

### MFCC — 80 features

40 coeficientes Mel-Frequency Cepstral, média e desvio padrão de cada. Capturam o "timbre" do som industrial.

| Feature | O que representa |
|---|---|
| `mfcc_1_mean` a `mfcc_40_mean` | Média de cada coeficiente MFCC |
| `mfcc_1_std` a `mfcc_40_std` | Variabilidade de cada coeficiente |

### Features Espectrais — 10 features

| Feature | Significado |
|---|---|
| `spectral_centroid_mean` | Centro de massa do espectro — grave ou agudo |
| `spectral_bandwidth_mean` | Largura da banda espectral |
| `spectral_rolloff_mean` | Frequência abaixo da qual está 85% da energia |
| `spectral_contrast_1_mean` a `spectral_contrast_7_mean` | Contraste entre picos e vales em 7 bandas |

### Features de Energia e Ritmo — 2 features

| Feature | Significado |
|---|---|
| `zcr_mean` | Zero-Crossing Rate — frequência dominante percebida |
| `rms_mean` | Root Mean Square — energia/potência do sinal |

### Features Estruturadas — 6 colunas

`machine_type`, `model_id`, `condition`, `duration_sec`, `sample_rate`, `channels`

---

## O Modelo MLP

### Arquitetura

```
Input (96 features numéricas)
  ↓
Hidden Layer 1 (64 neurônios, ReLU)
  ↓
Hidden Layer 2 (32 neurônios, ReLU)
  ↓
Output (1 neurônio, Sigmoid) → P(anomalia)
```

### Hard-Code (NumPy puro) — `ml/hard_code/neural_network_hardcode.py`

| Componente | Configuração |
|------------|--------------|
| Classe | `HardCodedMLP` |
| Inicialização | He initialization (`sqrt(2/fan_in)`) |
| Forward pass | ReLU nas hidden layers, Sigmoid na saída |
| Backward pass | Backpropagation manual com gradientes analíticos |
| Loss | Binary Cross-Entropy |
| Otimizador | Mini-batch SGD com momento (lr=0.01, momentum=0.9) |
| Treinamento | 300 épocas, batch_size=32 |
| Predição | Threshold 0.5 na sigmoid |

> [!info] 100% do forward/backward com operações matriciais do NumPy — sem autograd, TensorFlow ou PyTorch.

### Sklearn — `ml/library/neural_network_sklearn.py`

| Componente | Configuração |
|------------|--------------|
| Classe | `MLPClassifier` |
| Arquitetura | `hidden_layer_sizes=(64, 32)` |
| Otimizador | Adam (adaptativo) |
| Regularização | L2 (alpha=0.0001) |
| Treinamento | max_iter=500 |

### Hard-Code vs Sklearn

- Ambos produzem resultados idênticos (validando a implementação manual)
- Sklearn é ~6.7x mais rápido no treino (Adam + código C otimizado)
- Hard-code é mais lento mas didático (SGD com momento em Python puro)

---

## Baselines

| Baseline | Descrição |
|----------|-----------|
| **Dummy (majoritária)** | Sempre prevê a classe majoritária (normal) |
| **Regressão Logística** | Modelo linear como referência inferior |

---

## Avaliação e Comparação

**Arquivo:** `ml/evaluate.py` (split 80/20 com stratify + StandardScaler)

### Métricas no teste (841 amostras — 750 normais, 91 anomalias)

| Métrica | Baseline Majoritária | Reg. Logística | MLP Hard-Code | MLP Sklearn |
|---|---|---|---|---|
| Accuracy | 89,18% | 96,79% | 97,86% | **97,98%** |
| Precision | 0% | 95,71% | 96,20% | **97,44%** |
| Recall | 0% | 73,63% | **83,52%** | **83,52%** |
| F1-Score | 0 | 0,832 | 0,894 | **0,899** |
| Tempo Treino | ~0 ms | ~15 ms | ~2.600 ms | ~425 ms |

> [!warning] Baseline majoritária
> Atinge 89% de accuracy só pelo desbalanceamento, mas recall 0 (inútil). Os MLPs superam a regressão logística principalmente em recall da classe anomalia (+10 p.p.).

### Matriz de Confusão (MLP Sklearn)

```
                  Predito
                  Normal  Anomalia
Real Normal        748       2
Real Anomalia       15      76
```

- **2 falsos positivos** — paradas desnecessárias raras (precision 97,4%)
- **15 falsos negativos** — anomalias sutis não detectadas (recall 83,5%); erros dominantes, analisados por amostra em `report_analys.md`

### Análise das Features

As features mais discriminativas são os **MFCCs** (perfil timbral completo): `mfcc_35_mean`, `mfcc_31_mean`, `mfcc_10_mean`, `mfcc_3_mean` apresentam as maiores diferenças entre classes. Os erros concentram-se em anomalias cujo espectro foge do padrão da classe (defeitos sutis mascarados pelo ruído de fábrica a 0 dB SNR).

---

## Artefatos Gerados

- `data/processed/predictions.csv` — predição por amostra do teste (rastreabilidade)
- `data/processed/model_comparison.csv` — métricas dos 4 modelos
- Matrizes de confusão (PNG)
- `data/processed/models/` — `mlp_sklearn_pipeline.pkl`, `mlp_hardcode.pkl`, `scaler.pkl`, `feature_names.pkl`
- `report_analys.md` (raiz) — relatório completo de cada treino

---

## Comandos

```bash
make ml-train    # Roda hard-code + sklearn + evaluate
```
