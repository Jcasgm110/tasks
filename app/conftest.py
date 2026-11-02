import os

import psycopg2
import pytest

os.environ["POSTGRES_DB"] = "tasks_test"


def _create_test_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname="postgres",
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'tasks_test'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE tasks_test")
    conn.close()


_create_test_db()

from app import create_app, get_conn


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("TRUNCATE tasks RESTART IDENTITY")
    conn.close()
    return app.test_client()