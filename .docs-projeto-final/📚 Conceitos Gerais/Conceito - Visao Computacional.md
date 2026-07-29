---
title: "Visão Computacional - Features de Imagem"
date: 2025-07-03
tags:
  - conceito
  - cv
  - visao-computacional
  - opencv
  - imagem
---

# Visão Computacional — Features de Imagem

## Definição

Visão Computacional (CV) é o campo da IA que extrai informação de imagens. No nosso projeto, analisamos as fotos dos produtos para ver se características visuais (nitidez, brilho, cores) têm relação com o rating.

### Técnicas usadas

**OpenCV** é a biblioteca mais popular para processamento de imagem. As técnicas que usamos:

- **Laplaciano:** mede a nitidez da imagem. Uma foto borrada tem variância do Laplaciano baixa.
- **Canny Edge Detection:** detecta bordas. Imagens com muitos detalhes têm edge density alta.
- **K-Means (k=3):** agrupa pixels por cor para encontrar as 3 cores dominantes da foto.
- **HSV:** espaço de cor que separa matiz (H), saturação (S) e brilho (V). Mais intuitivo que RGB para análise visual.

### Hipótese

A hipótese é que produtos com fotos escuras, borradas ou de baixa qualidade visual podem ter ratings menores — seja porque a foto ruim indica produto de baixa qualidade, seja porque o cliente não consegue ver bem o que está comprando.

## Como foi implementado no projeto

**28 features extraídas** de cada imagem de produto, mas simplificamos para ~6 features principais devido ao tamanho das imagens (thumbnails 300x300):

| Feature | O que mede | Técnica |
|---------|-----------|---------|
| `brightness_mean` | Quão clara/escura é a foto | Média do canal V (HSV) |
| `blur_score` | Quão nítida/borrada | Variância do Laplaciano |
| `edge_density` | Quantos detalhes/contornos | Canny edge detection |
| `colorfulness_score` | Quão colorida/vibrante | Desvio padrão H + S |
| `saturation_mean` | Intensidade das cores | Média do canal S (HSV) |
| Dimensões | Tamanho e proporção | PIL/Pillow |

Baixamos 500 imagens de produtos via `requests` e processamos com OpenCV + Pillow. Os valores são armazenados na tabela `dim_products` e visualizados no dashboard do Metabase.

## Relacionado

- [[06-Machine-Learning#Features de Imagem CV]]
- [[07-Dashboard#Página 3 — Análise Visual (Imagem)]]
- [[04-Pipeline-ELT]]
