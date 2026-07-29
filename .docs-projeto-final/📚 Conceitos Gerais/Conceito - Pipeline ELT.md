---
title: "Pipeline ELT"
date: 2025-07-03
tags:
  - conceito
  - pipeline
  - elt
  - dados
---

# Pipeline ELT

## Definição

ELT significa *Extract, Load, Transform* (Extrair, Carregar, Transformar). É o fluxo de trabalho que move dados da fonte bruta até um formato utilizável para análise e machine learning.

Diferente do ETL tradicional (onde os dados são transformados ANTES de entrar no banco), no ELT você primeiro carrega os dados brutos no banco e só depois os transforma usando ferramentas como dbt. A vantagem é flexibilidade: você pode transformar os mesmos dados de várias formas diferentes depois.

## Como foi implementado no projeto

Nosso pipeline ELT tem 3 grandes fases:

**Extract (extrair):**
- Baixamos 2 datasets do Kaggle via Python
- Extraímos as URLs das imagens de produtos e baixamos 500 delas
- Tudo vai para `data/raw/`

**Load (carregar):**
- CSVs são enviados para o MinIO (simula o S3 da AWS)
- Os dados processados são carregados no PostgreSQL via SQLAlchemy
- A troca para S3/Snowflake reais é só mudar 4 linhas no `.env`

**Transform (transformar):**
- Scripts Python limpam os dados, extraem features de texto (NLP) e imagem (CV)
- dbt organiza em schema estrela (dimensões e fatos)
- A tabela final `ml_features` está pronta para consumo pelo modelo de ML e pelo Metabase

Tudo é orquestrado pelo Airflow — uma DAG que roda as 8 etapas na ordem certa.

## Relacionado

- [[04-Pipeline-ELT]]
- [[Conceito - DAG no Airflow]]
- [[Conceito - dbt e Modelagem]]
