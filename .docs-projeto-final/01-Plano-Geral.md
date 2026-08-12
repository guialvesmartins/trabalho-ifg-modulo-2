---
title: Plano Geral
date: 2025-07-03
tags:
  - plano
  - escopo
  - definicao
aliases:
  - Plano
  - Definição do Problema
  - Escopo
---

# Plano Geral

[[Home|Voltar ao índice]]

---

## 1. Definição do Problema

| Campo | Descrição |
|-------|-----------|
| **Domínio** | Indústria 4.0 / Manutenção Preditiva |
| **Tomador de decisão** | Engenheiro de manutenção industrial |
| **Decisão apoiada** | "Esta bomba industrial está operando com anomalia? Devo parar para manutenção?" |
| **Fontes de dados** | Metadados dos arquivos de áudio (estruturado) + Clipes `.wav` 16 kHz de bombas industriais (não estruturado) |
| **Tarefa de ML** | Classificação binária — prever se a bomba está `normal` ou com `anomalia` (contaminação, vazamento, desbalanceamento) |
| **Resultado esperado** | Sistema que analisa o som de cada bomba e classifica automaticamente, reduzindo paradas não programadas e manutenções desnecessárias |

**Impacto esperado:**
- Redução de paradas não programadas (detecta anomalia antes da falha)
- Redução de manutenções desnecessárias (não para máquina normal)
- Aumento da vida útil dos equipamentos
- Economia em custos de reparo emergencial

---

## 2. Fontes de Dados

| Dataset | Fonte | Tamanho |
|---------|-------|---------|
| MIMII Dataset — Pump | [Zenodo](https://zenodo.org/records/3384388) | ~7,87 GB (4.205 clipes) |

MIMII = *Malfunctioning Industrial Machine Investigation and Inspection* (Hitachi, Ltd. / Toyota Research, DCASE 2019, [arXiv:1909.09347](https://arxiv.org/abs/1909.09347)).

> [!info] Detalhes completos
> Ver [[02-Datasets]] para o dicionário de dados completo.

---

## 3. Tipos de Dados

| Tipo | Fonte | Features Geradas |
|------|-------|------------------|
| **Estruturado** | Paths dos `.wav` (`pump/id_XX/normal|abnormal/*.wav`) | `machine_type`, `model_id`, `condition`, `duration_sec`, `sample_rate`, `channels` |
| **Áudio (não estruturado)** | Clipes `.wav` 16 kHz | 92 features (MFCC, spectral, ZCR, RMS) via librosa |

> [!info] Features detalhadas
> Ver [[06-Machine-Learning#Features]] para a lista completa.

---

## 4. Arquitetura Resumida

- **Dev local:** Docker (Postgres, MinIO, Airflow, Metabase)
- **Prod:** AWS S3 + Snowflake (externos), resto local
- **Exercício acadêmico:** CloudFormation com arquitetura 100% AWS

> [!info] Diagramas completos
> Ver [[03-Arquitetura]] para os diagramas de cada ambiente.

---

## 5. Pipeline (8 Etapas)

```
Download MIMII → Upload S3 → Metadados → Features de Áudio → Merge → Carga Postgres → dbt → ML
```

> [!info] Pipeline detalhado
> Ver [[04-Pipeline-ELT]] para o passo a passo completo.

---

## 6. Tecnologias

| Camada | Tecnologias |
|--------|-------------|
| **Orquestração** | Apache Airflow 2.9 |
| **Storage** | MinIO (dev) / AWS S3 (prod) |
| **Processamento** | Python (pandas, numpy, librosa, soundfile, scikit-learn) |
| **Áudio** | librosa, soundfile |
| **Data Warehouse** | PostgreSQL (dev) / Snowflake (prod) |
| **Transformação** | dbt-core 1.8 |
| **Dashboard** | Metabase |
| **ML** | MLP binário (hard-code NumPy + sklearn MLPClassifier) |
| **Infra** | Docker, CloudFormation |

---

> [!warning] Atenção
> A troca entre ambiente dev e prod é feita apenas mudando 4 variáveis no `.env`. Ver [[11-Comandos#Ambiente]] para detalhes.
