import sqlite3
import random
import time
import argparse
import secrets
import string
from datetime import datetime

DB_PATH = "events.db"

NORMAL_HOURS = list(range(9, 19))
NORMAL_COUNTRY = "IN"
NORMAL_REQUEST_RATE = (1, 8)
NORMAL_SCOPE_COUNT = (1, 2)
NORMAL_ORGS_USED = 1

def generate_github_token():
    chars = string.ascii_letters + string.digits
    return "gho_" + ''.join(secrets.choice(chars) for _ in range(36))

def generate_google_token():
    chars = string.ascii_letters + string.digits + "-_"
    return "ya29.a0" + ''.join(secrets.choice(chars) for _ in range(58))

def generate_salesforce_token():
    chars = string.ascii_letters + string.digits
    return "00D5e000000HqEd!" + ''.join(secrets.choice(chars) for _ in range(36))

def generate_microsoft_token():
    header = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9"
    payload = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
    sig = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(43))
    return f"{header}.{payload}.{sig}"

PROVIDERS = [
    {"name": "github",      "gen": generate_github_token},
    {"name": "google",      "gen": generate_google_token},
    {"name": "salesforce",  "gen": generate_salesforce_token},
    {"name": "microsoft",   "gen": generate_microsoft_token},
]

TOKEN_POOL = []
for p in PROVIDERS:
    for _ in range(3):
        TOKEN_POOL.append({
            "token_id": p["gen"](),
            "provider": p["name"]
        })

def generate_normal_event():
    token = random.choice(TOKEN_POOL)
    return {
        "token_id": token["token_id"],
        "source": token["provider"],
        "hour_of_day": random.choice(NORMAL_HOURS),
        "ip_country": NORMAL_COUNTRY,
        "request_rate": random.randint(*NORMAL_REQUEST_RATE),
        "scope_count": random.randint(*NORMAL_SCOPE_COUNT),
        "num_orgs_used": NORMAL_ORGS_USED,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

def insert_event(conn, event):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO token_events
            (token_id, source, hour_of_day, ip_country, request_rate,
             scope_count, num_orgs_used, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (event["token_id"], event["source"], event["hour_of_day"],
          event["ip_country"], event["request_rate"], event["scope_count"],
          event["num_orgs_used"], event["timestamp"]))
    conn.commit()
    return cur.lastrowid

def run_batch(n):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    print(f"[SIMULATOR] Inserting {n} normal training events ...")
    for i in range(n):
        event = generate_normal_event()
        insert_event(conn, event)
        if (i + 1) % 50 == 0:
            print(f"  ... {i + 1}/{n} inserted")
    conn.close()
    print(f"[DONE] {n} normal events written to events.db")

def run_live(interval_seconds):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    print(f"[SIMULATOR] Live mode — new event every {interval_seconds}s. Ctrl+C to stop.\n")
    try:
        while True:
            event = generate_normal_event()
            row_id = insert_event(conn, event)
            print(f"[EVENT #{row_id}] {event['token_id'][:20]}... | "
                  f"{event['source']} | "
                  f"{event['ip_country']} | "
                  f"hour={event['hour_of_day']:02d} | "
                  f"rate={event['request_rate']} | "
                  f"scopes={event['scope_count']} | "
                  f"orgs={event['num_orgs_used']}")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n[STOPPED]")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, help="Insert N normal events for training")
    parser.add_argument("--live", action="store_true", help="Stream events continuously")
    parser.add_argument("--interval", type=float, default=3.0)
    args = parser.parse_args()

    if args.batch:
        run_batch(args.batch)
    elif args.live:
        run_live(args.interval)
    else:
        print("Use --batch N or --live")