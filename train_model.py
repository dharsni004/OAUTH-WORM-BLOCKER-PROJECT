import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib

DB_PATH = "events.db"
MODEL_PATH = "oauth_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

def train():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT * FROM token_events
        WHERE source IN ('simulated','github','google','salesforce','microsoft')
    """, conn)
    conn.close()

    print(f"[TRAIN] Loaded {len(df)} events from events.db")
    print(f"\n[TRAIN] Events per provider:")
    print(df['source'].value_counts().to_string())

    print(f"\n[TRAIN] Sample of NEW provider tokens:")
    new = df[df['source'].isin(['github','google','salesforce','microsoft'])]
    print(new[['token_id','source','hour_of_day','ip_country','request_rate']].head(10).to_string())
    print("...")

    le = LabelEncoder()
    df['ip_encoded'] = le.fit_transform(df['ip_country'])
    print(f"\n[TRAIN] Countries seen: {list(le.classes_)}")

    features = df[['hour_of_day', 'ip_encoded', 'request_rate', 'scope_count', 'num_orgs_used']]

    print("\n[TRAIN] Training Isolation Forest model ...")
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)
    print("[TRAIN] Training complete.")

    joblib.dump(model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    print(f"[SAVED] Model saved to {MODEL_PATH}")
    print(f"[SAVED] Label encoder saved to {ENCODER_PATH}")
    print("\n[DONE] Ready to run interceptor.")

if __name__ == "__main__":
    train()