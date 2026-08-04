# Projeto Final Integrado — Manutencao Preditiva Industrial com Som

**Curso:** Pos-Graduacao em Inteligencia Artificial Aplicada — IFG — Modulo 2
**Tema:** Classificacao de Anomalias em Maquinas Industriais usando Som (Audio + Dados Estruturados)

---

## Visao Geral

Sistema que classifica automaticamente se uma bomba industrial esta operando normalmente ou com anomalia, combinando:

- **Dados estruturados:** tipo de maquina, modelo, duracao do audio
- **Audio nao estruturado:** gravacoes .wav de maquinas reais (librosa: MFCC, spectral features)

Dataset: **MIMII Pump** (Hitachi/Toyota Research) — Zenodo

A arquitetura usa Docker no ambiente local (Postgres, MinIO, Airflow, Metabase) com integracao pronta para AWS S3 e Snowflake em producao.

### Decisao apoiada

> "Essa bomba industrial esta operando com anomalia? Devo parar para manutencao?"

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
              │ Audio + ML     │
              └───────────────┘
```

## Pre-requisitos

- Docker Desktop
- Python 3.11+
- Git

## Inicio Rapido

```bash
# Clonar
git clone <repo-url>
cd projeto-final

# Configurar ambiente
cp .env.example .env.local

# Subir servicos
make up

# Baixar dados do Zenodo e processar (7,87 GB, com resume automatico)
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
│
├── ingestion/                # Download Zenodo + upload S3
├── processing/               # Extracao de features de audio + merge
├── dags/                     # DAG do Airflow
├── dbt_project/              # Modelos dbt (staging, dimensions, facts, marts)
├── ml/                       # MLP hard-code + sklearn (classificacao binaria)
├── dashboard/                # Queries SQL do Metabase
├── infra/                    # CloudFormation (AWS)
├── tests/                    # Testes unitarios
└── report/                   # Relatorio e apresentacao final
```

## Pipeline (8 Etapas)

```
[1] Download Zenodo → [2] Upload S3 → [3] Metadados Estruturados
                                         └── [4] Audio Features (librosa: MFCC + spectral)
                                              └── [5] Merge → [6] Load Postgres → [7] dbt Run/Test → [8] ML Train
```

## Tecnologias

| Camada | Ferramentas |
|--------|-------------|
| Orquestracao | Apache Airflow 2.9 |
| Storage | MinIO (dev) / AWS S3 (prod) |
| Dados | pandas, numpy |
| Audio | librosa, soundfile |
| DW/Transform | PostgreSQL + dbt-core 1.8 (dev) / Snowflake (prod) |
| Dashboard | Metabase |
| ML | MLP (hard-code NumPy + sklearn MLPClassifier) + baselines (majoritaria, reg. logistica) |
| Infra | Docker, CloudFormation |

## Dataset

**MIMII Dataset** (Hitachi, Ltd.) — Sound Dataset for Malfunctioning Industrial Machine Investigation and Inspection

- Fonte: https://zenodo.org/records/3384388 (`0_dB_pump.zip`, 7,87 GB)
- Maquina: Pump (bomba industrial), 4 modelos (id_00, id_02, id_04, id_06)
- Arquivos: 4.205 .wav de 10s (16kHz, 8 canais) — 3.749 normais, 456 anomalias
- Condicoes: normal (funcionamento normal) e abnormal/anomaly (contaminacao, vazamento, desbalanceamento)
- SNR: 0 dB (som com ruido de fabrica real)

### Resultados (dataset real)

| Metrica | Baseline Majoritaria | Reg. Logistica | MLP Hard-Code | MLP Sklearn |
|---|---|---|---|---|
| Accuracy | 89,18% | 96,79% | 97,86% | **97,98%** |
| Recall (anomalia) | 0% | 73,63% | 83,52% | **83,52%** |
| F1-Score | 0 | 0,832 | 0,894 | **0,899** |

Detalhes, matriz de confusao e analise qualitativa: `report_analys.md`.

## Machine Learning

O `make ml-train` treina e compara 4 modelos no mesmo split (80/20 estratificado, StandardScaler):

1. **Baseline — Classe Majoritaria** (DummyClassifier): piso de referencia
2. **Baseline — Regressao Logistica**: modelo linear simples
3. **MLP Hard-Code** (NumPy puro): forward/backprop implementados do zero
4. **MLP Sklearn** (MLPClassifier 64x32, Adam)

Saidas geradas:

| Arquivo | Conteudo |
|---|---|
| `report_analys.md` | Relatorio completo do treinamento (metricas, analise qualitativa de acertos/erros, limitacoes) |
| `data/processed/model_comparison.csv` | Metricas de todos os modelos |
| `data/processed/predictions.csv` | Predicao por amostra do teste (rastreabilidade) |
| `data/processed/models/*.pkl` | Modelos exportados via **pickle** (pipeline sklearn pronto para inferencia + pesos do hard-code) |
| `data/processed/*_cm.png` | Matrizes de confusao |

Se o Postgres estiver ativo, as metricas e predicoes tambem sao carregadas nas tabelas `model_metrics` e `model_predictions`, alimentando o dashboard "Resultados do Modelo ML" no Metabase.

### Inferencia com o modelo exportado

```python
import pickle
with open("data/processed/models/mlp_sklearn_pipeline.pkl", "rb") as f:
    pipeline = pickle.load(f)
proba = pipeline.predict_proba(X_novo)[:, 1]  # P(anomalia)
```

## Dashboards (Metabase)

`make setup-metabase` cria automaticamente 3 dashboards com **filtro analitico por modelo de maquina**:

1. **Manutencao Preditiva — Visao Geral** — KPIs, distribuicao de condicoes, anomalias por modelo
2. **Analise de Audio por Modelo** — features espectrais e MFCC por modelo
3. **Resultados do Modelo ML** — acuracia, metricas comparadas, matriz de confusao e predicoes com erro

**Como o dashboard apoia a decisao:** o engenheiro de manutencao ve a taxa de anomalias por modelo de bomba, filtra o modelo de interesse e identifica as amostras com maior energia sonora (RMS) — candidatas a inspecao imediata. O dashboard de ML mostra a confiabilidade do classificador (recall da classe anomalia) antes de confiar nele para agendar paradas.

## Arquitetura AWS e Custos

Ver `docs/ARQUITETURA_AWS.md`: diagramas (local dev e equivalente 100% AWS), organizacao dos dados em camadas, registro de custos aproximados (~US$ 40/mes em uso academico) e instrucoes de deploy do template `infra/cloudformation.yaml`.

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
- `docs/ARQUITETURA_AWS.md` — Diagramas de arquitetura (dev e 100% AWS) + custos
- `docs/RELATORIO_TECNICAS.md` — Normalizacao dos audios + comparacao detalhada hard-code vs sklearn
- `report_analys.md` — Relatorio do ultimo treinamento (gerado por `make ml-train`)
- `report/` — Relatorio e apresentacao final
