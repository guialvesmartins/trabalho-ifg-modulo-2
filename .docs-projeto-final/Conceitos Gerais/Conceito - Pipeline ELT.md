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

Diferente do ETL tradicional (onde os dados são transformados ANTES de entrar no banco), no ELT você primeiro carrega os dados brutos e só depois transforma usando ferramentas como dbt. A vantagem é flexibilidade: você pode transformar os mesmos dados de várias formas diferentes depois.

## Como foi implementado no projeto

Nosso pipeline ELT tem 3 grandes fases:

**Extract (extrair):**
- Baixamos o dataset **MIMII Pump** (~7,87 GB) do Zenodo via Python
- São clipes `.wav` de 10 s, 16 kHz, de bombas industriais (normal + anomalia)
- Tudo vai para `data/raw/pump/`

**Load (carregar):**
- Os `.wav` são enviados para o MinIO (simula o S3 da AWS)
- As features processadas são carregadas no PostgreSQL via SQLAlchemy (`ml_features_raw`)
- A troca para S3/Snowflake reais é só mudar 4 variáveis no `.env`

**Transform (transformar):**
- Scripts Python extraem metadados dos paths e features de áudio (librosa: MFCC, spectral, ZCR, RMS)
- dbt organiza em schema estrela (dimensões e fatos)
- A tabela final `ml_features` está pronta para consumo pelo modelo de ML e pelo Metabase

Tudo é orquestrado pelo Airflow — uma DAG que roda as 8 etapas na ordem certa.

## Relacionado

- [[04-Pipeline-ELT]]
- [[Conceito - DAG no Airflow]]
- [[Conceito - dbt e Modelagem]]
