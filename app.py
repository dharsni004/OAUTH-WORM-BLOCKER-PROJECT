from flask import Flask, jsonify, render_template, redirect, request, session
import sqlite3
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

app = Flask(__name__)
app.secret_key = "oauthwormblockersecret"

DB_PATH = "events.db"
GITHUB_CLIENT_ID = "Ov23liOlFJqOZUBLTWeN"
GITHUB_CLIENT_SECRET = "d0f9130bd5012f762be73d40f369d302e99fbc25"

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

# ─── GitHub OAuth Routes ───────────────────────────────────────────

@app.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&scope=read:user"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code received from GitHub", 400

    response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
    )
    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return "Failed to get access token", 400

    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user = user_response.json()

    session["token"] = access_token
    session["username"] = user.get("login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO token_events
            (token_id, source, hour_of_day, ip_country, request_rate,
             scope_count, num_orgs_used, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"gh_{user.get('login')}",
        "real_github",
        datetime.now().hour,
        "IN",
        1,
        1,
        1,
        datetime.now().isoformat(timespec="seconds")
    ))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/logout")
def logout():
    token = session.get("token")
    if token:
        requests.delete(
            f"https://api.github.com/applications/{GITHUB_CLIENT_ID}/token",
            auth=(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET),
            json={"access_token": token}
        )
    session.clear()
    return redirect("/")

# ─── Dashboard & API Routes ────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        logged_in="token" in session,
        username=session.get("username", "")
    )

@app.route("/api/events")
def get_events():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, token_id, source, hour_of_day, ip_country,
               request_rate, scope_count, num_orgs_used,
               timestamp, risk_score, decision
        FROM token_events
        ORDER BY id DESC
        LIMIT 50
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/revoked")
def get_revoked():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT token_id, revoked_at, reason, triggering_event_id
        FROM revoked_tokens
        ORDER BY revoked_at DESC
        LIMIT 50
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM token_events")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM token_events WHERE decision='ANOMALOUS'")
    anomalous = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM token_events WHERE decision='normal'")
    normal = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM revoked_tokens")
    revoked = cur.fetchone()[0]
    conn.close()
    return jsonify({
        "total": total,
        "normal": normal,
        "anomalous": anomalous,
        "revoked": revoked
    })

@app.route("/api/chart")
def get_chart():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, decision
        FROM token_events
        WHERE decision IS NOT NULL
        ORDER BY id DESC
        LIMIT 40
    """)
    rows = cur.fetchall()
    conn.close()

    buckets = defaultdict(lambda: {"normal": 0, "anomalous": 0})
    for row in reversed(rows):
        ts = dict(row)["timestamp"][:16]
        decision = dict(row)["decision"]
        if decision == "normal":
            buckets[ts]["normal"] += 1
        elif decision == "ANOMALOUS":
            buckets[ts]["anomalous"] += 1

    labels = list(buckets.keys())[-15:]
    normal = [buckets[l]["normal"] for l in labels]
    anomalous = [buckets[l]["anomalous"] for l in labels]

    return jsonify({
        "labels": [l[11:] for l in labels],
        "normal": normal,
        "anomalous": anomalous
    })

@app.route("/api/inject", methods=["POST"])
def inject_attack():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO token_events
            (token_id, source, hour_of_day, ip_country, request_rate,
             scope_count, num_orgs_used, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("token_id", "tok_sim_001"),
        "attack_injection",
        data.get("hour", 3),
        data.get("ip", "RU"),
        data.get("rate", 50),
        data.get("scopes", 6),
        data.get("orgs", 4),
        datetime.now().isoformat(timespec="seconds")
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "injected"})

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="127.0.0.1", threaded=True)