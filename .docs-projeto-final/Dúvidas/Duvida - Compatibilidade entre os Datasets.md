---
title: "Compatibilidade entre os Datasets"
date: 2025-07-03
tags:
  - duvida
  - datasets
  - compatibilidade
  - dados
---

# Compatibilidade entre os Datasets

## A pergunta

> [!question] Os dois datasets se conversam bem? Como garantir que a imagem analisada é do produto certo?

## A resposta

Os datasets **não se conversam**, e foi exatamente por isso que usamos apenas o Dataset 1.

### O Dataset 1 já tem tudo

O `amazon_sales.csv` (1.465 linhas) é autossuficiente — cada linha contém:

| Coluna | Tipo | Uso |
|--------|------|-----|
| `product_id` | Chave única | Amarra tudo |
| `product_name`, `category` | Texto | Features estruturadas |
| `discounted_price`, `actual_price`, `discount_percentage` | Numérico | Features estruturadas |
| `rating` | 1 a 5 | **Target do modelo** |
| `review_title`, `review_content` | Texto | **NLP** — extraímos sentimento, palavras-chave |
| `img_link` | URL | **CV** — baixamos a foto e extraímos features visuais |

Ou seja, **o mesmo `product_id`** amarra o preço, a review e a foto — não tem risco de cruzar review de um produto com foto de outro.

### Por que o Dataset 2 ficou de fora

O Dataset 2 (`amazon_reviews.csv`, 568k linhas) tem reviews, mas:
- `ProductId` em formato diferente (não bate com o Dataset 1)
- **Não tem** coluna de imagem (`img_link`)
- **Não tem** preço, categoria, desconto
- Serviria apenas para enriquecer o vocabulário do NLP, mas o ganho seria marginal

### Decisão

Usamos **apenas o Dataset 1**. Ele sozinho entrega os 3 tipos de dados exigidos pelo PDF (estruturado + texto + imagem) com integridade referencial garantida pela chave `product_id`.

## Relacionado

- [[02-Datasets]]
- [[01-Plano-Geral]]
