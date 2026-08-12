---
title: "Avaliacao do Ambiente Local para Rodar o Projeto"
date: 2026-08-11
tags:
  - analise
  - ambiente-local
  - prerrequisitos
  - docker
  - python
---

# Avaliação do Ambiente Local para Rodar o Projeto

**Data:** 2026-08-11

## O que foi feito

Levantamento do ambiente local da máquina para verificar se há condições de subir o projeto final do zero (Docker + Airflow + dbt + ML). Foram verificados: Docker, Python, `make`, WSL, Chocolatey, CPU/RAM e disco livre.

## Motivo

O projeto exige um conjunto específico de ferramentas e versões. Antes de rodar `make up && make ingest && ...`, é necessário confirmar que o hardware e o software instalados suportam o fluxo completo (download de ~7,9 GB, build de imagem customizada do Airflow, treinamento do MLP).

## Resultado do Levantamento

| Item | Status | Detalhe |
|---|---|---|
| Docker | ⚠️ Instalado, daemon parado | Docker Desktop v29.3.1 + Compose v5.1.1. Necessário iniciar o app. |
| Python | ❌ 3.13.14 | `requirements.txt` exige Python **< 3.13** (numpy 1.26.4, pandas 2.2.2 e scikit-learn 1.5.1 não têm wheel para 3.13). |
| `make` | ❌ Não instalado | Makefile não roda no PowerShell (usa sintaxe Unix: `rm -rf`, `python3`). |
| WSL | ✅ docker-desktop | Backend do Docker presente. |
| Chocolatey | ✅ Disponível | Permite instalar as ferramentas faltantes. |
| CPU | ✅ i5-1135G7 (4C/8T) | Suficiente para o pipeline. |
| RAM | ✅ 16 GB | Apertado, mas suficiente (Docker Desktop + Airflow + Postgres + MinIO + Metabase + build). |
| Disco C: | ⚠️ 46,4 GB livres | Dataset ~16,3 GB (zip 7,87 GB + extraído ~8,4 GB) + ~6–8 GB de imagens Docker ≈ 25–30 GB. Cabe, mas com folga pequena. |

## Barreiras reais para subir (nesta ordem)

1. **Docker Desktop parado** — iniciar o app antes do `make up`.
2. **Python 3.13 incompatível** — os scripts locais (`process`, `ml-train`, `load-db`, `dbt-run`) rodam no Python do host. Instalar 3.11/3.12 e criar venv:
   ```powershell
   choco install python@3.12
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. **`make` ausente** — instalar via Chocolatey (`choco install make`) e executar pelo **Git Bash** (não PowerShell), ou rodar os comandos do Makefile manualmente.
4. **Download de ~7,9 GB** do Zenodo — leva tempo; o `ingestion/download_dataset.py` suporta retomada (HTTP Range).
5. **Build da imagem `pf-airflow-pipeline`** (Dockerfile.airflow) — compila psycopg2 (gcc) e instala librosa/dbt; requer rede estável e RAM. A 0 dB SNR do dataset real, o treino do MLP é viável em CPU (hard-code ~2,6 s).

## Impacto

**Veredicto:** a máquina **tem condições** de rodar o projeto — hardware e Docker estão OK. Faltam apenas ajustes de preparação de ambiente:

1. Iniciar o Docker Desktop.
2. Instalar Python 3.11/3.12 + criar venv (necessário, pois só há 3.13).
3. Instalar `make` (via choco) e usar Git Bash, ou rodar os comandos manualmente.
4. Liberar ~10 GB extras de disco antes do download do dataset.

Arquivos afetados: nenhum código alterado — avaliação de pré-requisitos apenas.

## Relacionado

- [[03-Arquitetura]]
- [[11-Comandos]]
- [[12-Passo-a-Passo]]
- [[04-Pipeline-ELT]]
