# Divisão da Apresentação — Projeto Final Módulo 2

**Disciplinas:** Aprendizagem de Máquina + Cloud Computing + Modelagem de Dados para IA

> Baseada nas guias individuais: `guia-apresentacao-guilherme.html`, `guia-apresentacao-walber.html`, `guia-apresentacao-daniel.html`, `guia-apresentacao-david.html`.

---

## 1. Guilherme — Problema de Negócio e Dataset MIMII (~ 3 minutos) · Slides 2–3

- Apresentação do problema de negócio e objetivo do projeto
- Manutenção preditiva vs. corretiva vs. preventiva (por que preditiva?)
- Decisão apoiada: "esta bomba está com anomalia? devo parar para manutenção?"
- Tomador de decisão: engenheiro de manutenção industrial
- Descrição do dataset MIMII Pump (Hitachi/Toyota Research — Zenodo, CC BY-SA 4.0, DCASE 2019)
- Características do áudio: 16 kHz, 8 canais, clipes de 10 s, ruído real de fábrica a **0 dB SNR**
- Contextualização da tarefa: classificação binária (normal × anômala)
- Desbalanceamento ~8:1 (3.749 normais × 456 anomalias) e por que a acurácia sozinha engana

---

## 2. Walber — Feature Engineering, Pipeline ELT e Orquestração (~ 3 minutos) · Slides 4–6

- Processamento de áudio com *librosa*: extração de features acústicas
  - MFCCs (80 features: 40 coeficientes, média + desvio) — timbre
  - Features espectrais (10: centroid, bandwidth, rolloff, contraste ×7) — forma do espectro
  - Features temporais (2: RMS energy, zero-crossing rate) — energia e vibração
  - Metadados estruturados (tipo, modelo, condição, duração, canais) + downmix 8→mono
- Quantitativo/qualitativo das features: **96 numéricas** → tabela final 103 colunas × 4.205 linhas
- Pipeline ELT em **8 etapas**: download → S3/MinIO → metadados → features → merge → carga Postgres → dbt → ML
- ELT vs. ETL (transforma dentro do banco, reprocessável)
- **Apache Airflow**: DAG com 8 tasks sequenciais, retries e reexecução
- **dbt**: 5 modelos em camadas (staging → dim/fact → marts) e **16 testes** de qualidade (not_null, unique, accepted_values)
- Papel do Snowflake/PostgreSQL como data warehouse

---

## 3. Daniel — Modelagem de Machine Learning (~ 3 minutos) · Slides 7–9

- Características dos modelos:
  - *Hard-code (NumPy)*: MLP do zero com backpropagation manual (SGD + momento)
  - *Biblioteca (scikit-learn)*: MLPClassifier com otimizador Adam
- Arquitetura da rede neural:
  - Topologia: Input(96) → Hidden1(64, ReLU) → Hidden2(32, ReLU) → Output(1, Sigmoid)
  - Funções de ativação: ReLU nas ocultas (evita vanishing gradient), Sigmoid na saída (probabilidade) — equivalente ao Softmax em binário
- Parâmetros de treinamento:
  - Hard-code: lr 0,01, momento 0,9, 300 épocas, batch 32, binary cross-entropy, He init
  - Sklearn: Adam, max_iter 500, regularização L2 (alpha 0,0001)
- Saída: P(anomalia) ∈ [0,1] com threshold 0,5
- Comparação justa: mesmo split (stratify 80/20), mesmo scaler → resultados empatados, validando a implementação manual

---

## 4. David — Cloud Computing, Resultados e Dashboard (~ 3 minutos) · Slides 10–12

- Arquitetura 100% AWS: **S3 → EC2 → Snowflake → dbt → SageMaker → Metabase**
- Papel de cada serviço (e o que substitui do ambiente local: MinIO→S3, Postgres→Snowflake, etc.)
- Troca dev ↔ prod por **4 variáveis de ambiente** (zero mudanças de código)
- Infraestrutura como código (AWS CloudFormation) + segurança (IAM, VPC, SG)
- Custos: ~R$40/mês (~40,50 USD) no cenário acadêmico
- Dashboard no Metabase: KPIs (amostras, taxa de anomalia, duração), filtro por modelo, anomalias por máquina, matriz de confusão
- Regra de decisão: P(anomalia) > 0,5 → agendar manutenção; senão → continuar operando

---

## Observações (correções das guias frente à divisão antiga)

- **Daniel**: saída é **1 neurônio sigmoid**, não "Output(2, Softmax)"; rapidez real ~**3×**, não 6,7×.
- **Walber**: **10** features espectrais (não 11 — sem flatness) e **16** testes dbt (não 14).
- **Guilherme**: ficou com problema + dataset; o pipeline ELT/arquitetura/DW foi para o Walber.
