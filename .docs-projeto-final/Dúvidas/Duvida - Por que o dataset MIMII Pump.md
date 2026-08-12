---
title: "Por que o dataset MIMII Pump"
date: 2025-07-03
tags:
  - duvida
  - datasets
  - mimii
  - audio
  - escolha
---

# Por que o dataset MIMII Pump

## A pergunta

> [!question] Por que usamos o MIMII (Pump) e não outro dataset? Por que só o som da bomba?

## A resposta

### O requisito do projeto

O trabalho precisa de **dados estruturados E não estruturados** para alimentar um modelo de ML — e o pipeline de dados (Airflow, dbt, Snowflake/S3, dashboard) precisa de uma fonte real e verificável.

### Tentativas anteriores

- **1ª tentativa:** Previsão de satisfação em e-commerce (dados estruturados + reviews com NLP + imagens com CV). **Descartada** — o grupo não aceitou o dataset e a abordagem.
- **2ª tentativa:** Buscamos datasets industriais no Kaggle com dados estruturados + áudio verificados. Nenhum atendia.
- **Candidato avaliado:** MIMII do Zenodo — mas só com motor industrial. O MIMII real tem fan, pump, slider e valve, **sem motor dedicado**.

### A escolha final

O **MIMII Dataset (Pump)** atende todos os requisitos:

| Requisito | Como o MIMII atende |
|-----------|--------------------|
| Dados estruturados | Metadados extraídos dos paths (tipo, modelo, condição, duração, sample rate) |
| Dados não estruturados | Clipes `.wav` de 10 s, 16 kHz, de bombas industriais em fábrica real |
| Origem confiável | Hitachi / Toyota Research (DCASE 2019), licença CC BY-SA 4.0, disponível no Zenodo |
| Tamanho suficiente | 4.205 clipes (3.749 normal + 456 anomalia) |
| Download por script | `download_dataset.py` baixa o zip do Zenodo via `requests` |

### Por que só `pump`?

- O escopo pede uma **tarefa de ML bem definida** — treinar para vários tipos de máquina misturados degradaria o modelo (cada máquina tem assinatura sonora diferente)
- Focamos em **um tipo de equipamento** (bomba) com 4 modelos físicos distintos (`id_00`, `id_02`, `id_04`, `id_06`), o que dá variação realista sem perder foco
- Anomalias reais: contaminação, vazamento e desbalanceamento — problemas típicos de manutenção

> [!note] Nomenclatura
> O dataset real usa `abnormal`; o pipeline normaliza para `anomaly` via `CONDITION_MAP`, pois todo o restante do projeto (dbt, ML, Metabase) usa `anomaly`.

## Relacionado

- [[02-Datasets]]
- [[01-Plano-Geral]]
