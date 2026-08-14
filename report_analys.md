# Relatório de Análise do Treinamento — Manutenção Preditiva Industrial

_Gerado automaticamente por `ml/evaluate.py` em 2026-08-11 00:34:53._

## 1. Dataset

- **Fonte:** MIMII Dataset (Pump, 0 dB SNR) — Zenodo
- **Amostras:** 4205 arquivos de áudio
- **Features numéricas:** 96 (MFCC, espectrais, ZCR, RMS, duração)
- **Distribuição:** 3749 normal (89.2%) | 456 anomalia (10.8%)
- **Split:** 80% treino / 20% teste, estratificado por classe (random_state=42)
- **Teste:** 841 amostras (750 normal, 91 anomalia)
- **Escalonamento:** StandardScaler ajustado apenas no treino

## 2. Modelos Comparados

| Modelo | Tipo | Papel |
|---|---|---|
| Classe Majoritária (Dummy) | Baseline | Piso de referência — sempre prediz 'normal' |
| Regressão Logística | Baseline | Modelo linear simples |
| MLP Hard-Code (NumPy) | Modelo principal | Forward/backprop implementados do zero |
| MLP Sklearn | Modelo principal | MLPClassifier(64, 32) com Adam |

## 3. Métricas no Conjunto de Teste

| Métrica | Majoritária | Reg. Logística | MLP Hard-Code | MLP Sklearn |
|---|---|---|---|---|
| Accuracy | 0.8918 | 0.9679 | 0.9786 | 0.9798 |
| Precision | 0.0000 | 0.9571 | 0.9620 | 0.9744 |
| Recall | 0.0000 | 0.7363 | 0.8352 | 0.8352 |
| F1-Score | 0.0000 | 0.8323 | 0.8941 | 0.8994 |
| Tempo Treino (ms) | 0.6 | 603.8 | 11337.2 | 3786.7 |
| Tempo Predição (ms) | 0.15 | 4.56 | 12.24 | 3.33 |

O baseline de classe majoritária atinge 89.2% de accuracy apenas por causa do desbalanceamento — mas tem recall 0 (não detecta nenhuma anomalia), o que o torna inútil para o problema. Todo modelo precisa superá-lo em recall/F1.

### Matriz de Confusão — MLP Hard-Code

| | Predito Normal | Predito Anomalia |
|---|---|---|
| **Real Normal** | 747 | 3 |
| **Real Anomalia** | 15 | 76 |

### Matriz de Confusão — MLP Sklearn

| | Predito Normal | Predito Anomalia |
|---|---|---|
| **Real Normal** | 748 | 2 |
| **Real Anomalia** | 15 | 76 |

Imagens: `data/processed/hardcode_cm.png` e `data/processed/sklearn_cm.png`.

## 4. Análise Qualitativa

### Exemplos de acertos (MLP Sklearn)

- `pump_id_04_anomaly_00000055` — real: **anomaly**, P(anomalia)=1.000
- `pump_id_02_anomaly_00000078` — real: **anomaly**, P(anomalia)=1.000
- `pump_id_02_anomaly_00000072` — real: **anomaly**, P(anomalia)=1.000

### Exemplos de erros (MLP Sklearn — 17 erros no teste)

- `pump_id_04_anomaly_00000019` (id_04) — real: **anomaly**, predito: **normal**, P(anomalia)=0.401
  - Possível causa: amostra atípica dentro da própria classe; features que mais desviam da média da classe real: mfcc_20_mean (2.1 desvios-padrao da media da classe real); rms_mean (1.7 desvios-padrao da media da classe real); mfcc_4_mean (1.7 desvios-padrao da media da classe real)
- `pump_id_02_anomaly_00000019` (id_02) — real: **anomaly**, predito: **normal**, P(anomalia)=0.000
  - Possível causa: amostra atípica dentro da própria classe; features que mais desviam da média da classe real: mfcc_30_std (6.2 desvios-padrao da media da classe real); mfcc_31_std (4.8 desvios-padrao da media da classe real); mfcc_29_std (3.1 desvios-padrao da media da classe real)
- `pump_id_00_anomaly_00000117` (id_00) — real: **anomaly**, predito: **normal**, P(anomalia)=0.000
  - Possível causa: amostra atípica dentro da própria classe; features que mais desviam da média da classe real: mfcc_32_std (5.0 desvios-padrao da media da classe real); mfcc_31_std (4.2 desvios-padrao da media da classe real); mfcc_23_std (3.4 desvios-padrao da media da classe real)
- `pump_id_04_anomaly_00000025` (id_04) — real: **anomaly**, predito: **normal**, P(anomalia)=0.001
  - Possível causa: amostra atípica dentro da própria classe; features que mais desviam da média da classe real: mfcc_20_mean (2.4 desvios-padrao da media da classe real); mfcc_4_mean (2.0 desvios-padrao da media da classe real); rms_mean (2.0 desvios-padrao da media da classe real)
- `pump_id_00_anomaly_00000110` (id_00) — real: **anomaly**, predito: **normal**, P(anomalia)=0.121
  - Possível causa: amostra atípica dentro da própria classe; features que mais desviam da média da classe real: rms_mean (1.8 desvios-padrao da media da classe real); mfcc_11_std (1.6 desvios-padrao da media da classe real); mfcc_35_std (1.6 desvios-padrao da media da classe real)

**Interpretação:** erros concentram-se em amostras cujo perfil espectral foge do padrão da própria classe — ex.: anomalias sutis (vazamento leve) que soam próximas do funcionamento normal, ou máquinas normais com ruído de fábrica atipicamente alto.

### Features mais discriminativas (média por classe)

| Feature | Média Normal | Média Anomalia | Diferença |
|---|---|---|---|
| `mfcc_35_mean` | 0.0697 | -1.2931 | -1954.3% |
| `mfcc_31_mean` | 0.1188 | -0.6089 | -612.4% |
| `mfcc_10_mean` | 0.1946 | 1.1339 | +482.6% |
| `mfcc_3_mean` | -1.5107 | -7.6651 | -407.4% |
| `mfcc_22_mean` | 0.1497 | -0.4596 | -407.0% |
| `mfcc_5_mean` | 1.6711 | -3.3167 | -298.5% |
| `mfcc_11_mean` | 1.2677 | -1.2929 | -202.0% |
| `mfcc_15_mean` | -1.2718 | 1.0604 | +183.4% |
| `mfcc_24_mean` | 0.6431 | -0.4969 | -177.3% |
| `mfcc_16_mean` | -1.1765 | 0.6971 | +159.3% |

## 5. Modelos Exportados (pickle)

| Arquivo | Conteúdo |
|---|---|
| `data/processed/models/mlp_sklearn_pipeline.pkl` | Pipeline sklearn (StandardScaler + MLPClassifier) pronto para inferência |
| `data/processed/models/mlp_hardcode.pkl` | Pesos e hiperparâmetros do hard-code (`carregar_modelo()`) |
| `data/processed/models/scaler.pkl` | StandardScaler ajustado no treino (para o hard-code) |
| `data/processed/models/feature_names.pkl` | Ordem das features esperada pelos modelos |

Exemplo de inferência:

```python
import pickle
with open('data/processed/models/mlp_sklearn_pipeline.pkl', 'rb') as f:
    pipeline = pickle.load(f)
proba = pipeline.predict_proba(X_novo)[:, 1]  # P(anomalia)
```

## 6. Limitações e Riscos

- Dataset desbalanceado (~5:1 normal:anomalia) — accuracy isolada engana; priorizar recall/F1 da classe anomalia.
- Modelo treinado com bombas específicas (id_00/02/04/06) e ruído de fábrica a 0 dB SNR — generalização para outras bombas/ambientes não é garantida.
- Threshold de decisão fixo em 0.5 — em produção, ajustar conforme o custo relativo de falso positivo (parada desnecessária) vs falso negativo (falha não detectada).
- Features agregadas por clip (médias) descartam a dinâmica temporal do som.
