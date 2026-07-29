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

Estamos construindo um sistema que **prevê a nota (1 a 5 estrelas) que um produto de e-commerce vai receber**, analisando três coisas ao mesmo tempo: o **preço e categoria do produto**, o **texto das reviews** e a **foto do produto**.

### O objetivo final

Um gerente de e-commerce abre o dashboard, vê quais produtos têm maior chance de receber notas baixas e age ANTES que o problema aconteça. Por exemplo: se fotos escuras estão associadas a notas ruins, ele manda refazer as fotos. Se reviews mencionam muito "atraso na entrega", ele aciona a logística.

### Como estamos fazendo — passo a passo

1. **Baixamos os dados** do Kaggle: 1.400 produtos da Amazon com preço, categoria, review em texto e link da foto

2. **Subimos tudo pro MinIO** (um "S3 de mentira" que roda no seu computador via Docker). Em produção, seria o S3 da AWS de verdade — troca 4 linhas no arquivo de configuração e funciona igual.

3. **Limpamos os dados estruturados**: tiramos cifrão, porcentagem, arrumamos números. Adicionamos colunas como `log_price` e agrupamos desconto em "baixo/médio/alto".

4. **Extraímos significado do texto**: o computador lê cada review e entende se é positiva ou negativa (VADER), quais palavras mais importam (TF-IDF), se tem reclamação, elogio, menção a preço ou entrega.

5. **Extraímos informação das fotos**: o computador analisa cada imagem do produto — está escura? borrada? muito colorida? — e transforma isso em números que o modelo consegue usar.

6. **Juntamos tudo** em uma tabela única com ~87 colunas numéricas e 1.350 produtos.

7. **Organizamos no banco** com dbt: criamos tabelas de produtos, categorias, reviews e a tabela final que o modelo de machine learning vai consumir.

8. **O Airflow orquestra tudo**: uma DAG (arquivo Python) define a ordem: baixar → subir → limpar → NLP e CV em paralelo → juntar → dbt → treinar modelo. Ela roda automaticamente todo dia ou sob demanda.

9. **Treinamos o modelo**: um Naive Bayes que aprende quais palavras e características visuais estão associadas a cada nota. Implementamos duas vezes: uma do zero (hard-code, para aprender a matemática) e uma com biblioteca pronta (sklearn, para comparar).

10. **Visualizamos no Metabase**: 4 painéis com KPIs, análise de sentimento, análise de imagem e resultados do modelo. Tudo configurado automaticamente via script.

### O que já está pronto

- Docker com 6 serviços rodando (Postgres, MinIO, Airflow, Metabase)
- Dados reais no banco (1.350 produtos, 500 com imagens processadas)
- Dashboard do Metabase com 4 painéis e dados ao vivo
- Pipeline de ponta a ponta testado (baixar → processar → db → dashboard)
- Estrutura pronta para S3 e Snowflake (troca de ambiente com 4 variáveis)

### O que falta

- Treinar o modelo Naive Bayes hard-code e sklearn com os dados reais
- Comparar os resultados e gerar as métricas (acurácia, precisão, recall, F1)
- Criar o CloudFormation YAML da AWS
- Escrever o relatório final e preparar a apresentação

## Relacionado

- [[🏠 Home]]
- [[12-Passo-a-Passo]]
- [[09-Checklist-Entrega]]
