import asyncio
import os
import random
import uuid
from datetime import datetime

import joblib
import pandas as pd
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "fraud_db"),
    "user": os.environ.get("DB_USER", "fraud_user"),
    "password": os.environ.get("DB_PASSWORD", "fraud_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5433"),
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


async def simulate_live_transactions():
    """Background task to insert realistic live transactions."""
    print("Starting live transaction simulator...")
    while True:
        await asyncio.sleep(random.randint(2, 6))  # New transaction every 2-6 seconds
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Fetch a random active card and its customer country
            cur.execute("""
                SELECT c.card_id, c.account_id, cust.country 
                FROM cards c
                JOIN accounts a ON c.account_id = a.account_id
                JOIN customers cust ON a.customer_id = cust.customer_id
                ORDER BY RANDOM() LIMIT 1
            """)
            card = cur.fetchone()

            # Fetch a merchant in the same country 90% of the time
            if card and random.random() < 0.90:
                cur.execute(
                    "SELECT merchant_id, latitude, longitude, country, category FROM merchants WHERE country = %s ORDER BY RANDOM() LIMIT 1",
                    (card[2],),
                )
            else:
                cur.execute(
                    "SELECT merchant_id, latitude, longitude, country, category FROM merchants ORDER BY RANDOM() LIMIT 1"
                )
            merchant = cur.fetchone()

            cur.execute("SELECT device_id FROM devices ORDER BY RANDOM() LIMIT 1")
            device = cur.fetchone()

            if card and merchant and device:
                # 5% chance of injecting a huge value anomaly
                is_anomaly = random.random() < 0.05

                category = merchant[4]
                import numpy as np

                # Categories mapping roughly from generate_data.py
                cat_mu = 4.0
                cat_sigma = 0.6
                if category == "Coffee Shop":
                    cat_mu, cat_sigma = 1.5, 0.5
                elif category == "Fast Food":
                    cat_mu, cat_sigma = 2.5, 0.5
                elif category == "Electronics":
                    cat_mu, cat_sigma = 5.8, 0.8
                elif category == "Travel":
                    cat_mu, cat_sigma = 6.2, 0.7

                amount = (
                    round(random.uniform(90000.0, 95000.0), 2)
                    if is_anomaly
                    else round(max(1.0, np.random.lognormal(cat_mu, cat_sigma)), 2)
                )

                cur.execute(
                    """
                    INSERT INTO transactions 
                    (transaction_id, account_id, card_id, merchant_id, device_id, timestamp, amount, currency, latitude, longitude, country, ip_address, payment_method, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        str(uuid.uuid4()),
                        card[1],
                        card[0],
                        merchant[0],
                        device[0],
                        datetime.now(),
                        amount,
                        "USD",
                        merchant[1],
                        merchant[2],
                        merchant[3],
                        "192.168.1.1",
                        "Card",
                        "SUCCESS",
                    ),
                )
                conn.commit()
                print(f"Live Simulation: Inserted transaction for {amount} USD")

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Simulation error: {e}")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_live_transactions())


# Load the ML model
model_path = os.path.join(
    os.path.dirname(__file__), "../ml/models/isolation_forest.joblib"
)
try:
    ml_model = joblib.load(model_path)
except Exception as e:
    print(f"Warning: Could not load ML model: {e}")
    ml_model = None


@app.get("/transactions")
def get_transactions(limit: int = 100, offset: int = 0, sort_by_risk: bool = True):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    order_clause = (
        "ORDER BY sql_risk_score DESC, timestamp DESC"
        if sort_by_risk
        else "ORDER BY timestamp DESC"
    )

    query = f"""
        SELECT 
            transaction_id, account_id, merchant_id, timestamp, amount, 
            sql_risk_score, rule_high_velocity, rule_amount_anomaly, 
            rule_impossible_travel, rule_new_device,
            rule_foreign_transaction, rule_late_night,
            rule_micro_testing, rule_rapid_category_hopping
        FROM transaction_features
        {order_clause}
        LIMIT %s OFFSET %s
    """

    cur.execute(query, (limit, offset))
    transactions = cur.fetchall()

    # Calculate ML score on the fly for these transactions to keep it simple
    if ml_model and transactions:
        # We need to fetch the full features for these transactions to run ML
        tx_ids = [t["transaction_id"] for t in transactions]
        format_strings = ",".join(["%s"] * len(tx_ids))
        feature_query = f"""
            SELECT transaction_id, amount, velocity_count, z_score, travel_speed_kmh, new_device_flag,
                   micro_charge_count, category_change_flag, 
                   CAST(rule_foreign_transaction AS INT) as rule_foreign_transaction, 
                   CAST(rule_late_night AS INT) as rule_late_night
            FROM transaction_features
            WHERE transaction_id IN ({format_strings})
        """
        cur.execute(feature_query, tuple(tx_ids))
        features_list = cur.fetchall()

        if features_list:
            feat_df = pd.DataFrame(features_list).fillna(0)
            X = feat_df[
                [
                    "amount",
                    "velocity_count",
                    "z_score",
                    "travel_speed_kmh",
                    "new_device_flag",
                    "micro_charge_count",
                    "category_change_flag",
                    "rule_foreign_transaction",
                    "rule_late_night",
                ]
            ]

            # Normal ML score is negative for anomalies. We map it to 0-100 risk score
            # A very negative score means high risk.
            scores = ml_model.decision_function(X)

            feat_df["ml_score_raw"] = scores
            # Map logic: Score < 0 is anomaly. Let's say -0.15 is 100 risk, 0 is 0 risk.
            # Normalizing: ml_risk = max(0, min(100, score * -1 * 1000))
            feat_df["ml_risk_score"] = feat_df["ml_score_raw"].apply(
                lambda x: max(0, min(100, int(x * -1000)))
            )

            # Join back to transactions
            ml_risk_dict = dict(
                zip(feat_df["transaction_id"], feat_df["ml_risk_score"])
            )
            for t in transactions:
                t["ml_risk_score"] = ml_risk_dict.get(t["transaction_id"], 0)
                # Hybrid score
                t["hybrid_risk_score"] = int(
                    (t["sql_risk_score"] * 0.6) + (t["ml_risk_score"] * 0.4)
                )

    cur.close()
    conn.close()
    return transactions


@app.get("/analytics/summary")
def get_analytics_summary():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN sql_risk_score >= 60 THEN 1 ELSE 0 END) as high_risk_transactions,
            SUM(CASE WHEN rule_high_velocity THEN 1 ELSE 0 END) as velocity_flags,
            SUM(CASE WHEN rule_amount_anomaly THEN 1 ELSE 0 END) as amount_flags,
            SUM(CASE WHEN rule_impossible_travel THEN 1 ELSE 0 END) as travel_flags,
            SUM(CASE WHEN rule_new_device THEN 1 ELSE 0 END) as device_flags,
            SUM(CASE WHEN rule_foreign_transaction THEN 1 ELSE 0 END) as foreign_flags,
            SUM(CASE WHEN rule_late_night THEN 1 ELSE 0 END) as late_night_flags,
            SUM(CASE WHEN rule_micro_testing THEN 1 ELSE 0 END) as micro_flags,
            SUM(CASE WHEN rule_rapid_category_hopping THEN 1 ELSE 0 END) as hopping_flags
        FROM transaction_features
    """)
    summary = cur.fetchone()

    cur.close()
    conn.close()
    return summary


@app.get("/transactions/{transaction_id}/investigate")
def investigate_transaction(transaction_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # 1. Fetch Transaction Details
    cur.execute(
        """
        SELECT *, 
               CAST(rule_foreign_transaction AS INT) as rule_foreign_transaction_int,
               CAST(rule_late_night AS INT) as rule_late_night_int
        FROM transaction_features WHERE transaction_id = %s
    """,
        (transaction_id,),
    )
    tx = cur.fetchone()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # 2. Add ML Score
    if ml_model:
        # Map back to original feature names expected by the model
        tx_for_ml = dict(tx)
        tx_for_ml["rule_foreign_transaction"] = tx_for_ml[
            "rule_foreign_transaction_int"
        ]
        tx_for_ml["rule_late_night"] = tx_for_ml["rule_late_night_int"]

        feat_df = pd.DataFrame([tx_for_ml]).fillna(0)
        X = feat_df[
            [
                "amount",
                "velocity_count",
                "z_score",
                "travel_speed_kmh",
                "new_device_flag",
                "micro_charge_count",
                "category_change_flag",
                "rule_foreign_transaction",
                "rule_late_night",
            ]
        ]
        raw_score = ml_model.decision_function(X)[0]
        tx["ml_risk_score"] = max(0, min(100, int(raw_score * -1000)))
        tx["hybrid_risk_score"] = int(
            (tx["sql_risk_score"] * 0.6) + (tx["ml_risk_score"] * 0.4)
        )
    else:
        tx["ml_risk_score"] = 0
        tx["hybrid_risk_score"] = tx["sql_risk_score"]

    # 3. Fetch past 10 transactions for this account
    cur.execute(
        """
        SELECT transaction_id, timestamp, amount, merchant_id, status 
        FROM transactions 
        WHERE account_id = %s 
        ORDER BY timestamp DESC LIMIT 10
    """,
        (tx["account_id"],),
    )
    history = cur.fetchall()

    tx["account_history"] = history

    cur.close()
    conn.close()

    return tx
