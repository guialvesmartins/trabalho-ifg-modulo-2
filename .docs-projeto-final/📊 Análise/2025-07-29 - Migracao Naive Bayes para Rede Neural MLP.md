---
title: "Migracao de Naive Bayes para Rede Neural MLP"
date: 2025-07-29
tags:
  - analise
  - ml
  - rede-neural
  - mlp
  - nlp
---

# Migracao de Naive Bayes para Rede Neural MLP

**Data:** 2025-07-29

## O que foi feito

1. **Modelo trocado**: Naive Bayes → Rede Neural Feedforward (MLP)
2. **NLP simplificado**: de ~50 features textuais para apenas 4 (polarity, review_length, contains_complaint, contains_praise)
3. **Features totais**: 22 features (12 estruturadas + 4 NLP + 6 CV)
4. **Arquitetura**: Input(22) → Hidden1(64, ReLU) → Hidden2(32, ReLU) → Output(4-5 classes, Softmax)
5. **Versão hard-code**: implementada do zero com NumPy (SGD + momento)
6. **Versão biblioteca**: sklearn MLPClassifier (Adam)
7. **Comparação executada** com resultados:

| Metrica | Hard-Code | Sklearn |
|---------|-----------|---------|
| Accuracy | 71.48% | 73.70% |
| F1 (macro) | 0.3098 | 0.3195 |
| Tempo Treino | 844ms | 657ms |

## Motivo

O usuário solicitou substituir Naive Bayes por rede neural, mantendo NLP de forma simplificada.

## Impacto

Arquivos alterados:
- `ml/hard_code/neural_network_hardcode.py` — NOVO: MLP do zero
- `ml/library/neural_network_sklearn.py` — NOVO: MLPClassifier (substitui Naive Bayes sklearn)
- `ml/evaluate.py` — atualizado para comparar NNs
- `ml/sklearn/` → renomeado para `ml/library/` (evitava conflito com biblioteca sklearn)
- `ml/hard_code/_old_naive_bayes_hardcode.py` — arquivado
- `ml/library/_old_naive_bayes.py` — arquivado
- `data/processed/ml_features.csv` — novo schema com 22 features
- `data/processed/model_comparison.csv` — resultados da comparação
- `data/processed/hardcode_cm.png` — matriz de confusão hard-code
- `data/processed/sklearn_cm.png` — matriz de confusão sklearn
- PostgreSQL: views recriadas com novo schema
- Metabase: cards NLP removidos, novos cards criados
- `Makefile`: target `ml-train` atualizado

## Relacionado

- [[06-Machine-Learning]]
- [[05-Modelagem-dbt]]
- [[Conceito - Naive Bayes]]
- [[Conceito - NLP e TF-IDF]]
