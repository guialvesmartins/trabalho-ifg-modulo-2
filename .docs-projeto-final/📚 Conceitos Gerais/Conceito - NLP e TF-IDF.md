---
title: "NLP e TF-IDF"
date: 2025-07-03
tags:
  - conceito
  - nlp
  - tf-idf
  - vader
  - texto
---

# NLP e TF-IDF

## Definição

NLP (*Natural Language Processing*) é o conjunto de técnicas para fazer o computador entender texto humano. No nosso caso, queremos extrair características numéricas de reviews de produtos para alimentar um modelo de machine learning.

### VADER (Valence Aware Dictionary and sEntiment Reasoner)

É um analisador de sentimento que, dado um texto, retorna um score de -1 (muito negativo) a +1 (muito positivo). Ele entende gírias, pontuação (!!!), CAPS LOCK e negações ("não é bom" = negativo). Não precisa treinar — é um dicionário pré-configurado.

- **polarity:** sentimento geral (-1 a 1)
- **subjectivity:** quão subjetivo/emocional é o texto (0 a 1)

### TF-IDF (Term Frequency — Inverse Document Frequency)

Mede a importância de uma palavra em um documento, considerando todo o corpus:

- **TF:** quantas vezes a palavra aparece naquela review
- **IDF:** em quantas reviews do total essa palavra aparece (quanto mais rara, mais importante)

Exemplo: "produto" aparece em quase TODAS as reviews → TF-IDF baixo. "defeituoso" aparece em poucas → TF-IDF alto (palavra mais informativa).

### Features customizadas

Além das técnicas prontas, criamos regras manuais para detectar menções a reclamação ("terrível", "quebrou"), elogio ("excelente", "recomendo"), preço ("caro", "barato") e entrega ("rápido", "atrasou").

## Como foi implementado no projeto

**217 features extraídas** de cada review:

| Categoria | Features | Técnica |
|-----------|----------|---------|
| Metadados | 4 | `len()`, `split()`, `.count()` |
| Estilo | 4 | Contagem de maiúsculas, exclamações, números |
| Sentimento | 3 | VADER |
| Palavras-chave | 50 (TF-IDF) | `TfidfVectorizer` do sklearn |
| Regex custom | 4 | Expressões regulares Python |
| **Total** | **~65** (reduzido para evitar overfitting) | |

Usamos `vaderSentiment` (biblioteca leve, sem necessidade de GPU ou modelo pesado) e `scikit-learn` para o TF-IDF. Tudo roda localmente em segundos.

## Relacionado

- [[06-Machine-Learning]]
- [[Conceito - Naive Bayes]]
- [[04-Pipeline-ELT]]
