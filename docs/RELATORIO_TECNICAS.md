# Relatório Técnico — Normalização dos Áudios e Comparação Hard-Code × Sklearn

Dados de referência: dataset MIMII Pump real (0 dB SNR), 4.205 clips, teste com 841 amostras (750 normais, 91 anomalias). Números extraídos da última execução de `ml/evaluate.py` (`data/processed/predictions.csv`).

---

## 1. Técnicas de normalização dos áudios

A normalização acontece em **duas camadas**: no sinal de áudio (durante a extração de features, `processing/extract_audio_features.py`) e nas features numéricas (antes do treino, `ml/evaluate.py`).

### 1.1 Normalização no nível do sinal (librosa)

| # | Técnica | Onde | O que faz |
|---|---|---|---|
| 1 | **Normalização de amplitude para [-1, 1]** | `librosa.load()` | Converte PCM 16-bit inteiro (−32768..32767) para float32 no intervalo [−1, 1] (divisão por 2¹⁵). Todos os clips passam a compartilhar a mesma escala numérica. |
| 2 | **Downmix 8 canais → mono** | `librosa.load(mono=True)` | O MIMII é gravado com array de 8 microfones; o downmix tira a **média dos canais**, produzindo um único sinal e eliminando a variação de posição de microfone como fator. |
| 3 | **Taxa de amostragem fixa (16 kHz)** | `librosa.load(sr=16000)` | Reamostra qualquer entrada para 16 kHz. No MIMII é um no-op (já é 16 kHz), mas garante que áudio de outra origem passe pelo mesmo eixo de frequências — as features ficam comparáveis por construção. |
| 4 | **Compressão logarítmica (dB) no espectro** | MFCC (interno) | O cálculo dos MFCCs aplica log na energia das bandas mel. Isso normaliza a faixa dinâmica: um ganho multiplicativo no volume (microfone mais perto/longe) vira um deslocamento aditivo constante, concentrado nos primeiros coeficientes — os demais ficam robustos a variação de ganho. |
| 5 | **Escala mel + DCT** | MFCC (interno) | A escala mel normaliza o eixo de frequência para a resolução perceptual; a DCT decorrelaciona os coeficientes — cada um carrega informação aproximadamente independente. |
| 6 | **Agregação temporal (média e desvio por coeficiente)** | `np.mean`/`np.std` sobre os frames | Reduz cada clip (~430 frames de 10 s) a um vetor de **tamanho fixo com 92 features**, independente da duração. É o que torna clips diferentes diretamente comparáveis num modelo tabular. |

### 1.2 Normalização no nível das features (pré-treino)

| # | Técnica | Onde | O que faz |
|---|---|---|---|
| 7 | **Preenchimento de nulos com 0** | `merge_features.py` / `evaluate.py` | Garante matriz densa após o LEFT JOIN. |
| 8 | **Padronização z-score (StandardScaler)** | `evaluate.py` | Cada uma das 96 features numéricas é transformada para média 0 e desvio 1. **Ajustado somente no treino** e aplicado ao teste (sem vazamento de dados). É crítica para o MLP: sem ela, features com escalas muito diferentes (ex.: `spectral_rolloff` em milhares vs `zcr` em centésimos) desequilibram os gradientes; a inicialização He pressupõe entradas padronizadas. O scaler ajustado é exportado (`models/scaler.pkl` e embutido no pipeline sklearn) para que a inferência em produção aplique exatamente a mesma transformação. |

### 1.3 O que deliberadamente NÃO normalizamos (e por quê)

- **Volume/energia por clip (peak ou RMS normalization):** *não* aplicamos. A energia do sinal (`rms_mean`) é um dos sinais discriminativos de anomalia (impactos, cavitação); normalizar o volume clip a clip apagaria essa informação.
- **Trimming de silêncio:** som industrial é contínuo — não há silêncio a remover.
- **Pre-emphasis / augmentation (pitch shift, time stretch):** não usados nesta versão; augmentation está listado como melhoria futura.

---

## 2. Hard-Code (NumPy) × Sklearn (MLPClassifier)

### 2.1 O que é idêntico (garantia de comparação justa)

Mesma arquitetura (96 → 64 → 32 → 1, ReLU nas ocultas, sigmoid na saída), mesma loss (binary cross-entropy), mesmo split 80/20 estratificado com `random_state=42`, mesmo StandardScaler, mesmo threshold de decisão (0,5).

### 2.2 O que é diferente

| Aspecto | Hard-Code (`HardCodedMLP`) | Sklearn (`MLPClassifier`) |
|---|---|---|
| **Otimizador** | Mini-batch **SGD com momento** (lr=0,01, momentum=0,9, batch=32) | **Adam** (lr=0,001, momentos adaptativos por parâmetro) |
| **Regularização** | Nenhuma | **L2 (alpha=0,0001)** por padrão |
| **Critério de parada** | 300 épocas fixas | Para quando a loss estabiliza (tol=1e-4, `n_iter_no_change=10`) |
| **Inicialização** | He (normal, √(2/fan_in)) | Glorot escalonada (uniforme) |
| **Aleatoriedade** | `np.random.seed(42)` — sequência própria de shuffles | `random_state=42` — gerador e ordem de consumo diferentes |
| **Implementação** | Loop Python + NumPy | Cython/BLAS otimizado |
| **Tempo de treino** | ~2.625 ms | ~425 ms (~6× mais rápido) |

Mesmo com "seed 42" nos dois, os geradores produzem **pesos iniciais e ordens de batch diferentes** — a seed igual não sincroniza nada entre as duas implementações.

### 2.3 Arquitetura e hiperparâmetros em detalhe

**Camadas (4 no total: entrada + 2 ocultas + saída):**

```
Camada de entrada :  96 neurônios (uma por feature normalizada)
Camada oculta 1   :  64 neurônios — ativação ReLU        (96×64 + 64 bias = 6.208 parâmetros)
Camada oculta 2   :  32 neurônios — ativação ReLU        (64×32 + 32 bias = 2.080 parâmetros)
Camada de saída   :   1 neurônio  — ativação Sigmoid     (32×1  + 1 bias  =    33 parâmetros)
                                                          Total: 8.321 parâmetros treináveis
```

**Funções de ativação:**

- **ReLU** (`max(0, z)`) nas duas camadas ocultas — não satura para valores positivos (evita gradientes que desaparecem), derivada trivial (0 ou 1) e combina com a inicialização He. No hard-code, forward e derivada estão em `_relu`/`_relu_derivative`; no sklearn, `activation="relu"`.
- **Sigmoid** (`1/(1+e^{-z})`) na camada de saída — comprime a saída para (0, 1), interpretável como P(anomalia), par natural da loss binary cross-entropy (a derivada combinada simplifica para `ŷ − y`). No sklearn é aplicada automaticamente em classificação binária (`out_activation_ = "logistic"`, verificado no modelo treinado).

**Taxa de aprendizado:**

| | Hard-Code | Sklearn |
|---|---|---|
| Valor | **0,01** (constante) | **0,001** (padrão do Adam) |
| Mecanismo | SGD com momento 0,9 — o momento acumula "velocidade" e permite lr maior sem oscilar | Adam adapta a taxa **por parâmetro** usando os momentos do gradiente — o 0,001 nominal vira um passo efetivo diferente para cada peso |

**Épocas de treinamento (valores da última execução, extraídos dos modelos exportados):**

| | Hard-Code | Sklearn |
|---|---|---|
| Configurado | 300 épocas fixas (batch=32) | `max_iter=500` com parada antecipada (tol=1e-4, 10 épocas sem melhora) |
| Efetivo | **300 épocas** (loss final 0,000034) | **58 épocas** (loss final 0,000829) |

O contraste é ilustrativo: o Adam do sklearn atingiu o platô em 58 épocas e parou; o hard-code seguiu até 300, chegando a uma loss de treino ~24× menor — que **não** se traduziu em métrica melhor no teste (97,86% vs 97,98%), um exemplo prático de que minimizar a loss de treino além do platô não melhora generalização.

### 2.4 Resultados lado a lado (teste, 841 amostras)

| Métrica | Hard-Code | Sklearn | Diferença |
|---|---|---|---|
| Accuracy | 97,86% | 97,98% | 0,12 p.p. (1 amostra) |
| Precision | 96,20% | 97,44% | 1 falso positivo a mais no hard-code |
| Recall | 83,52% | 83,52% | idêntico (15 FN cada) |
| F1-Score | 0,894 | 0,899 | — |
| Erros totais | 18 (3 FP + 15 FN) | 17 (2 FP + 15 FN) | 1 |

Anatomia da divergência (de `predictions.csv`):

- Em **832 de 841 amostras (98,9%) os dois modelos dão a mesma decisão**.
- **13 erros são comuns** aos dois — as mesmas anomalias sutis enganam ambos.
- Em **9 amostras eles discordam**: 5 erros exclusivos do hard-code e 4 exclusivos do sklearn (saldo líquido: 1 erro a mais no hard-code). Cada um acerta casos que o outro erra — ex.: o hard-code detecta `pump_id_02_anomaly_00000100` (P=0,98) que o sklearn deixa passar (P=0,27); o sklearn detecta `pump_id_06_anomaly_00000073` (P=0,99) que o hard-code descarta (P=0,02).

### 2.5 Por que existe discrepância, ainda que mínima

A função de custo de um MLP é **não-convexa**: existem muitos mínimos de qualidade equivalente, e qual deles é alcançado depende do ponto de partida e do caminho da otimização. As quatro causas concretas, em ordem de impacto:

1. **Trajetórias de otimização diferentes (Adam × SGD+momento).** Adam adapta a taxa de aprendizado por parâmetro; SGD+momento segue o gradiente com inércia constante. Partindo de pesos diferentes e percorrendo caminhos diferentes, cada um converge para um mínimo distinto — soluções igualmente boas globalmente, mas com **fronteiras de decisão que diferem exatamente nas regiões de baixa densidade** (as anomalias sutis, onde estão os 9 casos de discordância).
2. **Regularização L2 só no sklearn.** O termo `alpha=0,0001` penaliza pesos grandes e suaviza a fronteira de decisão — em fronteiras ligeiramente mais suaves, um ou outro ponto limítrofe muda de lado (é a origem provável do falso positivo a menos).
3. **Critérios de parada distintos.** O hard-code treina 300 épocas fixas e chega a loss ~3×10⁻⁵ (praticamente memoriza o treino, sem regularização); o sklearn interrompe quando a loss estabiliza. Graus de ajuste diferentes → generalização marginalmente diferente.
4. **Aleatoriedade não sincronizada** (inicialização e embaralhamento), como descrito em 2.2.

Importante: **não é ruído de arredondamento**. Nos 9 casos de discordância as probabilidades divergem fortemente (0,98 vs 0,27; 0,02 vs 0,99) — são fronteiras de decisão genuinamente diferentes, não a mesma fronteira com jitter em torno do threshold.

### 2.6 Conclusão

A concordância de 98,9% nas decisões e a diferença de uma única amostra nas métricas **validam a implementação manual**: forward pass, backpropagation e SGD do `HardCodedMLP` reproduzem o comportamento de uma biblioteca consolidada. A pequena vantagem do sklearn (1 FP a menos, 6× mais rápido) vem de refinamentos de engenharia — Adam, L2 e early stopping — e não de qualquer diferença conceitual do modelo. Esses refinamentos estão listados como melhorias futuras do hard-code.

---

## 3. O dataset traz um JSON de features pronto? Não — todas as features são extraídas por nós

O `0_dB_pump.zip` oficial do MIMII (Zenodo, record 3384388) contém **exclusivamente os 4.205 arquivos `.wav` brutos** organizados em `pump/id_XX/{normal,abnormal}/` — verificamos o conteúdo extraído: não há nenhum JSON, CSV ou arquivo de metadados/features acompanhando o dataset (os únicos arquivos não-`.wav` presentes são `.DS_Store` criados pelo macOS).

Consequências para o projeto:

- **As 92 features de áudio são 100% calculadas pelo nosso pipeline** (`processing/extract_audio_features.py`, com librosa) a partir do sinal bruto — nada é pré-fornecido pela Hitachi.
- **Os dados estruturados também são derivados por nós**: `machine_type`, `model_id` e `condition` vêm do parse dos caminhos dos arquivos, e `duration_sec`/`sample_rate`/`channels` da leitura do cabeçalho WAV com `soundfile`.
- Isso é um ponto forte para a banca: a etapa de "processamento e extração de atributos de dados não estruturados" (requisito 4.3) é integralmente autoral, e a rastreabilidade vai do `.wav` bruto até a predição (`file_id` liga áudio → features → tabelas dbt → `predictions.csv`).

*(Observação: o que existe de "features em JSON" no ecossistema MIMII são repositórios de terceiros/baselines do DCASE que publicam features já extraídas — não fazem parte do dataset oficial baixado e não foram usados.)*
