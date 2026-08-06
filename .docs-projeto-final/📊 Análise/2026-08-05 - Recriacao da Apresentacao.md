---
title: "Recriação da Apresentação (MIMII Pump)"
date: 2026-08-05
tags:
  - analise
  - documentacao
  - apresentacao
---

# Recriação da Apresentação (MIMII Pump)

**Data:** 2026-08-05

## O que foi feito

O arquivo `report/apresentacao.pptx` foi **recriado do zero** (12 slides, 16:9) porque o deck antigo ainda era do projeto **descartado** (Previsão de Satisfação em E-commerce: NLP + Visão Computacional + Naive Bayes). O novo conteúdo reflete o projeto atual aprovado:

1. **Capa** — Manutenção Preditiva Industrial com Som
2. **O Problema de Negócio** — paradas não programadas vs. manutenção preventiva; decisão "parar ou não?"
3. **Os Dados** — MIMII Pump (4.205 clipes, 8:1 desbalanceado, 4 modelos, 0 dB SNR)
4. **Arquitetura da Solução** — MinIO/S3 → PostgreSQL/Snowflake → Airflow → dbt → Metabase; dev→prod com 4 variáveis
5. **Pipeline ELT (9 etapas)** — do download ao treino, orquestrado pelo Airflow
6. **Modelagem dbt** — staging → dim/fact → mart + 16 testes (evidência de qualidade) — atende requisito "tabelas/modelos no Snowflake/dbt"
7. **Do Som às Features** — librosa: 92 features + 6 metadados = 96 números/clip
8. **Modelo de ML — MLP** — 96-64-32-1, hard-code (NumPy) × sklearn
9. **Resultados** — 97,98% acurácia, recall de anomalia 83,5%, matriz de confusão
10. **Dashboard Metabase** — 3 painéis + filtro `{{model_id}}`
11. **Cloud — AWS & Snowflake** — CloudFormation, custo acadêmico ~US$40/mês
12. **Conclusão & Próximos Passos**

## Requisitos do PDF de especificação atendidos

Visão geral, dados/atributos, evidências do pipeline, tabelas no dbt/Snowflake, resultados do ML, dashboard e decisões apoiadas — tudo coberto. **Notas de apresentação (speaker notes)** adicionadas em cada slide para apoio à fala dos 4 integrantes em 15 min.

## Detalhes técnicos

- Gerado com **pptxgenjs** (JS) em `LAYOUT_16x9` (10" × 5,625").
- Fontes: Calibri (títulos 31pt, corpo ≥ 11,5pt) — legibilidade em projeção.
- **Bugs encontrados e corrigidos:** linhas `LINE` com altura negativa no diagrama da rede corrompem o arquivo (PowerPoint recusa) — substituídas por conectores horizontais seguros; caixas de texto com x negativo; estouro de tabela/card no slide de dados.
- Validação final: `scripts/office/validate.py` (skill global do opencode) → **All validations PASSED**.
- Sem barras/listras decorativas de acento (regra da skill); paleta industrial navy/teal/amber.

## Impacto

- **Arquivo substituído:** `report/apresentacao.pptx` (12 slides, ~500 KB).
- Nenhum outro arquivo do projeto alterado.

## Relacionado

- [[2026-08-04 - Guia Visual HTML da Solucao]]
- [[06-Machine-Learning]]
- [[04-Pipeline-ELT]]
- [[10-Infra-AWS]]
