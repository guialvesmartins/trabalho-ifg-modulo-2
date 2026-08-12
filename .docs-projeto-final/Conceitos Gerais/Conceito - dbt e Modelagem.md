---
title: "dbt e Modelagem de Dados"
date: 2025-07-03
tags:
  - conceito
  - dbt
  - modelagem
  - schema-estrela
---

# dbt e Modelagem de Dados

## Definição

dbt (*data build tool*) é uma ferramenta que aplica engenharia de software à análise de dados: você escreve consultas SQL como se fossem código, versiona no Git, testa e documenta.

Em vez de ter um analista rodando queries manuais no banco, o dbt transforma dados brutos em tabelas limpas e organizadas de forma **reprodutível e testável**. É o T do ELT (Transform).

### Schema Estrela

É um jeito de organizar tabelas analíticas com:
- **Tabelas Fato** (*facts*): registram eventos (ex: uma análise de áudio com sua condição)
- **Tabelas Dimensão** (*dims*): descrevem entidades (ex: uma máquina/bomba)

O nome "estrela" vem do diagrama: uma fato no centro, várias dimensões ao redor.

## Como foi implementado no projeto

**5 modelos dbt** em 4 camadas (origem: tabela `public.ml_features_raw`):

| Camada | Modelo | Tipo | O que faz |
|--------|--------|------|-----------|
| Staging | `stg_pump_metadata` | View | Limpeza, dedup (`distinct on file_id`) e tipagem dos metadados |
| Staging | `stg_audio_features` | View | Cast para `numeric` das features de áudio |
| Dimensions | `dim_machines` | Table | Agregação por modelo (total, anomalias, normais) |
| Facts | `fact_audio_analysis` | Table | Join completo (condição + features) |
| Marts | `ml_features` | Table | Tabela final pronta para ML |

**16 testes automáticos** (`schema.yml`): `not_null`, `unique` e `accepted_values` (condition ∈ normal/anomaly, condition_binary ∈ 0/1).

Os profiles (`profiles.yml`) têm targets `dev` (Postgres) e `prod` (Snowflake), controlados por variáveis de ambiente — troca o `.env` e o dbt fala com outro banco automaticamente.

## Relacionado

- [[05-Modelagem-dbt]]
- [[Conceito - Pipeline ELT]]
- [[04-Pipeline-ELT]]
