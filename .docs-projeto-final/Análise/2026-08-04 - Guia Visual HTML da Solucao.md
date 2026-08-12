---
title: "Guia Visual HTML da Solução para a Banca"
date: 2026-08-04
tags:
  - analise
  - documentacao
  - apresentacao
---

# Guia Visual HTML da Solução para a Banca

**Data:** 2026-08-04

## O que foi feito

Criado o arquivo `report/explicacao_projeto.html` — um relatório didático em HTML único e autocontido (CSS + SVG + JS inline, sem CDN) para explicar o projeto à banca avaliadora. Contém 11 seções com navegação lateral fixa (scrollspy) e infográficos em SVG/CSS:

1. Visão Geral
2. Problema de Negócio
3. Os Dados (MIMII Pump)
4. Extração de Features
5. Pipeline ELT (Airflow + dbt)
6. Modelo de ML (MLP hard-code × sklearn)
7. Cloud Computing (dev × 100% AWS)
8. Dashboard Metabase
9. Status de Desenvolvimento (checklist vs. PDF de especificação)
10. Conceitos-chave & Como Reproduzir

## Motivo

O usuário pediu um relatório visual, fluido e fácil de navegar para entender a solução e saber explicá-la (prioridade: apresentação para a banca), incluindo o status de desenvolvimento dividido pelos pilares Dados, ML e Cloud Computing.

## Impacto

- **Arquivo novo:** `report/explicacao_projeto.html` (tema claro, português, números 100% dos documentos do repositório — `report_analys.md`, `docs/ARQUITETURA_AWS.md`, etc.)
- **Nenhum outro arquivo do projeto foi alterado.**
- Status consolidado: Dados ~90%, ML ~100%, Cloud ~75% (pendências: execução real em Snowflake/AWS e evidências de execução no repo).

## Atualizações

### 2026-08-05 — Resumo do fluxo no card do DAG

- A seção independente "Fluxo Passo a Passo" foi **removida** e seu conteúdo **movido para dentro do card "DAG `etl_pipeline` — execução sequencial"** (seção 5, Pipeline ELT), logo abaixo do fluxograma SVG.
- As 9 etapas foram **resumidas em uma frase cada** (grid `.mini-steps`, 3 colunas): o que acontece + script envolvido. Navegação lateral voltou a 10 itens.

### 2026-08-05 — Diagrama da arquitetura MLP corrigido

- O SVG do card "Arquitetura da rede" (seção 6, ML) estava com textos cortados (labels além do `viewBox` 520×300, ex.: `64 neurônios` em `y=306`).
- Redesenhado com precisão em `viewBox 0 0 520 330`: 5 nós visíveis por camada + elipse vertical `⋮` indicando os demais nós (96/64/32), conexões **completas** entre camadas adjacentes (25 + 25 + 5 linhas), rótulos de camada reposicionados dentro da área visível e saída (1 · Sigmoid) com rótulo sob o nó.

## Relacionado

- [[03-Arquitetura]]
- [[06-Machine-Learning]]
- [[04-Pipeline-ELT]]
- [[10-Infra-AWS]]
