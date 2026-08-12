---
title: Home
date: 2025-07-03
tags:
  - projeto-final
  - ifg
  - ia
  - indice
status: concluido
semana-atual: 8
---

# Projeto Final Integrado — Módulo 2

**Curso:** Pós-Graduação em Inteligência Artificial Aplicada — IFG
**Tema:** Manutenção Preditiva Industrial com Som (MIMII Pump)

> [!abstract] Objetivo
> Analisar o som de bombas industriais e classificar automaticamente se cada bomba está **normal** ou com **anomalia** (contaminação, vazamento, desbalanceamento), apoiando a decisão de manutenção preventiva.

---

## Navegação

| Seção | Nota | Descrição |
|-------|------|-----------|
| Plano | [[01-Plano-Geral]] | Definição do problema, escopo e resultado esperado |
| Dados | [[02-Datasets]] | MIMII Pump: estrutura, condições e download |
| Arquitetura | [[03-Arquitetura]] | Ambiente dev, prod e AWS |
| Pipeline | [[04-Pipeline-ELT]] | 8 etapas do pipeline ELT |
| dbt | [[05-Modelagem-dbt]] | Schema estrela, modelos e testes |
| ML | [[06-Machine-Learning]] | Features de áudio, MLP e avaliação |
| Dashboard | [[07-Dashboard]] | 3 dashboards do Metabase |
| Cronograma | [[08-Cronograma]] | Planejamento semanal |
| Checklist | [[09-Checklist-Entrega]] | Requisitos do PDF mapeados |
| Infra AWS | [[10-Infra-AWS]] | CloudFormation e serviços |
| Passo a Passo | [[12-Passo-a-Passo]] | Guia de implementação semana a semana |
| Comandos | [[11-Comandos]] | Referência rápida de comandos |
| Análise | [[Análise/Análise]] | Registro de mudanças e decisões |
| Dúvidas | [[Dúvidas/Dúvidas]] | Perguntas e respostas |
| Conceitos | [[Conceitos Gerais/Conceitos Gerais]] | Fundamentos e teoria |

> [!tip] Visão Visual
> Abra o [[Canvas do Projeto]] para uma visão geral gráfica do projeto.

---

## Progresso Geral

| Semana | Status | Tópico |
|--------|--------|--------|
| 1 | `concluído` | Docker, serviços base (Postgres, MinIO, Airflow, Metabase) |
| 2 | `concluído` | Download MIMII Pump + upload para S3/MinIO |
| 3 | `concluído` | Metadados + features de áudio (librosa) + merge |
| 4 | `concluído` | Projeto dbt completo (5 modelos, 14 testes) |
| 5 | `concluído` | DAG Airflow orquestrando tudo |
| 6 | `concluído` | MLP hard-code + sklearn + avaliação |
| 7 | `concluído` | Dashboard Metabase (3 dashboards) |
| 8 | `concluído` | Infra, CloudFormation, relatório, apresentação |

---

## Links Rápidos

| Serviço | URL |
|---------|-----|
| Airflow | [http://localhost:8080](http://localhost:8080) |
| Metabase | [http://localhost:3000](http://localhost:3000) |
| MinIO Console | [http://localhost:9001](http://localhost:9001) |
| MinIO API | [http://localhost:9000](http://localhost:9000) |

---

## Comandos Essenciais

```bash
make up          # Sobe ambiente + configura Metabase automaticamente
make down        # Derruba ambiente
make pipeline    # Dispara pipeline completo
make test        # Roda testes
make ingest      # Baixa MIMII e sobe pro S3
make process     # Metadados + features de áudio + merge
make load-db     # Carrega CSV no PostgreSQL
make dbt-run     # dbt run
make ml-train    # Treina e avalia modelos
```

%% ════════════════════════════════════════════ %%
%% Disciplinas: Aprendizagem de Máquina · Cloud Computing · Modelagem de Dados %%
%% ════════════════════════════════════════════ %%
