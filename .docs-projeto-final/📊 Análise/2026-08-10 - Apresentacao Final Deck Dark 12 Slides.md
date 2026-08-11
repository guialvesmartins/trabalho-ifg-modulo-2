---
title: "Apresentação Final — Deck Dark 12 Slides (4 Locutores)"
date: 2026-08-10
tags:
  - analise
  - apresentacao
  - design
---

# Apresentação Final — Deck Dark 12 Slides (4 Locutores)

**Data:** 2026-08-10

## O que foi feito

`report/apresentacao.pptx` foi **regenerado do zero** seguindo um prompt de "designer de apresentações executivas": deck dark mode (navy `#0A1024` + ciano `#22D3EE` + azul `#3B82F6`), fontes grandes, muito whitespace e conteúdo altamente resumido. Estrutura ampliada de 9 para **12 slides** (autorizado pelo grupo), com o locutor indicado no rodapé de cada slide:

1. **Título do Projeto** (Todos)
2. **O Problema de Negócio** (Integrantes 1 e 2)
3. **Os Dados — Dataset MIMII** (Integrantes 1 e 2)
4. **Extração de Features do Áudio** (Integrantes 1 e 2)
5. **Pipeline ELT — 8 Etapas** (Integrantes 1 e 2)
6. **Airflow e dbt — Orquestração** (Integrantes 1 e 2)
7. **O Modelo — Rede Neural (MLP)** (Integrante 3)
8. **Hard-Code vs Sklearn** (Integrante 3)
9. **Resultados e Métricas** (Integrante 3)
10. **Arquitetura 100% AWS** (Integrante 4)
11. **Dev ↔ Prod e Infraestrutura** (Integrante 4)
12. **Dashboard e Decisão Final** (Integrante 4)

## Motivo

O grupo aprovou expandir os 9 slides originais para até 12. A expansão balanceia a fala: Integrantes 1 e 2 ficam com o Pilar 1 (5 slides), Integrante 3 com o Pilar 2 (3 slides) e Integrante 4 com o Pilar 3 (3 slides), além de destacar diferenciais de banca — o MLP **hard-code em NumPy** (backprop/SGD do zero) e o **switch dev↔prod por 4 variáveis de ambiente**.

## Impacto

- **Arquivo substituído:** `report/apresentacao.pptx` (12 slides, 16:9, ~500 KB).
- Nenhum outro arquivo do projeto alterado.

## Detalhes técnicos

- Gerado com **pptxgenjs** (JS), layout 16:9 (10" × 5,625"); ícones vetoriais via `react-icons` + `sharp`.
- Paleta dark: fundo navy, cards `#111B3B`, bordas `#1E2B57`, acentos ciano/azul/índigo; fonte Segoe UI.
- **QA:** cada slide exportado via PowerPoint COM para PNG (1920×1080); medição numérica de largura de texto (PIL, fontes Segoe UI reais) para evitar quebras; verificação por pixel de cor de barras/matriz/footer.
- **Bugs corrigidos na iteração:** título da capa estourando 2 linhas; pílula "Zenodo" invadindo o rodapé do card no slide 3; anotação da matriz de confusão ultrapassando o card (slide 9); banners inferiores colidindo com o rodapé; títulos com quebra de linha; contraste de textos pequenos (dim → muted).

## Relacionado

- [[2026-08-05 - Recriacao da Apresentacao]]
- [[2026-08-04 - Guia Visual HTML da Solucao]]
