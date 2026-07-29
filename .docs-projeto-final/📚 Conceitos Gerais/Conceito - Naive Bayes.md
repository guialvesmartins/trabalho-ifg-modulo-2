---
title: "Naive Bayes"
date: 2025-07-03
tags:
  - conceito
  - ml
  - naive-bayes
  - classificacao
---

# Naive Bayes

## Definição

Naive Bayes é um algoritmo de classificação baseado no **Teorema de Bayes**, que calcula a probabilidade de algo pertencer a uma classe com base em evidências observadas.

O "Naive" (ingênuo) vem da suposição de que todas as características são independentes entre si — ou seja, a presença da palavra "bom" não tem relação com a presença da palavra "produto". Na prática, isso não é verdade, mas o algoritmo funciona surpreendentemente bem mesmo assim.

Para classificar uma review, o algoritmo pergunta: "dado que essa review contém as palavras X, Y, Z, qual a probabilidade dela ser nota 1? E nota 2? ... E nota 5?" e escolhe a classe com maior probabilidade.

### Laplace Smoothing

Se uma palavra nunca apareceu em reviews nota 5 durante o treino, a probabilidade seria zero — e multiplicar por zero zera tudo. O Laplace Smoothing adiciona um "chute" (+1) para cada palavra em cada classe, evitando esse problema.

### Log-space

Multiplicar centenas de probabilidades muito pequenas causa underflow numérico (o número fica tão pequeno que o computador arredonda para zero). Por isso trabalhamos em log-space: somamos logaritmos em vez de multiplicar probabilidades.

## Como foi implementado no projeto

**Hard-code** (`ml/hard_code/naive_bayes_hardcode.py`): implementamos o algoritmo do zero, só com Python e NumPy, seguindo exatamente a matemática descrita acima.

**Sklearn** (`ml/sklearn/naive_bayes_sklearn.py`): usamos o `MultinomialNB` da biblioteca scikit-learn com os mesmos dados.

**Comparação** (`ml/evaluate.py`): rodamos os dois lado a lado e comparamos acurácia, precisão, recall, F1-score e tempo de treino. O PDF pede exatamente essa comparação entre hard-code e biblioteca.

## Relacionado

- [[06-Machine-Learning]]
- [[Conceito - NLP e TF-IDF]]
