---
title: Machine Learning
date: 2025-07-03
tags:
  - ml
  - machine-learning
  - naive-bayes
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

**Classificação multiclasse** — prever rating do produto (1 a 5 estrelas)

| Atributo | Valor |
|----------|-------|
| **Tipo** | Classificação multiclasse (5 classes) |
| **Target** | `rating` ∈ {1, 2, 3, 4, 5} |
| **Features de entrada** | ~255 features (217 texto + 28 imagem + ~10 estruturadas) |
| **Algoritmo** | Naive Bayes (hard-code + sklearn) |

---

## Features de Texto (NLP) — 217 features

### Metadados (4)
`review_length`, `word_count`, `avg_word_length`, `sentence_count`

### Estilo (4)
`uppercase_ratio`, `exclamation_count`, `question_count`, `numeric_ratio`

### Sentimento — VADER (3)
`polarity` (-1 a 1), `subjectivity` (0 a 1), `compound_score`

### TF-IDF — Top 200 (200)
Palavras/bigramas mais relevantes do corpus de reviews

### Regex Custom (4)
`contains_complaint`, `contains_praise`, `contains_price_mention`, `contains_delivery_mention`

### Legibilidade — textstat (2)
`flesch_reading_ease`, `complex_word_ratio`

> [!tip] Total: **~217 features textuais** por review

---

## Features de Imagem (CV) — 28 features

### Dimensões — PIL (5)
`width`, `height`, `aspect_ratio`, `file_size_kb`, `format`

### Cores — OpenCV + K-Means (12)
`dominant_color_1_rgb` (3), `dominant_color_2_rgb` (3), `dominant_color_3_rgb` (3)
`brightness_mean`, `saturation_mean`, `colorfulness_score`

### Nitidez — OpenCV Laplacian (1)
`blur_score` (variância do Laplaciano)

### Complexidade Visual — OpenCV Canny + Harris (2)
`edge_density`, `corner_count`

### Textura — skimage GLCM (2)
`entropy`, `contrast`

### Histograma — OpenCV (6)
`hist_mean_r/g/b`, `hist_std_r/g/b`

> [!tip] Total: **~28 features visuais** por imagem

---

## Features Estruturadas — ~10 features

| Coluna original | Tratamento | Feature final |
|-----------------|------------|---------------|
| `category` | Lowercase, one-hot encoding | `cat_electronics`, `cat_clothing`, ... |
| `actual_price` | float, log transform | `log_price`, `price` |
| `discount_percentage` | float, bucket | `discount_bucket_low/med/high` |
| `rating_count` | int, log transform | `log_rating_count` |
| `rating` | int (1-5) → **TARGET** | `target_rating` |

---

## Baseline

| Baseline | Descrição |
|----------|-----------|
| **Simples** | Prever sempre a classe majoritária (rating mais frequente) |
| **Melhorado** | Prever apenas com dados estruturados (sem texto nem imagem) |
| **Completo** | Modelo com todas as features (estruturado + texto + imagem) |

---

## Naive Bayes Hard-Code

**Arquivo:** `ml/hard_code/naive_bayes_hardcode.py`

Algoritmo implementado do zero:

```python
# 1. Calcular log-prior para cada classe c = {1,2,3,4,5}
#    log P(classe c)

# 2. Para cada palavra w e cada classe c:
#    P(w|c) = (count(w, c) + alpha) / (total_palavras_c + alpha * |V|)
#    alpha = 1 (Laplace smoothing)

# 3. Classificar novo texto:
#    score(c) = log P(c) + Σ log P(w_i|c)
#    predição = argmax_c score(c)
```

> [!info] Opera em **log-space** para evitar underflow numérico. Suporta features binárias (presença/ausência) ou contagem de frequência.

---

## Naive Bayes com Sklearn

**Arquivo:** `ml/sklearn/naive_bayes_sklearn.py`

```python
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
```

> [!warning] Comparação justa
> Mesmos dados, mesma divisão train/test que o hard-code.

---

## Avaliação e Comparação

**Arquivo:** `ml/evaluate.py`

| Métrica | Hard-Code | Sklearn | Baseline |
|---------|-----------|---------|----------|
| Accuracy | | | |
| Precision (macro) | | | |
| Recall (macro) | | | |
| F1-Score (macro) | | | |
| Matriz de confusão | | | |
| Tempo de treino | | | |
| Tempo de predição | | | |

### Questões para o Relatório

- Os resultados são iguais/similares? Por quê?
- Onde o hard-code diverge do sklearn?
- Qual o impacto de adicionar features de texto vs só estruturadas?
- Imagens melhoraram a acurácia?

---

## Comandos

```bash
make ml-train    # Roda hard-code + sklearn + evaluate
```
