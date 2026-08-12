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

- [ ] Pelo menos 1 fonte de dados estruturados → `amazon_sales.csv`
- [ ] Pelo menos 1 fonte de dados não estruturados → Texto (reviews) + Imagens
- [ ] Dados suficientes para treino e teste → ~1400 produtos + ~35k reviews + ~500-1000 imagens
- [ ] Documentação da origem e campos → [[02-Datasets]] + `README.md`

---

## 4.3 — Processamento e Extração de Atributos

- [ ] Limpeza de dados estruturados → `process_structured.py`
- [ ] Extração de features de texto (NLP) → `extract_text_features.py`
- [ ] Extração de features de imagem (CV) → `extract_image_features.py`
- [ ] Merge final → `merge_features.py`

---

## 4.4 — Pipeline ELT (Airflow + dbt + Snowflake)

- [ ] DAG funcional no Airflow → `dags/etl_pipeline.py`
- [ ] Carga no banco (Postgres/Snowflake) → dbt + profiles
- [ ] Modelos staging, dimensions, facts, marts → 8 modelos em 4 camadas
- [ ] Pelo menos 2 testes dbt → 4 testes (not_null, unique, accepted_values)
- [ ] Documentação dos modelos → `schema.yml`
- [ ] Tabela final para ML → `ml_features`
- [ ] Fatos para dashboard → `fact_reviews` + `fact_sales`

---

## 4.5 — Armazenamento e Processamento em Nuvem

- [ ] Pelo menos 1 serviço AWS → S3 (usado em prod)
- [ ] Organização em camadas → `raw/`, `processed/`, `images/`
- [ ] CloudFormation YAML → `infra/cloudformation.yaml`
- [ ] Diagrama arquitetural → `infra/architecture_diagram.png`

---

## 4.6 — Aprendizagem de Máquina

- [ ] Tarefa definida → Classificação multiclasse (1-5 estrelas)
- [ ] Baseline → Classe majoritária + modelo só com estruturados
- [ ] Hard-code → `naive_bayes_hardcode.py` (Naive Bayes do zero)
- [ ] Biblioteca Python → `naive_bayes_sklearn.py` (MultinomialNB)
- [ ] Comparação → `evaluate.py` com métricas lado a lado
- [ ] Métricas → Accuracy, Precision, Recall, F1, Matriz de Confusão

---

## 4.7 — Visualização (Metabase)

- [ ] Indicadores principais → KPIs de vendas e satisfação
- [ ] Visualização dos dados tratados → Distribuições, análises
- [ ] Visualização dos resultados do modelo → Matriz de confusão, métricas
- [ ] Pelo menos 1 filtro → Categoria, preço, desconto, rating

---

## 7 — Entregáveis Finais

- [ ] Repositório Git → README, scripts, dbt, DAGs, ML, CloudFormation
- [ ] Apresentação → Todos os 4 integrantes
- [ ] Relatório → Documentação completa (`report/relatorio.md`)

---

## Contagem

| Seção | Itens | Concluídos | Pendentes |
|-------|-------|------------|-----------|
| 4.2 — Datasets | 4 | 0 | 4 |
| 4.3 — Processamento | 4 | 0 | 4 |
| 4.4 — Pipeline ELT | 7 | 0 | 7 |
| 4.5 — Nuvem | 4 | 0 | 4 |
| 4.6 — ML | 6 | 0 | 6 |
| 4.7 — Visualização | 4 | 0 | 4 |
| 7 — Entregáveis | 3 | 0 | 3 |
| **TOTAL** | **32** | **0** | **32** |

> [!todo] Progresso
> `0/32` itens concluídos — iniciar pela [[08-Cronograma#Semana 1|Semana 1]].
