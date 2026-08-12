---
title: Passo a Passo — Implementação
date: 2025-07-03
tags:
  - implementacao
  - passo-a-passo
  - guia
aliases:
  - Como Implementar
  - Guia de Implementação
---

# Passo a Passo — Implementação do Projeto

[[Home|Voltar ao índice]]

Este guia mapeia cada requisito do PDF para ações concretas de implementação, organizadas pelas 8 semanas do [[08-Cronograma]].

---

> [!important] Pré-requisitos
> - [x] Python 3.11+ instalado
> - [x] Docker Desktop rodando
> - [x] Git configurado
> - [x] ~8 GB de espaço livre em disco (dataset MIMII ~7,87 GB)

---

## Semana 1 — Estrutura Docker

**PDF: 4.4 (Pipeline), 4.5 (Nuvem)**

### 1.1 Criar `docker-compose.yml`

Serviços necessários:

| Serviço | Imagem | Porta | Propósito |
|---------|--------|-------|-----------|
| `postgres` | `postgres:16-alpine` | 5432 | Banco (mock do Snowflake) |
| `minio` | `minio/minio:latest` | 9000/9001 | Storage S3 (mock do AWS S3) |
| `airflow-init` | `apache/airflow:2.9.0` | — | Init: migration + admin user |
| `airflow-webserver` | `apache/airflow:2.9.0` | 8080 | UI do Airflow |
| `airflow-scheduler` | `apache/airflow:2.9.0` | — | Scheduler do Airflow |
| `metabase` | `metabase/metabase:latest` | 3000 | Dashboard BI |
| `metabase-setup` | `python:3.11-slim` | — | Config automática via API |

### 1.2 Criar `Dockerfile`

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y libsndfile1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

> [!info] `libsndfile1` é necessário para o `soundfile` ler os `.wav` do MIMII.

### 1.3 Criar `requirements.txt`

Inclui `librosa`, `soundfile`, `sqlalchemy`, `psycopg2-binary`, `pandas`, `numpy`, `scikit-learn`, `boto3`, `python-dotenv`, `requests`, `apache-airflow`, `dbt-core`, `dbt-postgres`.

### 1.4 Criar `.env.example`

```bash
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
DB_TYPE=postgres
DB_HOST=localhost
```

### 1.5 Criar `Makefile`

Ver [[11-Comandos#Makefile]] para os comandos completos.

### 1.6 Verificar

```bash
make up
# Esperar ~30s e acessar:
# Airflow:  http://localhost:8080 (admin/admin)
# Metabase: http://localhost:3000 (admin@projeto.com / ProjetoIFG2025!)
# MinIO:    http://localhost:9001 (minioadmin/minioadmin)
```

> [!tip] Se algum serviço falhar
> Ver logs com `docker compose logs <servico>`.

---

## Semana 2 — Dataset + Ingestão

**PDF: 4.2 (Conjuntos de dados)**

### 2.1 Criar `ingestion/download_dataset.py`

Baixa `0_dB_pump.zip` do Zenodo (`https://zenodo.org/records/3384388/files/0_dB_pump.zip`) via `requests`:
- Barra de progresso durante o download
- Retomada de download interrompido (HTTP Range)
- Remoção de dados sintéticos legados (`model_id_XX/`)
- Extração para `data/raw/pump/`

### 2.2 Criar `ingestion/load_raw_to_s3.py`

Usa `boto3` com `endpoint_url` configurável para subir todos os `.wav` para o bucket `raw/pump/` (MinIO em dev, AWS S3 em prod).

### 2.3 Verificar

```bash
make ingest
# Verificar no MinIO: http://localhost:9001 → bucket "raw" → pasta "pump"
```

---

## Semana 3 — Processamento e Features

**PDF: 4.3 (Processamento e extração de atributos)**

### 3.1 Criar `processing/process_structured.py`

Percorre `data/raw/pump/`, extrai dos paths (`machine_type`, `model_id`, `condition`) e lê metadata dos `.wav` com `soundfile`:
- Normaliza `abnormal` → `anomaly` (constante `CONDITION_MAP`)
- Gera `file_id` e o target `condition_binary` (anomaly=1)
- Saída: `data/processed/pump_metadata.csv`

### 3.2 Criar `processing/extract_audio_features.py`

Para cada `.wav`, carrega com `librosa.load(sr=16000, mono=True)` e extrai **92 features**:
- MFCC: `mfcc_1_mean`..`mfcc_40_mean` + `mfcc_1_std`..`mfcc_40_std` (80)
- Espectrais: `spectral_centroid_mean`, `spectral_bandwidth_mean`, `spectral_rolloff_mean`, `spectral_contrast_1_mean`..`_7_mean` (10)
- Energia/ritmo: `zcr_mean`, `rms_mean` (2)
- Saída: `data/processed/audio_features.csv`

> [!info] Lista completa
> Ver [[06-Machine-Learning#Features]].

### 3.3 Criar `processing/merge_features.py`

LEFT JOIN entre `pump_metadata.csv` e `audio_features.csv` por `file_id`, preenchendo nulos com 0. Saída: `data/processed/ml_features.csv` (103 colunas).

### 3.4 Criar `processing/load_to_postgres.py`

Lê `ml_features.csv` com pandas e insere no PostgreSQL como `public.ml_features_raw` via SQLAlchemy (`if_exists='replace'`).

### 3.5 Verificar

```bash
make process
make load-db
```

---

## Semana 4 — Projeto dbt

**PDF: 4.4 (Pipeline ELT — dbt)**

### 4.1 Criar os 5 modelos

| Camada | Modelo | Tipo | Descrição |
|--------|--------|------|-----------|
| Staging | `stg_pump_metadata` | View | Limpeza, dedup, tipagem |
| Staging | `stg_audio_features` | View | Cast para numeric |
| Dimensions | `dim_machines` | Table | Agregação por modelo |
| Facts | `fact_audio_analysis` | Table | Join completo |
| Marts | `ml_features` | Table | Pronto para ML |

### 4.2 Criar `profiles.yml`

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: airflow
      password: airflow
      port: 5432
      dbname: airflow
      schema: public
    prod:
      type: snowflake
      # configurado via env_var()
```

### 4.3 Criar `schema.yml` com testes

Ver [[05-Modelagem-dbt#Testes dbt  schema-yml]] — 16 testes (not_null, unique, accepted_values).

### 4.4 Verificar

```bash
make dbt-run
make dbt-test
# Todos os testes devem passar (0 falhas)
```

---

## Semana 5 — Airflow DAG

**PDF: 4.4 (Pipeline ELT — Airflow)**

### 5.1 Criar `dags/etl_pipeline.py`

DAG com **8 tasks sequenciais** (cada etapa depende da anterior):

```python
download_dataset >> load_raw_to_s3 >> process_structured >> extract_audio_features
extract_audio_features >> merge_features >> load_to_postgres >> dbt_run >> dbt_test >> ml_train_evaluate
```

- `PythonOperator` para cada script Python
- `BashOperator` para `dbt run` e `dbt test`
- Schedule: manual ou agendado

### 5.2 Verificar

Acessar http://localhost:8080, ativar a DAG e disparar manualmente. Todas as tarefas devem ficar verdes.

---

## Semana 6 — Machine Learning

**PDF: 4.6 (Aprendizagem de Máquina)**

### 6.1 Hard-Code MLP

**Arquivo:** `ml/hard_code/neural_network_hardcode.py` — classe `HardCodedMLP`
- Arquitetura: 96 → 64 (ReLU) → 32 (ReLU) → 1 (Sigmoid)
- He initialization, backprop manual, Binary Cross-Entropy
- Mini-batch SGD com momento (lr=0.01, momentum=0.9), 300 épocas, batch 32

### 6.2 Sklearn

**Arquivo:** `ml/library/neural_network_sklearn.py` — `MLPClassifier(hidden_layer_sizes=(64, 32), alpha=0.0001, max_iter=500)`

### 6.3 Avaliação

**Arquivo:** `ml/evaluate.py`
- Split 80/20 com stratify + StandardScaler
- Baselines: DummyClassifier + Regressão Logística
- Gera `report_analys.md`, matrizes de confusão, `predictions.csv` e modelos `.pkl`
- Carrega `model_metrics` e `model_predictions` para o Metabase (best-effort)

Resultados detalhados em [[06-Machine-Learning#Avaliação e Comparação]].

---

## Semana 7 — Dashboard Metabase

**PDF: 4.7 (Visualização da Informação)**

### 7.1 Configuração automática

Ao rodar `make up`, o `metabase-setup` configura a conexão com o Postgres e cria os **3 dashboards**:
1. Visão Geral (KPIs, distribuição, anomalias por modelo)
2. Análise de Áudio por Modelo (dim_machines, MFCC, spectral centroid, top RMS)
3. Resultados do Modelo ML (métricas, matriz de confusão, predições com erro)

Filtro por modelo de máquina via template-tag `{{model_id}}`.

### 7.2 Reexecutar manualmente

```bash
make setup-metabase   # script re-executável (arquiva cards/dashboards antigos)
make logs-setup       # acompanhar progresso
```

---

## Semana 8 — Infra AWS + Entrega Final

**PDF: 4.5 (Nuvem), 7 (Entregáveis)**

### 8.1 CloudFormation

Criar `infra/cloudformation.yaml` seguindo [[10-Infra-AWS]].

### 8.2 Diagrama arquitetural

Documentar em `docs/ARQUITETURA_AWS.md` (dev e 100% AWS + custos).

### 8.3 Relatório

`report_analys.md` — métricas, análise qualitativa de acertos/erros, features mais discriminativas e limitações.

### 8.4 Apresentação

`report/apresentacao.pptx` para defesa oral (12 slides, 4 locutores).

### 8.5 README final

Atualizar `README.md` com descrição, como rodar, tecnologias, estrutura e resultados.

---

## Mapeamento PDF → Entregas

| Seção PDF | Requisito | Onde entregar |
|-----------|-----------|---------------|
| 4.1 | Definição do problema | [[01-Plano-Geral]], `README.md`, relatório |
| 4.2 | Conjuntos de dados | [[02-Datasets]], `data/raw/pump/`, relatório |
| 4.3 | Processamento e features | `processing/*.py`, relatório |
| 4.4 | Pipeline ELT | `dags/etl_pipeline.py`, `dbt_project/`, relatório |
| 4.5 | Nuvem AWS | `infra/cloudformation.yaml`, `docs/ARQUITETURA_AWS.md`, relatório |
| 4.6 | ML | `ml/`, relatório |
| 4.7 | Dashboard | `scripts/setup_metabase.py`, Metabase, relatório |
| 5 | Avaliação | `ml/evaluate.py`, relatório |
| 7.1 | Repositório | Git + README |
| 7.2 | Apresentação | `report/apresentacao.pptx` |
| 7.3 | Relatório | `report_analys.md` |

---

## Fluxo completo para rodar do zero

```bash
make up             # 1. Sobe containers
make ingest         # 2. Baixa dados MIMII
make process        # 3. Extrai features
make load-db        # 4. Carrega no banco
make dbt-run        # 5. Transforma dados
make dbt-test       # 6. Valida qualidade
make ml-train       # 7. Treina modelo
```

---

> [!success] Sequência recomendada
> Cada semana constrói sobre a anterior. O [[09-Checklist-Entrega]] tem os 32 itens rastreáveis.

## Relacionado

- [[08-Cronograma]] — Cronograma detalhado com checklists
- [[09-Checklist-Entrega]] — 32 requisitos rastreáveis
- [[11-Comandos]] — Referência rápida de comandos
- [[01-Plano-Geral]] — Visão geral do problema
