import os

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def init_db():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id SERIAL PRIMARY KEY, "
            "title TEXT NOT NULL, "
            "done BOOLEAN NOT NULL DEFAULT false, "
            "created_at TIMESTAMP NOT NULL DEFAULT now())"
        )
    conn.close()


def create_app():
    app = Flask(__name__)
    init_db()

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        conn = get_conn()
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            rows = cur.fetchall()
        conn.close()
        return jsonify(rows)

    @app.route("/tasks", methods=["POST"])
    def add_task():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify(error="title é obrigatório"), 400
        conn = get_conn()
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
                (title,),
            )
            row = cur.fetchone()
        conn.close()
        return jsonify(row), 201

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        conn = get_conn()
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            deleted = cur.rowcount
        conn.close()
        if deleted == 0:
            return jsonify(error="não encontrada"), 404
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)