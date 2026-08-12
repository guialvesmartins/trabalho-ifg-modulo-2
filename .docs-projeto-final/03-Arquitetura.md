---
title: Arquitetura
date: 2025-07-03
tags:
  - arquitetura
  - docker
  - aws
  - cloud
aliases:
  - Arquitetura do Projeto
  - Infraestrutura
---

# Arquitetura

[[Home|Voltar ao índice]]

---

## Ambiente de Desenvolvimento (Docker)

```mermaid
graph TD
    subgraph "docker compose up"
        MinIO[MinIO :9000\nS3 Mock]
        PG[PostgreSQL :5432\nSnowflake Mock]
        AF[Airflow :8080]
        MB[Metabase :3000]
        PY[Python Scripts\ningest, process, ML]
        DBT[dbt-core\nvia Airflow/CLI]
    end

    PY --> MinIO
    PY --> PG
    AF --> PY
    AF --> DBT
    DBT --> PG
    MB --> PG
```

### Serviços Docker

| Serviço | Imagem | Porta |
|---------|--------|-------|
| PostgreSQL | `postgres:16-alpine` | 5432 |
| MinIO | `minio/minio:latest` | 9000, 9001 |
| Airflow | `apache/airflow:2.9.0` | 8080 |
| Metabase | `metabase/metabase:latest` | 3000 |
| metabase-setup | `python:3.11-slim` | — |

---

## Ambiente de Produção (Híbrido)

Apenas **S3** e **Snowflake** são serviços externos reais. O restante permanece local.

```mermaid
graph TD
    subgraph "AWS Cloud"
        S3[AWS S3\nraw/]
    end

    subgraph "Snowflake Cloud"
        SF[Snowflake\nSTAGING / DIMS / FACTS / MARTS]
    end

    subgraph "Local Docker"
        AF2[Airflow :8080]
        MB2[Metabase :3000]
        PY2[Python Scripts]
    end

    S3 --> PY2
    PY2 --> SF
    AF2 --> PY2
    AF2 --> SF
    MB2 --> SF
```

> [!tip] Troca de ambiente
> Basta mudar 4 variáveis no `.env`. Ver [[11-Comandos#Ambiente]].

---

## Arquitetura 100% AWS (CloudFormation — Exercício Acadêmico)

> [!info] Documentada no CloudFormation como exercício. Na prática, apenas S3 é usado como serviço real.

```mermaid
graph TD
    subgraph "AWS Cloud"
        S3_CF[S3\nraw/]
        GLUE[Glue Crawler]
        ATH[Athena]
        EC2[EC2\nAirflow]
        ECS[ECS\ndbt + ML]
        SM[SageMaker\nModelo ML]
        RS[Redshift\nData Warehouse]
        QS[QuickSight\nDashboard]
        CW[CloudWatch\nLogs + Alertas]
        IAM[IAM\nRoles + Policies]
    end

    S3_CF --> GLUE --> ATH
    S3_CF --> EC2
    S3_CF --> ECS
    EC2 --> RS
    ECS --> RS
    SM --> RS
    RS --> QS
    EC2 --> CW
    ECS --> CW
```

> [!info] Detalhes do CloudFormation
> Ver [[10-Infra-AWS]] para a lista completa de recursos.

---

## Variáveis de Ambiente

### `.env.local` (Desenvolvimento)

```bash
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
DB_TYPE=postgres
DB_HOST=localhost
```

### `.env.prod` (Produção)

```bash
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=<aws_access_key>
S3_SECRET_KEY=<aws_secret_key>
DB_TYPE=snowflake
DB_ACCOUNT=<snowflake_account>
```
