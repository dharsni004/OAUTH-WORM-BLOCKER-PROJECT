import sqlite3

DB_PATH = "events.db"

def setup():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS token_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            source TEXT NOT NULL,
            hour_of_day INTEGER NOT NULL,
            ip_country TEXT NOT NULL,
            request_rate INTEGER NOT NULL,
            scope_count INTEGER NOT NULL,
            num_orgs_used INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            risk_score REAL,
            decision TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS revoked_tokens (
            token_id TEXT PRIMARY KEY,
            revoked_at TEXT NOT NULL,
            reason TEXT NOT NULL,
            triggering_event_id INTEGER,
            FOREIGN KEY (triggering_event_id) REFERENCES token_events(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] Database ready at events.db")
    print("     Tables created: token_events, revoked_tokens")

if __name__ == "__main__":
    setup()
    