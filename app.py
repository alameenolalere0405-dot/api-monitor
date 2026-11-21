from flask import Flask, jsonify, render_template, request
import ipaddress
import socket
import sqlite3
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

app = Flask(__name__)
DATABASE = "pulse.db"
TIMEOUT_SECONDS = 8


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint_id INTEGER NOT NULL,
                checked_at TEXT NOT NULL,
                is_up INTEGER NOT NULL,
                status_code INTEGER,
                response_ms REAL,
                error TEXT,
                FOREIGN KEY(endpoint_id) REFERENCES endpoints(id)
            )
        """)


def validate_public_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False, "Enter a valid HTTP or HTTPS URL."
    if parsed.username or parsed.password:
        return False, "URLs containing credentials are not allowed."
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        addresses = socket.getaddrinfo(parsed.hostname, port)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return False, "Private or non-public network addresses are not allowed."
    except (OSError, ValueError):
        return False, "The hostname could not be resolved."
    return True, ""


def run_check(endpoint_id, url):
    valid, reason = validate_public_url(url)
    started = time.perf_counter()
    status_code = None
    error = None
    is_up = False

    try:
        if not valid:
            raise ValueError(reason)
        response = requests.get(
            url,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
            headers={"User-Agent": "PulseAPIMonitor/1.0"}
        )
        status_code = response.status_code
        is_up = 200 <= status_code < 400
        if not is_up:
            error = f"HTTP {status_code}"
    except (requests.RequestException, ValueError) as exc:
        error = str(exc)[:250]

    elapsed = round((time.perf_counter() - started) * 1000, 2)
    with get_db() as conn:
        conn.execute("""
            INSERT INTO checks
            (endpoint_id, checked_at, is_up, status_code, response_ms, error)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            endpoint_id,
            datetime.now(timezone.utc).isoformat(),
            int(is_up),
            status_code,
            elapsed,
            error
        ))

    return {
        "is_up": is_up,
        "status_code": status_code,
        "response_ms": elapsed,
        "error": error
    }


@app.route("/")
def index():
    with get_db() as conn:
        endpoints = conn.execute("""
            SELECT e.*,
                (SELECT is_up FROM checks WHERE endpoint_id=e.id ORDER BY id DESC LIMIT 1) AS last_up,
                (SELECT status_code FROM checks WHERE endpoint_id=e.id ORDER BY id DESC LIMIT 1) AS last_status,
                (SELECT response_ms FROM checks WHERE endpoint_id=e.id ORDER BY id DESC LIMIT 1) AS last_response,
                (SELECT ROUND(AVG(is_up)*100, 1) FROM checks WHERE endpoint_id=e.id) AS uptime
            FROM endpoints e ORDER BY e.id DESC
        """).fetchall()
        total = len(endpoints)
        up = sum(1 for item in endpoints if item["last_up"] == 1)
        checks = conn.execute("SELECT COUNT(*) AS n FROM checks").fetchone()["n"]

    return render_template(
        "index.html", endpoints=endpoints, total=total, up=up, checks=checks
    )


@app.post("/api/endpoints")
def add_endpoint():
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    url = (data.get("url") or "").strip()

    if not name or not url:
        return jsonify(error="Both name and URL are required."), 400

    valid, reason = validate_public_url(url)
    if not valid:
        return jsonify(error=reason), 400

    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO endpoints (name, url, created_at) VALUES (?, ?, ?)",
                (name[:80], url, datetime.now(timezone.utc).isoformat())
            )
            endpoint_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify(error="That URL is already being monitored."), 409

    return jsonify(id=endpoint_id, message="Endpoint added."), 201


@app.post("/api/endpoints/<int:endpoint_id>/check")
def check_endpoint(endpoint_id):
    with get_db() as conn:
        endpoint = conn.execute(
            "SELECT * FROM endpoints WHERE id=?", (endpoint_id,)
        ).fetchone()

    if not endpoint:
        return jsonify(error="Endpoint not found."), 404

    return jsonify(run_check(endpoint["id"], endpoint["url"]))


@app.delete("/api/endpoints/<int:endpoint_id>")
def delete_endpoint(endpoint_id):
    with get_db() as conn:
        conn.execute("DELETE FROM checks WHERE endpoint_id=?", (endpoint_id,))
        cursor = conn.execute("DELETE FROM endpoints WHERE id=?", (endpoint_id,))

    if cursor.rowcount == 0:
        return jsonify(error="Endpoint not found."), 404
    return jsonify(message="Endpoint deleted.")


@app.get("/api/endpoints/<int:endpoint_id>/history")
def endpoint_history(endpoint_id):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT checked_at, is_up, status_code, response_ms, error
            FROM checks WHERE endpoint_id=? ORDER BY id DESC LIMIT 20
        """, (endpoint_id,)).fetchall()
    return jsonify([dict(row) for row in rows])


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
