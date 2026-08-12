---
title: "Atualização do Vault para o Projeto MIMII Pump"
date: 2026-08-11
tags:
  - analise
  - vault
  - documentacao
  - atualizacao
---

# Atualização do Vault para o Projeto MIMII Pump

**Data:** 2026-08-11

## O que foi feito

O vault ainda documentava o **projeto descartado** (Previsão de Satisfação em E-commerce: NLP + CV + Naive Bayes). Todas as notas foram revisadas e atualizadas para o **projeto atual aprovado: Manutenção Preditiva Industrial com Som (MIMII Pump)**.

### Arquivos reescritos

- `Home.md`, `Bem-vindo.md` e `Canvas do Projeto.canvas` — tema, navegação, progresso e canvas
- `01-Plano-Geral.md` — problema de negócio (bomba com anomalia), fontes (Zenodo), tipos de dados (estruturado + áudio), tecnologias (librosa, MLP)
- `02-Datasets.md` — MIMII Pump: 4.205 clipes, condições normal/anomalia, 4 modelos, estrutura de diretórios, nomenclatura `abnormal`→`anomaly`
- `03-Arquitetura.md` — ajuste dos diagramas para o fluxo de áudio
- `04-Pipeline-ELT.md` — 8 etapas atuais (download → upload → metadados → features → merge → load → dbt → ML), DAG sequencial
- `05-Modelagem-dbt.md` — 5 modelos reais (stg_pump_metadata, stg_audio_features, dim_machines, fact_audio_analysis, ml_features) e 16 testes
- `06-Machine-Learning.md` — MLP binário, 92 features de áudio, arquitetura (64,32), métricas reais (~98% acurácia), matriz de confusão
- `07-Dashboard.md` — 3 dashboards do Metabase + filtro `{{model_id}}` + credenciais corretas
- `08-Cronograma.md` e `09-Checklist-Entrega.md` — tarefas do MIMII, marcadas como concluídas (32/32)
- `10-Infra-AWS.md`, `11-Comandos.md`, `12-Passo-a-Passo.md` — scripts, Makefile e modelos atualizados

### Conceitos Gerais

- **Removidos:** `Conceito - NLP e TF-IDF.md`, `Conceito - Visao Computacional.md` (obsoletos)
- **Substituído:** `Conceito - Naive Bayes.md` → `Conceito - Rede Neural MLP.md`
- **Criado:** `Conceito - MFCC e Features de Audio.md`
- **Atualizados:** DAG no Airflow (8 tasks sequenciais), Pipeline ELT e dbt e Modelagem (5 modelos, 16 testes)

### Dúvidas

- **Reescrita:** `Duvida - O que estamos fazendo neste projeto`
- **Substituída:** `Duvida - Compatibilidade entre os Datasets` → `Duvida - Por que o dataset MIMII Pump`

## Motivo

O vault é a documentação oficial do projeto e deve refletir o tema aprovado pela banca. Notas desatualizadas (vendas, NLP, CV, Naive Bayes) confundiriam a apresentação e a consulta futura.

## Impacto

- Arquivos afetados: todo `.docs-projeto-final/` (reescritura + `git mv`/`git rm` preservando histórico)
- Índices de `Análise`, `Dúvidas` e `Conceitos Gerais` atualizados
- Notas históricas de `Análise/` mantidas como registro (com links corrigidos)
- `workspace.json` ajustado para os novos nomes
- Nenhum wikilink quebrado (validado por script)

## Relacionado

- [[Análise/Análise]]
- [[Home]]
- [[06-Machine-Learning]]
