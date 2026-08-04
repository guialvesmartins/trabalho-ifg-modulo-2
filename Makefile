.PHONY: up down logs build pipeline ingest process dbt-run dbt-test dbt-docs ml-train test dashboard clean setup-metabase

include .env.local
export

up:
	docker compose up -d
	@echo "Aguardando servicos..."
	@sleep 5
	@echo "Metabase config. automatica em andamento (ver logs: make logs-setup)..."
	@echo "Airflow:    http://localhost:8080 (admin/admin)"
	@echo "Metabase:   http://localhost:3000 (admin@projeto.com / ProjetoIFG2025!)"
	@echo "MinIO API:  http://localhost:9000 (minioadmin/minioadmin)"
	@echo "MinIO Web:  http://localhost:9001"

logs-setup:
	docker compose logs -f metabase-setup

setup-metabase:
	python3 scripts/setup_metabase.py

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

ingest:
	python3 ingestion/download_dataset.py
	python3 ingestion/load_raw_to_s3.py

process:
	python3 processing/process_structured.py
	python3 processing/extract_audio_features.py
	python3 processing/merge_features.py

load-db:
	python3 processing/load_to_postgres.py

pipeline:
	@echo "Disparando DAG no Airflow..."
	docker compose exec airflow-webserver airflow dags trigger etl_pipeline

dbt-run:
	cd dbt_project && dbt run

dbt-test:
	cd dbt_project && dbt test

dbt-docs:
	cd dbt_project && dbt docs generate && dbt docs serve

ml-train:
	PYTHONPATH=. python3 ml/evaluate.py

test:
	python3 -m pytest tests/ -v

dashboard:
	@echo "Metabase: http://localhost:3000"

clean:
	docker compose down -v
	rm -rf data/raw/* data/processed/*
	rm -rf dbt_project/logs dbt_project/target
	@echo "Ambiente limpo."
