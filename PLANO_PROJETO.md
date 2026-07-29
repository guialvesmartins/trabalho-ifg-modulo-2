# Plano Completo — Projeto Final Integrado

**Curso:** Pós-Graduação em Inteligência Artificial Aplicada — IFG — Módulo 2
**Tema:** Previsão de Satisfação em E-commerce com Dados Multimodais (Texto + Imagens + Dados Estruturados)
**Disciplinas:** Aprendizagem de Máquina · Cloud Computing · Modelagem de Dados para IA

---

## 1. Definição do Problema

| Campo | Descrição |
|-------|-----------|
| **Domínio** | E-commerce / Marketplace |
| **Tomador de decisão** | Gerente de Produto e Operações |
| **Decisão apoiada** | Identificar quais produtos precisam de intervenção (qualidade, logística, preço, apresentação visual) para aumentar a satisfação do cliente |
| **Fontes de dados** | Dados de vendas (estruturado) + Reviews textuais (não estruturado) + Imagens de produtos (não estruturado) |
| **Tarefa de ML** | Classificação multiclasse — prever o rating (1 a 5 estrelas) combinando features textuais da review, features visuais da imagem do produto e dados estruturados do produto |
| **Resultado esperado** | Um sistema que classifica automaticamente o nível de satisfação esperado e identifica os fatores (texto, preço, imagem, categoria) que mais impactam a nota do cliente |

---

## 2. Datasets

### 2.1 Dataset 1 — Amazon Sales Dataset (Principal)

- **Kaggle:** `karkavelrajaj/amazon-sales-dataset`
- **Link:** https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset
- **Tamanho:** ~1.400 produtos
- **Colunas relevantes:**

| Coluna | Tipo | Uso |
|--------|------|-----|
| `product_name` | Texto | Nome do produto |
| `category` | Categórico | Categoria (Eletrônicos, Roupas, etc.) |
| `discounted_price` | Numérico | Preço com desconto (₹) |
| `actual_price` | Numérico | Preço original (₹) |
| `discount_percentage` | Numérico | % de desconto |
| `rating` | Numérico (1-5) | **Target do modelo** |
| `rating_count` | Numérico | Qtd de avaliações |
| `review_content` | **Texto (não estruturado)** | Conteúdo da review |
| `review_title` | **Texto (não estruturado)** | Título da review |
| `img_link` | **URL (imagem)** | Link da imagem do produto |
| `product_link` | URL | Link da página do produto |

**Este dataset sozinho já entrega os 3 tipos de dados: estruturado + texto + imagens.**

### 2.2 Dataset 2 — Amazon Product Reviews (Complementar NLP)

- **Kaggle:** `arhamrumi/amazon-product-reviews`
- **Link:** https://www.kaggle.com/datasets/arhamrumi/amazon-product-reviews
- **Tamanho:** ~35.000 reviews
- **Uso:** Enriquecer os dados textuais com mais exemplos de reviews para o modelo de NLP.

### 2.3 Imagens

- **Fonte:** Coluna `img_link` do Dataset 1
- **Processo:** Baixar ~500-1000 imagens de produtos via URLs
- **Armazenamento:** MinIO (local) / S3 (prod)

---

## 3. Arquitetura

### 3.1 Ambiente de Desenvolvimento (Local — Docker)

```
┌─────────────────────────────────────────────────────────┐
│                    docker compose up                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │  MinIO   │   │PostgreSQL│   │ Airflow  │            │
│  │  :9000   │   │  :5432   │   │  :8080   │            │
│  │ (S3 mock)│   │(Snowflake│   │          │            │
│  │          │   │   mock)  │   │          │            │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘            │
│       │              │              │                   │
│       │    ┌─────────┼──────────────┘                   │
│       │    │         │                                  │
│       ▼    ▼         ▼                                  │
│  ┌────────────────────────┐   ┌──────────┐             │
│  │     Python Scripts     │   │ Metabase │             │
│  │  (ingest, NLP, ML, CV) │   │  :3000   │             │
│  └────────────────────────┘   └──────────┘             │
│                                                         │
│  ┌────────────────────────┐                             │
│  │        dbt-core        │                             │
│  │   (via Airflow/CLI)    │                             │
│  └────────────────────────┘                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Ambiente de Produção (Serviços Externos Reais)

Apenas **S3** e **Snowflake** são externos. Todo o resto segue local.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  AWS S3 (prod)          Snowflake (prod)                │
│  ┌──────────┐           ┌──────────────┐                │
│  │ raw/     │           │ STAGING      │                │
│  │processed/│ ──dbt──▶  │ DIMENSIONS   │                │
│  │images/   │           │ FACTS        │                │
│  └──────────┘           │ MARTS        │                │
│                         └──────────────┘                │
│                                                         │
│  Local (Docker)                                        │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │ Airflow  │   │ Metabase │   │ Python   │            │
│  │  :8080   │   │  :3000   │   │ Scripts  │            │
│  └──────────┘   └──────────┘   └──────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**TROCA:** Basta mudar 4 variáveis no `.env`:

```bash
# .env.local
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
DB_TYPE=postgres
DB_HOST=postgres
DB_USER=airflow
DB_PASS=airflow
DB_NAME=airflow

# .env.prod
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=<aws_access_key>
S3_SECRET_KEY=<aws_secret_key>
DB_TYPE=snowflake
DB_ACCOUNT=<snowflake_account>
DB_USER=<snowflake_user>
DB_PASS=<snowflake_pass>
DB_WAREHOUSE=COMPUTE_WH
DB_DATABASE=PROD_DB
DB_SCHEMA=PUBLIC
```

---

### 3.3 Arquitetura 100% AWS (CloudFormation — Exercício Acadêmico)

Esta arquitetura é **documentada no CloudFormation** como exercício. Na prática, só S3 é usado como serviço real. Os demais seguem locais.

```
┌──────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐     ┌──────────┐     ┌─────────────┐               │
│  │   S3    │────▶│   Glue   │────▶│   Athena    │               │
│  │ (raw/   │     │ Crawler  │     │  (Query)    │               │
│  │processed│     └──────────┘     └─────────────┘               │
│  │ /images)│                                                    │
│  └─────────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐     ┌──────────┐     ┌──────────────┐             │
│  │  EC2    │     │   ECS    │     │  SageMaker   │             │
│  │(Airflow)│     │ (dbt, ML)│     │  (Modelo ML) │             │
│  └─────────┘     └──────────┘     └──────────────┘             │
│       │               │                   │                     │
│       ▼               ▼                   ▼                     │
│  ┌──────────────────────────────────────────────────┐          │
│  │              Redshift (Data Warehouse)            │          │
│  └──────────────────────┬───────────────────────────┘          │
│                         │                                       │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────┐          │
│  │            QuickSight (Dashboard)                 │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │  CloudWatch (Logs, Monitoramento, Alertas)       │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │  IAM (Roles, Policies, Security Groups, VPC)     │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Estrutura de Diretórios

```
projeto-final/
├── docker-compose.yml
├── Dockerfile
├── .env.local
├── .env.prod
├── .env.example
├── .gitignore
├── Makefile
├── requirements.txt
├── README.md
├── PLANO_PROJETO.md              ← Este arquivo
│
├── data/                         # Dados (gitignorados)
│   ├── raw/
│   │   ├── amazon_sales.csv
│   │   └── amazon_reviews.csv
│   └── processed/
│       ├── products_clean.csv
│       ├── reviews_clean.csv
│       ├── reviews_features.csv
│       └── images_features.csv
│
├── images/                       # Imagens baixadas (gitignoradas)
│   └── products/
│       ├── B000001.jpg
│       ├── B000002.jpg
│       └── ...
│
├── ingestion/
│   ├── download_dataset.py       # Baixa datasets do Kaggle
│   └── load_raw_to_s3.py         # Upload CSVs + imagens → MinIO/S3
│
├── processing/
│   ├── process_structured.py     # Limpeza dados estruturados
│   ├── extract_text_features.py  # NLP: metadados, VADER, TF-IDF
│   ├── extract_image_features.py # CV: cores, textura, blur, bordas
│   └── merge_features.py        # JOIN: tudo → tabela final
│
├── dags/
│   └── etl_pipeline.py           # DAG Airflow única
│
├── dbt_project/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_products.sql
│   │   │   ├── stg_reviews.sql
│   │   │   └── stg_images.sql
│   │   ├── dimensions/
│   │   │   ├── dim_products.sql
│   │   │   └── dim_categories.sql
│   │   ├── facts/
│   │   │   ├── fact_reviews.sql
│   │   │   └── fact_sales.sql
│   │   └── marts/
│   │       └── ml_features.sql
│   ├── macros/
│   ├── tests/
│   │   └── schema.yml
│   └── docs/
│
├── ml/
│   ├── hard_code/
│   │   └── naive_bayes_hardcode.py
│   ├── sklearn/
│   │   └── naive_bayes_sklearn.py
│   └── evaluate.py
│
├── dashboard/
│   └── metabase_questions.md     # Queries SQL do dashboard
│
├── infra/
│   ├── cloudformation.yaml
│   └── architecture_diagram.png
│
├── notebooks/
│   ├── 01_eda_structured.ipynb
│   ├── 02_eda_reviews_nlp.ipynb
│   └── 03_ml_experiments.ipynb
│
├── tests/
│   ├── test_processing.py
│   ├── test_nlp.py
│   └── test_ml.py
│
└── report/
    ├── relatorio.md
    └── apresentacao.pptx
```

---

## 5. Pipeline Completo (Ordem de Execução)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Pipeline ELT — 8 Etapas                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [1] download_dataset.py                                            │
│      Baixa datasets do Kaggle → data/raw/                           │
│      Kaggle: karkavelrajaj/amazon-sales-dataset                     │
│      Kaggle: arhamrumi/amazon-product-reviews                       │
│                          │                                          │
│                          ▼                                          │
│  [2] load_raw_to_s3.py                                              │
│      Upload pro MinIO/S3 bucket: raw/                               │
│      - raw/amazon_sales.csv                                         │
│      - raw/amazon_reviews.csv                                       │
│      - raw/images/*.jpg (download das URLs)                         │
│                          │                                          │
│                          ▼                                          │
│  [3] process_structured.py                                          │
│      Limpeza: nulos, dedup, padronização                            │
│      → MinIO/S3: processed/products_clean.csv                       │
│                          │                                          │
│       ┌──────────────────┼──────────────────┐                       │
│       ▼                  │                  ▼                       │
│  [4a] extract_text_      │           [4b] extract_image_            │
│       features.py        │                features.py               │
│       NLP:               │                CV:                       │
│       · review_length    │                · width, height           │
│       · word_count       │                · aspect_ratio            │
│       · polarity,        │                · brightness_mean         │
│         subjectivity     │                · saturation_mean         │
│         (VADER)          │                · edge_density            │
│       · TF-IDF top 200   │                · blur_score              │
│       · contains_        │                · dominant_colors (top 3) │
│         complaint/praise │                · colorfulness_score      │
│       · uppercase_ratio  │                · entropy                 │
│       · exclamation_cnt  │                                         │
│       · sentence_count   │                                         │
│                          │                                          │
│       └──────────────────┼──────────────────┘                       │
│                          ▼                                          │
│  [5] merge_features.py                                              │
│      JOIN: products_clean + reviews_features + images_features      │
│      → MinIO/S3: processed/ml_features.csv                          │
│                          │                                          │
│                          ▼                                          │
│  [6] dbt run (Airflow BashOperator)                                 │
│      staging → dimensions → facts → marts                           │
│      ┌─────────────┬──────────────┬──────────────┬──────────┐      │
│      │ staging     │ dimensions   │ facts        │ marts    │      │
│      ├─────────────┼──────────────┼──────────────┼──────────┤      │
│      │stg_products │dim_products  │fact_reviews  │ml_features│     │
│      │stg_reviews  │dim_categories│fact_sales    │          │      │
│      │stg_images   │              │              │          │      │
│      └─────────────┴──────────────┴──────────────┴──────────┘      │
│                          │                                          │
│                          ▼                                          │
│  [7] dbt test                                                       │
│      4 testes mínimos:                                              │
│      · dim_products: not_null(product_id), unique(product_id)       │
│      · fact_reviews: not_null(review_id), not_null(rating)          │
│      · fact_reviews: accepted_values(rating, [1,2,3,4,5])           │
│      · dim_categories: unique(category_name)                        │
│                          │                                          │
│                          ▼                                          │
│  [8] ml/train.py                                                    │
│      8a. naive_bayes_hardcode.py → Naive Bayes do zero              │
│      8b. naive_bayes_sklearn.py  → MultinomialNB (sklearn)          │
│      8c. evaluate.py             → comparação lado a lado           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Detalhamento: Extração de Features Não Estruturadas

### 6.1 Features de Texto (NLP) — `extract_text_features.py`

| Categoria | Técnica | Features geradas | Qtde |
|-----------|---------|------------------|------|
| **Metadados** | Python built-in | `review_length`, `word_count`, `avg_word_length`, `sentence_count` | 4 |
| **Estilo** | Python built-in | `uppercase_ratio`, `exclamation_count`, `question_count`, `numeric_ratio` | 4 |
| **Sentimento** | VADER (`vaderSentiment`) | `polarity` (-1 a 1), `subjectivity` (0 a 1), `compound_score` | 3 |
| **TF-IDF** | `sklearn.feature_extraction.text.TfidfVectorizer` | Top 200 palavras/bigramas mais relevantes | 200 |
| **Regex custom** | `re` (Python) | `contains_complaint`, `contains_praise`, `contains_price_mention`, `contains_delivery_mention` | 4 |
| **Legibilidade** | `textstat` | `flesch_reading_ease`, `complex_word_ratio` | 2 |

**Total de features textuais: ~217 por review**

### 6.2 Features de Imagem (CV) — `extract_image_features.py`

| Categoria | Técnica | Features geradas | Qtde |
|-----------|---------|------------------|------|
| **Dimensões** | PIL/Pillow | `width`, `height`, `aspect_ratio`, `file_size_kb`, `format` | 5 |
| **Cores** | OpenCV + K-Means (k=3) | `dominant_color_1_rgb`, `dominant_color_2_rgb`, `dominant_color_3_rgb`, `brightness_mean`, `saturation_mean`, `colorfulness_score` | 12 (3x3 RGB + 3) |
| **Nitidez** | OpenCV (Laplacian) | `blur_score` (variância do Laplaciano) | 1 |
| **Complexidade visual** | OpenCV (Canny) | `edge_density`, `corner_count` (Harris) | 2 |
| **Textura** | skimage | `entropy`, `contrast` (GLCM) | 2 |
| **Histograma** | OpenCV | `hist_mean_r`, `hist_mean_g`, `hist_mean_b`, `hist_std_r`, `hist_std_g`, `hist_std_b` | 6 |

**Total de features visuais: ~28 por imagem**

### 6.3 Features Estruturadas

| Coluna original | Tratamento | Feature final |
|-----------------|------------|---------------|
| `category` | Lowercase, one-hot encoding | `cat_electronics`, `cat_clothing`, ... |
| `actual_price` | float, log transform | `log_price`, `price` |
| `discount_percentage` | float, bucket | `discount_bucket_low/med/high` |
| `rating_count` | int, log transform | `log_rating_count` |
| `rating` | int (1-5) → **TARGET** | `target_rating` |

---

## 7. Modelagem dbt

### 7.1 Schema Estrela

```
                         ┌─────────────────┐
                         │  dim_categories  │
                         ├─────────────────┤
                         │ category_id (PK) │
                         │ category_name    │
                         │ total_products   │
                         │ avg_rating       │
                         └────────┬────────┘
                                  │
                                  │ 1:N
                                  │
┌─────────────────┐    ┌─────────┴────────┐    ┌─────────────────┐
│  dim_products   │    │   fact_sales     │    │   fact_reviews  │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ product_id (PK) │◄───│ product_id (FK)  │    │ review_id (PK)  │
│ product_name    │    │ actual_price     │    │ product_id (FK) │
│ category_id(FK) │    │ discounted_price │    │ rating          │
│ actual_price    │    │ discount_pct     │    │ review_title    │
│ disc_price      │    │ rating           │    │ review_content  │
│ discount_pct    │    │ rating_count     │    │ polarity        │
│ rating          │    └──────────────────┘    │ subjectivity    │
│ rating_count    │                            │ review_length   │
│ image_url       │                            │ word_count      │
│ brightness      │                            │ blur_score      │
│ blur_score      │                            │ edge_density    │
│ dominant_color  │                            │ ...             │
│ ...             │                            │ (217 features)  │
└─────────────────┘                            └────────┬────────┘
                                                        │
                                                        │ JOIN
                                                        ▼
                                              ┌─────────────────┐
                                              │   ml_features   │
                                              │   (marts)       │
                                              ├─────────────────┤
                                              │ Todas as        │
                                              │ features em uma │
                                              │ única tabela    │
                                              │ pronta pro ML   │
                                              └─────────────────┘
```

### 7.2 Modelos dbt

| Camada | Modelo | Descrição |
|--------|--------|-----------|
| **Staging** | `stg_products` | Renomeia, tipa e deduplica `ml_features.csv` |
| **Staging** | `stg_reviews` | Renomeia, tipa e deduplica reviews |
| **Staging** | `stg_images` | Renomeia, tipa e deduplica features de imagem |
| **Dimension** | `dim_products` | Tabela de produtos, SCD type 1 |
| **Dimension** | `dim_categories` | Tabela de categorias únicas com métricas agregadas |
| **Fact** | `fact_reviews` | Reviews com todas as features NLP + imagem |
| **Fact** | `fact_sales` | Métricas de venda por produto |
| **Mart** | `ml_features` | JOIN final: todas as features prontas para o modelo ML |

### 7.3 Testes dbt (schema.yml)

```yaml
version: 2

models:
  - name: dim_products
    columns:
      - name: product_id
        tests:
          - not_null
          - unique

  - name: fact_reviews
    columns:
      - name: review_id
        tests:
          - not_null
      - name: rating
        tests:
          - not_null
          - accepted_values:
              values: [1, 2, 3, 4, 5]

  - name: dim_categories
    columns:
      - name: category_name
        tests:
          - unique
```

---

## 8. Aprendizagem de Máquina

### 8.1 Tarefa

**Classificação multiclasse** (5 classes: rating 1 a 5)

Entrada:
- Features textuais (~217 cols)
- Features de imagem (~28 cols)
- Features estruturadas (~10 cols)
- **Total: ~255 features de entrada**

Saída:
- Rating predito: 1, 2, 3, 4 ou 5

### 8.2 Baseline

- Baseline simples: **prever sempre a classe majoritária** (rating mais frequente)
- Baseline melhorado: **prever apenas com dados estruturados** (preço, desconto, categoria)
- Comparar com modelo completo (estruturado + texto + imagem)

### 8.3 Implementação Hard-Code

`ml/hard_code/naive_bayes_hardcode.py`

Algoritmo implementado do zero, sem bibliotecas de ML:

```
1. Calcular log-prior: log P(classe c) para c = {1,2,3,4,5}
2. Para cada palavra w no vocabulário e cada classe c:
   P(w|c) = (count(w, c) + alpha) / (total_palavras_c + alpha * |V|)
   alpha = 1 (Laplace smoothing)
3. Para classificar um novo texto:
   score(c) = log P(c) + Σ log P(w_i|c) para cada palavra w_i
   predição = argmax_c score(c)
```

Trabalha com features binárias (palavra presente/ausente) ou contagem de frequência.
Opera em log-space para evitar underflow numérico.

### 8.4 Implementação com Biblioteca

`ml/sklearn/naive_bayes_sklearn.py`

```python
from sklearn.naive_bayes import MultinomialNB
# Usa as mesmas features do hard-code
# Comparação justa: mesmos dados, mesma divisão train/test
```

### 8.5 Avaliação e Comparação

`ml/evaluate.py`

| Métrica | Hard-Code | Sklearn | Baseline |
|---------|-----------|---------|----------|
| Accuracy | X | X | X |
| Precision (macro) | X | X | X |
| Recall (macro) | X | X | X |
| F1-Score (macro) | X | X | X |
| Matriz de confusão | X | X | X |
| Tempo de treino | X | X | — |
| Tempo de predição | X | X | — |

Discussão no relatório:
- Os resultados são iguais/similares? Por quê?
- Onde o hard-code diverge do sklearn?
- Qual o impacto de adicionar features de texto vs só estruturadas?

---

## 9. Dashboard — Metabase

### Página 1 — Visão Geral

- **KPIs:** Total de vendas, Rating médio, % Reviews negativas (<3), Total de produtos
- **Gráfico de barras:** Média de rating por categoria
- **Linha:** Evolução do rating médio (se houver data)
- **Tabela:** Top 10 produtos com pior rating

### Página 2 — Análise de Sentimento (NLP)

- **Nuvem de palavras:** Top palavras em reviews positivas (4-5) vs negativas (1-2)
- **Histograma:** Distribuição de `polarity` por rating
- **Barras empilhadas:** `contains_complaint` vs `contains_praise` por categoria
- **Tabela:** Reviews com maior dissonância (ex: rating 5 mas polaridade negativa)

### Página 3 — Análise Visual (Imagem)

- **Tabela:** Produtos com `blur_score` alto (imagem ruim) e seu rating médio
- **Scatter plot:** `brightness_mean` vs `rating` (imagens escuras têm pior nota?)
- **Barras:** Cor dominante mais frequente por categoria

### Página 4 — Resultados do Modelo ML

- **Matriz de confusão** (heatmap)
- **Tabela de métricas:** Accuracy, Precision, Recall, F1 por classe
- **Comparativo:** Hard-code vs Sklearn — gráfico de barras lado a lado
- **Top features:** Palavras mais importantes para cada classe de rating

### Filtros Globais

- Período (se disponível)
- Categoria do produto
- Faixa de preço
- Faixa de desconto
- Rating

---

## 10. Airflow DAG

`dags/etl_pipeline.py`

```python
# DAG: etl_pipeline
# Schedule: @daily ou manual
# Tasks: 8 sequenciais

download_task >> load_to_s3_task >> process_structured_task
process_structured_task >> extract_text_features_task
process_structured_task >> extract_image_features_task
[extract_text_features_task, extract_image_features_task] >> merge_features_task
merge_features_task >> dbt_run_task >> dbt_test_task >> ml_train_evaluate_task
```

Cada task usa `PythonOperator` ou `BashOperator` chamando os scripts Python.

---

## 11. CloudFormation — Serviços AWS

`infra/cloudformation.yaml`

| Recurso AWS | Propósito | Tipo de recurso |
|-------------|-----------|-----------------|
| **S3 Bucket** | Armazenamento raw/processed/images | `AWS::S3::Bucket` |
| **EC2 Instance** | Airflow (t3.medium) | `AWS::EC2::Instance` |
| **ECS Cluster + Task** | dbt + scripts Python | `AWS::ECS::Cluster`, `AWS::ECS::TaskDefinition` |
| **Redshift Cluster** | Data Warehouse (substituto Snowflake) | `AWS::Redshift::Cluster` |
| **SageMaker Notebook** | Treinamento do modelo ML | `AWS::SageMaker::NotebookInstance` |
| **QuickSight** | Dashboard (substituto Metabase) | (manual, sem CF resource nativo) |
| **CloudWatch Logs** | Monitoramento | `AWS::Logs::LogGroup` |
| **IAM Roles** | Permissões entre serviços | `AWS::IAM::Role` |
| **VPC + Subnets** | Rede | `AWS::EC2::VPC`, `AWS::EC2::Subnet` |
| **Security Groups** | Firewall | `AWS::EC2::SecurityGroup` |

---

## 12. Comandos do Makefile

```makefile
# Docker
make up          # docker compose up -d
make down        # docker compose down
make logs        # docker compose logs -f

# Pipeline (via Airflow CLI no container)
make pipeline    # Trigger da DAG manualmente

# dbt (dentro do container)
make dbt-run     # dbt run
make dbt-test    # dbt test
make dbt-docs    # dbt docs generate && dbt docs serve

# ML
make ml-train    # Roda train.py (hard-code + sklearn + evaluate)

# Testes
make test        # pytest tests/

# Comandos individuais
make ingest      # Só download + upload pro S3
make process     # Só processamento + NLP + CV
make dashboard   # Mostra URL do Metabase
```

---

## 13. Ordem de Desenvolvimento (Cronograma)

| Semana | Etapas | O que entregar |
|--------|--------|----------------|
| **Semana 1** | Estrutura inicial | `docker-compose.yml` funcional, Postgres + MinIO + Airflow + Metabase rodando |
| **Semana 2** | Datasets + Ingestão | Datasets baixados, imagens baixadas, scripts de upload no S3 prontos |
| **Semana 3** | Processamento | `process_structured.py` + `extract_text_features.py` + `extract_image_features.py` + `merge_features.py` prontos e testados |
| **Semana 4** | dbt | Projeto dbt completo: staging, dimensions, facts, marts + 4 testes passando |
| **Semana 5** | Airflow | DAG completa orquestrando todas as etapas |
| **Semana 6** | Machine Learning | Hard-code Naive Bayes + sklearn + avaliação comparativa |
| **Semana 7** | Dashboard | Metabase configurado, 4 páginas do dashboard prontas |
| **Semana 8** | Infra + Entrega | CloudFormation YAML, diagrama, relatório, apresentação, README final |

---

## 14. Checklist de Requisitos do PDF

### 4.2 — Conjuntos de dados

- [x] Pelo menos 1 fonte de dados estruturados → `amazon_sales.csv` (produtos, preços, categorias)
- [x] Pelo menos 1 fonte de dados não estruturados → texto das reviews + imagens de produtos
- [x] Dados suficientes para treino e teste → ~1400 produtos + ~35k reviews + ~500-1000 imagens
- [x] Documentação da origem e campos → neste arquivo e no README

### 4.3 — Processamento e Extração de Atributos

- [x] Limpeza de dados estruturados → `process_structured.py`
- [x] Extração de features de texto (NLP) → `extract_text_features.py` (VADER, TF-IDF, metadados)
- [x] Extração de features de imagem (CV) → `extract_image_features.py` (cores, nitidez, bordas, textura)
- [x] Merge final → `merge_features.py`

### 4.4 — Pipeline ELT (Airflow + dbt + Snowflake)

- [x] DAG funcional no Airflow → `dags/etl_pipeline.py`
- [x] Carga no Snowflake (Postgres local) → dbt + profiles
- [x] Modelos staging, dimensions, facts → 8 modelos em 4 camadas
- [x] Pelo menos 2 testes dbt → 4 testes (not_null, unique, accepted_values)
- [x] Documentação dos modelos → `schema.yml`
- [x] Tabela final para ML + fatos para dashboard → `ml_features` + `fact_reviews` + `fact_sales`

### 4.5 — Armazenamento e Processamento em Nuvem

- [x] Pelo menos 1 serviço AWS → S3 (usado em prod)
- [x] Organização em camadas → raw/, processed/, images/
- [x] CloudFormation YAML → `infra/cloudformation.yaml`
- [x] Diagrama arquitetural → `infra/architecture_diagram.png`

### 4.6 — Aprendizagem de Máquina

- [x] Tarefa definida → Classificação multiclasse (1-5 estrelas)
- [x] Baseline → Classe majoritária + modelo só com estruturados
- [x] Hard-code → `naive_bayes_hardcode.py` (Naive Bayes do zero)
- [x] Biblioteca Python → `naive_bayes_sklearn.py` (MultinomialNB)
- [x] Comparação → `evaluate.py` com métricas lado a lado
- [x] Métricas → Accuracy, Precision, Recall, F1, Matriz de Confusão

### 4.7 — Visualização (Metabase)

- [x] Indicadores principais → KPIs de vendas e satisfação
- [x] Visualização dos dados tratados → Distribuições, análises
- [x] Visualização dos resultados do modelo → Matriz de confusão, métricas
- [x] Pelo menos 1 filtro → Categoria, preço, desconto, rating

### 7 — Entregáveis

- [x] Repositório Git → README, scripts, dbt, DAGs, ML, CloudFormation
- [x] Apresentação → Todos os 4 integrantes
- [x] Relatório → Documentação completa

---

## 15. Tecnologias e Bibliotecas

### Python (requirements.txt)

```
# Data
pandas==2.2.2
numpy==1.26.4

# NLP
vaderSentiment==3.3.2
scikit-learn==1.5.1
textstat==0.7.4

# Computer Vision
opencv-python==4.10.0
Pillow==10.4.0
scikit-image==0.24.0

# Cloud
boto3==1.34.0

# Airflow
apache-airflow==2.9.0
apache-airflow-providers-amazon==8.20.0
apache-airflow-providers-postgres==5.10.0

# dbt
dbt-core==1.8.0
dbt-postgres==1.8.0
dbt-snowflake==1.8.0

# Kaggle download
kagglehub==0.3.0

# Utils
python-dotenv==1.0.1
pyyaml==6.0.1
matplotlib==3.9.0
seaborn==0.13.2
tqdm==4.66.0
```

### Docker Images

- `postgres:16-alpine`
- `minio/minio:latest`
- `apache/airflow:2.9.0`
- `metabase/metabase:latest`
- `python:3.11-slim` (Dockerfile customizado com requirements.txt)

---

## 16. Instruções de Uso Rápido

```bash
# 1. Clonar repositório
git clone <repo>
cd projeto-final

# 2. Configurar variáveis
cp .env.example .env.local
# Editar .env.local se necessário

# 3. Subir ambiente
make up

# 4. Baixar datasets
make ingest

# 5. Rodar pipeline completo
make pipeline

# 6. Ver resultados
# Metabase: http://localhost:3000
# Airflow:   http://localhost:8080
# MinIO:     http://localhost:9001

# 7. Trocar para produção (S3 + Snowflake)
cp .env.prod .env
make pipeline
```
