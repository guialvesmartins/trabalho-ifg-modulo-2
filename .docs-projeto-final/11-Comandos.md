---
title: Comandos
date: 2025-07-03
tags:
  - comandos
  - makefile
  - docker
  - dbt
  - referencia
aliases:
  - Referência de Comandos
  - Makefile
---

# Referência de Comandos

[[Home|Voltar ao índice]]

---

## Makefile

```bash
# Docker
make up              # docker compose up -d + configura Metabase automaticamente
make down            # docker compose down
make logs            # docker compose logs -f
make build           # docker compose build
make logs-setup      # Logs do container metabase-setup
make setup-metabase  # Roda scripts/setup_metabase.py manualmente

# Pipeline
make pipeline        # Dispara DAG manualmente no Airflow
make ingest          # Download MIMII + upload S3
make process         # Metadados + features de áudio + merge
make load-db         # Carrega CSV no PostgreSQL

# dbt
make dbt-run         # dbt run
make dbt-test        # dbt test
make dbt-docs        # dbt docs generate && dbt docs serve

# ML
make ml-train        # Treina hard-code + sklearn + avalia

# Testes
make test            # pytest tests/

# Dashboard
make dashboard       # Mostra URL do Metabase (http://localhost:3000)

# Limpeza
make clean           # docker compose down -v + remove dados processados
```

---

## Docker

```bash
# Subir ambiente
docker compose up -d

# Ver logs de um serviço específico
docker compose logs -f airflow
docker compose logs -f postgres
docker compose logs -f minio
docker compose logs -f metabase-setup

# Acessar container
docker compose exec airflow bash
docker compose exec postgres psql -U airflow

# Derrubar tudo (remove volumes)
docker compose down -v
```

---

## Ambiente

```bash
# Desenvolvimento
cp .env.example .env.local
make up

# Produção (S3 + Snowflake reais)
cp .env.example .env.prod
# Editar .env.prod com credenciais reais (4 variáveis: S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, DB_TYPE/DB_ACCOUNT)
make up && make pipeline
```

> [!info] Troca dev/prod
> Apenas 4 variáveis de ambiente separam o ambiente local do AWS + Snowflake. `boto3` usa `endpoint_url` e o dbt `profiles.yml` usa `env_var()`.

---

## Python Scripts (Manuais)

```bash
# Ingestão
python ingestion/download_dataset.py     # Zenodo → data/raw/pump/
python ingestion/load_raw_to_s3.py       # .wav → MinIO/S3

# Processamento
python processing/process_structured.py  # metadados → pump_metadata.csv
python processing/extract_audio_features.py  # librosa → audio_features.csv
python processing/merge_features.py      # merge → ml_features.csv
python processing/load_to_postgres.py    # CSV → PostgreSQL

# ML
python ml/evaluate.py                    # baselines + hard-code + sklearn
python ml/hard_code/neural_network_hardcode.py
python ml/library/neural_network_sklearn.py
```

---

## dbt

```bash
# Dentro do container dbt ou com dbt instalado localmente
cd dbt_project

dbt run             # Rodar todos os modelos
dbt run --select staging    # Rodar só staging
dbt run --select marts      # Rodar só marts
dbt test            # Rodar testes (16)
dbt test --select dim_machines   # Testar modelo específico
dbt docs generate   # Gerar documentação
dbt docs serve      # Servir documentação (porta 8081)
```

---

## MinIO (AWS CLI)

```bash
# Configurar alias (dev local)
aws configure --profile minio set aws_access_key_id minioadmin
aws configure --profile minio set aws_secret_access_key minioadmin

# Listar buckets
aws s3 ls --endpoint-url http://localhost:9000

# Listar arquivos
aws s3 ls s3://raw/pump/ --endpoint-url http://localhost:9000

# Upload manual
aws s3 cp data/raw/pump/id_00/normal/00000000.wav s3://raw/pump/id_00/normal/ --endpoint-url http://localhost:9000

# Download manual
aws s3 cp s3://processed/ml_features.csv . --endpoint-url http://localhost:9000
```

---

## PostgreSQL

```bash
# Conectar via psql
docker compose exec postgres psql -U airflow -d airflow

# Listar tabelas
\dt

# Ver schema do dbt
SELECT table_name FROM information_schema.tables WHERE table_schema IN ('public', 'public_analytics');
```

---

## Troubleshooting

```bash
# Resetar ambiente completamente
make down
docker compose down -v
docker system prune -f
make up

# Verificar se todos os serviços estão saudáveis
docker compose ps

# Logs de um serviço específico
docker compose logs airflow | tail -50

# Reiniciar um serviço
docker compose restart airflow
```
