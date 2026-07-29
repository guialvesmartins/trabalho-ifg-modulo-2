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

[[🏠 Home|Voltar ao índice]]

---

## 1. Definição do Problema

| Campo | Descrição |
|-------|-----------|
| **Domínio** | E-commerce / Marketplace |
| **Tomador de decisão** | Gerente de Produto e Operações |
| **Decisão apoiada** | Identificar quais produtos precisam de intervenção (qualidade, logística, preço, apresentação visual) |
| **Fontes de dados** | Dados de vendas (estruturado) + Reviews textuais (não estruturado) + Imagens de produtos (não estruturado) |
| **Tarefa de ML** | Classificação multiclasse — prever o rating (1 a 5 estrelas) combinando features textuais, visuais e estruturadas |
| **Resultado esperado** | Sistema que classifica automaticamente o nível de satisfação e identifica os fatores que mais impactam a nota |

---

## 2. Fontes de Dados

| Dataset | Fonte | Tamanho |
|---------|-------|---------|
| Amazon Sales Dataset | [Kaggle](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) | ~1.400 produtos |
| Amazon Product Reviews | [Kaggle](https://www.kaggle.com/datasets/arhamrumi/amazon-product-reviews) | ~35.000 reviews |
| Imagens de produtos | Coluna `img_link` do Dataset 1 | ~500-1000 imagens |

> [!info] Detalhes completos
> Ver [[02-Datasets]] para o dicionário de dados completo.

---

## 3. Tipos de Dados

| Tipo | Fonte | Features Geradas |
|------|-------|------------------|
| **Estruturado** | `amazon_sales.csv` | Preço, desconto, categoria, rating_count |
| **Texto (NLP)** | `review_content`, `review_title` | ~217 features (VADER, TF-IDF, metadados) |
| **Imagem (CV)** | `img_link` | ~28 features (cores, nitidez, textura, bordas) |

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
Download Datasets → Upload S3 → Process Structured → [NLP ∥ CV] → Merge → dbt → ML Train
```

> [!info] Pipeline detalhado
> Ver [[04-Pipeline-ELT]] para o passo a passo completo.

---

## 6. Tecnologias

| Camada | Tecnologias |
|--------|-------------|
| **Orquestração** | Apache Airflow 2.9 |
| **Storage** | MinIO (dev) / AWS S3 (prod) |
| **Processamento** | Python (pandas, numpy, sklearn, OpenCV) |
| **NLP** | VADER, TF-IDF, textstat |
| **CV** | OpenCV, Pillow, scikit-image |
| **Data Warehouse** | PostgreSQL (dev) / Snowflake (prod) |
| **Transformação** | dbt-core 1.8 |
| **Dashboard** | Metabase |
| **ML** | Naive Bayes (hard-code + sklearn MultinomialNB) |
| **Infra** | Docker, CloudFormation |

---

> [!warning] Atenção
> A troca entre ambiente dev e prod é feita apenas mudando 4 variáveis no `.env`. Ver [[11-Comandos#Ambiente]] para detalhes.
