# Fluxo Completo do Projeto — Explicação em Linguagem Natural

Este projeto é um sistema completo de manutenção preditiva industrial usando análise de som. A ideia é simples: dado o som de uma bomba industrial em operação, conseguimos classificar se ela está operando normalmente ou se apresenta alguma anomalia (contaminação, vazamento, desbalanceamento etc.). Para isso, combinamos dois tipos de informação: dados estruturados (tipo de máquina, modelo, duração do áudio) e áudio não estruturado (gravações .wav de máquinas reais em fábrica). Tudo isso é orquestrado por um pipeline automatizado que vai desde o download dos dados brutos até um dashboard interativo onde um engenheiro de manutenção pode tomar decisões sobre parar ou não uma máquina.

A seguir, vamos percorrer cada etapa desse pipeline, explicando o que acontece em cada uma delas e por quê.

---

## 1. De onde vêm os dados

O dataset utilizado é o **MIMII** (Malfunctioning Industrial Machine Investigation and Inspection), criado pela Hitachi/Toyota Research e disponível publicamente no Zenodo. Especificamente, usamos o subconjunto da bomba industrial (pump) com nível de ruído de 0 dB — ou seja, o som da máquina misturado com ruído real de fábrica.

Cada arquivo .wav é uma gravação de 16 kHz com 16 bits por amostra, capturada por um array de 8 microfones. O dataset contém 4 modelos diferentes de bomba (model_id 00, 02, 04, 06), cada um com gravações em duas condições:

- **normal:** funcionamento normal da máquina (milhares de clipes)
- **abnormal:** máquina com defeito (contaminação, vazamento, desbalanceamento — centenas de clipes)

Os metadados (tipo de máquina, modelo, condição) são extraídos da própria estrutura de diretórios do dataset (`pump/id_XX/{normal,abnormal}/*.wav`), sem necessidade de um CSV externo. Durante o processamento, a condição `abnormal` é normalizada para `anomaly` — valor usado pelo restante do pipeline (dbt, ML, Metabase).

O download é feito por um script Python (`ingestion/download_dataset.py`) que baixa diretamente do Zenodo (~7,9 GB, com suporte a retomada de download interrompido) e extrai os arquivos para `data/raw/pump/`.

---

## 2. Como os dados chegam no armazenamento

Com os arquivos .wav extraídos, o script `ingestion/load_raw_to_s3.py` faz o upload de todos eles para um bucket `raw/` no nosso armazenamento. Em desenvolvimento, esse armazenamento é o **MinIO**, um serviço que funciona exatamente como o Amazon S3, mas roda localmente dentro de um container Docker.

A estrutura no bucket fica:

```
s3://raw/pump/
├── pump/model_id_00/normal/00000000.wav
├── pump/model_id_00/normal/00000001.wav
├── ...
├── pump/model_id_00/anomaly/00000000.wav
├── pump/model_id_02/normal/...
└── ...
```

O código usa `boto3` com endpoint configurável — em produção, basta trocar a variável `S3_ENDPOINT` de `http://minio:9000` para `https://s3.amazonaws.com`.

---

## 3. Processamento dos dados estruturados

O script `processing/process_structured.py` percorre todos os arquivos .wav extraídos e constrói um CSV com os metadados extraídos dos caminhos:

| file_id | machine_type | model_id | condition | duration_sec | sample_rate | condition_binary |
|---------|-------------|----------|-----------|-------------|-------------|-----------------|
| pump_id_00_normal_00000000 | pump | id_00 | normal | 10.0 | 16000 | 0 |
| pump_id_00_anomaly_00000001 | pump | id_00 | anomaly | 10.0 | 16000 | 1 |

A coluna `condition_binary` é o **target do modelo de ML**: 0 para normal, 1 para anomalia.

---

## 4. Extração de features do áudio

O script `processing/extract_audio_features.py` é o coração do processamento de dados não estruturados. Para cada arquivo .wav, ele extrai features acústicas usando a biblioteca **librosa**:

- **MFCC (Mel-Frequency Cepstral Coefficients):** 40 coeficientes (média + desvio padrão) que capturam a "impressão digital" sonora da máquina — são os mesmos coeficientes usados em reconhecimento de fala, mas aqui eles descrevem o timbre do som industrial.
- **Spectral Centroid:** indica onde a "energia" do espectro está concentrada — sons agudos têm centroide mais alto.
- **Spectral Bandwidth:** largura da banda espectral.
- **Spectral Rolloff:** frequência abaixo da qual está concentrada 85% da energia.
- **Spectral Contrast:** contraste entre picos e vales do espectro (7 bandas).
- **Zero-Crossing Rate:** taxa de cruzamento por zero — indica a frequência dominante.
- **RMS Energy:** energia/potência do sinal — máquinas com defeito tendem a ter padrões diferentes de energia.

No total, são extraídas 92 features por arquivo de áudio. A extração roda em paralelo (multiprocessing, um worker por núcleo de CPU) — essencial para o dataset real, com milhares de arquivos de 10 segundos e 8 canais. O resultado é salvo em `data/processed/audio_features.csv`.

---

## 5. Merge das features

O script `processing/merge_features.py` faz o join entre os metadados estruturados (`pump_metadata.csv`) e as features de áudio (`audio_features.csv`) usando `file_id` como chave. O resultado é um dataset único em `data/processed/ml_features.csv` com 4.205 linhas (3.749 normais, 456 anomalias) e 103 colunas, pronto para ser consumido pelo modelo de Machine Learning.

---

## 6. Carga no PostgreSQL (para dbt)

O script `processing/load_to_postgres.py` carrega o `ml_features.csv` em uma tabela `public.ml_features_raw` no PostgreSQL usando SQLAlchemy. Essa tabela é a fonte dos modelos dbt.

---

## 7. Pipeline dbt (transformações analíticas)

O **dbt** (data build tool) transforma os dados brutos em tabelas analíticas organizadas em camadas:

### Staging (staging)
- `stg_pump_metadata` — limpa e tipa os metadados, deduplica por file_id
- `stg_audio_features` — limpa e tipa as features de áudio

### Dimensions (analytics)
- `dim_machines` — agrega por machine_type e model_id: total de amostras, contagem de normal vs anomalia, duração média

### Facts (analytics)
- `fact_audio_analysis` — join entre metadados e features, tabela principal para análise

### Marts (marts)
- `ml_features` — join final com dim_machines, pronto para consumo pelo modelo

O dbt também executa **testes de qualidade**:
- `file_id` é único e não nulo
- `condition` só pode ser "normal" ou "anomaly"
- `condition_binary` só pode ser 0 ou 1

---

## 8. Modelo de Machine Learning (MLP Binário)

A tarefa de ML é **classificação binária**: dado um conjunto de features extraídas do áudio de uma bomba, o modelo decide se a máquina está normal (0) ou com anomalia (1).

Implementamos o mesmo modelo de duas formas, conforme exigido pelo projeto:

### Hard-Code (NumPy puro)
`ml/hard_code/neural_network_hardcode.py` — MLP com 2 camadas ocultas (64→32 neurônios, ReLU), 1 neurônio de saída com sigmoid, treinado com mini-batch SGD + momento, binary cross-entropy loss. Tudo implementado manualmente com operações matriciais do NumPy.

### Biblioteca (sklearn)
`ml/library/neural_network_sklearn.py` — MLPClassifier do scikit-learn com a mesma arquitetura (64→32, ReLU, Adam), permitindo comparar a implementação manual com uma biblioteca consolidada.

### Baselines
Antes dos MLPs, dois baselines são avaliados no mesmo split para contextualizar os resultados:
- **Classe majoritária** (DummyClassifier) — sempre prediz "normal"; mostra o piso de accuracy causado pelo desbalanceamento (e recall 0, que o torna inútil na prática)
- **Regressão Logística** — modelo linear simples

### Avaliação
`ml/evaluate.py` roda os 4 modelos, compara métricas (accuracy, precision, recall, F1-score) e gera:
- `report_analys.md` — relatório completo do treinamento: métricas, análise qualitativa com exemplos de acertos e erros (e possíveis causas), features mais discriminativas e limitações
- `data/processed/model_comparison.csv` — tabela comparativa
- `data/processed/predictions.csv` — predição por amostra do teste (rastreabilidade dado → predição)
- `data/processed/models/*.pkl` — modelos exportados via **pickle**: pipeline sklearn (scaler + MLP) pronto para inferência e pesos do hard-code (recarregáveis com `carregar_modelo()`)
- `data/processed/hardcode_cm.png` — matriz de confusão hard-code
- `data/processed/sklearn_cm.png` — matriz de confusão sklearn

Com o Postgres ativo, métricas e predições também são carregadas nas tabelas `model_metrics` e `model_predictions`, que alimentam o dashboard "Resultados do Modelo ML".

---

## 9. Orquestração com Airflow

Todo o pipeline é orquestrado por uma **DAG do Apache Airflow** (`dags/etl_pipeline.py`) com 8 tarefas sequenciais:

```
[1] download_dataset     → Baixa do Zenodo
[2] load_to_s3           → Upload para MinIO/S3
[3] process_structured   → Extrai metadados dos paths
[4] extract_audio_features → Extrai features com librosa
[5] merge_features       → Junta estruturado + áudio
[5b] load_to_postgres    → Carrega no PostgreSQL
[6] dbt_run              → Executa modelos dbt
[7] dbt_test             → Roda testes de qualidade
[8] ml_train_evaluate    → Treina e avalia MLP
```

---

## 10. Dashboard (Metabase)

O Metabase consome as tabelas do PostgreSQL (via dbt) e exibe dashboards para tomada de decisão:

### Dashboard 1: Visão Geral
- Total de amostras analisadas
- Taxa de anomalia (%)
- Duração média dos áudios
- Distribuição normal vs anomalia
- Anomalias por modelo de máquina

### Dashboard 2: Análise de Áudio por Modelo
- Resumo por modelo (tabela)
- MFCC-1 médio por modelo
- Spectral Centroid: normal vs anomalia
- Top 10 amostras com maior energia (RMS)

### Dashboard 3: Resultados do Modelo ML
- Acurácia do modelo no conjunto de teste (KPI)
- Métricas comparadas (baselines vs hard-code vs sklearn)
- Matriz de confusão
- Predições com erro (insumo da análise qualitativa)

Os dashboards 1 e 2 possuem **filtro analítico por modelo de máquina** — o engenheiro seleciona a bomba de interesse e todos os gráficos vinculados são recortados.

### Decisão apoiada:
> **"Essa bomba industrial está operando com anomalia? Devo parar para manutenção?"**

O engenheiro de manutenção pode:
1. Ver a taxa de anomalia em tempo real
2. Identificar quais modelos de máquina são mais problemáticos
3. Priorizar manutenções com base na severidade (RMS)
4. Reduzir paradas não programadas e custos de reparo

---

## 11. Infraestrutura

### Ambiente de Desenvolvimento (Docker Compose)
- **PostgreSQL 16** — banco de dados (mock do Snowflake)
- **MinIO** — armazenamento S3-compatível (mock do AWS S3)
- **Apache Airflow 2.9** — orquestrador do pipeline
- **Metabase** — dashboard de visualização

### Ambiente de Produção (AWS)
O arquivo `infra/cloudformation.yaml` define a arquitetura equivalente 100% em nuvem AWS:
- **S3** para armazenamento de áudio
- **EC2** para execução do Airflow
- **Snowflake** como data warehouse (substitui PostgreSQL)
- **CloudFormation** para infraestrutura como código

A troca entre dev e prod é feita apenas alterando 4 variáveis de ambiente no arquivo `.env`.
