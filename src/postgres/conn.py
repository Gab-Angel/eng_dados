import psycopg2
from psycopg2.extras import RealDictCursor
from decouple import config
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_conn():
    return psycopg2.connect(
        dbname=config("POSTGRES_DB"),
        host=config("POSTGRES_HOST"),
        port=config("POSTGRES_PORT"),
        user=config("POSTGRES_USER"),
        password=config("POSTGRES_PASSWORD"),
        cursor_factory=RealDictCursor
    )



def create_table():
    try:
        with open(SCHEMA_PATH, "r") as f:
            table_schema = f.read()

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(table_schema)
                print("Tabelas criadas com Sucesso")

    except Exception as e:
        print(f"Erro ao criar tabela: {e}")


if __name__ == "__main__":
    create_table()
