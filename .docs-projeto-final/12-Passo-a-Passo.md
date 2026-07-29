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

[[🏠 Home|Voltar ao índice]]

Este guia mapeia cada requisito do PDF para ações concretas de implementação, organizadas pelas 8 semanas do [[08-Cronograma]].

---

> [!important] Pré-requisitos
> - [ ] Python 3.11+ instalado
> - [ ] Docker Desktop rodando
> - [ ] Git configurado
> - [ ] Conta Kaggle com API key (`~/.kaggle/kaggle.json`)

---

## Semana 1 — Estrutura Docker

**PDF: 4.4 (Pipeline), 4.5 (Nuvem)**

### 1.1 Criar `docker-compose.yml`

Serviços necessários:

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000", "9001:9001"]
    volumes: [miniodata:/data]

  airflow-init:
    image: apache/airflow:2.9.0
    entrypoint: /bin/bash
    command: -c "airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com"
    environment:
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow

  airflow-webserver:
    image: apache/airflow:2.9.0
    depends_on: [postgres, airflow-init]
    ports: ["8080:8080"]
    environment:
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
    command: webserver
    volumes: [./dags:/opt/airflow/dags, ./:/opt/airflow/project]

  airflow-scheduler:
    image: apache/airflow:2.9.0
    depends_on: [postgres, airflow-init]
    environment:
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
    command: scheduler
    volumes: [./dags:/opt/airflow/dags, ./:/opt/airflow/project]

  metabase:
    image: metabase/metabase:latest
    ports: ["3000:3000"]
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: airflow
      MB_DB_PORT: 5432
      MB_DB_USER: airflow
      MB_DB_PASS: airflow
      MB_DB_HOST: postgres
    depends_on: [postgres]

volumes:
  pgdata:
  miniodata:
```

### 1.2 Criar `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

### 1.3 Criar `requirements.txt`

Ver [[11-Comandos]] para a lista completa de bibliotecas.

### 1.4 Criar `.env.example`

```bash
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
DB_TYPE=postgres
DB_HOST=postgres
DB_USER=airflow
DB_PASS=airflow
DB_NAME=airflow
```

### 1.5 Criar `Makefile`

Ver [[11-Comandos#Makefile]] para os comandos completos.

### 1.6 Verificar

```bash
make up
# Esperar ~30s e acessar:
# Airflow:  http://localhost:8080 (admin/admin)
# Metabase: http://localhost:3000
# MinIO:    http://localhost:9001 (minioadmin/minioadmin)
```

> [!tip] Se algum serviço falhar
> Ver logs com `docker compose logs <servico>`.

---

## Semana 2 — Datasets + Ingestão

**PDF: 4.2 (Conjuntos de dados)**

### 2.1 Criar `ingestion/download_dataset.py`

```python
"""Baixa datasets do Kaggle para data/raw/"""
import kagglehub
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Dataset 1: Amazon Sales (~1400 produtos)
path1 = kagglehub.dataset_download("karkavelrajaj/amazon-sales-dataset")
df1 = pd.read_csv(Path(path1) / "amazon.csv")
df1.to_csv(RAW_DIR / "amazon_sales.csv", index=False)
print(f"Dataset 1 salvo: {len(df1)} linhas")

# Dataset 2: Amazon Reviews (~35k reviews)
path2 = kagglehub.dataset_download("arhamrumi/amazon-product-reviews")
df2 = pd.read_csv(Path(path2) / "Reviews.csv")
df2.to_csv(RAW_DIR / "amazon_reviews.csv", index=False)
print(f"Dataset 2 salvo: {len(df2)} linhas")
```

### 2.2 Criar `ingestion/load_raw_to_s3.py`

```python
"""Upload para MinIO/S3 usando boto3"""
import boto3
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
)

BUCKET = "raw"

# Criar bucket se não existir
try:
    s3.create_bucket(Bucket=BUCKET)
except:
    pass

# Upload CSVs
for csv_file in Path("data/raw").glob("*.csv"):
    s3.upload_file(str(csv_file), BUCKET, f"{csv_file.name}")
    print(f"Upload: {csv_file.name}")

# Download e upload de imagens
import pandas as pd
df = pd.read_csv("data/raw/amazon_sales.csv")
image_links = df["img_link"].dropna().unique()[:1000]  # limite 1000

for i, url in enumerate(image_links):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            ext = url.split(".")[-1].split("?")[0][:4]
            key = f"images/{i:06d}.{ext}"
            s3.put_object(Bucket=BUCKET, Key=key, Body=resp.content)
            if (i + 1) % 100 == 0:
                print(f"Imagens: {i+1}/{len(image_links)}")
    except:
        pass
```

### 2.3 Verificar

```bash
make ingest
# Verificar no MinIO: http://localhost:9001 → bucket "raw"
```

---

## Semana 3 — Processamento e Features

**PDF: 4.3 (Processamento e extração de atributos)**

### 3.1 Criar `processing/process_structured.py`

```python
"""Limpeza de dados estruturados"""
import pandas as pd
import numpy as np

def process_structured(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Remover símbolos monetários e converter
    df["discounted_price"] = df["discounted_price"].str.replace("₹", "").str.replace(",", "").astype(float)
    df["actual_price"] = df["actual_price"].str.replace("₹", "").str.replace(",", "").astype(float)
    
    # 2. Converter percentual
    df["discount_percentage"] = df["discount_percentage"].str.replace("%", "").astype(float) / 100
    
    # 3. Remover duplicatas
    df = df.drop_duplicates(subset=["product_name"])
    
    # 4. Tratar nulos
    df = df.dropna(subset=["rating", "product_name"])
    df["rating"] = df["rating"].astype(int)
    df["rating_count"] = df["rating_count"].str.replace(",", "").astype(float).astype(int)
    
    # 5. Features derivadas
    df["log_price"] = np.log1p(df["actual_price"])
    df["log_rating_count"] = np.log1p(df["rating_count"])
    df["price_difference"] = df["actual_price"] - df["discounted_price"]
    
    # 6. Bucket de desconto
    df["discount_bucket"] = pd.cut(
        df["discount_percentage"],
        bins=[0, 0.2, 0.5, 1.0],
        labels=["low", "medium", "high"]
    )
    
    return df
```

### 3.2 Criar `processing/extract_text_features.py`

```python
"""Extração de features de NLP (~217 features)"""
import pandas as pd
import numpy as np
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
import textstat

def extract_text_features(df: pd.DataFrame) -> pd.DataFrame:
    analyzer = SentimentIntensityAnalyzer()
    
    # Combinar título + conteúdo da review
    df["full_review"] = df["review_title"].fillna("") + " " + df["review_content"].fillna("")
    
    # --- Metadados (4) ---
    df["review_length"] = df["full_review"].str.len()
    df["word_count"] = df["full_review"].str.split().str.len()
    df["avg_word_length"] = df["review_length"] / df["word_count"].replace(0, 1)
    df["sentence_count"] = df["full_review"].str.count(r"[.!?]+")
    
    # --- Estilo (4) ---
    df["uppercase_ratio"] = df["full_review"].apply(
        lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1)
    )
    df["exclamation_count"] = df["full_review"].str.count("!")
    df["question_count"] = df["full_review"].str.count(r"\?")
    df["numeric_ratio"] = df["full_review"].apply(
        lambda x: sum(1 for c in x if c.isdigit()) / max(len(x), 1)
    )
    
    # --- Sentimento VADER (3) ---
    sentiment = df["full_review"].apply(lambda x: analyzer.polarity_scores(x))
    df["polarity"] = sentiment.apply(lambda x: x["compound"])
    df["subjectivity"] = sentiment.apply(lambda x: x["pos"] + x["neg"])
    df["compound_score"] = sentiment.apply(lambda x: x["compound"])
    
    # --- TF-IDF (200) ---
    vectorizer = TfidfVectorizer(
        max_features=200, ngram_range=(1, 2),
        stop_words="english", min_df=2
    )
    tfidf_matrix = vectorizer.fit_transform(df["full_review"])
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=[f"tfidf_{w}" for w in vectorizer.get_feature_names_out()]
    )
    df = pd.concat([df, tfidf_df], axis=1)
    
    # --- Regex Custom (4) ---
    complaints = r"\b(bad|terrible|awful|poor|worst|broke|broken|defect|return|refund|disappointed|waste)\b"
    praise = r"\b(great|excellent|amazing|love|best|perfect|fantastic|wonderful|recommend)\b"
    price = r"\b(price|cheap|expensive|cost|worth|value|money)\b"
    delivery = r"\b(delivery|shipping|arrived|package|fast|slow|days|quick)\b"
    
    df["contains_complaint"] = df["full_review"].str.contains(complaints, case=False).astype(int)
    df["contains_praise"] = df["full_review"].str.contains(praise, case=False).astype(int)
    df["contains_price_mention"] = df["full_review"].str.contains(price, case=False).astype(int)
    df["contains_delivery_mention"] = df["full_review"].str.contains(delivery, case=False).astype(int)
    
    # --- Legibilidade (2) ---
    df["flesch_reading_ease"] = df["full_review"].apply(textstat.flesch_reading_ease)
    df["complex_word_ratio"] = df["full_review"].apply(
        lambda x: sum(1 for w in x.split() if textstat.textstat.syllable_count(w) >= 3) / max(len(x.split()), 1)
    )
    
    return df
```

### 3.3 Criar `processing/extract_image_features.py`

```python
"""Extração de features de imagem (~28 features)"""
import cv2
import numpy as np
from PIL import Image
from skimage.feature import graycomatrix, graycoprops
import pandas as pd

def extract_image_features(image_path: str) -> dict:
    features = {}
    
    # --- Dimensões (5) ---
    img = Image.open(image_path)
    w, h = img.size
    features["width"] = w
    features["height"] = h
    features["aspect_ratio"] = w / h
    import os
    features["file_size_kb"] = os.path.getsize(image_path) / 1024
    features["format"] = img.format
    
    # --- Converter para OpenCV ---
    cv_img = cv2.imread(image_path)
    if cv_img is None:
        return features
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    
    # --- Brilho e Saturação (3) ---
    features["brightness_mean"] = np.mean(hsv[:, :, 2])
    features["saturation_mean"] = np.mean(hsv[:, :, 1])
    features["colorfulness_score"] = np.std(hsv[:, :, 0]) + np.std(hsv[:, :, 1])
    
    # --- Cores dominantes (9) ---
    pixels = cv_img_rgb.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(pixels, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = centers.astype(int)
    for i in range(3):
        features[f"dominant_color_{i+1}_r"] = centers[i][0] / 255.0
        features[f"dominant_color_{i+1}_g"] = centers[i][1] / 255.0
        features[f"dominant_color_{i+1}_b"] = centers[i][2] / 255.0
    
    # --- Nitidez (1) ---
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    features["blur_score"] = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # --- Complexidade Visual (2) ---
    edges = cv2.Canny(gray, 100, 200)
    features["edge_density"] = np.sum(edges > 0) / (w * h)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)
    features["corner_count"] = np.sum(dst > 0.01 * dst.max())
    
    # --- Textura (2) ---
    glcm = graycomatrix(gray, [1], [0], 256, symmetric=True, normed=True)
    features["entropy"] = -np.sum(glcm * np.log2(glcm + 1e-10))
    features["contrast"] = graycoprops(glcm, "contrast")[0, 0]
    
    # --- Histograma (6) ---
    for i, c in enumerate(["r", "g", "b"]):
        hist = cv2.calcHist([cv_img_rgb], [i], None, [256], [0, 256])
        features[f"hist_mean_{c}"] = np.mean(hist)
        features[f"hist_std_{c}"] = np.std(hist)
    
    return features
```

### 3.4 Criar `processing/merge_features.py`

```python
"""JOIN de todas as features em uma tabela final"""
import pandas as pd

def merge_all(products, reviews_features, images_features):
    merged = products.merge(reviews_features, on="product_id", how="left")
    merged = merged.merge(images_features, on="product_id", how="left")
    merged.to_csv("data/processed/ml_features.csv", index=False)
    return merged
```

---

## Semana 4 — Projeto dbt

**PDF: 4.4 (Pipeline ELT — dbt)**

### 4.1 Inicializar projeto dbt

```bash
pip install dbt-postgres
dbt init dbt_project
cd dbt_project
```

### 4.2 Configurar `profiles.yml`

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
```

### 4.3 Criar modelos

Criar os 8 arquivos SQL conforme [[05-Modelagem-dbt#Modelos por Camada]].

### 4.4 Criar `schema.yml` com testes

Ver [[05-Modelagem-dbt#Testes dbt  schema-yml]].

### 4.5 Verificar

```bash
make dbt-run
make dbt-test
# Todos os testes devem passar (0 falhas)
```

---

## Semana 5 — Airflow DAG

**PDF: 4.4 (Pipeline ELT — Airflow)**

### 5.1 Criar `dags/etl_pipeline.py`

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "grupo",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_pipeline",
    default_args=default_args,
    description="Pipeline ELT completo",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["projeto-final"],
) as dag:
    
    t1 = PythonOperator(
        task_id="download_datasets",
        python_callable=lambda: __import__("ingestion.download_dataset").download_dataset.main(),
    )
    t2 = PythonOperator(
        task_id="load_to_s3",
        python_callable=lambda: __import__("ingestion.load_raw_to_s3").load_raw_to_s3.main(),
    )
    t3 = PythonOperator(
        task_id="process_structured",
        python_callable=lambda: __import__("processing.process_structured").process_structured.main(),
    )
    t4a = PythonOperator(
        task_id="extract_text_features",
        python_callable=lambda: __import__("processing.extract_text_features").extract_text_features.main(),
    )
    t4b = PythonOperator(
        task_id="extract_image_features",
        python_callable=lambda: __import__("processing.extract_image_features").extract_image_features.main(),
    )
    t5 = PythonOperator(
        task_id="merge_features",
        python_callable=lambda: __import__("processing.merge_features").merge_features.main(),
    )
    t6 = BashOperator(task_id="dbt_run", bash_command="cd dbt_project && dbt run")
    t7 = BashOperator(task_id="dbt_test", bash_command="cd dbt_project && dbt test")
    t8 = BashOperator(task_id="ml_train", bash_command="python ml/train.py")
    
    t1 >> t2 >> t3
    t3 >> [t4a, t4b] >> t5
    t5 >> t6 >> t7 >> t8
```

### 5.2 Verificar

Acessar http://localhost:8080, ativar a DAG e disparar manualmente.

---

## Semana 6 — Machine Learning

**PDF: 4.6 (Aprendizagem de Máquina)**

### 6.1 Hard-Code Naive Bayes

**Arquivo:** `ml/hard_code/naive_bayes_hardcode.py`

Implementar seguindo o algoritmo descrito em [[06-Machine-Learning#Naive Bayes Hard-Code]].

### 6.2 Sklearn

**Arquivo:** `ml/sklearn/naive_bayes_sklearn.py`

```python
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

df = pd.read_csv("data/processed/ml_features.csv")
X = df.drop(columns=["rating", "product_id", "review_id"])
y = df["rating"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = MultinomialNB()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))
```

### 6.3 Avaliação

**Arquivo:** `ml/evaluate.py`

Produzir tabela comparativa conforme [[06-Machine-Learning#Avaliação e Comparação]].

---

## Semana 7 — Dashboard Metabase

**PDF: 4.7 (Visualização da Informação)**

### 7.1 Conectar Metabase ao banco

1. Acessar http://localhost:3000
2. Configurar conexão PostgreSQL (host: `postgres`, db: `airflow`)
3. Criar as 4 páginas conforme [[07-Dashboard]]

### 7.2 Criar queries

Documentar em `dashboard/metabase_questions.md`.

---

## Semana 8 — Infra AWS + Entrega Final

**PDF: 4.5 (Nuvem), 7 (Entregáveis)**

### 8.1 CloudFormation

Criar `infra/cloudformation.yaml` seguindo [[10-Infra-AWS]].

### 8.2 Diagrama arquitetural

Gerar `infra/architecture_diagram.png` com todos os componentes.

### 8.3 Relatório

Preencher `report/relatorio.md` com todos os tópicos obrigatórios do PDF.

### 8.4 Apresentação

Criar `report/apresentacao.pptx` para defesa oral.

### 8.5 README final

Atualizar `README.md` com:
- Descrição do projeto
- Como rodar
- Tecnologias
- Estrutura de diretórios
- Resultados

---

## Mapeamento PDF → Entregas

| Seção PDF | Requisito | Onde entregar |
|-----------|-----------|---------------|
| 4.1 | Definição do problema | [[01-Plano-Geral]], `README.md`, relatório |
| 4.2 | Conjuntos de dados | [[02-Datasets]], `data/raw/`, relatório |
| 4.3 | Processamento e features | `processing/*.py`, relatório |
| 4.4 | Pipeline ELT | `dags/etl_pipeline.py`, `dbt_project/`, relatório |
| 4.5 | Nuvem AWS | `infra/cloudformation.yaml`, `infra/architecture_diagram.png`, relatório |
| 4.6 | ML | `ml/`, relatório |
| 4.7 | Dashboard | `dashboard/`, Metabase, relatório |
| 5 | Avaliação | `ml/evaluate.py`, relatório |
| 7.1 | Repositório | Git + README |
| 7.2 | Apresentação | `report/apresentacao.pptx` |
| 7.3 | Relatório | `report/relatorio.md` |

---

> [!success] Sequência recomendada
> Comece agora pela **Semana 1**. Cada semana constrói sobre a anterior. O [[09-Checklist-Entrega]] tem os 32 itens rastreáveis.

## Relacionado

- [[08-Cronograma]] — Cronograma detalhado com checklists
- [[09-Checklist-Entrega]] — 32 requisitos rastreáveis
- [[11-Comandos]] — Referência rápida de comandos
- [[01-Plano-Geral]] — Visão geral do problema
