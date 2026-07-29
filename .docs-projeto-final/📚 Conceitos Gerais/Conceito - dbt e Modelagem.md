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
- **Tabelas Fato** (*facts*): registram eventos/acontencimentos (ex: uma review, uma venda)
- **Tabelas Dimensão** (*dims*): descrevem entidades (ex: produto, categoria)

O nome "estrela" vem do diagrama: uma fato no centro, várias dimensões ao redor.

## Como foi implementado no projeto

**8 modelos dbt** em 4 camadas:

| Camada | Modelos | O que faz |
|--------|---------|-----------|
| Staging | `stg_products`, `stg_reviews`, `stg_images` | Renomeia colunas, ajusta tipos, limpa dados brutos |
| Dimensions | `dim_products`, `dim_categories` | Tabelas de consulta (quais produtos existem? quais categorias?) |
| Facts | `fact_reviews`, `fact_sales` | Registros de reviews e métricas de venda |
| Marts | `ml_features` | JOIN final: uma tabela única com todas as features prontas pro modelo ML |

**4 testes automáticos:**
- `product_id` não pode ser nulo nem duplicado
- `review_id` não pode ser nulo
- `rating` só pode ser 1, 2, 3, 4 ou 5
- `category_name` não pode ser duplicado

Os profiles (`profiles.yml`) têm targets `dev` (Postgres) e `prod` (Snowflake), controlados por variáveis de ambiente — troca o `.env` e o dbt fala com outro banco automaticamente.

## Relacionado

- [[05-Modelagem-dbt]]
- [[Conceito - Pipeline ELT]]
- [[04-Pipeline-ELT]]
