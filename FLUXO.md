# Fluxo Completo do Projeto — Explicação em Linguagem Natural

Este projeto é um sistema completo de previsão de satisfação do cliente em e-commerce. A ideia é simples: dado um produto vendido na Amazon (com seu preço, categoria, reviews dos clientes e foto do produto), conseguimos prever qual será a nota que um cliente daria — de 1 a 5 estrelas. Para isso, combinamos três tipos de informação: dados estruturados (preço, desconto, categoria), texto não estruturado (as reviews que os clientes escreveram) e imagens (as fotos dos produtos). Tudo isso é orquestrado por um pipeline automatizado que vai desde o download dos dados brutos até um dashboard interativo onde um gerente de produto pode tomar decisões.

A seguir, vamos percorrer cada etapa desse pipeline, explicando o que acontece em cada uma delas e por quê.

---

## 1. De onde vêm os dados

Tudo começa com dois datasets públicos hospedados no Kaggle, uma plataforma que reúne milhares de conjuntos de dados gratuitos para projetos de ciência de dados.

O primeiro e principal dataset é o **Amazon Sales Dataset**, que contém cerca de 1.400 produtos vendidos na Amazon Índia. Cada linha desse dataset representa um produto e já traz, em um único lugar, os três tipos de dados que precisamos:

- **Dados estruturados:** nome do produto, categoria (Eletrônicos, Roupas, etc.), preço original em rúpias, preço com desconto, percentual de desconto, nota média do produto (de 1 a 5 — essa é a coluna que queremos prever) e quantidade de avaliações.
- **Texto não estruturado:** o título da review e o conteúdo completo da review que um cliente escreveu sobre aquele produto.
- **Imagens:** uma URL que aponta para a foto do produto no site da Amazon.

O segundo dataset, chamado **Amazon Product Reviews**, é complementar: ele contém cerca de 35 mil reviews adicionais, o que nos dá muito mais exemplos de texto para treinar nossos modelos de processamento de linguagem natural.

O download de ambos é feito por um script Python (`ingestion/download_dataset.py`) que usa a biblioteca `kagglehub` para baixar diretamente do Kaggle e salvar os arquivos CSV brutos na pasta `data/raw/`. Se você rodar o projeto pela primeira vez, é esse script que vai puxar tudo do Kaggle automaticamente — não precisa baixar nada manualmente.

---

## 2. Como os dados chegam no armazenamento

Com os CSVs em mãos, o próximo passo é enviar tudo para um sistema de armazenamento em nuvem (ou, no ambiente de desenvolvimento, um simulador local de nuvem). O script `ingestion/load_raw_to_s3.py` faz duas coisas:

Primeiro, ele sobe os arquivos CSV (`amazon_sales.csv` e `amazon_reviews.csv`) para um bucket chamado `raw/` no nosso armazenamento. Em desenvolvimento, esse armazenamento é o **MinIO**, um serviço que funciona exatamente como o Amazon S3, mas roda localmente dentro de um container Docker. Isso significa que o código que escrevemos para acessar o armazenamento funciona igualzinho tanto no seu computador quanto na nuvem da AWS — é só trocar o endereço nas variáveis de ambiente.

Segundo, o script lê a coluna `img_link` do dataset de vendas, que contém as URLs das fotos dos produtos na Amazon. Ele baixa cada imagem (até um limite de 1.000 para não sobrecarregar) e também faz o upload delas para o bucket, dentro da pasta `raw/images/`. As imagens são salvas com nomes numéricos sequenciais (0.jpg, 1.jpg, 2.jpg...) e também são copiadas localmente para a pasta `images/products/` para acesso rápido.

A organização do bucket segue uma hierarquia de camadas:
- `raw/` guarda os dados como vieram, sem nenhum processamento — é a camada de ingestão bruta.
- `processed/` vai guardar os dados após cada etapa de limpeza e extração de features — é a camada pronta para consumo.
- `raw/images/` guarda as imagens brutas baixadas das URLs.

Essa separação entre `raw/` e `processed/` é um padrão de engenharia de dados chamado arquitetura em camadas (ou "medallion architecture"): você nunca modifica os dados originais; em vez disso, cada etapa de transformação gera uma nova cópia, mantendo a rastreabilidade. Se algo der errado lá na frente, você sempre pode voltar ao dado original.

---

## 3. O que fazemos com os dados estruturados

Agora que os dados brutos estão armazenados, começa a faxina. O script `processing/process_structured.py` pega o arquivo `amazon_sales.csv` e executa uma série de limpezas e transformações.

O primeiro desafio é que os preços vêm como texto no formato indiano: algo como "₹1,299". O script remove o símbolo da rúpia, tira as vírgulas e converte para número decimal. O mesmo acontece com o percentual de desconto, que vem como "45%" — removemos o sinal de percentual e dividimos por 100 para ficar como fração (0.45). A contagem de avaliações também vem com vírgulas no meio ("12,345") e precisa ser convertida para inteiro.

Em seguida, fazemos a limpeza propriamente dita: removemos linhas duplicadas (mesmo nome de produto e mesmo ID aparecendo mais de uma vez) e eliminamos produtos que não têm nota (rating vazio), já que a nota é justamente o que queremos prever — não faz sentido manter registros sem o alvo do modelo.

Depois da limpeza, criamos colunas novas que ajudam o modelo de machine learning a entender melhor os dados:

- **log_price**: o logaritmo do preço original. Por que logaritmo? Porque preços de produtos variam muito — um fone de ouvido custa 500 rúpias, um notebook custa 50.000. Essa diferença de escala (duas ordens de grandeza) pode confundir o modelo. O logaritmo comprime essa escala, aproximando os valores.
- **log_rating_count**: mesma ideia, mas para a quantidade de avaliações. Um produto com 10 avaliações e outro com 10.000 avaliações têm pesos muito diferentes — o logaritmo suaviza isso.
- **price_difference**: a diferença entre o preço original e o preço com desconto. Um desconto grande pode influenciar a satisfação do cliente.
- **discount_bucket**: uma categorização do desconto em "baixo" (menos de 20%), "médio" (entre 20% e 50%) e "alto" (acima de 50%), mais uma categoria "desconhecido" para quando o dado está vazio. Isso transforma uma variável contínua em faixas que o modelo pode interpretar mais facilmente.
- **One-hot encoding das categorias**: a coluna `category` contém valores como "Electronics", "Clothing", "Home & Kitchen". Como modelos de machine learning não entendem texto, transformamos cada categoria em uma coluna binária (0 ou 1). Por exemplo, se o produto é da categoria "Electronics", a coluna `cat_Electronics` recebe 1 e as outras (`cat_Clothing`, `cat_Home_Kitchen`, etc.) recebem 0.

O resultado dessa etapa é salvo como `products_clean.csv` na pasta `data/processed/`. Esse arquivo tem as mesmas linhas do original (menos as removidas), mas agora com colunas novas, colunas numéricas no formato correto e categorias expandidas em colunas binárias.

---

## 4. Como extraímos significado do texto das reviews

Essa é uma das etapas mais interessantes do projeto. O script `processing/extract_text_features.py` pega as reviews escritas por clientes e extrai delas centenas de características numéricas que descrevem o conteúdo, o tom e o estilo do texto. Tudo isso usando técnicas de Processamento de Linguagem Natural (NLP, na sigla em inglês).

O primeiro passo é juntar o título da review com o conteúdo num texto único. Por exemplo, se o título é "Ótimo produto!" e o conteúdo é "Chegou rápido e funciona bem", o texto completo vira "Ótimo produto! Chegou rápido e funciona bem".

A partir desse texto completo, extraímos seis famílias de features:

**Metadados do texto** — são características puramente quantitativas, que não dependem do significado das palavras:
- Tamanho total da review em caracteres
- Quantidade de palavras
- Tamanho médio das palavras
- Quantidade de frases (contando pontos finais, exclamações e interrogações)

**Estilo de escrita** — aqui medimos como a pessoa escreve:
- Proporção de letras maiúsculas (muita maiúscula = pode indicar raiva)
- Quantidade de exclamações
- Quantidade de perguntas
- Proporção de dígitos numéricos no texto (pessoas insatisfeitas tendem a citar números, datas, versões)

**Análise de sentimento** — usando uma ferramenta chamada VADER (Valence Aware Dictionary and sEntiment Reasoner), que é um analisador de sentimentos especializado em textos curtos de redes sociais e reviews. O VADER nos dá três valores:
- **Polaridade:** um número de -1 (muito negativo) a +1 (muito positivo). Por exemplo, "Esse produto é horrível, nunca mais compro" teria polaridade próxima de -0.8, enquanto "Simplesmente perfeito, recomendo demais" ficaria perto de +0.9.
- **Subjetividade:** a soma das pontuações positiva e negativa. Quanto mais próximo de 1, mais carregado de opinião é o texto. Reviews puramente descritivas ("O produto é azul, pesa 200g") teriam subjetividade baixa.
- **Compound score:** uma versão normalizada da polaridade, já pronta para uso em modelos.

O VADER funciona com um dicionário pré-construído de milhares de palavras, cada uma com uma pontuação de sentimento. Ele também entende intensificadores ("muito bom" é mais positivo que "bom"), negações ("não é bom" é negativo mesmo contendo a palavra "bom") e até emojis. É uma ferramenta rápida e que não precisa de treinamento — funciona "out of the box".

**Detecção por padrões (regex)** — usamos expressões regulares para identificar menções específicas no texto:
- `contains_complaint`: o texto contém palavras de reclamação? (ex: "quebrou", "defeito", "decepção", "reembolso", "péssimo")
- `contains_praise`: o texto contém palavras de elogio? (ex: "excelente", "incrível", "perfeito", "recomendo")
- `contains_price_mention`: o cliente mencionou preço? (ex: "barato", "caro", "custo-benefício")
- `contains_delivery_mention`: o cliente mencionou entrega? (ex: "demorou", "entregue", "chegou rápido")

**Legibilidade do texto** — usando a biblioteca `textstat`, calculamos:
- **Flesch Reading Ease:** uma pontuação de 0 a 100 que indica quão fácil é ler o texto. Textos muito simples (frases curtas, palavras curtas) têm pontuação alta; textos complexos têm pontuação baixa.
- **Proporção de palavras complexas:** palavras com 3 ou mais sílabas. Indica o nível de sofisticação do vocabulário usado.

**TF-IDF — as 200 palavras mais importantes** — esta é a extração mais poderosa. TF-IDF significa "Term Frequency — Inverse Document Frequency" (Frequência do Termo — Frequência Inversa nos Documentos). É uma técnica que identifica quais palavras são realmente importantes para distinguir uma review da outra.

Funciona assim: se uma palavra aparece muitas vezes em uma review específica (alta frequência local), mas aparece em quase todas as reviews (baixa raridade global), ela é pouco informativa. Por exemplo, a palavra "produto" aparece em quase toda review, então ela não ajuda a diferenciar uma review positiva de uma negativa. Já a palavra "defeituoso" aparece em poucas reviews, e quando aparece, provavelmente indica insatisfação.

O algoritmo seleciona as 200 palavras (ou bigramas — pares de palavras como "não funciona" ou "muito bom") com maior pontuação TF-IDF em todo o conjunto de reviews e cria uma matriz: cada review vira uma linha, cada palavra vira uma coluna, e cada célula contém um número representando a importância daquela palavra naquela review. É como transformar texto em uma planilha que o computador consegue processar matematicamente.

No total, cada review gera aproximadamente 217 features numéricas (4 de metadados + 4 de estilo + 3 de VADER + 4 de regex + 2 de legibilidade + 200 de TF-IDF).

O resultado dessa etapa é salvo como `reviews_features.csv`.

---

## 5. Como extraímos informações das imagens dos produtos

Enquanto o NLP processa o texto, o script `processing/extract_image_features.py` faz o equivalente para as imagens dos produtos. Ele usa técnicas de Visão Computacional (Computer Vision, ou CV) para extrair características visuais que possam influenciar a satisfação do cliente — afinal, uma foto de produto mal tirada, escura ou borrada pode gerar uma impressão negativa.

O script processa cada imagem de produto baixada e extrai seis categorias de features:

**Dimensões da imagem** — usando a biblioteca PIL/Pillow:
- Largura e altura em pixels
- Proporção (aspect ratio = largura dividida pela altura)
- Tamanho do arquivo em kilobytes
- Formato da imagem (JPEG, PNG, WebP)

**Análise de cores** — usando OpenCV (a biblioteca mais famosa de visão computacional):
- Convertemos a imagem para o espaço de cores HSV (Hue/Saturation/Value, ou Matiz/Saturação/Brilho), que é mais próximo de como humanos percebem cor do que o RGB tradicional.
- **Brilho médio:** o canal V (Value) do HSV nos diz quão clara ou escura é a imagem. Imagens muito escuras podem indicar fotos de baixa qualidade.
- **Saturação média:** quão vibrantes ou "lavadas" são as cores. Imagens muito dessaturadas parecem sem graça.
- **Colorfulness score:** uma medida combinada que captura o quão colorida é a imagem como um todo.
- **Cores dominantes:** usando o algoritmo K-Means (um algoritmo de agrupamento), identificamos as 3 cores mais predominantes na imagem. Para cada cor dominante, extraímos seus valores R, G e B, totalizando 9 valores (3 cores x 3 canais). Por exemplo, a foto de uma camiseta vermelha teria a cor dominante próxima de (255, 0, 0).

**Nitidez da imagem** — uma imagem borrada transmite falta de profissionalismo. Calculamos o blur_score usando o operador Laplaciano, que mede a taxa de variação de intensidade entre pixels vizinhos. Uma imagem nítida tem bordas bem definidas e, portanto, alta variância do Laplaciano. Uma imagem borrada tem transições suaves e baixa variância. É um detector de "está fora de foco".

**Complexidade visual** — usamos o detector de bordas Canny para encontrar todas as bordas na imagem (transições bruscas de cor ou intensidade) e calculamos a densidade de bordas: quantos pixels da imagem fazem parte de alguma borda. Uma foto de produto com fundo branco liso tem baixa densidade de bordas; uma foto cheia de detalhes (como uma placa de circuito) tem alta densidade. Também contamos **cantos** usando o detector de cantos de Harris — regiões onde duas bordas se encontram. Cantos são características importantes para descrever a estrutura visual.

**Análise de textura com GLCM** — GLCM significa Gray Level Co-occurrence Matrix (Matriz de Co-ocorrência de Níveis de Cinza). É uma técnica estatística que analisa a textura da imagem: quão repetitivos são os padrões, quão granulada ou lisa é a superfície. Extraímos duas métricas:
- **Entropia:** mede a aleatoriedade da textura. Uma imagem com textura caótica (como uma parede de tijolos) tem entropia alta; uma superfície lisa (como um fundo branco) tem entropia baixa.
- **Contraste:** mede a diferença de intensidade entre pixels vizinhos. Alto contraste significa variações bruscas de claro para escuro.

**Histograma de cores** — dividimos a imagem nos canais vermelho, verde e azul e calculamos a média e o desvio padrão de cada canal. Isso nos dá uma "assinatura" da distribuição de cores da imagem: uma foto predominantemente azulada terá média alta no canal azul, por exemplo.

No total, cada imagem gera aproximadamente 28 features numéricas (5 de dimensões + 12 de cores + 1 de nitidez + 2 de complexidade + 2 de textura + 6 de histograma).

O resultado dessa etapa é salvo como `images_features.csv`.

---

## 6. Como juntamos tudo em uma tabela só

Chegamos ao momento de unificar tudo. O script `processing/merge_features.py` é o responsável por fazer o "cruzamento" de todas as tabelas que geramos até agora, produzindo uma única tabela que será a entrada do modelo de machine learning.

O processo de merge funciona assim:

- Começamos com a tabela `products_clean.csv` como base, que contém os dados estruturados dos produtos (preços, categorias codificadas, ID do produto).
- Fazemos um LEFT JOIN com `reviews_features.csv` usando `product_id` como chave. Ou seja: para cada produto, anexamos todas as 217 features textuais extraídas da review daquele produto.
- Fazemos um LEFT JOIN com `images_features.csv`, também pelo `product_id`, anexando as 28 features visuais.

O LEFT JOIN garante que mesmo se algum produto não tiver features de texto ou de imagem (porque o download da imagem falhou, por exemplo), ele ainda aparece na tabela final — as colunas que faltam são preenchidas com zero.

O script também faz uma limpeza final importante:
- Remove colunas que não servem para o modelo de machine learning, como URLs (`img_link`, `product_link`) e o texto bruto das reviews (já que as features numéricas extraídas do texto são mais úteis para o modelo do que o texto em si).
- Remove colunas completamente vazias (que podem surgir quando um dataset opcional não foi carregado).
- Preenche valores nulos remanescentes com zero, garantindo que o modelo receba uma matriz limpa e completa, sem buracos.

O resultado é a tabela `ml_features.csv`, que é o "produto final" de todo o pipeline de dados. Essa tabela contém, aproximadamente:
- Cerca de 1.400 linhas (uma por produto)
- Cerca de 255 colunas de features (dados estruturados + NLP + imagens)
- Uma coluna `rating` (1 a 5) que é o alvo que o modelo vai aprender a prever

Essa tabela é salva tanto localmente (`data/processed/ml_features.csv`) quanto pode ser carregada no banco de dados via dbt para consumo pelo Metabase.

---

## 7. O que o dbt faz com esses dados

dbt significa "data build tool" e é uma ferramenta que organiza as transformações de dados dentro do banco de uma forma modular, testável e versionada. Em vez de escrever scripts Python soltos que fazem INSERT e UPDATE no banco, o dbt permite que você escreva consultas SQL organizadas em camadas, como se fossem peças de Lego que se encaixam. Cada peça é um "modelo", e o dbt descobre automaticamente as dependências entre eles e executa tudo na ordem certa.

Nosso projeto dbt tem quatro camadas de modelos:

**Camada Staging (3 modelos):**
- `stg_products.sql`: pega os dados limpos de produtos, renomeia colunas para um padrão consistente com snake_case (ex: `product_name`), garante os tipos corretos (número é número, texto é texto) e remove duplicatas que possam ter passado.
- `stg_reviews.sql`: faz o mesmo para as features de texto extraídas das reviews.
- `stg_images.sql`: faz o mesmo para as features de imagem.

A staging é como a "sala de recepção" dos dados: tudo que entra no banco passa por aqui para ser padronizado antes de seguir adiante.

**Camada Dimensions (2 modelos):**
- `dim_products.sql`: cria uma tabela de dimensão com todos os atributos descritivos de cada produto — nome, preços, desconto, URL da imagem, features visuais. É uma tabela do tipo "Slowly Changing Dimension" (SCD Tipo 1), ou seja, se um produto for atualizado, sobrescrevemos os valores antigos (não mantemos histórico).
- `dim_categories.sql`: agrega os produtos por categoria e calcula métricas úteis como quantidade de produtos na categoria e nota média. Isso cria uma tabela de referência que o dashboard pode usar para comparar categorias.

**Camada Facts (2 modelos):**
- `fact_reviews.sql`: tabela de fatos que armazena cada review individual com suas features textuais completas (polaridade, subjetividade, TF-IDF, etc.) e features de imagem associadas ao produto da review. Cada linha é um evento de review.
- `fact_sales.sql`: tabela de fatos com métricas de venda por produto — preço, desconto, nota, quantidade de avaliações. É a tabela que responde perguntas como "qual categoria tem melhor custo-benefício?".

**Camada Marts (1 modelo):**
- `ml_features.sql`: faz o JOIN final entre as dimensões e fatos para produzir a tabela única e achatada que o modelo de machine learning consome. É essencialmente uma versão "curada" do `ml_features.csv`, agora dentro do banco de dados, pronta para ser consultada pelo Python ou pelo Metabase.

Além dos modelos, o dbt também roda **4 testes de qualidade de dados** (definidos no arquivo `tests/schema.yml`):

1. **`product_id` não pode ser nulo e deve ser único** na tabela de produtos. Se houver dois produtos com o mesmo ID ou um produto sem ID, algo está errado — o dbt grita.
2. **`review_id` não pode ser nulo** na tabela de reviews. Toda review precisa de identificação.
3. **`rating` não pode ser nulo e só pode conter os valores 1, 2, 3, 4 ou 5** na tabela de reviews. Se alguém tentar inserir uma nota 6 ou -1, o teste falha.
4. **`category_name` deve ser único** na tabela de categorias. Não pode ter categoria duplicada.

Esses testes são como alarmes: se algum dado inválido entrar no pipeline, você fica sabendo imediatamente, antes que ele contamine o modelo de machine learning ou o dashboard.

---

## 8. Como o Airflow orquestra tudo isso

Até agora, descrevemos vários scripts Python que fazem coisas diferentes. Mas alguém precisa coordenar a ordem em que eles rodam, garantir que um script não comece antes do outro terminar, e permitir que execuções sejam agendadas automaticamente. Esse "maestro" é o Apache Airflow, e o nosso projeto tem uma DAG (Directed Acyclic Graph, ou Grafo Acíclico Dirigido) definida no arquivo `dags/etl_pipeline.py`.

O fluxo da DAG tem 8 tarefas encadeadas:

1. **download_datasets:** baixa os CSVs do Kaggle.
2. **load_to_s3:** sobe tudo para o MinIO/S3 (CSVs + imagens).
3. **process_structured:** limpa e transforma os dados estruturados.
4. **4a. extract_text_features** e **4b. extract_image_features:** rodam em paralelo, porque extrair features de texto e extrair features de imagem são tarefas completamente independentes — uma não precisa da outra. Isso acelera o pipeline.
5. **merge_features:** junta todas as tabelas em `ml_features.csv`.
6. **dbt_run:** executa todos os modelos dbt (staging → dimensions → facts → marts).
7. **dbt_test:** roda os 4 testes de qualidade. Se algum falhar, o pipeline para aqui.
8. **ml_train_evaluate:** treina os modelos de machine learning e gera a comparação.

A DAG está configurada para rodar automaticamente uma vez por dia (`@daily`), mas também pode ser disparada manualmente a qualquer momento pelo comando `make pipeline` (ou diretamente na interface web do Airflow, em `http://localhost:8080`).

Cada tarefa é envolvida em um PythonOperator (que chama uma função Python) ou BashOperator (que executa um comando de terminal). A sintaxe do Airflow usa os operadores `>>` para definir dependências: `t1 >> t2` significa "t2 só roda depois que t1 terminar com sucesso". O fluxo completo fica assim:

`t1 >> t2 >> t3 >> [t4a, t4b] >> t5 >> t6 >> t7 >> t8`

Os colchetes em `[t4a, t4b]` indicam que essas duas tarefas podem rodar em paralelo, e `t5` só começa quando ambas terminarem.

---

## 9. Como o modelo de Machine Learning aprende

A etapa final do pipeline técnico é treinar o modelo de machine learning que vai prever a nota (1 a 5 estrelas) com base nas ~255 features que extraímos. O algoritmo escolhido é o **Naive Bayes Multinomial**, um dos classificadores mais clássicos e eficientes para tarefas de classificação de texto.

O projeto implementa o Naive Bayes de duas formas diferentes, e depois as compara:

### 9.1 Implementação Hard-Code (do zero)

O arquivo `ml/hard_code/naive_bayes_hardcode.py` implementa o algoritmo completamente do zero, usando apenas Python com NumPy — sem importar nenhuma biblioteca de machine learning. O objetivo é entender o que realmente acontece "dentro da caixa preta".

O Naive Bayes funciona com um princípio simples de probabilidade. Imagine que você quer saber a probabilidade de uma review ter nota 5, dado que ela contém as palavras "excelente", "qualidade" e "recomendo". O teorema de Bayes diz que:

Probabilidade(nota 5 | palavras) = Probabilidade(palavras | nota 5) x Probabilidade(nota 5) / Probabilidade(palavras)

O "naive" (ingênuo) do nome vem de uma suposição simplificadora: assumimos que cada palavra é independente das outras. Na prática, isso não é verdade (a palavra "não" seguida de "bom" tem um significado diferente), mas a suposição funciona surpreendentemente bem na maioria dos casos e torna a matemática muito mais simples.

A implementação hard-code segue três passos:

**Passo 1 — Calcular os log-priors:** Para cada classe (1, 2, 3, 4, 5 estrelas), calculamos o logaritmo da probabilidade da classe: log(quantidade de reviews da classe / total de reviews). O logaritmo é usado para evitar underflow numérico — quando você multiplica centenas de probabilidades pequenas (como 0.001 x 0.0005 x 0.0002 ...), o número fica tão minúsculo que o computador arredonda para zero. Trabalhando em log-space, somamos logaritmos em vez de multiplicar probabilidades, mantendo a precisão.

**Passo 2 — Calcular as probabilidades condicionais:** Para cada palavra do vocabulário e cada classe, calculamos: P(palavra | classe) = (quantas vezes a palavra aparece na classe + alpha) / (total de palavras na classe + alpha x tamanho do vocabulário). O "alpha" é o fator de **Laplace Smoothing** (suavização de Laplace), geralmente com valor 1. Ele resolve o problema da "probabilidade zero": se uma palavra nunca apareceu nos treinos da classe 5, a probabilidade seria zero, e multiplicar por zero zeraria toda a previsão. Com Laplace smoothing, palavras nunca vistas recebem uma probabilidade pequena mas não nula.

**Passo 3 — Classificar um novo texto:** Para uma review nova, calculamos um score para cada classe: score(classe) = log-prior + soma dos log-probabilidades de cada palavra da review. A classe com o maior score é a predição.

O modelo trabalha com features binárias: para cada palavra do vocabulário TF-IDF, a feature é 1 se a palavra aparece na review e 0 se não aparece. Essa binarização é feita antes do treinamento — convertemos os valores contínuos do TF-IDF para presença/ausência, que é o que o Naive Bayes Multinomial espera.

### 9.2 Implementação com Scikit-Learn

O arquivo `ml/sklearn/naive_bayes_sklearn.py` faz exatamente a mesma coisa, mas usando `MultinomialNB` da biblioteca scikit-learn — a biblioteca de machine learning mais popular do Python. A ideia é comparar: será que a nossa implementação hard-code chega nos mesmos resultados da implementação profissional?

Para garantir uma comparação justa, ambos os modelos:
- Usam exatamente os mesmos dados (as mesmas linhas do `ml_features.csv`)
- Usam exatamente as mesmas features (as 200 colunas TF-IDF)
- Usam a mesma divisão treino/teste (80% para treinar, 20% para testar) com a mesma semente aleatória (random_state=42), garantindo que as mesmas reviews caiam no treino e no teste
- Usam o mesmo alpha de Laplace Smoothing (1.0)

Além dos dois modelos, calculamos também um **baseline**: prever sempre a classe mais frequente do conjunto de treino. Se o dataset tem mais notas 4 do que qualquer outra coisa, o baseline chuta 4 para tudo. É o modelo mais burro possível e serve como "nota de corte": se nosso modelo não for melhor que isso, tem algo errado.

### 9.3 Avaliação e Comparação

O arquivo `ml/evaluate.py` roda os três (hard-code, sklearn e baseline) e compara usando 5 métricas:

- **Acurácia:** percentual de reviews em que o modelo acertou a nota. Se o modelo acertou 300 de 400 reviews, a acurácia é 75%. É a métrica mais intuitiva, mas pode enganar quando as classes são desbalanceadas (se 80% das reviews são nota 5, um modelo que chuta 5 sempre teria 80% de acurácia sem aprender nada).

- **Precisão (macro):** das reviews que o modelo classificou como nota 5, quantas realmente eram nota 5? É uma métrica de "quão confiáveis são as predições positivas". Calculamos a média (macro) entre as 5 classes para não privilegiar a classe majoritária.

- **Recall (macro):** de todas as reviews que realmente eram nota 5, quantas o modelo identificou corretamente? É uma métrica de "quão completas são as detecções". Também usamos a média macro.

- **F1-Score (macro):** a média harmônica entre precisão e recall. É uma métrica única que equilibra as duas — útil quando você não quer ter que escolher entre privilegiar precisão ou recall.

- **Matriz de Confusão:** uma tabela 5x5 onde cada célula (i,j) mostra quantas reviews da classe i foram classificadas como classe j. A diagonal principal (onde i=j) são os acertos; fora da diagonal são os erros. A matriz revela padrões interessantes, como "o modelo confunde nota 3 com nota 4 com frequência" ou "nota 1 quase nunca é confundida com nota 5".

Além das métricas, o script também mede o **tempo de treino** e **tempo de predição** de cada modelo (em milissegundos). O scikit-learn, por ser implementado em Cython com código compilado, tende a ser significativamente mais rápido que nossa versão em Python puro. Mas os resultados numéricos devem ser muito próximos, já que ambos implementam o mesmo algoritmo com os mesmos parâmetros.

O script gera ainda dois arquivos de imagem com as matrizes de confusão (`hardcode_confusion.png` e `sklearn_confusion.png`) e um CSV com a tabela comparativa, todos salvos em `data/processed/`.

---

## 10. Como visualizamos os resultados no Metabase

De nada adianta ter um pipeline sofisticado e um modelo treinado se ninguém consegue ver os resultados de forma clara. O Metabase é a ferramenta de dashboard que fecha o ciclo, transformando os dados processados em gráficos interativos que respondem perguntas de negócio.

O dashboard está organizado em 4 páginas:

**Página 1 — Visão Geral:**
- Indicadores numéricos (KPIs) no topo: total de vendas, nota média geral, percentual de reviews negativas (nota abaixo de 3), total de produtos cadastrados.
- Gráfico de barras da nota média por categoria. Um gerente de produto olha para isso e identifica rapidamente: "a categoria Eletrônicos tem nota 3.2, enquanto Roupas tem 4.5 — por quê?"
- Gráfico de linha mostrando a evolução da nota média ao longo do tempo (quando os dados tiverem data).
- Tabela com o top 10 produtos de pior nota — os que precisam de intervenção urgente.

**Página 2 — Análise de Sentimento (NLP):**
- Nuvem de palavras comparativa: palavras mais frequentes em reviews positivas (nota 4-5) versus negativas (nota 1-2).
- Histograma da distribuição de polaridade para cada nota. A expectativa é que reviews nota 5 tenham polaridade concentrada perto de +1, enquanto nota 1 fique perto de -1.
- Gráfico de barras empilhadas mostrando, para cada categoria, a proporção de reviews que mencionam reclamação vs. elogio.
- Tabela de "reviews dissonantes": casos onde a nota é 5 mas a polaridade do texto é negativa (ou vice-versa). São situações curiosas que merecem investigação — talvez o cliente tenha dado 5 estrelas por engano, ou o texto contenha ironia que o VADER não captou.

**Página 3 — Análise Visual (Imagem):**
- Tabela dos produtos com maior blur_score (imagem mais borrada) e sua nota média. A hipótese é que fotos ruins correlacionam com notas mais baixas.
- Gráfico de dispersão (scatter plot) de brilho médio da imagem vs. nota. Será que imagens muito escuras estão associadas a produtos mal avaliados?
- Gráfico de barras da cor dominante mais frequente por categoria. Por curiosidade: eletrônicos tendem a ser pretos/prateados; roupas, coloridas.

**Página 4 — Resultados do Modelo ML:**
- Mapa de calor (heatmap) da matriz de confusão.
- Tabela com as métricas (acurácia, precisão, recall, F1) detalhadas por classe e no agregado.
- Gráfico de barras lado a lado comparando as métricas do modelo hard-code vs. sklearn vs. baseline.
- Top features: as palavras com maior peso para cada classe de rating. Por exemplo, quais palavras mais contribuem para uma review ser classificada como nota 1? Provavelmente "defeito", "quebrou", "reembolso".

**Filtros globais** permitem que o usuário recorte os dados por:
- Categoria do produto
- Faixa de preço
- Faixa de desconto
- Nota

Na prática, um gerente de produto abriria o dashboard e faria perguntas como: "Me mostre os produtos da categoria Eletrônicos com nota abaixo de 3 e preço acima de 500 reais. Quais são? O que as reviews dizem? As imagens são boas?" — tudo respondido em alguns cliques.

---

## 11. Como funciona na nuvem (AWS)

O projeto inclui um template de CloudFormation (`infra/cloudformation.yaml`) que descreve uma arquitetura completa na AWS como exercício acadêmico. O CloudFormation funciona como uma receita de bolo: você escreve um arquivo YAML declarando todos os recursos que precisa, e a AWS provisiona tudo automaticamente, na ordem certa, gerenciando dependências entre os serviços.

A arquitetura proposta inclui:

- **S3 (Simple Storage Service):** bucket com as pastas `raw/`, `processed/` e `images/`, substituindo o MinIO local. O S3 é o serviço de armazenamento de objetos da AWS — praticamente infinito, altamente durável e acessível de qualquer lugar.

- **EC2 (Elastic Compute Cloud):** uma máquina virtual do tipo t3.medium rodando o Apache Airflow, substituindo os containers Docker locais. A EC2 é como "alugar um computador na nuvem".

- **ECS (Elastic Container Service) + Fargate:** cluster de containers para rodar os scripts Python de processamento e o dbt de forma isolada e escalável. Cada execução do pipeline dispara tarefas ECS que sobem, executam e morrem — você paga apenas pelo tempo de execução.

- **SageMaker:** ambiente gerenciado para treinamento de machine learning. Em vez de rodar `naive_bayes_hardcode.py` no seu laptop, você sobe um notebook SageMaker com muito mais poder computacional.

- **Redshift:** data warehouse (armazém de dados) em substituição ao PostgreSQL local. O Redshift é otimizado para consultas analíticas em grandes volumes de dados — foi feito para cenários como o nosso dashboard, onde você faz agregações, filtros e joins em milhões de linhas.

- **QuickSight:** ferramenta de dashboard nativa da AWS, substituindo o Metabase. Oferece funcionalidades similares, mas integrada ao ecossistema AWS.

- **CloudWatch:** coleta de logs, métricas e alarmes de todos os serviços. Se algo der errado no pipeline, o CloudWatch registra e pode disparar alertas.

- **IAM (Identity and Access Management):** gerencia permissões entre os serviços (roles, policies, security groups, VPC). Define quem pode acessar o quê — por exemplo, a EC2 do Airflow tem permissão para ler/escrever no S3, mas não para deletar o banco Redshift.

É importante frisar que, neste projeto acadêmico, **apenas o S3 é realmente usado nos scripts de código**. Todo o resto (EC2, ECS, SageMaker, Redshift, QuickSight) roda localmente via Docker como substitutos — PostgreSQL no lugar do Redshift, Metabase no lugar do QuickSight, containers locais no lugar das instâncias EC2. O CloudFormation existe como demonstração de que sabemos projetar a arquitetura para a nuvem, mesmo que a execução prática seja local.

---

## 12. Como trocar do ambiente de desenvolvimento para produção

Uma das decisões de design mais importantes do projeto foi tornar o ambiente de desenvolvimento indistinguível do ambiente de produção do ponto de vista do código. Conseguimos isso graças ao padrão de "inversão de dependência": todo o código Python acessa o armazenamento via biblioteca `boto3` (o SDK oficial da AWS), e todo o acesso a banco de dados passa por perfis de conexão configuráveis.

No ambiente de desenvolvimento (local), o arquivo `.env.local` configura:
- `S3_ENDPOINT=http://minio:9000` — o MinIO finge ser o S3
- `S3_ACCESS_KEY=minioadmin` / `S3_SECRET_KEY=minioadmin`
- `DB_TYPE=postgres` — PostgreSQL finge ser o Snowflake

Para migrar para produção (usando serviços reais da AWS e Snowflake), basta substituir o arquivo `.env` pelo conteúdo de `.env.prod`:
- `S3_ENDPOINT=https://s3.amazonaws.com` — S3 de verdade
- Credenciais reais da AWS
- `DB_TYPE=snowflake` — Snowflake de verdade, com account, warehouse e database reais

O código-fonte não muda uma linha. Os scripts continuam chamando `boto3.client("s3")` e o dbt continua rodando `dbt run` — o que muda é apenas para onde essas chamadas apontam. Isso reduz drasticamente o risco de bugs de "funciona na minha máquina", porque o código que você testou localmente é literalmente o mesmo que roda em produção.

É a mesma lógica por trás dos 4 containers Docker definidos no `docker-compose.yml`: Postgres, MinIO, Airflow (webserver + scheduler) e Metabase. Com um único comando (`make up`), você sobe um ambiente completo que simula a nuvem no seu computador.

---

## 13. O que cada arquivo e pasta faz

Para encerrar, um panorama rápido da estrutura do projeto:

- **`docker-compose.yml`:** define os 4 serviços Docker que compõem o ambiente local. É o ponto de entrada do projeto — `make up` e tudo sobe.
- **`Dockerfile`:** imagem customizada baseada em Python 3.11 com todas as dependências instaladas (`requirements.txt`). Usada para rodar scripts que precisam de OpenCV, scikit-learn e outras bibliotecas pesadas.
- **`Makefile`:** atalhos para comandos frequentes. `make up` sobe o ambiente, `make pipeline` dispara a DAG, `make ml-train` roda os modelos, `make test` roda os testes automatizados, etc.
- **`requirements.txt`:** lista de todas as bibliotecas Python com versões fixas (pandas, numpy, opencv-python, scikit-learn, vaderSentiment, textstat, boto3, apache-airflow, dbt-core, etc.).
- **`.env.local` / `.env.prod` / `.env.example`:** arquivos de configuração de ambiente. O `.env.example` é o template; `.env.local` é desenvolvimento; `.env.prod` é produção.
- **`notebooks/`:** Jupyter notebooks com análises exploratórias (EDA) e experimentos de machine learning feitos antes de escrever os scripts definitivos.
- **`data/raw/`:** arquivos CSV originais baixados do Kaggle (gitignorados por serem grandes).
- **`data/processed/`:** arquivos gerados em cada etapa do pipeline — `products_clean.csv`, `reviews_features.csv`, `images_features.csv`, `ml_features.csv` e os resultados do modelo (CSV + PNGs).
- **`images/products/`:** imagens de produtos baixadas (gitignoradas).
- **`ingestion/`:** scripts de ingestão — download do Kaggle e upload para S3/MinIO.
- **`processing/`:** scripts de extração e limpeza — dados estruturados, features de texto (NLP), features de imagem (CV) e merge final.
- **`dags/`:** a DAG do Airflow que orquestra o pipeline completo.
- **`dbt_project/`:** o projeto dbt com modelos SQL organizados em staging, dimensions, facts e marts, mais testes e documentação.
- **`ml/`:** implementações de machine learning — `hard_code/` com Naive Bayes do zero, `sklearn/` com MultinomialNB da scikit-learn, e `evaluate.py` para comparação.
- **`dashboard/`:** queries SQL e definições dos gráficos do Metabase (ainda a serem populadas).
- **`infra/`:** o template CloudFormation com a arquitetura AWS.
- **`tests/`:** testes automatizados com pytest para validar processamento, NLP e ML.
- **`report/`:** relatório final e apresentação do projeto.
- **`PLANO_PROJETO.md`:** planejamento detalhado de todas as etapas, arquitetura e requisitos. É o documento de design do projeto.
- **`FLUXO.md`:** este arquivo — a explicação narrativa de como tudo funciona junto.
