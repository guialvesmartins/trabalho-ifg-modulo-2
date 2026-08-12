---
title: "Guias de Apresentação HTML por Integrante"
date: 2026-08-12
tags:
  - analise
  - apresentacao
  - guia-estudo
  - html
---

# Guias de Apresentação HTML por Integrante

**Data:** 2026-08-12

## O que foi feito

Criados 4 guias de estudo em HTML autocontidos (um por integrante da apresentação), em `report/`, para dominar o conteúdo dos ~3 min de cada um:

- `guia-apresentacao-guilherme.html` — Visão Geral e Arquitetura (problema, MIMII, ELT, Airflow, dbt, fluxo até o Metabase)
- `guia-apresentacao-walber.html` — Processamento e Feature Engineering (metadados, librosa, MFCC/espectrais/temporais, merge)
- `guia-apresentacao-daniel.html` — Modelagem de ML (hard-code vs sklearn, arquitetura, backprop, SGD+Adam, métricas)
- `guia-apresentacao-david.html` — Resultados e Demonstração Prática (dashboards Metabase, matriz de confusão, inferência ao vivo)

## Motivo

Cada integrante precisa dominar sua parte e responder bem à banca. Um guia de estudo consistente com o código real do projeto (e não com o slide — que continha imprecisões) reduz risco de erro na apresentação.

## Impacto

- **Design:** série coesa (dark/light, tipografia fluida, assinatura visual própria por integrante); cada guia tem pitch de 30 s, roteiro narrado de 3 min, domínio conceitual, números para decorar e simulado de perguntas da banca.
- **Correções importantes embutidas:**
  - Daniel: saída é **Sigmoid(1)** no hard-code (não Softmax(2)) — explicada a equivalência binária.
  - Walber: StandardScaler é aplicado no **ML**, não no processamento; total real é 4.205 linhas/92 features (não 2.400).
  - Guilherme: 16 testes dbt e números do dataset real.
  - David: métricas reais de `report_analys.md` (2026-08-11) e tempos de treino atualizados.
- Arquivos afetados: `report/guia-apresentacao-{guilherme,walber,daniel,david}.html`

## Relacionado

- [[2026-08-04 - Guia Visual HTML da Solucao]]
- [[2026-08-10 - Apresentacao Final Deck Dark 12 Slides]]
- [[06-Machine-Learning]]
- [[03-Arquitetura]]
- [[04-Pipeline-ELT]]
- [[07-Dashboard]]
