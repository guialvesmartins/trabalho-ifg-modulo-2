# Regras do Vault Obsidian — Projeto Final IFG

## Localização do Vault

O vault do Obsidian está em `.docs-projeto-final/`. Todas as notas usam **Obsidian Flavored Markdown** (wikilinks `[[Nota]]`, callouts `> [!tipo]`, frontmatter YAML, etc.).

Sempre que fizer alterações em arquivos do projeto fora do vault, avalie se deve registrar no vault.

---

## Categorias do Vault

### 📊 Análise (`.docs-projeto-final/📊 Análise/`)

**Quando salvar:** Mudanças estruturais no projeto, decisões de arquitetura, refatorações significativas, criação/exclusão de arquivos importantes, mudanças no pipeline, alterações no docker-compose, novos scripts.

**Formato do arquivo:**
- Nome: `AAAA-MM-DD - Titulo Curto.md`
- Deve ter frontmatter: `title`, `date`, `tags: [analise, <contexto>]`
- Deve linkar para as notas relevantes do vault (ex: `[[03-Arquitetura]]`)
- Deve descrever: O que foi feito, por quê, e o que mudou

**Template:**

```markdown
---
title: "Titulo Descritivo"
date: AAAA-MM-DD
tags:
  - analise
  - <tag-especifica>
---

# Título Descritivo

**Data:** AAAA-MM-DD

## O que foi feito

Descrição clara da mudança.

## Motivo

Por que essa mudança foi necessária.

## Impacto

O que mudou no projeto. Arquivos afetados: `caminho/arquivo.py`

## Relacionado

- [[Nota Relacionada]]
```

Após criar o arquivo, **atualizar** o índice `📊 Análise/📊 Análise.md` adicionando um link `[[Nome do Arquivo]]` na seção de índice.

---

### ❓ Dúvidas (`.docs-projeto-final/❓ Dúvidas/`)

**Quando salvar:** Toda vez que o usuário fizer uma pergunta e você responder com uma explicação não trivial (conceitos, decisões de código, comparações, "como funciona", "por que usar X vs Y"). NÃO salvar perguntas operacionais simples (ex: "lista arquivos", "roda comando X").

**Formato do arquivo:**
- Nome: `Duvida - Titulo Curto.md`
- Deve ter frontmatter: `title`, `date`, `tags: [duvida, <tema>]`
- Deve conter: A pergunta do usuário e a resposta dada

**Template:**

```markdown
---
title: "Título da Dúvida"
date: AAAA-MM-DD
tags:
  - duvida
  - <tag-especifica>
---

# Título da Dúvida

## Pergunta

> [!question] Pergunta do usuário
> (colocar aqui a pergunta original)

## Resposta

(Resposta completa e didática)

## Relacionado

- [[Nota Relacionada]]
```

Após criar o arquivo, **atualizar** o índice `❓ Dúvidas/❓ Dúvidas.md` adicionando um link.

---

### 📚 Conceitos Gerais (`.docs-projeto-final/📚 Conceitos Gerais/`)

**Quando salvar:** Conceitos teóricos, fundamentos, padrões de projeto, ou conhecimento geral que surgir durante o desenvolvimento e for útil para referência futura. Exemplos: "O que é TF-IDF", "Como funciona Laplace Smoothing", "Padrão Star Schema no dbt", "Diferença entre ETL e ELT".

**Formato do arquivo:**
- Nome: `Conceito - Nome do Conceito.md`
- Deve ter frontmatter: `title`, `date`, `tags: [conceito, <tema>]`
- Deve conter: Explicação didática com exemplos quando relevante

**Template:**

```markdown
---
title: "Nome do Conceito"
date: AAAA-MM-DD
tags:
  - conceito
  - <tag-especifica>
---

# Nome do Conceito

## Definição

(Explicação clara e objetiva)

## Exemplo

(Exemplo prático relacionado ao projeto)

## Relacionado

- [[Nota Relacionada]]
```

Após criar o arquivo, **atualizar** o índice `📚 Conceitos Gerais/📚 Conceitos Gerais.md` adicionando um link.

---

## Regras Gerais

1. **Sempre use Obsidian Flavored Markdown** — wikilinks `[[...]]`, callouts `> [!tipo]`, frontmatter YAML, checklists `- [ ]`.
2. **Sempre adicione tags** no frontmatter para facilitar busca.
3. **Sempre atualize o índice** da categoria ao criar um novo arquivo.
4. **Link para notas do vault** sempre que fizer referência a partes do projeto.
5. **Não crie notas para ações triviais** — apenas para conteúdo com valor de referência futura.
6. **Se estiver em dúvida se deve salvar, salve**. Melhor ter informação sobrando do que faltando.
7. **Após cada sessão de trabalho relevante**, verifique se há algo novo para registrar no vault.

## Checklist Pós-Sessão

Antes de encerrar uma sessão de trabalho significativa, verifique:
- [ ] Houve mudanças estruturais no projeto? → Salvar em 📊 Análise
- [ ] O usuário fez perguntas com respostas não triviais? → Salvar em ❓ Dúvidas
- [ ] Surgiram conceitos importantes? → Salvar em 📚 Conceitos Gerais
