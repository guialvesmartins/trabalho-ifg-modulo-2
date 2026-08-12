---
title: "DAG no Airflow"
date: 2025-07-03
tags:
  - conceito
  - airflow
  - dag
  - orquestracao
---

# DAG no Airflow

## Definição

DAG significa *Directed Acyclic Graph* (Grafo Direcionado Acíclico). No Apache Airflow, é um arquivo Python que define **o que executar, em qual ordem e com quais dependências**. Cada passo é uma *task*, e as setas entre elas definem a sequência.

É como uma receita de bolo automatizada: primeiro bate os ovos, depois mistura a farinha, depois leva ao forno — tudo na ordem certa, e algumas etapas podem acontecer ao mesmo tempo (como untar a forma enquanto a massa descansa).

## Como foi implementado no projeto

**Arquivo:** `dags/etl_pipeline.py`

Nossa DAG tem 8 tarefas encadeadas:

```
[1] Baixar MIMII           → sempre primeiro
[2] Upload pro MinIO/S3    → depende do [1]
[3] Extrair metadados      → depende do [2]
[4] Extrair features áudio → depende do [3]
[5] Juntar features        → depende do [4]
[6] Carregar no Postgres   → depende do [5]
[7] Rodar dbt              → depende do [6]
[8] Treinar ML             → depende do [7]
```

As tarefas são **sequenciais** — cada etapa depende dos dados produzidos pela anterior (a extração de features precisa dos metadados, o merge precisa das duas, e assim por diante).

Cada tarefa usa `PythonOperator` (chama script Python) ou `BashOperator` (roda comando no terminal, como `dbt run`).

## Relacionado

- [[04-Pipeline-ELT]]
- [[Conceito - Pipeline ELT]]
- [[Conceito - dbt e Modelagem]]
