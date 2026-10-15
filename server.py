
import os

import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify

app = Flask(__name__)


def get_database_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(
        database_url,
        connect_timeout=10,
        row_factory=dict_row
    )


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "server": "Smart Supermarket Server",
        "status": "running"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"})


@app.route("/health/db", methods=["GET"])
def database_health():
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS result")
                cursor.fetchone()

        return jsonify({
            "database": "connected",
            "status": "OK"
        })

    except Exception:
        app.logger.exception("Database health check failed")
        return jsonify({
            "database": "connection_failed",
            "status": "ERROR"
        }), 503


@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, price::float AS price
                    FROM public.products
                    ORDER BY id
                """)
                products = cursor.fetchall()

        return jsonify({
            "status": "success",
            "count": len(products),
            "products": products
        })

    except Exception:
        app.logger.exception("Could not load products")
        return jsonify({
            "status": "error",
            "message": "Could not load products"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
