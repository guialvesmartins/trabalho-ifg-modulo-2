---
title: Dashboard
date: 2025-07-03
tags:
  - dashboard
  - metabase
  - visualizacao
aliases:
  - Metabase
  - Visualização
---

# Dashboard — Metabase

[[🏠 Home|Voltar ao índice]]

---

## Página 1 — Visão Geral

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **KPIs** | Number | Total de vendas, Rating médio, % Reviews negativas (<3), Total de produtos |
| **Rating por categoria** | Bar chart | Média de rating por categoria |
| **Evolução do rating** | Line chart | Rating médio ao longo do tempo (se houver data) |
| **Piores produtos** | Table | Top 10 produtos com pior rating |

---

## Página 2 — Análise de Sentimento (NLP)

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **Nuvem de palavras** | Word cloud | Top palavras em reviews positivas (4-5) vs negativas (1-2) |
| **Distribuição de polaridade** | Histogram | `polarity` agrupado por rating |
| **Complaint vs Praise** | Stacked bar | `contains_complaint` vs `contains_praise` por categoria |
| **Dissonância** | Table | Reviews com rating 5 mas polaridade negativa |

---

## Página 3 — Análise Visual (Imagem)

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **Imagens ruins** | Table | Produtos com `blur_score` alto e seu rating médio |
| **Brilho vs Rating** | Scatter plot | `brightness_mean` vs `rating` |
| **Cor dominante** | Bar chart | Cor dominante mais frequente por categoria |

> [!question] Hipóteses a testar
> Imagens escuras ou borradas estão associadas a ratings mais baixos?

---

## Página 4 — Resultados do Modelo ML

| Widget | Tipo | Descrição |
|--------|------|-----------|
| **Matriz de confusão** | Heatmap | 5x5 matriz de confusão |
| **Métricas por classe** | Table | Accuracy, Precision, Recall, F1 para cada rating |
| **Hard-code vs Sklearn** | Grouped bar | Comparação lado a lado |
| **Top features** | Bar chart | Palavras mais importantes para cada classe de rating |

---

## Filtros Globais

- [ ] Período (se disponível)
- [ ] Categoria do produto
- [ ] Faixa de preço
- [ ] Faixa de desconto
- [ ] Rating

---

## Configuração Automática

Ao rodar `make up`, o container `metabase-setup` configura automaticamente:
- Conexão com o banco PostgreSQL
- 4 dashboards com perguntas SQL pré-configuradas

**Acesso:**
- URL: [http://localhost:3000](http://localhost:3000)
- Email: `admin@projeto.com`
- Senha: `admin123`

> [!tip] Setup manual
> Se precisar reconfigurar, rode `make setup-metabase` a qualquer momento.
> Para ver o progresso da configuração: `make logs-setup`

---

## Configuração Manual (alternativa)

```bash
# Metabase disponível em
http://localhost:3000

# Conexão com o banco (PostgreSQL ou Snowflake)
Host: postgres (ou conta Snowflake)
Port: 5432
Database: airflow
User: airflow
Password: airflow
```

> [!info] Queries SQL
> As queries SQL de cada widget estão documentadas em `dashboard/metabase_questions.md`.
