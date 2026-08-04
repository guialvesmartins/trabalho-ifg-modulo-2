# Relatório — Projeto Final Integrado: Pipeline de Dados em Nuvem para Aprendizagem de Máquina

**Curso:** Pós-Graduação em Inteligência Artificial Aplicada — IFG — Módulo 2
**Tema:** Manutenção Preditiva Industrial com Som (MIMII Pump)

---

## 1. Definição do problema e decisão apoiada

**Domínio de aplicação:** Indústria 4.0 / Manutenção Preditiva.

**Usuário / tomador de decisão:** engenheiro de manutenção industrial.

**Decisão apoiada:** *"Esta bomba industrial está operando com anomalia? Devo parar para manutenção?"*

Uma fábrica possui dezenas de bombas industriais operando 24/7. Paradas não programadas custam caro (produção parada, reparos emergenciais); manutenções desnecessárias também têm custo. O sistema analisa o som de cada bomba e classifica automaticamente se ela está normal ou com anomalia (contaminação, vazamento, desbalanceamento).

**Fontes de dados:** dataset MIMII (Hitachi/Toyota Research) — áudio industrial real + metadados estruturados.

**Tarefa de Aprendizagem de Máquina:** classificação binária (normal × anomalia).

**Resultado esperado:** redução de paradas não programadas, redução de manutenções desnecessárias e priorização de inspeções via dashboard.

## 2. Conjuntos de dados

**MIMII Dataset** (Malfunctioning Industrial Machine Investigation and Inspection) — Hitachi, Ltd., publicado no DCASE 2019 Workshop (arXiv:1909.09347), licença CC BY-SA 4.0.

- **Fonte:** Zenodo — `https://zenodo.org/records/3384388` (`0_dB_pump.zip`, 7,87 GB)
- **Máquina:** Pump (bomba industrial), 4 modelos (id_00, id_02, id_04, id_06)
- **Áudio:** clipes de 10 s, 16 kHz, 8 canais (array de microfones), misturados com ruído real de fábrica (0 dB SNR)
- **Condições:** `normal` (funcionamento normal) e `abnormal` (defeitos reais), normalizada para `anomaly` no pipeline

**Dados estruturados** (extraídos dos paths e do cabeçalho dos arquivos): `machine_type`, `model_id`, `condition`, `duration_sec`, `sample_rate`, `channels`.

**Dados não estruturados:** os próprios arquivos `.wav`.

**Limitações dos dados:** desbalanceamento (~7:1 normal:anomalia), um único tipo de máquina por modelo treinado, ruído de fábrica específico do ambiente de gravação.

## 3. Arquitetura geral da solução

**Desenvolvimento (local, Docker Compose):** MinIO (mock do S3), PostgreSQL 16 (mock do Snowflake), Airflow 2.9, Metabase. A troca dev → prod é feita apenas por variáveis de ambiente (`.env.local` → `.env.prod`) — `boto3` muda o `endpoint_url` e o dbt muda o target via `env_var()`, sem alteração de código.

**Produção (100% AWS + Snowflake):** S3 (raw + processed), EC2 (Airflow + scripts), SageMaker (treino), Snowflake via external stage, Metabase em ECS, CloudWatch para logs — provisionada pelo template `infra/cloudformation.yaml` (VPC, sub-redes, IAM com menor privilégio, Security Groups).

Diagramas completos (dev e AWS) e organização dos dados em camadas: `docs/ARQUITETURA_AWS.md`.

## 4. Processamento e extração de atributos

**Estruturados** (`processing/process_structured.py`): parse dos paths, tipagem, normalização de condição, criação do target `condition_binary`, deduplicação — saída `pump_metadata.csv`.

**Não estruturados** (`processing/extract_audio_features.py`): para cada `.wav`, librosa extrai 92 features — 80 MFCC (40 coeficientes × média/desvio), 11 espectrais (centroid, bandwidth, rolloff, 7 bandas de contrast) e 2 de energia (ZCR, RMS). Extração paralelizada por multiprocessing.

**Merge** (`processing/merge_features.py`): LEFT JOIN por `file_id` → `ml_features.csv` (uma linha por áudio, ~100 colunas), com nulls preenchidos.

## 5. Pipeline de ELT (Airflow + dbt + Snowflake/Postgres)

DAG `etl_pipeline` com 9 tasks sequenciais: download → upload S3 → metadados → features de áudio → merge → carga no banco → `dbt run` → `dbt test` → treino/avaliação ML.

**Modelos dbt (5):** staging (`stg_pump_metadata`, `stg_audio_features` — views), dimensions (`dim_machines`), facts (`fact_audio_analysis`), marts (`ml_features` — tabela final para o ML e para o dashboard).

**Testes dbt (16):** `not_null`, `unique` (file_id) e `accepted_values` (condition ∈ {normal, anomaly}; condition_binary ∈ {0,1}) — todos documentados com `description` em `dbt_project/tests/schema.yml`.

## 6. Uso de recursos da AWS

- **S3:** buckets `raw` (áudio bruto, versionado) e `processed` (CSVs e modelos `.pkl`)
- **EC2 t3.medium:** Airflow + scripts de processamento (UserData instala Docker, Python e dependências)
- **SageMaker Notebook ml.t3.medium:** ambiente de treino
- **CloudWatch Logs:** logs centralizados, retenção de 30 dias
- **IAM:** roles de menor privilégio (EC2→S3 e SageMaker→S3)
- **CloudFormation:** infraestrutura como código (`infra/cloudformation.yaml`)

**Custos aproximados registrados** (uso acadêmico, ~176 h/mês): ~US$ 20,50/mês em AWS + ~US$ 20/mês de Snowflake (detalhamento em `docs/ARQUITETURA_AWS.md`).

## 7. Tarefa de Aprendizagem de Máquina, modelos e métricas

**Tarefa:** classificação binária — P(anomalia) a partir de 96 features numéricas.

**Preparação:** remoção de colunas de ID/texto, split 80/20 estratificado (random_state=42), StandardScaler ajustado apenas no treino.

**Modelos comparados no mesmo split:**

1. **Baseline — classe majoritária** (DummyClassifier)
2. **Baseline — Regressão Logística**
3. **MLP hard-code** (NumPy puro): 96→64→32→1, ReLU + sigmoid, backpropagation manual, mini-batch SGD com momento, binary cross-entropy — sem frameworks de deep learning
4. **MLP sklearn** (MLPClassifier 64×32, Adam, L2)

**Métricas:** accuracy, precision, recall, F1-score e matriz de confusão — os valores da última execução, junto com a análise qualitativa de acertos/erros e as features mais discriminativas, estão em **`report_analys.md`** (gerado automaticamente a cada treino).

**Registro dos resultados:** `model_comparison.csv` (métricas), `predictions.csv` (predição por amostra — rastreabilidade), modelos exportados via pickle em `data/processed/models/`.

## 8. Dashboard e principais análises

Três dashboards no Metabase (criados automaticamente por `scripts/setup_metabase.py`):

1. **Manutenção Preditiva — Visão Geral:** KPIs (total de amostras, taxa de anomalia, duração média), distribuição de condições, anomalias por modelo
2. **Análise de Áudio por Modelo:** resumo por modelo, MFCC-1 médio, spectral centroid normal × anomalia, top 10 RMS
3. **Resultados do Modelo ML:** acurácia (KPI), métricas comparadas, matriz de confusão, predições com erro

**Filtro analítico:** os dashboards 1 e 2 têm filtro por modelo de máquina vinculado aos cards.

**Como o dashboard apoia a decisão:** o engenheiro identifica qual modelo de bomba concentra anomalias, filtra o modelo de interesse, prioriza as amostras de maior energia (RMS) para inspeção e consulta a confiabilidade do classificador (recall de anomalia) antes de agendar uma parada.

## 9. Limitações e próximos passos

**Limitações:**
- Desbalanceamento de classes — accuracy isolada engana; decisões devem olhar recall/F1 da classe anomalia
- Modelo específico para as bombas e o ambiente acústico do MIMII — sem garantia de generalização
- Features agregadas por clip descartam dinâmica temporal
- Threshold fixo de 0,5 — deveria ser calibrado pelo custo real de FP (parada desnecessária) vs FN (falha não detectada)

**Próximos passos:**
- Estender para os demais tipos de máquina do MIMII (fan, slider, valve)
- Validação cruzada (k-fold) e ajuste de hiperparâmetros
- Early stopping e regularização L2 no hard-code
- Data augmentation de áudio (pitch shift, time stretch)
- Deploy do modelo exportado (pickle) no SageMaker + monitoramento de drift
