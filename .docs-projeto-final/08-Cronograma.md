---
title: Cronograma
date: 2025-07-03
tags:
  - cronograma
  - planejamento
  - semanas
aliases:
  - Semanas
  - Planejamento
  - Cronograma de Entregas
---

# Cronograma — 8 Semanas

[[Home|Voltar ao índice]]

---

> [!important] Legenda
> `[ ]` Pendente &nbsp; `[/]` Em andamento &nbsp; `[x]` Concluído

---

## Semana 1 — Estrutura Inicial

**Objetivo:** Ambiente Docker funcional

- [x] `docker-compose.yml` criado e funcional
- [x] PostgreSQL rodando na porta 5432
- [x] MinIO rodando nas portas 9000/9001
- [x] Airflow rodando na porta 8080
- [x] Metabase rodando na porta 3000
- [x] `Dockerfile` customizado com Python 3.11 + requirements.txt (librosa, soundfile, sqlalchemy, psycopg2-binary)
- [x] `.env.local` configurado
- [x] `Makefile` com comandos básicos (`up`, `down`, `logs`)

> [!tip] Verificação
> `make up` deve subir todos os serviços sem erros.

---

## Semana 2 — Dataset + Ingestão

**Objetivo:** Dados disponíveis no S3/MinIO

- [x] `download_dataset.py` funcional (Zenodo → `data/raw/pump/`)
- [x] `load_raw_to_s3.py` funcional (.wav → MinIO/S3 `raw/pump/`)
- [x] Download com retomada (HTTP Range)
- [x] Remoção de dados sintéticos legados (`model_id_XX/`)
- [x] `make ingest` funcional

> [!tip] Verificação
> `aws s3 ls s3://raw/pump/ --endpoint-url http://localhost:9000` deve listar os arquivos.

---

## Semana 3 — Processamento

**Objetivo:** Features extraídas e merge finalizado

- [x] `process_structured.py` — metadados dos paths + `condition_binary`
- [x] `extract_audio_features.py` — librosa (MFCC, spectral, ZCR, RMS — 92 features)
- [x] `merge_features.py` — JOIN por `file_id`
- [x] `load_to_postgres.py` — CSV → `public.ml_features_raw`
- [x] Testes unitários passando (`make test`)

> [!tip] Verificação
> `data/processed/ml_features.csv` deve existir com 103 colunas.

---

## Semana 4 — dbt

**Objetivo:** Projeto dbt completo com testes

- [x] 2 modelos staging (`stg_pump_metadata`, `stg_audio_features`)
- [x] 1 dimensão (`dim_machines`)
- [x] 1 fato (`fact_audio_analysis`)
- [x] 1 mart (`ml_features`)
- [x] 16 testes dbt passando (`dbt test`)
- [x] `schema.yml` documentado
- [x] `make dbt-run` e `make dbt-test` funcionais

> [!tip] Verificação
> `dbt test` deve retornar 0 falhas.

---

## Semana 5 — Airflow

**Objetivo:** DAG orquestrando pipeline completo

- [x] `dags/etl_pipeline.py` com 8 tarefas encadeadas
- [x] `PythonOperator` para scripts Python
- [x] `BashOperator` para dbt
- [x] DAG visível e executável no Airflow (localhost:8080)

> [!tip] Verificação
> Disparar DAG manualmente → todas as tarefas verdes.

---

## Semana 6 — Machine Learning

**Objetivo:** MLP implementado e avaliado

- [x] `neural_network_hardcode.py` — MLP do zero (NumPy, backprop, SGD + momento)
- [x] `neural_network_sklearn.py` — MLPClassifier do sklearn
- [x] `evaluate.py` — comparação com métricas
- [x] Baseline majoritária (DummyClassifier) calculada
- [x] Regressão Logística calculada
- [x] Matriz de confusão para os modelos
- [x] Comparação lado a lado documentada (`report_analys.md`)

> [!tip] Verificação
> `make ml-train` deve imprimir tabela comparativa.

---

## Semana 7 — Dashboard

**Objetivo:** Metabase com 3 dashboards configurados

- [x] Dashboard 1: Visão Geral (KPIs, distribuição, anomalias por modelo)
- [x] Dashboard 2: Análise de Áudio por Modelo
- [x] Dashboard 3: Resultados do Modelo ML (métricas, matriz de confusão)
- [x] Filtro por modelo de máquina (template-tag `{{model_id}}`)
- [x] `scripts/setup_metabase.py` re-executável

> [!tip] Verificação
> Os 3 dashboards devem estar acessíveis em http://localhost:3000.

---

## Semana 8 — Infra + Entrega Final

**Objetivo:** Documentação final e apresentação

- [x] `cloudformation.yaml` completo e validado
- [x] `docs/ARQUITETURA_AWS.md` (diagramas dev e 100% AWS + registro de custos)
- [x] `report_analys.md` finalizado
- [x] `apresentacao.pptx` pronta (todos integrantes)
- [x] `README.md` completo com instruções de uso
- [x] `make test` passando em todos os módulos
- [x] Repositório Git organizado e limpo

> [!tip] Verificação
> Checklist completo do [[09-Checklist-Entrega]] com todos os itens marcados.

---

## Marcos (Milestones)

| Semana | Marco |
|--------|-------|
| 1 | `make up` funcional |
| 2 | `make ingest` funcional |
| 3 | `make process` + `make load-db` funcional |
| 4 | `make dbt-test` passando |
| 5 | DAG completa no Airflow |
| 6 | `make ml-train` comparativo |
| 7 | Dashboard completo |
| 8 | **ENTREGA FINAL** |
