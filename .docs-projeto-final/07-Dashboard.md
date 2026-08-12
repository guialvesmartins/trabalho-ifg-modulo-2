---
title: Dashboard
date: 2025-07-03
tags:
  - dashboard
  - metabase
  - visualizacao
aliases:
  - Metabase
  - Visualização
---

# Dashboard — Metabase

[[Home|Voltar ao índice]]

---

## Dashboard 1 — Visão Geral

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **KPI — Total de Amostras** | Number | `SELECT COUNT(*) FROM fact_audio_analysis` |
| **KPI — Taxa de Anomalia (%)** | Number | `ROUND(100.0 * SUM(condition_binary) / COUNT(*), 1)` |
| **KPI — Duração Média (s)** | Number | `ROUND(AVG(duration_sec)::numeric, 2)` |
| **Distribuição de Condições** | Pie chart | normal vs anomalia |
| **Anomalias por Modelo** | Bar chart | Contagem de anomalias por `model_id` |

---

## Dashboard 2 — Análise de Áudio por Modelo

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **Resumo por Modelo** | Table | Dados de `dim_machines` (total, anomalias, normais) |
| **MFCC-1 Médio por Modelo** | Bar chart | Média de `mfcc_1_mean` por `model_id` |
| **Spectral Centroid vs Condição** | Comparison | `spectral_centroid_mean` normal vs anomalia |
| **Top 10 Maior RMS** | Table | Amostras com maior energia (possível anomalia severa) |

---

## Dashboard 3 — Resultados do Modelo ML

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **KPI — Acurácia do Modelo (%)** | Number | Acurácia do MLP sklearn no teste (tabela `model_predictions`) |
| **Métricas dos Modelos** | Table | Comparativo baselines vs MLPs (tabela `model_metrics`) |
| **Matriz de Confusão (Sklearn)** | Heatmap | Contagens real × predito |
| **Predições com Erro** | Table | Amostras mal classificadas — insumo da análise qualitativa |

---

## Filtros

Os dashboards 1 e 2 têm **filtro por modelo de máquina** (parâmetro mapeado via template-tag `{{model_id}}` nos cards SQL — cláusula opcional `[[AND model_id = {{model_id}}]]`).

> [!info] Schemas
> Os cards SQL referenciam os schemas do dbt: `public_analytics.fact_audio_analysis` e `public_analytics.dim_machines`. As tabelas `model_metrics` e `model_predictions` ficam em `public`.

---

## Configuração Automática

Ao rodar `make up`, o container `metabase-setup` configura automaticamente:
- Conexão com o banco PostgreSQL
- 3 dashboards com perguntas SQL pré-configuradas (`scripts/setup_metabase.py`)

**Acesso:**
- URL: [http://localhost:3000](http://localhost:3000)
- Email: `admin@projeto.com`
- Senha: `ProjetoIFG2025!`

> [!tip] Setup manual / reexecução
> O `setup_metabase.py` é re-executável (arquiva cards/dashboards antigos de mesmo nome antes de recriar). Para rodar manualmente: `make setup-metabase`. Para ver o progresso: `make logs-setup`.

---

## Configuração Manual (alternativa)

```bash
# Metabase disponível em
http://localhost:3000

# Conexão com o banco (PostgreSQL ou Snowflake)
Host: postgres (ou conta Snowflake)
Port: 5432
Database: airflow
User: airflow
Password: airflow
```
