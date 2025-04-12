import psycopg2
import os
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        host=os.getenv("NEON_HOST"),
        dbname=os.getenv("NEON_DB"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        port=5432,
        sslmode="require"
    )

def log_detection_to_db(timestamp, status, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO detection_logs (timestamp, status, image_path) VALUES (%s, %s, %s)",
        (timestamp, status, image_path)
    )
    conn.commit()
    cur.close()
    conn.close()

def fetch_logs(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT timestamp, status, image_path FROM detection_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
