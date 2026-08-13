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

Reconstruídos do zero 4 guias de estudo em HTML autocontidos (um por integrante), em `report/`, **fiéis ao `apresentacao.pptx`** — que organiza a apresentação por pilares:

- `guia-apresentacao-guilherme.html` — Pilar 1 (slides 2–3): problema de negócio + dataset MIMII
- `guia-apresentacao-walber.html` — Pilar 1 (slides 4–6): features de áudio + pipeline ELT + Airflow/dbt
- `guia-apresentacao-daniel.html` — Pilar 2 (slides 7–9): arquitetura MLP, hard-code vs sklearn, resultados/métricas
- `guia-apresentacao-david.html` — Pilar 3 (slides 10–12): arquitetura AWS, dev→prod, dashboard/decisão

## Motivo

Cada integrante precisa dominar sua parte e responder bem à banca. Os guias seguem a divisão real do slide (por pilares) para que ninguém pise no assunto do outro, e corrigem imprecisões do deck contra o código do projeto.

## Impacto

- **Design:** série coesa (dark/light, tipografia fluida, assinatura visual própria por integrante); cada guia tem pitch de 30 s, roteiro narrado de 3 min, domínio conceitual, números para decorar, simulado da banca e um bloco "🎯 foco / 👥 colegas" para delimitar cada parte.
- **Correções slide × código embutidas:**
  - Daniel: saída é **Sigmoid(1)** no hard-code (não Softmax(2)); slide diz "6,7× mais rápido", relatório mostra ~3×.
  - Walber: slide diz "11 espectrais" e "14 testes dbt"; o código tem **10 espectrais** e **16 testes** (`schema.yml`).
  - David: conteúdo passou de "resultados + demo" para **Cloud + dashboard** (demo ao vivo removida por decisão do grupo).
- Arquivos afetados: `report/guia-apresentacao-{guilherme,walber,daniel,david}.html`

## Relacionado

- [[2026-08-04 - Guia Visual HTML da Solucao]]
- [[2026-08-10 - Apresentacao Final Deck Dark 12 Slides]]
- [[06-Machine-Learning]]
- [[03-Arquitetura]]
- [[04-Pipeline-ELT]]
- [[07-Dashboard]]
