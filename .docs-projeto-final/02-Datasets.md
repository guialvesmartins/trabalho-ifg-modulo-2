---
title: Datasets
date: 2025-07-03
tags:
  - dados
  - datasets
  - mimii
  - audio
aliases:
  - Dados
  - Fontes de Dados
---

# Datasets

[[Home|Voltar ao índice]]

---

## MIMII Dataset — Pump (Principal)

| Atributo | Valor |
|----------|-------|
| **Criador** | Hitachi, Ltd. / Toyota Research |
| **Publicação** | DCASE 2019 Workshop ([arXiv:1909.09347](https://arxiv.org/abs/1909.09347)) |
| **Licença** | CC BY-SA 4.0 |
| **Link** | [Zenodo — 0_dB_pump.zip](https://zenodo.org/records/3384388) |
| **Tamanho** | ~7,87 GB |
| **Total** | 4.205 clipes de áudio (10 s, 16 kHz) |
| **Arquivo** | `data/raw/pump/` |

### Condições

| Condição | Clipes | Descrição |
|----------|--------|-----------|
| `normal` | 3.749 | Funcionamento normal da bomba |
| `anomaly` | 456 | Contaminação, vazamento, desbalanceamento |

> [!warning] Desbalanceamento
> Taxa de anomalia de ~10,8% (proporção ~8:1). Por isso o split usa `stratify` e a avaliação prioriza recall/F1 da classe minoritária.

### Modelos de Bomba (4)

`id_00`, `id_02`, `id_04`, `id_06`

### Estrutura de Diretórios

```
pump/
├── id_00/
│   ├── normal/    (*.wav)
│   └── abnormal/  (*.wav)
├── id_02/ ...
├── id_04/ ...
└── id_06/ ...
```

> [!important] Nomenclatura
> O dataset real usa `id_XX` e `abnormal`. O pipeline normaliza `abnormal` → `anomaly` (constante `CONDITION_MAP` em `process_structured.py` e `extract_audio_features.py`). Todo o restante (dbt, ML, Metabase) usa `anomaly`.

---

## Características do Áudio

- 16 kHz de sample rate, 16 bits por amostra
- Gravado com array de 8 microfones (**8 canais**)
- Misturado com ruído real de fábrica (0 dB SNR)
- `librosa.load(mono=True)` faz downmix na extração de features
- Clipes de 10 segundos

---

## Colunas Estruturadas

| Coluna | Tipo | Uso |
|--------|------|-----|
| `file_id` | Texto | Chave única (`machine_type_model_id_condition_stem`) |
| `machine_type` | Categórico | `pump` |
| `model_id` | Categórico | `id_00`, `id_02`, `id_04`, `id_06` |
| `condition` | Categórico | `normal` / `anomaly` |
| `condition_binary` | Numérico (0/1) | **🎯 Target do modelo** (anomaly=1) |
| `duration_sec` | Numérico | Duração do clipe |
| `sample_rate` | Numérico | 16000 |
| `channels` | Numérico | 8 |

---

## Download

```bash
# Via Makefile
make ingest

# Manual (scripts Python)
python ingestion/download_dataset.py    # Baixa 0_dB_pump.zip do Zenodo → data/raw/
python ingestion/load_raw_to_s3.py      # Upload .wav → MinIO/S3
```

> [!tip] Download retomável
> `download_dataset.py` suporta retomada de download interrompido (HTTP Range) e remove dados sintéticos legados (`model_id_XX/`) antes de extrair o dataset real.

---

## Estrutura no S3/MinIO

```
bucket/
└── raw/
    └── pump/
        ├── id_00/
        │   ├── normal/
        │   └── abnormal/
        ├── id_02/
        ├── id_04/
        └── id_06/
```
