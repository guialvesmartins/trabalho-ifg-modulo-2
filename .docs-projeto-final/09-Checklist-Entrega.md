---
title: Checklist de Entrega
date: 2025-07-03
tags:
  - checklist
  - entrega
  - requisitos
  - pdf
aliases:
  - Checklist
  - Requisitos
---

# Checklist de Entrega — Requisitos do PDF

[[Home|Voltar ao índice]]

---

> [!important] Mapeamento PDF
> Cada item abaixo corresponde a um requisito do documento de especificação do projeto.

---

## 4.2 — Conjuntos de Dados

- [x] Pelo menos 1 fonte de dados estruturados → metadados dos paths MIMII (`pump_metadata.csv`)
- [x] Pelo menos 1 fonte de dados não estruturados → clipes `.wav` de bombas industriais
- [x] Dados suficientes para treino e teste → 4.205 clipes MIMII (3.749 normal + 456 anomalia)
- [x] Documentação da origem e campos → [[02-Datasets]] + `README.md`

---

## 4.3 — Processamento e Extração de Atributos

- [x] Limpeza de dados estruturados → `process_structured.py` (parse de paths, dedup, tipagem)
- [x] Extração de features de áudio → `extract_audio_features.py` (librosa: MFCC, spectral, ZCR, RMS)
- [x] Merge final → `merge_features.py` (LEFT JOIN por `file_id`)
- [x] Carga no banco → `load_to_postgres.py` (tabela `ml_features_raw`)

---

## 4.4 — Pipeline ELT (Airflow + dbt + Snowflake)

- [x] DAG funcional no Airflow → `dags/etl_pipeline.py` (8 tasks sequenciais)
- [x] Carga no banco (Postgres/Snowflake) → dbt + profiles
- [x] Modelos staging, dimensions, facts, marts → 5 modelos em 4 camadas
- [x] Pelo menos 2 testes dbt → 16 testes (not_null, unique, accepted_values)
- [x] Documentação dos modelos → `schema.yml`
- [x] Tabela final para ML → `ml_features`
- [x] Fatos para dashboard → `fact_audio_analysis` + `dim_machines`

---

## 4.5 — Armazenamento e Processamento em Nuvem

- [x] Pelo menos 1 serviço AWS → S3 (usado em prod)
- [x] Organização em camadas → `raw/pump/` no bucket
- [x] CloudFormation YAML → `infra/cloudformation.yaml`
- [x] Diagrama arquitetural → `docs/ARQUITETURA_AWS.md`

---

## 4.6 — Aprendizagem de Máquina

- [x] Tarefa definida → Classificação binária (normal vs anomalia)
- [x] Baseline → DummyClassifier (majoritária) + Regressão Logística
- [x] Hard-code → `neural_network_hardcode.py` (MLP do zero com NumPy)
- [x] Biblioteca Python → `neural_network_sklearn.py` (MLPClassifier)
- [x] Comparação → `evaluate.py` com métricas lado a lado
- [x] Métricas → Accuracy, Precision, Recall, F1, Matriz de Confusão

---

## 4.7 — Visualização (Metabase)

- [x] Indicadores principais → KPIs (total, taxa de anomalia, duração média)
- [x] Visualização dos dados tratados → Distribuições, análise por modelo
- [x] Visualização dos resultados do modelo → Matriz de confusão, métricas
- [x] Pelo menos 1 filtro → Modelo de máquina (`{{model_id}}`)

---

## 7 — Entregáveis Finais

- [x] Repositório Git → README, scripts, dbt, DAGs, ML, CloudFormation
- [x] Apresentação → Todos os 4 integrantes
- [x] Relatório → Documentação completa (`report_analys.md` + `README.md`)

---

## Contagem

| Seção | Itens | Concluídos | Pendentes |
|-------|-------|------------|-----------|
| 4.2 — Datasets | 4 | 4 | 0 |
| 4.3 — Processamento | 4 | 4 | 0 |
| 4.4 — Pipeline ELT | 7 | 7 | 0 |
| 4.5 — Nuvem | 4 | 4 | 0 |
| 4.6 — ML | 6 | 6 | 0 |
| 4.7 — Visualização | 4 | 4 | 0 |
| 7 — Entregáveis | 3 | 3 | 0 |
| **TOTAL** | **32** | **32** | **0** |

> [!success] Progresso
> `32/32` itens concluídos — projeto finalizado e pronto para apresentação.
