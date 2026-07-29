#!/usr/bin/env python3
"""
Script de configuracao automatica do Metabase.
Cria a conexao com o banco, as perguntas SQL e os dashboards via API REST.

Uso: python3 scripts/setup_metabase.py
"""

import requests
import time
import json
import sys
import os

METABASE_URL = os.getenv("METABASE_URL", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("METABASE_ADMIN", "admin@projeto.com")
ADMIN_PASS = os.getenv("METABASE_PASS", "ProjetoIFG2025!")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASS = os.getenv("DB_PASS", "airflow")
DB_NAME = os.getenv("DB_NAME", "airflow")

session = requests.Session()
token = None


def wait_for_metabase(timeout=120):
    """Espera o Metabase ficar disponivel."""
    print("[1/7] Aguardando Metabase iniciar...")
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
    """Configura usuario admin se for o primeiro acesso."""
    global token
    print("[2/7] Verificando configuracao inicial...")

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
                "site_name": "Projeto Final IFG",
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
    """Adiciona o PostgreSQL como fonte de dados."""
    print("[3/7] Adicionando conexao com PostgreSQL...")

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

    db_id = r.json().get("id")
    print(f"       Banco adicionado (ID: {db_id}).")
    return db_id


def sync_database(db_id):
    """Forca o sync do banco para detectar tabelas."""
    print("[4/7] Sincronizando schema do banco...")

    r = session.post(f"{METABASE_URL}/api/database/{db_id}/sync_schema")
    if r.status_code != 200:
        print(f"       Aviso: sync pode falhar se nao houver tabelas ainda. OK.")
    else:
        print("       Schema sincronizado.")

    time.sleep(3)
    return True


def create_card(name, sql, display="table", description=""):
    """Cria uma pergunta SQL (card) no Metabase."""
    payload = {
        "name": name,
        "display": display,
        "description": description,
        "dataset_query": {
            "type": "native",
            "native": {"query": sql},
            "database": db_id,
        },
        "visualization_settings": {},
    }

    r = session.post(f"{METABASE_URL}/api/card", json=payload)
    if r.status_code == 200:
        return r.json().get("id")
    else:
        print(f"       ERRO ao criar card '{name}': {r.text}")
        return None


def create_dashboard(name, description=""):
    """Cria um dashboard no Metabase."""
    payload = {
        "name": name,
        "description": description,
    }
    r = session.post(f"{METABASE_URL}/api/dashboard", json=payload)
    if r.status_code == 200:
        return r.json().get("id")
    else:
        print(f"       ERRO ao criar dashboard '{name}': {r.text}")
        return None


def add_card_to_dashboard(dashboard_id, card_id):
    """Adiciona um card a um dashboard."""
    payload = {"cardId": card_id}
    r = session.post(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards",
        json=payload,
    )
    return r.status_code == 200


def setup_collections():
    """Cria as colecoes (pastas) para organizar as perguntas."""
    print("[5/7] Criando colecoes...")

    collections = {
        "Visao Geral": "KPIs e metricas principais do e-commerce.",
        "Analise de Sentimento": "Analise de NLP sobre as reviews.",
        "Analise Visual": "Features de imagem e seu impacto.",
        "Resultados ML": "Metricas e comparacoes do modelo.",
    }

    created = {}
    personal_id = None

    r = session.get(f"{METABASE_URL}/api/collection")
    if r.status_code == 200:
        for col in r.json():
            if col.get("name") == "Our analytics":
                personal_id = col.get("id")
            if col.get("name") in collections:
                created[col.get("name")] = col.get("id")

    if personal_id is None:
        print("ERRO: Nao encontrou colecao 'Our analytics'.")
        return created

    for name, desc in collections.items():
        if name not in created:
            r = session.post(f"{METABASE_URL}/api/collection", json={
                "name": name, "description": desc,
                "parent_id": personal_id, "color": "#509EE3",
            })
            if r.status_code == 200:
                created[name] = r.json().get("id")
                print(f"       Colecao '{name}' criada.")
            else:
                print(f"       ERRO ao criar colecao '{name}': {r.text}")

    return created


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

    print("[6/7] Criando perguntas SQL e dashboards...")

    cards = {
        "KPI - Total de Produtos": {
            "sql": "SELECT COUNT(*) AS total_produtos FROM dim_products",
            "display": "scalar",
            "desc": "Quantos produtos estao cadastrados?",
        },
        "KPI - Rating Medio": {
            "sql": "SELECT ROUND(AVG(rating)::numeric, 2) AS rating_medio FROM dim_products",
            "display": "scalar",
            "desc": "Qual o rating medio de todos os produtos?",
        },
        "KPI - Reviews Negativas (%)": {
            "sql": "SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE rating <= 2) / COUNT(*), 1) AS pct_negativas FROM dim_products",
            "display": "scalar",
            "desc": "Porcentagem de produtos com rating baixo.",
        },
        "Rating por Categoria": {
            "sql": "SELECT category_name, ROUND(AVG(rating)::numeric, 2) AS avg_rating FROM dim_categories c JOIN dim_products p ON p.category_id = c.category_id GROUP BY category_name ORDER BY avg_rating DESC",
            "display": "bar",
            "desc": "Media de rating por categoria de produto.",
        },
        "Top 10 Piores Produtos": {
            "sql": "SELECT product_name, rating, rating_count, category FROM dim_products ORDER BY rating ASC, rating_count DESC LIMIT 10",
            "display": "table",
            "desc": "Produtos com pior avaliacao que precisam de atencao.",
        },
        "Polaridade por Rating": {
            "sql": "SELECT rating, ROUND(AVG(polarity)::numeric, 3) AS avg_polarity, COUNT(*) AS qtd_reviews FROM fact_reviews GROUP BY rating ORDER BY rating",
            "display": "bar",
            "desc": "Relacao entre nota e sentimento do texto.",
        },
        "Reviews com Dissonancia": {
            "sql": "SELECT p.product_name, r.rating, ROUND(r.polarity::numeric, 3) AS polarity, r.review_content FROM fact_reviews r JOIN dim_products p ON p.product_id = r.product_id WHERE r.rating >= 4 AND r.polarity < 0 LIMIT 20",
            "display": "table",
            "desc": "Reviews com nota alta mas texto negativo.",
        },
        "Blur Score vs Rating": {
            "sql": "SELECT p.product_name, ROUND(p.blur_score::numeric, 0) AS blur_score, p.rating FROM dim_products p WHERE p.blur_score IS NOT NULL ORDER BY p.blur_score DESC LIMIT 15",
            "display": "table",
            "desc": "Produtos com imagens borradas e seus ratings.",
        },
        "Brilho vs Rating": {
            "sql": "SELECT ROUND(brightness_mean::numeric, 1) AS brightness, rating, product_name FROM dim_products WHERE brightness_mean IS NOT NULL ORDER BY brightness_mean ASC LIMIT 30",
            "display": "scatter",
            "desc": "Ha relacao entre brilho da imagem e rating?",
        },
        "Top Features TF-IDF por Rating 5": {
            "sql": "SELECT split_part(feature, '_', 2) AS palavra, avg_valor FROM (SELECT unnest(array['tfidf_great','tfidf_excellent','tfidf_amazing','tfidf_love','tfidf_best']) AS feature) f CROSS JOIN (SELECT AVG(tfidf_great) AS tfidf_great, AVG(tfidf_excellent) AS tfidf_excellent, AVG(tfidf_amazing) AS tfidf_amazing, AVG(tfidf_love) AS tfidf_love, AVG(tfidf_best) AS tfidf_best FROM ml_features WHERE rating = 5) t CROSS JOIN LATERAL (VALUES ('tfidf_great', t.tfidf_great), ('tfidf_excellent', t.tfidf_excellent), ('tfidf_amazing', t.tfidf_amazing), ('tfidf_love', t.tfidf_love), ('tfidf_best', t.tfidf_best)) AS v(feature, avg_valor) WHERE f.feature = v.feature ORDER BY avg_valor DESC",
            "display": "bar",
            "desc": "Palavras mais frequentes em reviews nota 5.",
        },
    }

    card_ids = {}
    for name, config in cards.items():
        cid = create_card(name, config["sql"], config["display"], config["desc"])
        if cid:
            card_ids[name] = cid
            print(f"       Card '{name}' criado (ID: {cid}).")

    print("[7/7] Montando dashboards...")

    dashboards = {
        "Visao Geral": {
            "desc": "KPIs e metricas principais do e-commerce.",
            "cards": [
                "KPI - Total de Produtos",
                "KPI - Rating Medio",
                "KPI - Reviews Negativas (%)",
                "Rating por Categoria",
                "Top 10 Piores Produtos",
            ],
        },
        "Analise de Sentimento (NLP)": {
            "desc": "Analise das reviews com tecnicas de NLP.",
            "cards": [
                "Polaridade por Rating",
                "Reviews com Dissonancia",
            ],
        },
        "Analise Visual (Imagens)": {
            "desc": "Impacto das features de imagem no rating.",
            "cards": [
                "Blur Score vs Rating",
                "Brilho vs Rating",
            ],
        },
        "Resultados do Modelo ML": {
            "desc": "Metricas e analise do modelo de ML.",
            "cards": [
                "Top Features TF-IDF por Rating 5",
            ],
        },
    }

    for dash_name, dash_config in dashboards.items():
        dash_id = create_dashboard(dash_name, dash_config["desc"])
        if dash_id:
            print(f"       Dashboard '{dash_name}' criado (ID: {dash_id}).")
            for card_name in dash_config["cards"]:
                if card_name in card_ids:
                    ok = add_card_to_dashboard(dash_id, card_ids[card_name])
                    if ok:
                        print(f"          Card '{card_name}' adicionado.")
                    else:
                        print(f"          ERRO ao adicionar card '{card_name}'.")

    print("\n========================================")
    print("Configuracao do Metabase concluida!")
    print(f"Acesse: {METABASE_URL}")
    print(f"Login: {ADMIN_EMAIL}")
    print(f"Senha: {ADMIN_PASS}")
    print("========================================")


if __name__ == "__main__":
    main()
