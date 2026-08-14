# Documentação Mínima — Projeto Final IFG (Pós-IA, Módulo 2)

> Introdução rápida ao projeto para os integrantes do grupo. Para detalhes, veja os links no final.

## 1. O que é o projeto

**Manutenção Preditiva Industrial com Som.** Um pipeline de dados completo que analisa o áudio de bombas industriais e classifica automaticamente se a máquina está operando **normal** ou com **anomalia** (classificação binária). O projeto integra as três disciplinas do módulo: **Aprendizagem de Máquina**, **Cloud Computing** e **Modelagem de Dados para IA**.

## 2. Problema de negócio

- **Cenário:** uma fábrica tem dezenas de bombas operando 24/7. Paradas não programadas custam caro; manutenções desnecessárias também.
- **Decisão apoiada:** "Esta bomba está com anomalia? Devo parar para manutenção?"
- **Tomador de decisão:** engenheiro de manutenção industrial.
- **Impacto esperado:** menos paradas não programadas, menos manutenções desnecessárias, maior vida útil dos equipamentos e economia em reparos emergenciais.

## 3. Dataset — MIMII Pump

- **Fonte:** MIMII Dataset (Hitachi/Toyota Research), baixado do Zenodo (~7,5 GB). Licença CC BY-SA 4.0.
- **Conteúdo:** clipes de áudio `.wav` de 10 s (16 kHz) de 4 modelos de bomba industrial, gravados em fábrica real com ruído de fundo.
- **Condições:** `normal` (~1.000 clipes por modelo) e `anomaly` (~200 por modelo — contaminação, vazamento, desbalanceamento).
- **Dados estruturados:** metadados extraídos dos caminhos dos arquivos (`machine_type`, `model_id`, `condition`, duração, sample rate, canais).
- **Dados não estruturados:** o próprio áudio, do qual extraímos 92 features numéricas (MFCC, espectrais, ZCR, RMS) com a biblioteca **librosa**.

## 4. Tecnologias

| Tecnologia | Papel no projeto |
|---|---|
| **Python** | Linguagem de todo o pipeline |
| **AWS S3 / MinIO** | Storage dos áudios brutos (MinIO = mock local do S3) |
| **Snowflake / PostgreSQL** | Data warehouse (Postgres = mock local do Snowflake) |
| **Apache Airflow** | Orquestração do pipeline (DAG com 8 tasks) |
| **dbt** | Transformação e testes de qualidade dos dados |
| **Docker Compose** | Sobe todo o ambiente local com um comando |
| **librosa** | Extração de features do áudio |
| **NumPy / scikit-learn** | Modelos de ML (hard-code e biblioteca) |
| **Metabase** | Dashboards de BI |

Dev e prod são separados por apenas 4 variáveis de ambiente (MinIO+Postgres local ↔ S3+Snowflake na nuvem), sem mudar código.

## 5. Fluxo do pipeline (8 etapas)

1. **Download** — `ingestion/download_dataset.py`: baixa o MIMII Pump do Zenodo e extrai para `data/raw/pump/`.
2. **Upload para S3/MinIO** — `ingestion/load_raw_to_s3.py`: sobe os `.wav` para o bucket `raw/`.
3. **Metadados** — `processing/process_structured.py`: extrai metadados dos caminhos dos arquivos → `pump_metadata.csv` (2.400 linhas, com o target `condition_binary`).
4. **Features de áudio** — `processing/extract_audio_features.py`: extrai 92 features por arquivo com librosa → `audio_features.csv`.
5. **Merge** — `processing/merge_features.py`: junta metadados + features → `ml_features.csv` (2.400 linhas × 103 colunas).
6. **Carga no banco** — `processing/load_to_postgres.py`: insere o CSV no PostgreSQL (tabela `ml_features_raw`).
7. **dbt (run + test)** — 5 modelos em camadas (staging → dimensions → facts → marts) e 14 testes de qualidade (not_null, unique, accepted_values).
8. **ML** — `ml/evaluate.py`: treina e compara 4 modelos, gera métricas, matrizes de confusão e o relatório `report_analys.md`.

Tudo isso é orquestrado pela DAG `dags/etl_pipeline.py` no Airflow, e os resultados aparecem em 3 dashboards no Metabase.

## 6. Modelo de ML

Rede neural **MLP binária** (entrada de 96 features → 64 neurônios ReLU → 32 ReLU → 1 sigmoid = probabilidade de anomalia), em **duas implementações**:

- **Hard-code** (`ml/hard_code/neural_network_hardcode.py`): 100% NumPy — funções `treinar()`/`prever()` com forward pass, backpropagation e SGD com momento escritos do zero, sem frameworks.
- **Sklearn** (`ml/library/neural_network_sklearn.py`): `MLPClassifier` com a mesma arquitetura.

Ambos são comparados com dois baselines (DummyClassifier e Regressão Logística), usando o mesmo split e scaler. **Resultado:** o MLP sklearn atinge ~98% de acurácia (F1 0,899, recall da anomalia 83,5%) e o hard-code praticamente empata (97,86%, F1 0,894) — validando a implementação manual; o sklearn treina ~3x mais rápido. As features que mais separam normal de anomalia são os **MFCCs** (`mfcc_35_mean`, `mfcc_31_mean`, `mfcc_10_mean`, `mfcc_3_mean`).

## 7. Como rodar

```bash
make up        # 1. Sobe os containers (Postgres, MinIO, Airflow, Metabase)
make ingest    # 2. Baixa o dataset e sobe para o MinIO
make process   # 3. Extrai metadados + features de áudio + merge
make load-db   # 4. Carrega o CSV no PostgreSQL
make dbt-run   # 5. Roda os modelos dbt
make dbt-test  # 6. Roda os testes de qualidade
make ml-train  # 7. Treina e avalia os modelos
```

**Serviços locais:**

| Serviço | URL | Usuário / Senha |
|---|---|---|
| Airflow | http://localhost:8080 | `admin` / `admin` |
| Metabase | http://localhost:3000 | `admin@projeto.com` / `ProjetoIFG2025!` |
| MinIO | http://localhost:9001 | `minioadmin` / `minioadmin` |

## 8. Onde aprofundar

- `README.md` — documentação principal do projeto
- `FLUXO.md` — explicação detalhada de cada etapa do pipeline
- `report_analys.md` — relatório do último treinamento (métricas, análise de erros)
- `docs/ARQUITETURA_AWS.md` — diagramas de arquitetura (dev e 100% AWS) e custos
- `CLAUDE.md` — contexto completo e histórico de decisões do projeto
