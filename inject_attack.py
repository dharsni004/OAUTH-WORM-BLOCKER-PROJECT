import sqlite3
import argparse
from datetime import datetime

DB_PATH = "events.db"

def inject(token_id, ip_country, hour, rate, scopes, orgs):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO token_events
            (token_id, source, hour_of_day, ip_country, request_rate,
             scope_count, num_orgs_used, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        token_id,
        "attack_injection",
        hour,
        ip_country,
        rate,
        scopes,
        orgs,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    event_id = cur.lastrowid
    conn.close()

    print(f"\n[ATTACK INJECTED]")
    print(f"  token_id     : {token_id}")
    print(f"  ip_country   : {ip_country}")
    print(f"  hour_of_day  : {hour}")
    print(f"  request_rate : {rate}")
    print(f"  scope_count  : {scopes}")
    print(f"  num_orgs_used: {orgs}")
    print(f"  event_id     : #{event_id}")
    print(f"\n  --> Watch your interceptor window now.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject a fake anomalous OAuth event")
    parser.add_argument("--token", default="tok_sim_001")
    parser.add_argument("--ip", default="RU", help="Suspicious country code")
    parser.add_argument("--hour", type=int, default=3, help="Off-hours (e.g. 3 AM)")
    parser.add_argument("--rate", type=int, default=50, help="Spike in request rate")
    parser.add_argument("--scopes", type=int, default=6, help="Excessive scope count")
    parser.add_argument("--orgs", type=int, default=4, help="Multi-org token reuse")
    args = parser.parse_args()

    inject(args.token, args.ip, args.hour, args.rate, args.scopes, args.orgs)
    