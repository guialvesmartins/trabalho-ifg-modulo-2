---
title: "Configuracao Automatica do Metabase"
date: 2025-07-03
tags:
  - analise
  - metabase
  - dashboard
  - automacao
---

# Configuracao Automatica do Metabase

**Data:** 2025-07-03

## O que foi feito

Criado script `scripts/setup_metabase.py` que configura automaticamente o Metabase via API REST, eliminando a necessidade de configuracao manual pela interface web.

O script:
1. Aguarda o Metabase iniciar (health check)
2. Cria usuario admin no primeiro acesso (ou faz login)
3. Adiciona o PostgreSQL como data source
4. Sincroniza o schema do banco
5. Cria 10 perguntas SQL (cards) com visualizacoes pre-definidas (scalar, bar, table, scatter)
6. Cria 4 dashboards e adiciona os cards correspondentes

Adicionado servico `metabase-setup` no `docker-compose.yml` que roda automaticamente apos o Metabase estar pronto.

## Impacto

Arquivos alterados:
- `scripts/setup_metabase.py` — script de configuracao automatica
- `docker-compose.yml` — adicionado servico metabase-setup
- `Makefile` — adicionados comandos `setup-metabase` e `logs-setup`
- `.docs-projeto-final/07-Dashboard.md` — atualizado com instrucoes

Acesso apos `make up`:
- URL: http://localhost:3000
- Login: admin@projeto.com / admin123

## Relacionado

- [[07-Dashboard]]
- [[🏠 Home]]
