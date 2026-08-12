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
make up              # docker compose up -d
make down            # docker compose down
make logs            # docker compose logs -f
make build           # docker compose build

# Pipeline
make pipeline        # Dispara DAG manualmente no Airflow
make ingest          # Download datasets + upload S3
make process         # Processamento + NLP + CV

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
export ENV_FILE=.env.local
make up

# Produção (S3 + Snowflake reais)
cp .env.example .env.prod
# Editar .env.prod com credenciais reais
export ENV_FILE=.env.prod
make up && make pipeline
```

---

## Python Scripts (Manuais)

```bash
# Ingestão
python ingestion/download_dataset.py
python ingestion/load_raw_to_s3.py

# Processamento
python processing/process_structured.py
python processing/extract_text_features.py
python processing/extract_image_features.py
python processing/merge_features.py

# ML
python ml/hard_code/naive_bayes_hardcode.py
python ml/sklearn/naive_bayes_sklearn.py
python ml/evaluate.py
```

---

## dbt

```bash
# Dentro do container dbt ou com dbt instalado localmente
cd dbt_project

dbt deps            # Instalar dependências
dbt run             # Rodar todos os modelos
dbt run --select staging   # Rodar só staging
dbt run --select marts      # Rodar só marts
dbt test            # Rodar testes
dbt test --select dim_products  # Testar modelo específico
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
aws s3 ls s3://raw/ --endpoint-url http://localhost:9000
aws s3 ls s3://processed/ --endpoint-url http://localhost:9000

# Upload manual
aws s3 cp data/raw/amazon_sales.csv s3://raw/ --endpoint-url http://localhost:9000

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
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
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
