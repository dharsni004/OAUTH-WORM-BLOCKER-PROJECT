import sqlite3
import joblib
import time
import numpy as np
from datetime import datetime

DB_PATH = "events.db"
MODEL_PATH = "oauth_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

def load_model():
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
    print("[INTERCEPTOR] Model loaded. Watching for new events...\n")
    return model, le

def score_event(model, le, event):
    # Encode ip_country — if unseen country comes in, handle it
    try:
        ip_encoded = le.transform([event['ip_country']])[0]
    except ValueError:
        # Country never seen in training = automatically suspicious
        ip_encoded = 99

    features = np.array([[
        event['hour_of_day'],
        ip_encoded,
        event['request_rate'],
        event['scope_count'],
        event['num_orgs_used']
    ]])

    prediction = model.predict(features)[0]   # -1 = anomaly, 1 = normal
    score = model.decision_function(features)[0]  # raw score, more negative = more anomalous
    return prediction, round(score, 4)

def revoke_token(conn, token_id, event_id, reason):
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO revoked_tokens
            (token_id, revoked_at, reason, triggering_event_id)
        VALUES (?, ?, ?, ?)
    """, (token_id, datetime.now().isoformat(timespec="seconds"), reason, event_id))
    conn.commit()

def update_event_decision(conn, event_id, risk_score, decision):
    cur = conn.cursor()
    cur.execute("""
        UPDATE token_events
        SET risk_score = ?, decision = ?
        WHERE id = ?
    """, (risk_score, decision, event_id))
    conn.commit()

def watch(poll_interval=2.0):
    model, le = load_model()
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    last_seen_id = 0

    # Start from the latest existing event so we only watch NEW ones
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM token_events")
    row = cur.fetchone()
    if row[0]:
        last_seen_id = row[0]

    print(f"[INTERCEPTOR] Watching from event ID > {last_seen_id}\n")

    try:
        while True:
            cur.execute("""
                SELECT id, token_id, source, hour_of_day, ip_country,
                       request_rate, scope_count, num_orgs_used
                FROM token_events
                WHERE id > ? AND decision IS NULL
                ORDER BY id ASC
            """, (last_seen_id,))
            new_events = cur.fetchall()

            for row in new_events:
                event_id, token_id, source, hour, ip, rate, scopes, orgs = row
                event = {
                    "hour_of_day": hour,
                    "ip_country": ip,
                    "request_rate": rate,
                    "scope_count": scopes,
                    "num_orgs_used": orgs
                }

                prediction, score = score_event(model, le, event)

                if prediction == -1:
                    decision = "ANOMALOUS"
                    revoke_token(conn, token_id, event_id, f"Anomaly score: {score}")
                    update_event_decision(conn, event_id, score, decision)
                    print(f"[EVENT #{event_id}] {token_id} | {ip} | "
                          f"hour={hour:02d} | rate={rate} | "
                          f"scopes={scopes} | orgs={orgs}")
                    print(f"  --> SCORE: {score}  |  ⚠️  ANOMALOUS — TOKEN REVOKED\n")
                else:
                    decision = "normal"
                    update_event_decision(conn, event_id, score, decision)
                    print(f"[EVENT #{event_id}] {token_id} | {ip} | "
                          f"hour={hour:02d} | rate={rate} | "
                          f"scopes={scopes} | orgs={orgs}  -->  score={score}  OK")

                last_seen_id = event_id

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n[INTERCEPTOR] Stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    watch()
    