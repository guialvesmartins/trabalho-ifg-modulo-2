---
title: "Rede Neural MLP"
date: 2025-07-03
tags:
  - conceito
  - ml
  - mlp
  - rede-neural
  - backpropagation
---

# Rede Neural MLP

## Definição

Uma **MLP** (*Multi-Layer Perceptron*) é um tipo de rede neural feedforward: camadas de neurônios conectadas em sequência, onde cada neurônio soma suas entradas ponderadas, aplica uma função de ativação e passa o resultado adiante.

No projeto, a MLP responde a uma pergunta binária: **"esta bomba está com anomalia?"** → sim (1) ou não (0).

### Arquitetura do projeto

```
Input (96 features numéricas)
  ↓
Hidden Layer 1 (64 neurônios, ReLU)
  ↓
Hidden Layer 2 (32 neurônios, ReLU)
  ↓
Output (1 neurônio, Sigmoid) → P(anomalia)
```

### Funções de ativação

- **ReLU** (`max(0, x)`): usada nas camadas ocultas — introduz não-linearidade e ajuda a evitar o desaparecimento do gradiente
- **Sigmoid** (`1 / (1 + e^-x)`): na saída — comprime o valor para 0..1, interpretável como probabilidade

### Treinamento (Backpropagation)

1. **Forward pass:** as features passam pela rede e produzem uma predição
2. **Loss (Binary Cross-Entropy):** mede o erro entre predição e valor real
3. **Backward pass:** derivadas da loss em relação a cada peso (regra da cadeia) — calculadas analiticamente
4. **Otimizador:** atualiza os pesos na direção que reduz o erro

- **Hard-code:** mini-batch **SGD com momento** (lr=0.01, momentum=0.9), 300 épocas, batch 32
- **Sklearn:** **Adam** (adaptativo), L2 (alpha=0.0001), max_iter=500

## Como foi implementado no projeto

**Hard-code** (`ml/hard_code/neural_network_hardcode.py`): implementamos 100% do forward/backward com operações matriciais do NumPy — sem autograd, TensorFlow ou PyTorch. Inicialização **He** (`sqrt(2/fan_in)`), threshold 0.5 na sigmoid.

**Sklearn** (`ml/library/neural_network_sklearn.py`): `MLPClassifier(hidden_layer_sizes=(64, 32))` com os mesmos dados, split e scaler.

**Comparação** (`ml/evaluate.py`): ambos atingem resultados idênticos (validando a implementação manual); o sklearn é ~6.7x mais rápido no treino. O MLP supera a regressão logística principalmente no **recall da classe anomalia** (+10 p.p.).

> [!warning] Desbalanceamento
> O dataset tem ~8:1 (normal:anomalia). O split usa `stratify` e a avaliação prioriza recall/F1 da classe minoritária.

## Relacionado

- [[06-Machine-Learning]]
- [[Conceito - MFCC e Features de Audio]]
