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

- [ ] `docker-compose.yml` criado e funcional
- [ ] PostgreSQL rodando na porta 5432
- [ ] MinIO rodando nas portas 9000/9001
- [ ] Airflow rodando na porta 8080
- [ ] Metabase rodando na porta 3000
- [ ] `Dockerfile` customizado com Python 3.11 + requirements.txt
- [ ] `.env.local` configurado
- [ ] `Makefile` com comandos básicos (`up`, `down`, `logs`)

> [!tip] Verificação
> `make up` deve subir todos os serviços sem erros.

---

## Semana 2 — Datasets + Ingestão

**Objetivo:** Dados disponíveis no S3/MinIO

- [ ] `download_dataset.py` funcional (Kaggle → `data/raw/`)
- [ ] `load_raw_to_s3.py` funcional (CSVs + imagens → MinIO)
- [ ] ~500-1000 imagens baixadas das URLs
- [ ] Estrutura `raw/` no bucket organizada
- [ ] `make ingest` funcional

> [!tip] Verificação
> `aws s3 ls s3://raw/ --endpoint-url http://localhost:9000` deve listar os arquivos.

---

## Semana 3 — Processamento

**Objetivo:** Features extraídas e merge finalizado

- [ ] `process_structured.py` — limpeza (nulos, dedup, padronização)
- [ ] `extract_text_features.py` — NLP (~217 features)
- [ ] `extract_image_features.py` — CV (~28 features)
- [ ] `merge_features.py` — JOIN final
- [ ] Testes unitários passando (`make test`)

> [!tip] Verificação
> `processed/ml_features.csv` deve existir no bucket com ~255 colunas.

---

## Semana 4 — dbt

**Objetivo:** Projeto dbt completo com testes

- [ ] 3 modelos staging (`stg_products`, `stg_reviews`, `stg_images`)
- [ ] 2 dimensões (`dim_products`, `dim_categories`)
- [ ] 2 fatos (`fact_reviews`, `fact_sales`)
- [ ] 1 mart (`ml_features`)
- [ ] 4 testes dbt passando (`dbt test`)
- [ ] `schema.yml` documentado
- [ ] `make dbt-run` e `make dbt-test` funcionais

> [!tip] Verificação
> `dbt test` deve retornar 0 falhas.

---

## Semana 5 — Airflow

**Objetivo:** DAG orquestrando pipeline completo

- [ ] `dags/etl_pipeline.py` com 8 tarefas encadeadas
- [ ] Tarefas NLP e CV rodando em paralelo
- [ ] `PythonOperator` para scripts Python
- [ ] `BashOperator` para dbt
- [ ] DAG visível e executável no Airflow (localhost:8080)

> [!tip] Verificação
> Disparar DAG manualmente → todas as tarefas verdes.

---

## Semana 6 — Machine Learning

**Objetivo:** Naive Bayes implementado e avaliado

- [ ] `naive_bayes_hardcode.py` — algoritmo do zero
- [ ] `naive_bayes_sklearn.py` — MultinomialNB do sklearn
- [ ] `evaluate.py` — comparação com métricas
- [ ] Baseline (classe majoritária) calculada
- [ ] Baseline melhorada (só estruturadas) calculada
- [ ] Matriz de confusão para ambos os modelos
- [ ] Comparação lado a lado documentada

> [!tip] Verificação
> `make ml-train` deve imprimir tabela comparativa.

---

## Semana 7 — Dashboard

**Objetivo:** Metabase com 4 páginas configuradas

- [ ] Página 1: KPIs e visão geral
- [ ] Página 2: Análise de sentimento (NLP)
- [ ] Página 3: Análise visual (imagens)
- [ ] Página 4: Resultados do modelo ML
- [ ] Filtros globais configurados
- [ ] Queries documentadas em `dashboard/metabase_questions.md`

> [!tip] Verificação
> As 4 páginas devem estar acessíveis em http://localhost:3000.

---

## Semana 8 — Infra + Entrega Final

**Objetivo:** Documentação final e apresentação

- [ ] `cloudformation.yaml` completo e validado
- [ ] `architecture_diagram.png` gerado
- [ ] `relatorio.md` finalizado
- [ ] `apresentacao.pptx` pronta (todos integrantes)
- [ ] `README.md` completo com instruções de uso
- [ ] `make test` passando em todos os módulos
- [ ] Repositório Git organizado e limpo

> [!tip] Verificação
> Checklist completo do [[09-Checklist-Entrega]] com todos os itens marcados.

---

## Marcos (Milestones)

| Semana | Marco |
|--------|-------|
| 1 | `make up` funcional |
| 2 | `make ingest` funcional |
| 3 | `make process` funcional |
| 4 | `make dbt-test` passando |
| 5 | DAG completa no Airflow |
| 6 | `make ml-train` comparativo |
| 7 | Dashboard completo |
| 8 | **ENTREGA FINAL** |
