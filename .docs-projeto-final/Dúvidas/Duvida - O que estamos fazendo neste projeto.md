---
title: "O que estamos fazendo neste projeto"
date: 2025-07-03
tags:
  - duvida
  - visao-geral
  - explicacao
  - passo-a-passo
---

# O que estamos fazendo neste projeto

## A pergunta

> [!question] O que exatamente estamos construindo, como estamos fazendo e qual o objetivo final?

## A resposta

### Em uma frase

Estamos construindo um sistema de **manutenção preditiva industrial** que escuta o som de bombas e responde: **"esta bomba está com anomalia? Devo parar para manutenção?"**

### O objetivo final

O engenheiro de manutenção abre o dashboard, vê quais bombas têm maior chance de estar com anomalia e age ANTES que a falha aconteça. Paradas não programadas custam caro (produção parada, reparo emergencial), e manutenções desnecessárias também têm custo. O sistema analisa o som e classifica automaticamente.

### Como estamos fazendo — passo a passo

1. **Baixamos os dados**: o dataset **MIMII Pump** (Hitachi/Toyota, ~7,87 GB) do Zenodo — 4.205 clipes de som de bombas industriais reais, entre `normal` e `anomalia` (contaminação, vazamento, desbalanceamento).

2. **Subimos os `.wav` pro MinIO** (um "S3 de mentira" que roda no seu computador via Docker). Em produção, seria o S3 da AWS de verdade — troca 4 linhas no `.env` e funciona igual.

3. **Extraímos os metadados**: percorremos os paths (`pump/id_XX/normal|abnormal/*.wav`) e montamos uma tabela com `model_id`, `condition`, duração, sample rate e o target `condition_binary`.

4. **Transformamos o som em números**: com **librosa**, extraímos 92 features de cada clipe — MFCC (timbre), features espectrais, zero-crossing rate e RMS (energia).

5. **Juntamos tudo** em uma tabela única com 103 colunas (96 features numéricas).

6. **Carregamos no banco** e organizamos com **dbt** em schema estrela: dimensão de máquinas (`dim_machines`), fato de análise de áudio (`fact_audio_analysis`) e a tabela final `ml_features`.

7. **O Airflow orquestra tudo**: uma DAG (arquivo Python) define a ordem: baixar → subir → metadados → features → merge → banco → dbt → treinar modelo.

8. **Treinamos o modelo**: uma **rede neural MLP** binária (normal vs anomalia). Implementamos duas vezes: uma do zero com NumPy (hard-code, para aprender a matemática) e uma com biblioteca pronta (sklearn, para comparar). Também comparamos com baselines (majoritária e regressão logística).

9. **Visualizamos no Metabase**: 3 dashboards com KPIs, análise de áudio por modelo e resultados do ML. Tudo configurado automaticamente via script.

### O que já está pronto

- Docker com 6 serviços rodando (Postgres, MinIO, Airflow, Metabase)
- Pipeline de ponta a ponta implementado e testado
- Modelo MLP treinado no dataset real com **~98% de acurácia** (recall da anomalia 83,5%)
- Dashboards do Metabase com filtro por modelo de máquina
- Estrutura pronta para S3 e Snowflake (troca de ambiente com 4 variáveis)
- Relatório `report_analys.md`, CloudFormation e apresentação

## Relacionado

- [[Home]]
- [[12-Passo-a-Passo]]
- [[09-Checklist-Entrega]]
