#!/usr/bin/env python3
"""
Script de configuracao automatica do Metabase.
Cria a conexao com o banco, as perguntas SQL, os dashboards e o filtro
analitico por modelo de maquina via API REST.

Re-executavel: cards e dashboards com os mesmos nomes sao arquivados e
recriados, refletindo o estado atual do banco.

Uso: python3 scripts/setup_metabase.py
"""

import json
import os
import sys
import time

import requests

METABASE_URL = os.getenv("METABASE_URL", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("METABASE_ADMIN", "admin@projeto.com")
ADMIN_PASS = os.getenv("METABASE_PASS", "ProjetoIFG2025!")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASS = os.getenv("DB_PASS", "airflow")
DB_NAME = os.getenv("DB_NAME", "airflow")

# Filtro analitico por modelo de maquina (requisito 4.7 do projeto)
MODEL_FILTER_PARAM_ID = "8f7a1b2c"
MODEL_TEMPLATE_TAG = {
    "model_id": {
        "id": "c3d4e5f6-0000-0000-0000-000000000001",
        "name": "model_id",
        "display-name": "Modelo da Maquina",
        "type": "text",
        "required": False,
    }
}

session = requests.Session()
token = None
db_id = None


def wait_for_metabase(timeout=120):
    print("[1/8] Aguardando Metabase iniciar...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = session.get(f"{METABASE_URL}/api/health", timeout=5)
            if r.status_code == 200:
                print("       Metabase esta pronto!")
                return True
        except Exception:
            pass
        time.sleep(2)
    print("ERRO: Metabase nao iniciou dentro do timeout.")
    return False


def setup_admin():
    global token
    print("[2/8] Verificando configuracao inicial...")

    r = session.get(f"{METABASE_URL}/api/session/properties")
    if r.status_code != 200:
        print("ERRO: Nao foi possivel acessar o Metabase.")
        return False

    setup_token = r.json().get("setup-token")

    if setup_token:
        print("       Primeiro acesso detectado. Criando admin...")
        r = session.post(f"{METABASE_URL}/api/setup", json={
            "token": setup_token,
            "user": {
                "first_name": "Admin",
                "last_name": "Projeto",
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASS,
            },
            "prefs": {
                "site_name": "Manutencao Preditiva Industrial",
                "site_locale": "pt-BR",
            },
        })
        if r.status_code != 200:
            print(f"       ERRO ao criar admin: {r.text}")
            return False

        token = r.json().get("id")
        print("       Admin criado com sucesso.")
    else:
        print("       Metabase ja configurado. Fazendo login...")
        r = session.post(f"{METABASE_URL}/api/session", json={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASS,
        })
        if r.status_code != 200:
            print(f"       ERRO ao fazer login: {r.text}")
            return False
        token = r.json().get("id")

    session.headers.update({"X-Metabase-Session": token})
    return True


def add_database():
    print("[3/8] Adicionando conexao com PostgreSQL...")

    payload = {
        "engine": "postgres",
        "name": "Projeto Final - PostgreSQL",
        "details": {
            "host": DB_HOST,
            "port": DB_PORT,
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASS,
            "ssl": False,
        },
        "is_full_sync": True,
        "is_on_demand": False,
    }

    r = session.get(f"{METABASE_URL}/api/database")
    databases = r.json().get("data", [])

    for db in databases:
        if db.get("name") == payload["name"]:
            print(f"       Banco ja configurado (ID: {db['id']}).")
            return db["id"]

    r = session.post(f"{METABASE_URL}/api/database", json=payload)
    if r.status_code != 200:
        print(f"       ERRO: {r.text}")
        return None

    new_id = r.json().get("id")
    print(f"       Banco adicionado (ID: {new_id}).")
    return new_id


def sync_database(database_id):
    print("[4/8] Sincronizando schema do banco...")
    r = session.post(f"{METABASE_URL}/api/database/{database_id}/sync_schema")
    if r.status_code != 200:
        print("       Aviso: sync pode falhar se nao houver tabelas ainda. OK.")
    else:
        print("       Schema sincronizado.")
    time.sleep(3)
    return True


def archive_existing(card_names, dashboard_names):
    """Arquiva cards e dashboards antigos com os mesmos nomes (re-execucao)."""
    print("[5/8] Arquivando versoes antigas de cards/dashboards...")

    r = session.get(f"{METABASE_URL}/api/card")
    if r.status_code == 200:
        for card in r.json():
            if card.get("name") in card_names and not card.get("archived"):
                session.put(f"{METABASE_URL}/api/card/{card['id']}",
                            json={"archived": True})

    r = session.get(f"{METABASE_URL}/api/dashboard")
    if r.status_code == 200:
        for dash in r.json():
            if dash.get("name") in dashboard_names and not dash.get("archived"):
                session.put(f"{METABASE_URL}/api/dashboard/{dash['id']}",
                            json={"archived": True})


def create_card(name, sql, display="table", description="", with_model_filter=False):
    native = {"query": sql}
    if with_model_filter:
        native["template-tags"] = MODEL_TEMPLATE_TAG

    payload = {
        "name": name,
        "display": display,
        "description": description,
        "dataset_query": {
            "type": "native",
            "native": native,
            "database": db_id,
        },
        "visualization_settings": {},
    }

    r = session.post(f"{METABASE_URL}/api/card", json=payload)
    if r.status_code == 200:
        return r.json().get("id")
    print(f"       ERRO ao criar card '{name}': {r.text[:200]}")
    return None


def create_dashboard(name, description=""):
    payload = {"name": name, "description": description}
    r = session.post(f"{METABASE_URL}/api/dashboard", json=payload)
    if r.status_code == 200:
        return r.json().get("id")
    print(f"       ERRO ao criar dashboard '{name}': {r.text[:200]}")
    return None


def populate_dashboard(dashboard_id, entries, with_filter=False):
    """Adiciona cards ao dashboard via API nova (PUT dashcards); usa a API
    antiga (POST /cards) como fallback para versoes anteriores do Metabase."""
    parameters = []
    if with_filter:
        parameters = [{
            "id": MODEL_FILTER_PARAM_ID,
            "name": "Modelo da Maquina",
            "slug": "modelo_da_maquina",
            "type": "string/=",
            "sectionId": "string",
        }]

    dashcards = []
    row, col = 0, 0
    for i, entry in enumerate(entries):
        size_x = 8 if entry["display"] in ("table",) else 6
        size_y = 4
        if col + size_x > 24:
            row += size_y
            col = 0
        mappings = []
        if with_filter and entry.get("filterable"):
            mappings = [{
                "parameter_id": MODEL_FILTER_PARAM_ID,
                "card_id": entry["card_id"],
                "target": ["variable", ["template-tag", "model_id"]],
            }]
        dashcards.append({
            "id": -(i + 1),
            "card_id": entry["card_id"],
            "row": row,
            "col": col,
            "size_x": size_x,
            "size_y": size_y,
            "parameter_mappings": mappings,
        })
        col += size_x

    payload = {"dashcards": dashcards}
    if parameters:
        payload["parameters"] = parameters

    r = session.put(f"{METABASE_URL}/api/dashboard/{dashboard_id}", json=payload)
    if r.status_code == 200:
        return True

    # Fallback: API antiga (< v0.49)
    ok = True
    for entry in entries:
        r = session.post(
            f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards",
            json={"cardId": entry["card_id"]},
        )
        ok = ok and r.status_code == 200
    return ok


def main():
    global db_id

    if not wait_for_metabase():
        sys.exit(1)
    if not setup_admin():
        sys.exit(1)

    db_id = add_database()
    if db_id is None:
        sys.exit(1)

    sync_database(db_id)

    # [[...]] = clausula opcional do Metabase: o filtro so e aplicado
    # quando o usuario escolhe um valor no dashboard.
    cards = {
        "KPI - Total de Amostras": {
            "sql": "SELECT COUNT(*) AS total_amostras FROM public_analytics.fact_audio_analysis",
            "display": "scalar",
            "desc": "Total de arquivos de audio analisados.",
        },
        "KPI - Taxa de Anomalia (%)": {
            "sql": "SELECT ROUND(100.0 * SUM(condition_binary) / COUNT(*), 1) AS pct_anomalia FROM public_analytics.fact_audio_analysis",
            "display": "scalar",
            "desc": "Porcentagem de maquinas com anomalia detectada.",
        },
        "KPI - Duracao Media (s)": {
            "sql": "SELECT ROUND(AVG(duration_sec)::numeric, 2) AS duracao_media FROM public_analytics.fact_audio_analysis",
            "display": "scalar",
            "desc": "Duracao media dos arquivos de audio.",
        },
        "Anomalias por Modelo": {
            "sql": "SELECT model_id, SUM(condition_binary) AS anomalias, COUNT(*) - SUM(condition_binary) AS normais FROM public_analytics.fact_audio_analysis WHERE 1=1 [[AND model_id = {{model_id}}]] GROUP BY model_id ORDER BY model_id",
            "display": "bar",
            "desc": "Distribuicao de normal vs anomalia por modelo de maquina.",
            "filter": True,
        },
        "Distribuicao de Condicoes": {
            "sql": "SELECT condition, COUNT(*) AS total FROM public_analytics.fact_audio_analysis WHERE 1=1 [[AND model_id = {{model_id}}]] GROUP BY condition ORDER BY condition",
            "display": "pie",
            "desc": "Proporcao de maquinas normais vs com anomalia.",
            "filter": True,
        },
        "Top 10 Maior RMS": {
            "sql": "SELECT file_id, model_id, condition, ROUND(rms_mean::numeric, 6) AS rms_mean FROM public_analytics.fact_audio_analysis WHERE 1=1 [[AND model_id = {{model_id}}]] ORDER BY rms_mean DESC LIMIT 10",
            "display": "table",
            "desc": "Amostras com maior energia (RMS) — possivel anomalia severa.",
            "filter": True,
        },
        "Media MFCC-1 por Modelo": {
            "sql": "SELECT model_id, ROUND(AVG(mfcc_1_mean)::numeric, 4) AS avg_mfcc1 FROM public_analytics.fact_audio_analysis WHERE 1=1 [[AND model_id = {{model_id}}]] GROUP BY model_id ORDER BY model_id",
            "display": "bar",
            "desc": "Coeficiente MFCC-1 medio por modelo de maquina.",
            "filter": True,
        },
        "Spectral Centroid vs Condicao": {
            "sql": "SELECT condition, ROUND(AVG(spectral_centroid_mean)::numeric, 2) AS avg_centroid FROM public_analytics.fact_audio_analysis WHERE 1=1 [[AND model_id = {{model_id}}]] GROUP BY condition",
            "display": "bar",
            "desc": "Centroide espectral medio para maquinas normais vs anomalas.",
            "filter": True,
        },
        "Resumo por Modelo": {
            "sql": "SELECT * FROM public_analytics.dim_machines ORDER BY model_id",
            "display": "table",
            "desc": "Tabela resumo com metricas por modelo de maquina.",
        },
        # --- Resultados do modelo de ML (tabelas geradas por ml/evaluate.py) ---
        "KPI - Acuracia do Modelo (%)": {
            "sql": "SELECT ROUND(100.0 * SUM(CASE WHEN y_true = pred_sklearn THEN 1 ELSE 0 END) / COUNT(*), 2) AS acuracia FROM model_predictions",
            "display": "scalar",
            "desc": "Acuracia do MLP sklearn no conjunto de teste.",
        },
        "Metricas dos Modelos": {
            "sql": "SELECT * FROM model_metrics",
            "display": "table",
            "desc": "Comparacao de metricas: baselines vs MLP hard-code vs MLP sklearn.",
        },
        "Matriz de Confusao (Sklearn)": {
            "sql": "SELECT CASE y_true WHEN 1 THEN 'anomalia' ELSE 'normal' END AS real, CASE pred_sklearn WHEN 1 THEN 'anomalia' ELSE 'normal' END AS predito, COUNT(*) AS total FROM model_predictions GROUP BY 1, 2 ORDER BY 1, 2",
            "display": "table",
            "desc": "Matriz de confusao do MLP sklearn no conjunto de teste.",
        },
        "Predicoes com Erro": {
            "sql": "SELECT file_id, model_id, condition_real, CASE pred_sklearn WHEN 1 THEN 'anomalia' ELSE 'normal' END AS predito, proba_sklearn FROM model_predictions WHERE erro_sklearn = 1 ORDER BY proba_sklearn DESC",
            "display": "table",
            "desc": "Amostras do teste classificadas incorretamente — insumo da analise qualitativa.",
        },
    }

    dashboards = {
        "Manutencao Preditiva — Visao Geral": {
            "desc": "KPIs e metricas principais do monitoramento industrial. Filtro por modelo de maquina.",
            "cards": [
                "KPI - Total de Amostras",
                "KPI - Taxa de Anomalia (%)",
                "KPI - Duracao Media (s)",
                "Distribuicao de Condicoes",
                "Anomalias por Modelo",
            ],
            "filter": True,
        },
        "Analise de Audio por Modelo": {
            "desc": "Detalhamento das features de audio por modelo de maquina. Filtro por modelo.",
            "cards": [
                "Resumo por Modelo",
                "Media MFCC-1 por Modelo",
                "Spectral Centroid vs Condicao",
                "Top 10 Maior RMS",
            ],
            "filter": True,
        },
        "Resultados do Modelo ML": {
            "desc": "Metricas, matriz de confusao e erros do modelo de Machine Learning.",
            "cards": [
                "KPI - Acuracia do Modelo (%)",
                "Metricas dos Modelos",
                "Matriz de Confusao (Sklearn)",
                "Predicoes com Erro",
            ],
            "filter": False,
        },
    }

    archive_existing(set(cards), set(dashboards))

    print("[6/8] Criando perguntas SQL...")
    card_ids = {}
    for name, config in cards.items():
        cid = create_card(
            name, config["sql"], config["display"], config["desc"],
            with_model_filter=config.get("filter", False),
        )
        if cid:
            card_ids[name] = cid
            print(f"       Card '{name}' criado (ID: {cid}).")

    print("[7/8] Montando dashboards...")
    for dash_name, dash_config in dashboards.items():
        dash_id = create_dashboard(dash_name, dash_config["desc"])
        if not dash_id:
            continue
        print(f"       Dashboard '{dash_name}' criado (ID: {dash_id}).")

        entries = []
        for card_name in dash_config["cards"]:
            if card_name in card_ids:
                entries.append({
                    "card_id": card_ids[card_name],
                    "display": cards[card_name]["display"],
                    "filterable": cards[card_name].get("filter", False),
                })
        ok = populate_dashboard(dash_id, entries, with_filter=dash_config["filter"])
        status = "OK" if ok else "ERRO"
        print(f"          {len(entries)} cards adicionados [{status}]"
              + (" + filtro por modelo" if dash_config["filter"] else ""))

    print("[8/8] Concluido.")
    print("\n========================================")
    print("Configuracao do Metabase concluida!")
    print(f"Acesse: {METABASE_URL}")
    print(f"Login: {ADMIN_EMAIL}")
    print(f"Senha: {ADMIN_PASS}")
    print("========================================")


if __name__ == "__main__":
    main()
