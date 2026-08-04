"""Load merged features CSV into PostgreSQL for dbt consumption."""

import os

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

load_dotenv(find_dotenv())

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASS = os.getenv("DB_PASS", "airflow")
DB_NAME = os.getenv("DB_NAME", "airflow")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")


def main():
    csv_path = os.path.join("data", "processed", "ml_features.csv")

    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found. Run merge_features.py first.")
        return

    print(f"Loading {csv_path} into PostgreSQL...")
    df = pd.read_csv(csv_path)

    table_name = "ml_features_raw"
    connection_string = (
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(connection_string)

    # Views do dbt (staging) dependem desta tabela — o replace do pandas
    # falha sem CASCADE. As views sao recriadas no proximo `dbt run`.
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {DB_SCHEMA}.{table_name} CASCADE"))

    df.to_sql(
        table_name,
        engine,
        schema=DB_SCHEMA,
        if_exists="append",
        index=False,
    )

    print(f"  Loaded {len(df)} rows into {DB_SCHEMA}.{table_name}")
    print("Done.")


if __name__ == "__main__":
    main()
