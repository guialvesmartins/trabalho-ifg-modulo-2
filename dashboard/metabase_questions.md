---
title: "Dashboard Metabase — Projeto Final"
date: 2026-07-03
tags:
  - dashboard
  - metabase
  - sql
  - ecommerce
---

# Dashboard Metabase — Pipeline de Dados e Machine Learning em E-commerce

> [!info] Objetivo
> Este documento contém todas as queries SQL e configurações necessárias para montar o dashboard no Metabase, conectado ao banco de dados PostgreSQL onde o dbt materializou as tabelas do data warehouse.

---

## 1. Configuração do Metabase

### Conexão com o PostgreSQL

1. Acesse o Metabase em `http://<host>:3000`
2. Vá em **Admin** > **Bancos de Dados** > **Adicionar banco de dados**
3. Preencha os campos:

| Campo              | Valor                                |
|--------------------|--------------------------------------|
| Tipo de banco      | PostgreSQL                           |
| Nome               | `ecommerce-dw`                       |
| Host               | `<endereço-do-rds>`                  |
| Porta              | `5432`                               |
| Nome do banco      | `ecommerce`                          |
| Nome de usuário    | `metabase_user`                      |
| Senha              | `********`                           |
| Schemas            | `analytics`                          |

4. Clique em **Salvar**

> [!warning] Atenção
> O usuário `metabase_user` deve ter permissão apenas de leitura (`SELECT`) nas tabelas do schema `analytics`. Nunca utilize o usuário `admin` ou `dbt_user` para o Metabase.

---

## 2. Página 1 — Visão Geral

> [!abstract] Descrição
> Painel principal com indicadores de alto nível sobre o catálogo de produtos e as avaliações dos clientes.

### 2.1 KPI — Total de Produtos

**Tipo:** Cartão de Número (Number Card / KPI)

```sql
SELECT COUNT(*) AS total_produtos
FROM analytics.dim_products
WHERE is_active = TRUE
```

### 2.2 KPI — Nota Média Geral

**Tipo:** Cartão de Número (Number Card / KPI)

```sql
SELECT ROUND(AVG(rating), 2) AS nota_media_geral
FROM analytics.fact_reviews
WHERE rating IS NOT NULL
```

### 2.3 KPI — Percentual de Avaliações Negativas

**Tipo:** Cartão de Número com Progresso (Progress Card)

```sql
SELECT
    ROUND(
        100.0 * COUNT(CASE WHEN rating <= 2 THEN 1 END) / COUNT(*),
        1
    ) AS pct_avaliacoes_negativas
FROM analytics.fact_reviews
WHERE rating IS NOT NULL
```

### 2.4 KPI — Total de Avaliações

**Tipo:** Cartão de Número (Number Card / KPI)

```sql
SELECT COUNT(*) AS total_avaliacoes
FROM analytics.fact_reviews
```

### 2.5 Gráfico de Barras — Nota Média por Categoria

**Tipo:** Gráfico de Barras (Bar Chart)
- **Eixo X:** `categoria_nome`
- **Eixo Y:** `nota_media`
- **Ordenação:** Decrescente pela nota média

```sql
SELECT
    c.categoria_nome,
    ROUND(AVG(f.rating), 2) AS nota_media,
    COUNT(f.review_id) AS qtde_avaliacoes
FROM analytics.fact_reviews f
INNER JOIN analytics.dim_products p
    ON f.product_id = p.product_id
INNER JOIN analytics.dim_categories c
    ON p.category_id = c.category_id
WHERE f.rating IS NOT NULL
GROUP BY c.categoria_nome
HAVING COUNT(f.review_id) >= 5
ORDER BY nota_media DESC
```

### 2.6 Tabela — Top 10 Produtos com Pior Avaliação

**Tipo:** Tabela (Table)
- **Colunas:** `product_id`, `titulo_produto`, `nota_media`, `qtde_avaliacoes`, `categoria_nome`

```sql
SELECT
    p.product_id,
    p.titulo_produto,
    ROUND(AVG(f.rating), 2) AS nota_media,
    COUNT(f.review_id) AS qtde_avaliacoes,
    c.categoria_nome
FROM analytics.fact_reviews f
INNER JOIN analytics.dim_products p
    ON f.product_id = p.product_id
INNER JOIN analytics.dim_categories c
    ON p.category_id = c.category_id
WHERE f.rating IS NOT NULL
  AND p.is_active = TRUE
GROUP BY p.product_id, p.titulo_produto, c.categoria_nome
HAVING COUNT(f.review_id) >= 3
ORDER BY nota_media ASC
LIMIT 10
```

---

## 3. Página 2 — Análise de Sentimento

> [!abstract] Descrição
> Análise detalhada da polaridade (sentimento) das avaliações, cruzando com as notas atribuídas pelos clientes.

### 3.1 Distribuição de Polaridade por Nota (Histograma)

**Tipo:** Gráfico de Barras Empilhadas (Stacked Bar Chart)
- **Eixo X:** `rating` (1 a 5)
- **Eixo Y:** quantidade de avaliações
- **Série (stack):** faixa de polaridade (negativa, neutra, positiva)

```sql
SELECT
    f.rating,
    CASE
        WHEN ml.polarity IS NULL THEN 'sem_analise'
        WHEN ml.polarity < -0.05 THEN 'negativa'
        WHEN ml.polarity > 0.05 THEN 'positiva'
        ELSE 'neutra'
    END AS faixa_polaridade,
    COUNT(*) AS qtde_avaliacoes
FROM analytics.fact_reviews f
LEFT JOIN analytics.ml_features ml
    ON f.review_id = ml.review_id
WHERE f.rating IS NOT NULL
GROUP BY f.rating, faixa_polaridade
ORDER BY f.rating, faixa_polaridade
```

### 3.2 Tabela — Produtos com Nota 5 mas Polaridade Negativa (Dissonância)

**Tipo:** Tabela (Table)
- **Colunas:** `product_id`, `titulo_produto`, `review_text`, `rating`, `polarity`

```sql
SELECT
    p.product_id,
    p.titulo_produto,
    LEFT(f.review_text, 200) AS review_text,
    f.rating,
    ml.polarity,
    ml.subjectivity
FROM analytics.fact_reviews f
INNER JOIN analytics.dim_products p
    ON f.product_id = p.product_id
INNER JOIN analytics.ml_features ml
    ON f.review_id = ml.review_id
WHERE f.rating = 5
  AND ml.polarity < -0.1
ORDER BY ml.polarity ASC
```

> [!tip] Insight
> Avaliações com nota máxima (5) mas polaridade negativa indicam dissonância entre a nota e o conteúdo textual. Esses casos merecem investigação — podem ser fraudes, erros de cadastro ou clientes que deram nota alta por inércia mas expressaram insatisfação no texto.

---

## 4. Página 3 — Análise Visual

> [!abstract] Descrição
> Cruzamento das métricas de qualidade de imagem dos produtos com as avaliações recebidas.

### 4.1 Tabela — Produtos com Alta Pontuação de Desfoque (blur_score)

**Tipo:** Tabela (Table)
- **Colunas:** `product_id`, `titulo_produto`, `blur_score`, `nota_media`, `qtde_avaliacoes`

```sql
SELECT
    p.product_id,
    p.titulo_produto,
    mlf.blur_score,
    ROUND(AVG(f.rating), 2) AS nota_media,
    COUNT(f.review_id) AS qtde_avaliacoes
FROM analytics.ml_features mlf
INNER JOIN analytics.dim_products p
    ON mlf.product_id = p.product_id
LEFT JOIN analytics.fact_reviews f
    ON p.product_id = f.product_id
WHERE mlf.blur_score IS NOT NULL
  AND mlf.blur_score > 0.8
GROUP BY p.product_id, p.titulo_produto, mlf.blur_score
HAVING COUNT(f.review_id) >= 2
ORDER BY mlf.blur_score DESC
LIMIT 20
```

### 4.2 Gráfico de Dispersão — Brilho vs Nota Média

**Tipo:** Gráfico de Dispersão (Scatter Plot)
- **Eixo X:** `brightness` (brilho médio da imagem)
- **Eixo Y:** `nota_media`
- **Tamanho da bolha:** `qtde_avaliacoes`
- **Cor por:** `categoria_nome`

```sql
SELECT
    p.product_id,
    p.titulo_produto,
    mlf.brightness,
    ROUND(AVG(f.rating), 2) AS nota_media,
    COUNT(f.review_id) AS qtde_avaliacoes,
    c.categoria_nome
FROM analytics.ml_features mlf
INNER JOIN analytics.dim_products p
    ON mlf.product_id = p.product_id
INNER JOIN analytics.dim_categories c
    ON p.category_id = c.category_id
LEFT JOIN analytics.fact_reviews f
    ON p.product_id = f.product_id
WHERE mlf.brightness IS NOT NULL
  AND f.rating IS NOT NULL
GROUP BY p.product_id, p.titulo_produto, mlf.brightness, c.categoria_nome
ORDER BY nota_media DESC
```

---

## 5. Página 4 — Resultados de Machine Learning

> [!abstract] Descrição
> Visualização dos resultados do modelo de classificação de sentimento treinado no SageMaker, incluindo matriz de confusão e palavras mais relevantes por classe.

### 5.1 Dados para Matriz de Confusão

**Tipo:** Tabela (Table)
- **Colunas:** `rating_real`, `rating_predito`, `qtde`

```sql
SELECT
    rating_real,
    rating_predito,
    COUNT(*) AS qtde
FROM analytics.ml_predictions
WHERE split = 'test'
GROUP BY rating_real, rating_predito
ORDER BY rating_real, rating_predito
```

> [!note] Montagem no Metabase
> Use os dados dessa query em uma visualização **Pivot Table**:
> - **Linhas:** `rating_real`
> - **Colunas:** `rating_predito`
> - **Valor:** `qtde`
>
> Isso formará a matriz de confusão 5×5 automaticamente.

### 5.2 Top Palavras TF-IDF por Classe de Rating

**Tipo:** Gráfico de Barras (Bar Chart)
- **Eixo X:** `palavra`
- **Eixo Y:** `tfidf_score`
- **Filtro por:** `rating_classe`

```sql
SELECT
    palavra,
    rating_classe,
    tfidf_score
FROM analytics.tfidf_top_words
WHERE ranking <= 15
ORDER BY rating_classe, tfidf_score DESC
```

> [!tip] Dica
> Configure um filtro de dashboard para o campo `rating_classe` a fim de alternar entre as palavras mais importantes de cada nota (1 a 5).

### 5.3 Acurácia do Modelo por Classe de Rating

**Tipo:** Gráfico de Barras (Bar Chart)
- **Eixo X:** `rating_classe`
- **Eixo Y:** `acuracia`

```sql
SELECT
    rating_real AS rating_classe,
    ROUND(
        100.0 * SUM(CASE WHEN rating_real = rating_predito THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS acuracia
FROM analytics.ml_predictions
WHERE split = 'test'
GROUP BY rating_real
ORDER BY rating_real
```

---

## 6. Filtros Globais (Dashboard Filters)

> [!abstract] Descrição
> Os filtros globais permitem que o usuário refine todos os gráficos do dashboard simultaneamente. Configure-os no Metabase conforme abaixo.

### 6.1 Filtro — Categoria

| Campo               | Valor                           |
|----------------------|---------------------------------|
| **Tipo**            | Lista suspensa (Dropdown)       |
| **Campo de origem** | `categoria_nome` em `dim_categories` |
| **Vínculo com cards** | Todos os cards que usam `dim_categories` |

### 6.2 Filtro — Faixa de Preço

| Campo               | Valor                           |
|----------------------|---------------------------------|
| **Tipo**            | Controle deslizante (Slider)    |
| **Campo de origem** | `preco` em `dim_products`       |
| **Valor mínimo**    | `0`                             |
| **Valor máximo**    | Automático (baseado nos dados)  |
| **Vínculo com cards** | Cards que referenciam `dim_products.preco` |

### 6.3 Filtro — Faixa de Desconto

| Campo               | Valor                           |
|----------------------|---------------------------------|
| **Tipo**            | Controle deslizante (Slider)    |
| **Campo de origem** | `desconto_percentual` em `dim_products` |
| **Valor mínimo**    | `0`                             |
| **Valor máximo**    | `100`                           |
| **Vínculo com cards** | Cards que referenciam `dim_products.desconto_percentual` |

### Como Vincular os Filtros

Para cada card do dashboard, edite as queries e adicione cláusulas `WHERE` com variáveis de template do Metabase:

```sql
-- Exemplo de condição para filtro de categoria
{% raw %}
WHERE c.categoria_nome IN ({{categoria}})
{% endraw %}

-- Exemplo de condição para filtro de preço
{% raw %}
WHERE p.preco BETWEEN {{preco_min}} AND {{preco_max}}
{% endraw %}

-- Exemplo de condição para filtro de desconto
{% raw %}
WHERE p.desconto_percentual BETWEEN {{desconto_min}} AND {{desconto_max}}
{% endraw %}
```

> [!warning] Nota sobre variáveis
> O Metabase utiliza `{% raw %}{{variavel}}{% endraw %}` como sintaxe de template. Ao configurar os filtros no dashboard, o Metabase automaticamente substitui os valores selecionados pelo usuário.

---

## 7. Como o Dashboard Apoia a Tomada de Decisão

O dashboard foi projetado para fornecer uma visão completa do ecossistema do e-commerce, integrando dados transacionais (avaliações, produtos, categorias) com resultados de machine learning (análise de sentimento, métricas visuais, previsões do modelo). Cada página atende a um perfil de stakeholder:

- **Visão Geral (Página 1):** Gestores de negócio conseguem identificar rapidamente a saúde do catálogo — quantos produtos ativos, quais categorias têm melhor e pior desempenho em avaliações, e quais produtos específicos precisam de atenção urgente (top 10 piores avaliados). Os KPIs consolidados facilitam o acompanhamento de metas mensais.

- **Análise de Sentimento (Página 2):** A equipe de CX (Customer Experience) pode detectar dissonâncias entre nota numérica e sentimento textual. Um produto com nota 5 mas polaridade negativa no texto sugere que o cliente não entendeu a escala ou que há viés na nota. Esses casos podem ser priorizados para ações de follow-up com o cliente.

- **Análise Visual (Página 3):** A equipe de conteúdo e marketing pode avaliar se a qualidade das imagens dos produtos (desfoque, brilho) tem correlação com avaliações ruins. Produtos com imagens desfocadas e baixas notas devem ter suas imagens refeitas como ação corretiva de baixo custo e alto impacto.

- **Resultados de ML (Página 4):** O time de dados acompanha a performance do modelo de classificação de sentimento. A matriz de confusão mostra onde o modelo erra mais, e as palavras TF-IDF revelam quais termos o modelo considera mais relevantes para cada classe de rating. Isso permite iterar e melhorar o modelo continuamente.

Os filtros globais de categoria, faixa de preço e desconto permitem que qualquer stakeholder segmente a análise para seu contexto específico, transformando o dashboard em uma ferramenta flexível de exploração de dados, não apenas um relatório estático.

---

> [!success] Próximos Passos
> - Após configurar o dashboard no Metabase, salve-o como **"E-commerce Analytics — Projeto Final"**
> - Compartilhe via link público ou incorpore em ferramentas como Notion/Confluence
> - Configure **assinaturas de e-mail** (Metabase Enterprise) para envio semanal dos KPIs principais
