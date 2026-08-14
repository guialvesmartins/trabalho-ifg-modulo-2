---
title: "Reescrita do Hard-Code MLP para Estilo Manual"
date: 2026-08-14
tags:
  - analise
  - ml
  - hard-code
  - apresentacao
---

# Reescrita do Hard-Code MLP para Estilo Manual

**Data:** 2026-08-14

## O que foi feito

O `ml/hard_code/neural_network_hardcode.py` foi reescrito de uma **classe** (`HardCodedMLP`) para **funções procedurais** com cara de "escrito à mão" e fácil de explicar:

- `treinar()` — loop de treinamento (forward + backward + SGD com momento)
- `prever()` / `prever_probabilidade()` — inferência com threshold 0,5
- `salvar_modelo()` / `carregar_modelo()` — persistência via pickle
- Funções auxiliares com nomes em português (`relu`, `derivada_relu`, `sigmoid`, `inicializar_pesos`, `forward`, `backward`, `perda_bce`) e comentários passo a passo de cada equação

Os hiperparâmetros foram **mantidos idênticos** (64→32→1, ReLU/sigmoid, BCE, SGD+momento lr 0,01 / 0,9, 300 épocas, batch 32, seed 42), de modo que **os resultados não mudam** — permanecem os do `report_analys.md` (hard-code 97,86% / F1 0,894; sklearn 97,98% / F1 0,899).

## Motivo

O código anterior era "top demais": classe com `cache` de forward, `loss_history`, nomes enxutos (`_forward`, `_backward`) — parecia código de engenheiro, não de aluno. O grupo queria que a implementação manual **parecesse realmente manual** e fosse **fácil de explicar para a banca** como foi construída.

## Impacto

Arquivos alterados:
- `ml/hard_code/neural_network_hardcode.py` — reescrita procedural
- `ml/evaluate.py` — passa a usar `treinar()`/`prever()`/`prever_probabilidade()`/`salvar_modelo()`
- `tests/test_ml.py` — 4 testes atualizados para a API procedural
- `report_analys.md` — referência `carregar_modelo()` no lugar de `HardCodedMLP.load()`
- `report/apresentacao.pptx` — slide 8 corrigido de "~6,7× mais rápido" para "~3× mais rápido" (11,3 s vs 3,8 s)
- Guias HTML (`guia-apresentacao-daniel.html`, `explicacao_projeto.html`) e `divisao-apresentacao.md` — números harmonizados
- `README.md`, `CLAUDE.md`, `FLUXO.md`, `doc_min.md`, `docs/RELATORIO_TECNICAS.md`, vault `06-Machine-Learning.md`, `12-Passo-a-Passo.md`, `Conceito - Rede Neural MLP.md` — referências à classe e a velocidade ~3×

## Relacionado

- [[06-Machine-Learning]]
- [[Conceito - Rede Neural MLP]]
- [[2026-08-12 - Guias de Apresentacao HTML por Integrante]]
