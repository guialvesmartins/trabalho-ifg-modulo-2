---
title: Datasets
date: 2025-07-03
tags:
  - dados
  - datasets
  - kaggle
aliases:
  - Dados
  - Fontes de Dados
---

# Datasets

[[Home|Voltar ao índice]]

---

## Dataset 1 — Amazon Sales Dataset (Principal)

| Atributo | Valor |
|----------|-------|
| **Kaggle ID** | `karkavelrajaj/amazon-sales-dataset` |
| **Link** | [abrir no Kaggle](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) |
| **Tamanho** | ~1.400 produtos |
| **Arquivo** | `data/raw/amazon_sales.csv` |

### Colunas

| Coluna | Tipo | Uso |
|--------|------|-----|
| `product_name` | Texto | Nome do produto |
| `category` | Categórico | Categoria (Eletrônicos, Roupas, etc.) |
| `discounted_price` | Numérico | Preço com desconto (₹) |
| `actual_price` | Numérico | Preço original (₹) |
| `discount_percentage` | Numérico | % de desconto |
| `rating` | Numérico (1-5) | **🎯 Target do modelo** |
| `rating_count` | Numérico | Quantidade de avaliações |
| `review_content` | **Texto** | Conteúdo da review |
| `review_title` | **Texto** | Título da review |
| `img_link` | **URL** | Link da imagem do produto |
| `product_link` | URL | Link da página do produto |

> [!success] Este dataset sozinho já entrega os 3 tipos de dados
> Estruturado + Texto + Imagens.

---

## Dataset 2 — Amazon Product Reviews (Complementar NLP)

| Atributo | Valor |
|----------|-------|
| **Kaggle ID** | `arhamrumi/amazon-product-reviews` |
| **Link** | [abrir no Kaggle](https://www.kaggle.com/datasets/arhamrumi/amazon-product-reviews) |
| **Tamanho** | ~35.000 reviews |
| **Arquivo** | `data/raw/amazon_reviews.csv` |
| **Uso** | Enriquecer os dados textuais com mais exemplos de reviews |

---

## Imagens de Produtos

| Atributo | Valor |
|----------|-------|
| **Fonte** | Coluna `img_link` do Dataset 1 |
| **Quantidade** | ~500-1000 imagens |
| **Formato** | JPEG/PNG |
| **Armazenamento dev** | MinIO (`raw/images/`) |
| **Armazenamento prod** | AWS S3 (`images/`) |
| **Diretório local** | `images/products/` |

---

## Download

```bash
# Via Makefile
make ingest

# Manual (scripts Python)
python ingestion/download_dataset.py    # Baixa do Kaggle → data/raw/
python ingestion/load_raw_to_s3.py      # Upload → MinIO/S3
```

> [!warning] Requisito
> É necessário ter o `kagglehub` instalado e credenciais Kaggle configuradas (`~/.kaggle/kaggle.json`).

---

## Estrutura no S3/MinIO

```
bucket/
├── raw/
│   ├── amazon_sales.csv
│   ├── amazon_reviews.csv
│   └── images/
│       ├── B000001.jpg
│       ├── B000002.jpg
│       └── ...
└── processed/
    ├── products_clean.csv
    ├── reviews_clean.csv
    ├── reviews_features.csv
    ├── images_features.csv
    └── ml_features.csv
```
