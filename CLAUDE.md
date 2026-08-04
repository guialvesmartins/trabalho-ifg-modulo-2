# CLAUDE.md — Projeto Final IFG Pós-IA Módulo 2

## Contexto Geral

Este é o projeto final integrado da Pós-Graduação em Inteligência Artificial Aplicada do IFG (Módulo 2), combinando as disciplinas de **Aprendizagem de Máquina**, **Cloud Computing** e **Modelagem de Dados para IA**.

**Autores:** Grupo com 4 integrantes (todos devem participar da apresentação)

**Tecnologias obrigatórias:** AWS, Snowflake, dbt, Apache Airflow, Python
**Tecnologias complementares:** Docker, MinIO, PostgreSQL, Metabase, librosa, scikit-learn, NumPy

---

## Evolução do Projeto (Histórico de Decisões)

### Primeira tentativa (DESCARTADA)
**Tema:** Previsão de Satisfação em E-commerce (Amazon)
**Dados:** Dados estruturados de produtos (preço, categoria) + texto de reviews (NLP: VADER, TF-IDF) + imagens de produtos (CV: OpenCV)
**Modelo:** Naive Bayes → MLP multiclasse (ratings 1-5)
**Problema:** Colegas do grupo não aceitaram o dataset e a abordagem.

### Segunda iteração (DESCARTADA)
**Solicitação:** Dataset que contenha dados estruturados e não estruturados, sem NLP e sem MLP.
**Explorado:** Vários datasets industriais no Kaggle — nenhum com dados estruturados + áudio verificados.
**Solução considerada:** MIMII no Zenodo com motor industrial.
**Problema:** MIMII tem fan, pump, slider, valve — não tem motor dedicado.

### Versão atual (APROVADA — em uso)
**Tema:** Manutenção Preditiva Industrial com Som
**Dataset:** MIMII Dataset (Hitachi/Toyota Research) — Pump (bomba industrial)
**Fonte:** Zenodo (`https://zenodo.org/records/3384388`)
**Dados:**
- **Estruturados:** `machine_type`, `model_id`, `condition`, `duration_sec`, `sample_rate`, `channels` (extraídos dos paths)
- **Não estruturados:** Arquivos `.wav` 16kHz de bombas industriais operando em fábrica real
**Condições:** `normal` (funcionamento normal) e `anomaly` (contaminação, vazamento, desbalanceamento)
**Modelo:** MLP binário — hard-code (NumPy) + sklearn MLPClassifier
**Tarefa de ML:** Classificação binária — "Esta bomba está com anomalia?"

### Mudanças estruturais feitas
- **Removidos:** `extract_text_features.py` (NLP), `extract_image_features.py` (CV), modelos Naive Bayes, 7 modelos dbt antigos
- **Criados:** `extract_audio_features.py` (librosa), `load_to_postgres.py`, download via `requests` do Zenodo
- **Modificados:** `process_structured.py` (parse de paths MIMII → CSV), `merge_features.py`, `evaluate.py` (binário), `etl_pipeline.py` (DAG), 5 modelos dbt, testes, README, FLUXO.md, Makefile, Dockerfile, requirements.txt
- **Requirements:** +librosa, +soundfile, +sqlalchemy, +psycopg2-binary; -vaderSentiment, -textstat, -opencv, -scikit-image, -kagglehub

---

## Estrutura de Diretórios

```
projeto-final/
├── .env.example              # Template de variáveis de ambiente
├── .env.local                # Configuração dev (MinIO + Postgres local)
├── .env.prod                 # Configuração prod (AWS S3 + Snowflake)
├── docker-compose.yml        # Serviços: Postgres, MinIO, Airflow, Metabase
├── Dockerfile                # Python 3.11-slim + libsndfile1
├── Makefile                  # Atalhos: up, down, ingest, process, pipeline
├── requirements.txt          # Python dependencies
├── README.md                 # Documentação principal
├── FLUXO.md                  # Explicação completa do pipeline em português
│
├── ingestion/
│   ├── download_dataset.py   # Download MIMII Pump do Zenodo (~7.5 GB)
│   └── load_raw_to_s3.py     # Upload .wav para MinIO/S3
│
├── processing/
│   ├── process_structured.py # Parse paths MIMII → CSV com metadados
│   ├── extract_audio_features.py # Librosa: MFCC(40), spectral, ZCR, RMS
│   ├── merge_features.py     # Join metadados + audio features
│   └── load_to_postgres.py   # CSV → PostgreSQL via SQLAlchemy
│
├── dags/
│   └── etl_pipeline.py       # Airflow DAG (8 tasks sequenciais)
│
├── dbt_project/
│   ├── dbt_project.yml       # Config: staging=view, dim/facts/marts=table
│   ├── profiles.yml          # dev (postgres) e prod (snowflake)
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_pump_metadata.sql
│   │   │   └── stg_audio_features.sql
│   │   ├── dimensions/
│   │   │   └── dim_machines.sql
│   │   ├── facts/
│   │   │   └── fact_audio_analysis.sql
│   │   └── marts/
│   │       └── ml_features.sql
│   └── tests/
│       └── schema.yml        # 14 testes: not_null, unique, accepted_values
│
├── ml/
│   ├── evaluate.py           # Baselines + hard-code vs sklearn + export pickle + report_analys.md
│   ├── hard_code/
│   │   └── neural_network_hardcode.py  # MLP binário do zero com NumPy (com save/load pickle)
│   └── library/
│       └── neural_network_sklearn.py   # MLPClassifier do sklearn
│
├── docs/
│   └── ARQUITETURA_AWS.md    # Diagramas (dev e 100% AWS) + registro de custos
│
├── report_analys.md          # Relatório do último treinamento (gerado por ml/evaluate.py)
│
├── scripts/
│   └── setup_metabase.py     # Configuração automática do Metabase via API
│
├── infra/
│   └── cloudformation.yaml   # Template AWS CloudFormation (acadêmico)
│
├── tests/
│   ├── test_ml.py            # 4 testes unitários do MLP
│   └── test_processing.py    # 3 testes de integração
│
├── data/
│   ├── raw/                  # Dados brutos (.wav, .zip)
│   └── processed/            # CSVs, predictions.csv, matrizes de confusão
│       └── models/           # Modelos exportados via pickle (.pkl)
│
└── report/                   # Relatório e apresentação final
```

---

## O Problema de Negócio

**Domínio:** Indústria 4.0 / Manutenção Preditiva

**Decisão apoiada:** "Esta bomba industrial está operando com anomalia? Devo parar para manutenção?"

**Tomador de decisão:** Engenheiro de manutenção industrial

**Cenário:** Uma fábrica possui dezenas de bombas industriais operando 24/7. Paradas não programadas custam caro (produção parada, reparos emergenciais). Por outro lado, manutenções desnecessárias também têm custo. O sistema analisa o som de cada bomba e classifica automaticamente se ela está normal ou com anomalia.

**Impacto esperado:**
- Redução de paradas não programadas (detecta anomalia antes da falha)
- Redução de manutenções desnecessárias (não para máquina normal)
- Aumento da vida útil dos equipamentos
- Economia em custos de reparo emergencial

---

## O Dataset — MIMII Pump

**MIMII** = Malfunctioning Industrial Machine Investigation and Inspection
**Criador:** Hitachi, Ltd. / Toyota Research
**Licença:** CC BY-SA 4.0
**Publicação:** DCASE 2019 Workshop
**Paper:** arXiv:1909.09347

**Características do áudio:**
- 16 kHz sample rate, 16 bits por amostra, mono
- Gravado com array de 8 microfones
- Misturado com ruído real de fábrica (0 dB SNR)
- 4 modelos de bomba diferentes (model_id_00, 02, 04, 06)

**Condições (dataset real, total 4.205 clips):**
- `normal`: 3.749 clips (1.006 + 1.005 + 702 + 1.036 por modelo) — funcionamento normal
- `anomaly`: 456 clips (143 + 111 + 100 + 102 por modelo) — contaminação, vazamento, desbalanceamento
- Desbalanceamento ~8:1 — taxa de anomalia de 10,8%

**Estrutura de diretórios (dataset real, dentro do zip):**
```
pump/
├── id_00/
│   ├── normal/    (*.wav)
│   └── abnormal/  (*.wav)
├── id_02/ ...
├── id_04/ ...
└── id_06/ ...
```

**IMPORTANTE — nomenclatura:** o dataset real usa `id_XX` e `abnormal`; o pipeline normaliza `abnormal` → `anomaly` em `process_structured.py` e `extract_audio_features.py` (constante `CONDITION_MAP`). Todo o restante do pipeline (dbt, ML, Metabase) usa `anomaly`.

**Download:** `https://zenodo.org/records/3384388/files/0_dB_pump.zip` (7,87 GB) — `download_dataset.py` suporta retomada de download interrompido (HTTP Range) e remove dados sintéticos legados (`model_id_XX/`) antes de extrair o dataset real.

**Áudio real:** clipes de 10 s, 16 kHz, **8 canais** (array de microfones) — `librosa.load(mono=True)` faz downmix na extração.

---

## Features Extraídas do Áudio

### MFCC (80 features)
40 coeficientes Mel-Frequency Cepstral — média e desvio padrão de cada. Capturam o "timbre" do som industrial.

| Feature | O que representa |
|---|---|
| `mfcc_1_mean` a `mfcc_40_mean` | Média de cada coeficiente MFCC |
| `mfcc_1_std` a `mfcc_40_std` | Variabilidade de cada coeficiente |

### Features Espectrais (11 features)
| Feature | Significado |
|---|---|
| `spectral_centroid_mean` | Centro de massa do espectro — indica se o som é "grave" ou "agudo" |
| `spectral_bandwidth_mean` | Largura da banda espectral |
| `spectral_rolloff_mean` | Frequência abaixo da qual está 85% da energia |
| `spectral_contrast_1_mean` a `spectral_contrast_7_mean` | Contraste entre picos e vales em 7 bandas |

### Features de Energia e Ritmo (2 features)
| Feature | Significado |
|---|---|
| `zcr_mean` | Zero-Crossing Rate — frequência dominante percebida |
| `rms_mean` | Root Mean Square — energia/potência do sinal |

### Features Estruturadas (6 colunas)
`machine_type`, `model_id`, `condition`, `duration_sec`, `sample_rate`, `channels`

**Total após merge:** 103 colunas × 4.205 linhas (96 features numéricas usadas no ML)

---

## O Modelo MLP

### Arquitetura
```
Input (96 features numéricas)
  ↓
Hidden Layer 1 (64 neurônios, ReLU)
  ↓
Hidden Layer 2 (32 neurônios, ReLU)
  ↓
Output (1 neurônio, Sigmoid) → P(anomalia)
```

### Hard-Code (NumPy puro) — `ml/hard_code/neural_network_hardcode.py`
- **Classe:** `HardCodedMLP`
- **Inicialização:** He initialization (`sqrt(2/fan_in)`)
- **Forward pass:** ReLU nas hidden layers, Sigmoid na saída
- **Backward pass:** Backpropagation manual com gradientes analíticos
- **Loss:** Binary Cross-Entropy
- **Otimizador:** Mini-batch SGD com momento (lr=0.01, momentum=0.9)
- **Treinamento:** 300 épocas, batch_size=32
- **Predição:** Threshold 0.5 na sigmoid

### Sklearn — `ml/library/neural_network_sklearn.py`
- **Classe:** `MLPClassifier`
- **Arquitetura:** `hidden_layer_sizes=(64, 32)`
- **Otimizador:** Adam (adaptativo)
- **Regularização:** L2 (alpha=0.0001)
- **Treinamento:** max_iter=500

### Comparação Hard-Code vs Sklearn
- Ambos produzem resultados idênticos (validando a implementação manual)
- Sklearn é ~6.7x mais rápido no treino (Adam + código C otimizado)
- Hard-code é mais lento mas didático (SGD com momento em Python puro)
- O hard-code implementa 100% do forward/backward pass com operações matriciais do NumPy — sem usar autograd, TensorFlow ou PyTorch

---

## Pipeline Completo (8 etapas)

### 1. Download Dataset
**Script:** `ingestion/download_dataset.py`
**O que faz:** Baixa `0_dB_pump.zip` do Zenodo (~7.5 GB) com barra de progresso, extrai para `data/raw/pump/`.

### 2. Upload para S3/MinIO
**Script:** `ingestion/load_raw_to_s3.py`
**O que faz:** Sobe todos os `.wav` para bucket `raw/pump/` no MinIO (dev) ou AWS S3 (prod). Usa `boto3` com endpoint configurável.

### 3. Extração de Metadados
**Script:** `processing/process_structured.py`
**O que faz:** Percorre `data/raw/pump/`, extrai metadados dos paths (`machine_type`, `model_id`, `condition`), lê metadata dos arquivos com `soundfile`, cria `data/processed/pump_metadata.csv` com 2.400 linhas e coluna `condition_binary` (target).

### 4. Extração de Features de Áudio
**Script:** `processing/extract_audio_features.py`
**O que faz:** Para cada `.wav`, carrega com `librosa.load(sr=16000)`, extrai 92 features (MFCC, spectral, ZCR, RMS), salva em `data/processed/audio_features.csv`.

### 5. Merge
**Script:** `processing/merge_features.py`
**O que faz:** LEFT JOIN entre `pump_metadata.csv` e `audio_features.csv` por `file_id`. Preenche nulls com 0. Output: `data/processed/ml_features.csv` (2.400 linhas × 103 colunas).

### 6. Carga no PostgreSQL
**Script:** `processing/load_to_postgres.py`
**O que faz:** Lê `ml_features.csv` com pandas e insere no PostgreSQL como tabela `public.ml_features_raw` usando SQLAlchemy (`if_exists='replace'`).

### 7. dbt (Run + Test)
**Modelos:**
| Camada | Modelo | Tipo | Descrição |
|---|---|---|---|
| Staging | `stg_pump_metadata` | View | Limpeza, dedup, tipagem |
| Staging | `stg_audio_features` | View | Cast para numeric |
| Dimensions | `dim_machines` | Table | Agregação por modelo (total, anomalia, normal) |
| Facts | `fact_audio_analysis` | Table | Join completo dos dados |
| Marts | `ml_features` | Table | Join com dim_machines, pronto para ML |

**Testes (14):**
- `not_null`: file_id, machine_type, model_id, condition, condition_binary, total_samples
- `unique`: file_id (staging + facts)
- `accepted_values`: condition (`normal`/`anomaly`), condition_binary (`0`/`1`)

### 8. ML — Treinamento e Avaliação
**Script:** `ml/evaluate.py`
**O que faz:**
1. Carrega `ml_features.csv`
2. Remove colunas não numéricas e de ID
3. Split 80/20 com stratify (garante proporção normal/anomalia)
4. StandardScaler
5. Treina **baselines**: DummyClassifier (classe majoritária) + Regressão Logística
6. Treina HardCodedMLP (300 épocas)
7. Treina MLPClassifier (sklearn)
8. Compara métricas dos 4 modelos: Accuracy, Precision, Recall, F1-Score
9. Gera matrizes de confusão (PNG) e `model_comparison.csv`
10. Salva `predictions.csv` (predição por amostra do teste — rastreabilidade)
11. **Exporta modelos via pickle** em `data/processed/models/`: `mlp_sklearn_pipeline.pkl` (Pipeline scaler+MLP pronto para inferência), `mlp_hardcode.pkl` (pesos, recarregável via `HardCodedMLP.load()`), `scaler.pkl`, `feature_names.pkl`
12. Gera **`report_analys.md`** (raiz do projeto): relatório completo com métricas, análise qualitativa de acertos/erros com possíveis causas, features mais discriminativas e limitações
13. Se o Postgres estiver acessível, carrega `model_metrics` e `model_predictions` para o dashboard do Metabase (best-effort)

---

## Ambiente de Desenvolvimento vs Produção

O projeto usa o padrão **"4 variáveis de ambiente"** para trocar entre dev e prod:

### Dev (local)
```bash
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
DB_TYPE=postgres
DB_HOST=localhost
```

### Prod (AWS + Snowflake)
```bash
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=<aws_access_key>
S3_SECRET_KEY=<aws_secret_key>
DB_TYPE=snowflake
DB_ACCOUNT=<snowflake_account>
```

**Arquivos de ambiente:**
- `.env.example` — template para novos usuários
- `.env.local` — configuração dev (já incluso no `Makefile`)
- `.env.prod` — template prod (preencher credenciais reais)

**Mecanismo de switch:**
- `boto3` usa `endpoint_url` → aponta para MinIO ou S3 real
- `dbt profiles.yml` usa `env_var()` → seleciona target `dev` ou `prod`
- Nenhuma mudança de código necessária entre ambientes

---

## Docker Compose

### Serviços
| Serviço | Imagem | Porta | Propósito |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | 5432 | Banco de dados (mock do Snowflake) |
| `minio` | `minio/minio:latest` | 9000 (API), 9001 (Web) | Storage S3 (mock do AWS S3) |
| `airflow-init` | `apache/airflow:2.9.0` | — | Init: migration + admin user |
| `airflow-webserver` | `apache/airflow:2.9.0` | 8080 | UI do Airflow |
| `airflow-scheduler` | `apache/airflow:2.9.0` | — | Scheduler do Airflow |
| `metabase` | `metabase/metabase:latest` | 3000 | Dashboard BI |
| `metabase-setup` | `python:3.11-slim` | — | Config automática via API |

### Credenciais padrão
| Serviço | URL | Usuário | Senha |
|---|---|---|---|
| Airflow | `http://localhost:8080` | `admin` | `admin` |
| Metabase | `http://localhost:3000` | `admin@projeto.com` | `ProjetoIFG2025!` |
| MinIO | `http://localhost:9001` | `minioadmin` | `minioadmin` |

---

## Metabase — Dashboards Automáticos

### Dashboard 1: Visão Geral
- **KPI — Total de Amostras:** `SELECT COUNT(*) FROM fact_audio_analysis`
- **KPI — Taxa de Anomalia (%):** `ROUND(100.0 * SUM(condition_binary) / COUNT(*), 1)`
- **KPI — Duração Média (s):** `ROUND(AVG(duration_sec)::numeric, 2)`
- **Distribuição de Condições:** Pie chart normal vs anomalia
- **Anomalias por Modelo:** Bar chart por model_id

### Dashboard 2: Análise de Áudio por Modelo
- **Resumo por Modelo:** Tabela de `dim_machines`
- **MFCC-1 Médio por Modelo:** Bar chart
- **Spectral Centroid vs Condição:** Comparação normal/anomalia
- **Top 10 Maior RMS:** Amostras com maior energia (possível anomalia severa)

### Dashboard 3: Resultados do Modelo ML
- **KPI — Acurácia do Modelo (%):** do MLP sklearn no teste (tabela `model_predictions`)
- **Métricas dos Modelos:** tabela comparativa baselines vs MLPs (tabela `model_metrics`)
- **Matriz de Confusão (Sklearn):** contagens real × predito
- **Predições com Erro:** amostras mal classificadas — insumo da análise qualitativa

### Filtro analítico
Os dashboards 1 e 2 têm **filtro por modelo de máquina** (parâmetro de dashboard mapeado via template-tag `{{model_id}}` nos cards SQL — cláusula opcional `[[AND model_id = {{model_id}}]]`).

**Observação técnica:** os cards SQL referenciam os schemas do dbt (`public_analytics.fact_audio_analysis`, `public_analytics.dim_machines`); `model_metrics`/`model_predictions` ficam em `public`. O `setup_metabase.py` é re-executável (arquiva cards/dashboards antigos de mesmo nome antes de recriar) e usa a API nova de dashcards (PUT) com fallback para a antiga.

---

## Comandos do Makefile

```bash
make up            # Sobe todos os containers Docker
make down          # Para todos os containers
make build         # Reconstrói imagem Docker
make ingest        # Download + upload para MinIO/S3
make process       # Extrai metadados + audio features + merge
make load-db       # Carrega CSV no PostgreSQL
make pipeline      # Dispara DAG no Airflow
make dbt-run       # Executa modelos dbt localmente
make dbt-test      # Executa testes dbt
make ml-train      # Treina e avalia MLP (hard-code vs sklearn)
make test          # Roda pytest
make clean         # Remove containers, volumes e dados processados
```

### Fluxo completo para rodar do zero:
```bash
make up             # 1. Sobe containers
make ingest         # 2. Baixa dados
make process        # 3. Extrai features
make load-db        # 4. Carrega no banco
make dbt-run        # 5. Transforma dados
make dbt-test       # 6. Valida qualidade
make ml-train       # 7. Treina modelo
```

---

## Resultados do Modelo (dataset MIMII real, 0 dB SNR)

### Métricas (teste: 841 amostras — 750 normais, 91 anomalias)
| Métrica | Baseline Majoritária | Reg. Logística | MLP Hard-Code | MLP Sklearn |
|---|---|---|---|---|
| Accuracy | 89,18% | 96,79% | 97,86% | **97,98%** |
| Precision | 0% | 95,71% | 96,20% | **97,44%** |
| Recall | 0% | 73,63% | **83,52%** | **83,52%** |
| F1-Score | 0 | 0,832 | 0,894 | **0,899** |
| Tempo Treino | ~0 ms | ~15 ms | ~2.600 ms | ~425 ms |

O baseline majoritário atinge 89% de accuracy só pelo desbalanceamento, mas recall 0 (inútil). Os MLPs superam a regressão logística principalmente em recall da classe anomalia (+10 p.p.).

### Matriz de Confusão (MLP Sklearn)
```
                  Predito
                  Normal  Anomalia
Real Normal        748       2
Real Anomalia       15      76
```

- **2 falsos positivos** — paradas desnecessárias raras (precision 97,4%)
- **15 falsos negativos** — anomalias sutis não detectadas (recall 83,5%) — os erros dominantes; análise por amostra em `report_analys.md`

### Análise das Features
Com o dataset real, as features mais discriminativas são os **MFCCs** (perfil timbral completo), não as espectrais agregadas: `mfcc_35_mean`, `mfcc_31_mean`, `mfcc_10_mean`, `mfcc_3_mean` apresentam as maiores diferenças entre classes. Os erros do modelo concentram-se em anomalias cujo espectro foge do padrão da própria classe (defeitos sutis mascarados pelo ruído de fábrica a 0 dB SNR).

**Relatório completo de cada treino:** `report_analys.md` (gerado automaticamente pelo `ml/evaluate.py`).

---

## Observações Importantes

### Para a banca avaliadora
1. **Hard-code do zero:** O `HardCodedMLP` implementa forward pass, backpropagation, SGD com momento e binary cross-entropy inteiramente com NumPy — sem frameworks de deep learning.
2. **Comparação justa:** Mesmo dataset, mesmo split, mesmo scaler, métricas idênticas para ambos.
3. **Dataset real:** O pipeline roda sobre o MIMII real do Zenodo (7,87 GB, 4.205 arquivos, 0 dB SNR) — os resultados e o `report_analys.md` refletem dados de bombas industriais reais com ruído de fábrica.
4. **Pipeline reprodutível:** Qualquer pessoa com Docker pode rodar `make up && make ingest && make process && make load-db && make dbt-run && make dbt-test && make ml-train` e obter os mesmos resultados.
5. **Dev/prod switch:** Apenas 4 variáveis de ambiente separam o ambiente local do ambiente AWS+Snowflake.

### Melhorias futuras
- Adicionar mais tipos de máquina (fan, slider, valve)
- Implementar early stopping e regularização L2 no hard-code
- Adicionar data augmentation nos áudios (pitch shift, time stretch)
- Integrar com SageMaker para deploy do modelo
- Implementar validação cruzada (k-fold)
- Adicionar monitoramento de drift do modelo em produção

### Riscos e limitações
- Dataset desbalanceado (~8:1 normal:anomalia) — usar stratify no split e priorizar recall/F1
- Falsos negativos (recall 83,5%) são o erro dominante — anomalias sutis mascaradas pelo ruído de fábrica
- Modelo treinado para um tipo específico de bomba — pode não generalizar para outros equipamentos
- Ruído de fábrica diferente pode afetar a performance em novo ambiente
- Threshold de decisão (0.5) pode ser ajustado conforme criticidade da aplicação
