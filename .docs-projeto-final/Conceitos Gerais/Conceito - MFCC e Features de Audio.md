---
title: "MFCC e Features de Áudio"
date: 2025-07-03
tags:
  - conceito
  - audio
  - mfcc
  - librosa
  - processamento
---

# MFCC e Features de Áudio

## Definição

Para que um modelo de machine learning "entenda" um som, é preciso transformar a onda de áudio em **números** — chamados de *features de áudio*. No projeto usamos a biblioteca **librosa** (Python) para extrair 92 features de cada clipe de 10 segundos de uma bomba industrial.

### MFCC (Mel-Frequency Cepstral Coefficients)

Os MFCC são a técnica mais usada para descrever o **timbre** de um som — o "formato" do espectro que diferencia uma voz de outra, ou uma bomba normal de uma com defeito.

1. O sinal é dividido em janelas curtas (ex: 25 ms)
2. Para cada janela calcula-se o espectro de frequências (FFT)
3. As frequências são convertidas para a **escala Mel** (que imita o ouvido humano)
4. Aplica-se o logaritmo e a transformada cosseno → obtém-se **coeficientes cepstrais**

Usamos **40 coeficientes** e, para cada um, a **média** e o **desvio padrão** ao longo do clipe (80 features). A média captura o timbre "médio"; o desvio captura como ele varia no tempo.

### Features Espectrais (10)

| Feature | O que mede |
|---------|-----------|
| `spectral_centroid` | Centro de massa do espectro — grave vs agudo |
| `spectral_bandwidth` | Largura da banda espectral |
| `spectral_rolloff` | Frequência abaixo de 85% da energia |
| `spectral_contrast_1..7` | Diferença entre picos e vales em 7 bandas |

### Energia e Ritmo (2)

| Feature | O que mede |
|---------|-----------|
| `zero_crossing_rate` (ZCR) | Quantas vezes o sinal cruza o zero — relacionado à frequência dominante |
| `root_mean_square` (RMS) | Energia/potência do sinal — "quão alto" o som está |

## Como foi implementado no projeto

**Arquivo:** `processing/extract_audio_features.py`

```python
import librosa

y, sr = librosa.load(wav_path, sr=16000, mono=True)  # downmix dos 8 canais

mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)      # 40 coeficientes
mfcc_mean = np.mean(mfcc, axis=1)                        # média de cada um
mfcc_std  = np.std(mfcc, axis=1)                         # desvio de cada um
```

O MIMII foi gravado com 8 microfones; `mono=True` faz o downmix para um único canal. As 92 features resultantes alimentam o MLP (96 features numéricas no total, somando os metadados).

## Relacionado

- [[06-Machine-Learning]]
- [[02-Datasets]]
- [[04-Pipeline-ELT]]
