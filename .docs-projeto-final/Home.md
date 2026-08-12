---
title: Home
date: 2025-07-03
tags:
  - projeto-final
  - ifg
  - ia
  - indice
status: em-andamento
semana-atual: 1
---

# Projeto Final Integrado — Módulo 2

**Curso:** Pós-Graduação em Inteligência Artificial Aplicada — IFG
**Tema:** Previsão de Satisfação em E-commerce com Dados Multimodais

> [!abstract] Objetivo
> Classificar automaticamente o rating (1 a 5 estrelas) de produtos de e-commerce combinando **dados estruturados**, **reviews textuais** e **imagens de produtos**.

---

## Navegação

| Seção | Nota | Descrição |
|-------|------|-----------|
| 📋 Plano | [[01-Plano-Geral]] | Definição do problema, escopo e resultado esperado |
| 📊 Dados | [[02-Datasets]] | Fontes de dados, colunas e dicionário |
| 🏗️ Arquitetura | [[03-Arquitetura]] | Ambiente dev, prod e AWS |
| ⚙️ Pipeline | [[04-Pipeline-ELT]] | 8 etapas do pipeline ELT |
| 🗄️ dbt | [[05-Modelagem-dbt]] | Schema estrela, modelos e testes |
| 🤖 ML | [[06-Machine-Learning]] | Features, Naive Bayes e avaliação |
| 📈 Dashboard | [[07-Dashboard]] | 4 páginas do Metabase |
| 📅 Cronograma | [[08-Cronograma]] | Planejamento semanal |
| ✅ Checklist | [[09-Checklist-Entrega]] | Requisitos do PDF mapeados |
| ☁️ Infra AWS | [[10-Infra-AWS]] | CloudFormation e serviços |
| 🚀 Passo a Passo | [[12-Passo-a-Passo]] | Guia de implementação semana a semana |
| 🔧 Comandos | [[11-Comandos]] | Referência rápida de comandos |
| Análise | [[Análise/Análise]] | Registro de mudanças e decisões |
| Dúvidas | [[Dúvidas/Dúvidas]] | Perguntas e respostas |
| Conceitos | [[Conceitos Gerais/Conceitos Gerais]] | Fundamentos e teoria |

> [!tip] Visão Visual
> Abra o [[Canvas do Projeto]] para uma visão geral gráfica do projeto.

---

## Progresso Geral

| Semana | Status | Tópico |
|--------|--------|--------|
| 1 | `em-andamento` | Docker, serviços base (Postgres, MinIO, Airflow, Metabase) |
| 2 | `pendente` | Datasets, ingestão, download de imagens |
| 3 | `pendente` | Processamento: NLP + CV + merge |
| 4 | `pendente` | Projeto dbt completo |
| 5 | `pendente` | DAG Airflow orquestrando tudo |
| 6 | `pendente` | Naive Bayes hard-code + sklearn + avaliação |
| 7 | `pendente` | Dashboard Metabase (4 páginas) |
| 8 | `pendente` | Infra, CloudFormation, relatório, apresentação |

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
make ingest      # Baixa datasets e sobe pro S3
make ml-train    # Treina e avalia modelos
```

%% ════════════════════════════════════════════ %%
%% Disciplinas: Aprendizagem de Máquina · Cloud Computing · Modelagem de Dados %%
%% ════════════════════════════════════════════ %%
