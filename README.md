# Projeto Final Integrado — Previsao de Satisfacao em E-commerce

**Curso:** Pos-Graduacao em Inteligencia Artificial Aplicada — IFG — Modulo 2
**Tema:** Previsao de Satisfacao em E-commerce com Dados Multimodais (Texto + Imagens + Dados Estruturados)

---

## Visao Geral

Sistema que classifica automaticamente o nivel de satisfacao (rating 1 a 5 estrelas) de produtos de e-commerce, combinando:

- **Dados estruturados:** precos, descontos, categorias
- **Texto nao estruturado:** reviews de clientes (NLP: VADER, TF-IDF)
- **Imagens:** fotos dos produtos (CV: cores, nitidez, textura)

A arquitetura usa Docker no ambiente local (Postgres, MinIO, Airflow, Metabase) com integracao pronta para AWS S3 e Snowflake em producao.

## Arquitetura

```
Docker Compose (dev)
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   MinIO  │  │PostgreSQL│  │ Airflow  │  │ Metabase │
│  :9000   │  │  :5432   │  │  :8080   │  │  :3000   │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     └──────────────┴─────────────┴──────────────┘
                      │
              ┌───────┴───────┐
              │ Python Scripts │
              │ NLP + CV + ML  │
              └───────────────┘
```

## Pre-requisitos

- Docker Desktop
- Python 3.11+
- Git
- Conta Kaggle (para download dos datasets)

## Inicio Rapido

```bash
# Clonar
git clone <repo-url>
cd projeto-final

# Configurar ambiente
cp .env.example .env.local

# Subir servicos
make up

# Apos servicos saudaveis, baixar dados e rodar pipeline
make ingest
make process

# Ver resultados
# Airflow:   http://localhost:8080 (admin/admin)
# Metabase:  http://localhost:3000
# MinIO:     http://localhost:9001 (minioadmin/minioadmin)
```

## Estrutura

```
projeto-final/
├── docker-compose.yml        # Servicos (Postgres, MinIO, Airflow, Metabase)
├── Dockerfile                # Imagem Python 3.11 customizada
├── Makefile                  # Comandos de atalho
├── requirements.txt          # Bibliotecas Python
├── FLUXO.md                  # Explicacao completa em linguagem natural
│
├── ingestion/                # Download e upload de dados
├── processing/               # NLP, CV e merge de features
├── dags/                     # DAG do Airflow
├── dbt_project/              # Modelos dbt (staging, dimensions, facts, marts)
├── ml/                       # Naive Bayes hard-code + sklearn
├── dashboard/                # Queries SQL do Metabase
├── infra/                    # CloudFormation (AWS)
├── tests/                    # Testes unitarios
├── notebooks/                # Jupyter notebooks (EDA)
└── report/                   # Relatorio e apresentacao final
```

## Pipeline (8 Etapas)

```
[1] Download Kaggle → [2] Upload S3 → [3] Limpeza Estruturada
                                         ├── [4a] NLP (VADER + TF-IDF)
                                         └── [4b] CV (Cores + Textura)
                                         └── [5] Merge → [6] dbt Run → [7] dbt Test → [8] ML Train
```

## Tecnologias

| Camada | Ferramentas |
|--------|-------------|
| Orquestracao | Apache Airflow 2.9 |
| Storage | MinIO (dev) / AWS S3 (prod) |
| Dados | pandas, numpy |
| NLP | VADER, TF-IDF (scikit-learn), textstat |
| CV | OpenCV, Pillow, scikit-image |
| DW/Transform | PostgreSQL + dbt-core 1.8 (dev) / Snowflake (prod) |
| Dashboard | Metabase |
| ML | Naive Bayes (hard-code + sklearn MultinomialNB) |
| Infra | Docker, CloudFormation |

## Ambiente de Producao

Para usar S3 e Snowflake reais:

```bash
# Editar .env.prod com credenciais reais
cp .env.prod .env
make up && make pipeline
```

Apenas 4 variaveis mudam entre dev e prod.

## Documentacao Completa

- `FLUXO.md` — Explicacao do projeto em linguagem natural
- `PLANO_PROJETO.md` — Especificacao tecnica detalhada
- `.docs-projeto-final/` — Vault Obsidian com planejamento e tracking
