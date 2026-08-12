---
title: "Remoção de Emojis dos Nomes no Vault"
date: 2026-08-11
tags:
  - analise
  - vault
  - organizacao
---

# Remoção de Emojis dos Nomes no Vault

**Data:** 2026-08-11

## O que foi feito

Renomeadas as pastas e arquivos do vault que tinham emojis no nome, usando apenas texto ASCII/accentuado:

| Antes | Depois |
|---|---|
| `📊 Análise/` | `Análise/` |
| `📊 Análise/📊 Análise.md` | `Análise/Análise.md` |
| `❓ Dúvidas/` | `Dúvidas/` |
| `❓ Dúvidas/❓ Dúvidas.md` | `Dúvidas/Dúvidas.md` |
| `📚 Conceitos Gerais/` | `Conceitos Gerais/` |
| `📚 Conceitos Gerais/📚 Conceitos Gerais.md` | `Conceitos Gerais/Conceitos Gerais.md` |
| `🏠 Home.md` | `Home.md` |

Todos os wikilinks que apontavam para os caminhos antigos foram atualizados em `Home.md`, `Bem-vindo.md`, `Canvas do Projeto.canvas`, nas 12 notas numeradas, nos índices das três categorias e no `workspace.json`. O `.opencode/instructions.md` (regras que o agente segue) também foi atualizado com os novos caminhos.

## Motivo

Nomes com emoji causam problemas em alguns scripts, CLIs e no git em ambiente Windows. Renomear para ASCII puro torna o vault mais portável e evita quebra de links.

## Impacto

- Arquivos afetados: renomeação via `git mv` (histórico preservado) em todo o `.docs-projeto-final/` e edição de `.opencode/instructions.md`
- Links e navegação interna funcionam normalmente após a troca de nome
- A nota histórica `2025-07-03 - Estruturacao do Vault e Passo a Passo.md` mantém os nomes antigos como registro do que foi criado na época

## Relacionado

- [[Análise/Análise]]
- [[Home]]
- [[Bem-vindo]]
