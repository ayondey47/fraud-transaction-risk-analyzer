import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/fraud_cases.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                merchant TEXT,
                category TEXT,
                amount REAL,
                card_last4 TEXT,
                location TEXT,
                upload_batch TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scored_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER UNIQUE,
                rule_score REAL,
                ml_score REAL,
                final_score REAL,
                risk_tier TEXT,
                scored_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS review_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                decision TEXT,
                notes TEXT,
                decided_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            )
        """)
        conn.commit()


def clear_all():
    with get_connection() as conn:
        conn.execute("DELETE FROM review_decisions")
        conn.execute("DELETE FROM scored_cases")
        conn.execute("DELETE FROM transactions")
        conn.commit()


def save_transactions(df: pd.DataFrame, batch_id: str) -> list:
    ids = []
    with get_connection() as conn:
        for _, row in df.iterrows():
            cur = conn.execute(
                """INSERT INTO transactions (date, merchant, category, amount, card_last4, location, upload_batch)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (str(row["date"]), row["merchant"], row["category"],
                 float(row["amount"]), str(row["card_last4"]),
                 row["location"], batch_id)
            )
            ids.append(cur.lastrowid)
        conn.commit()
    return ids


def get_transactions() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM transactions ORDER BY id", conn)


def save_scores(scores: pd.DataFrame):
    with get_connection() as conn:
        for _, row in scores.iterrows():
            conn.execute(
                """INSERT INTO scored_cases (transaction_id, rule_score, ml_score, final_score, risk_tier)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(transaction_id) DO UPDATE SET
                   rule_score=excluded.rule_score, ml_score=excluded.ml_score,
                   final_score=excluded.final_score, risk_tier=excluded.risk_tier,
                   scored_at=datetime('now')""",
                (int(row["transaction_id"]), float(row["rule_score"]),
                 float(row["ml_score"]), float(row["final_score"]), row["risk_tier"])
            )
        conn.commit()


def get_scored_cases() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
            SELECT t.id as transaction_id, t.date, t.merchant, t.category,
                   t.amount, t.card_last4, t.location,
                   s.rule_score, s.ml_score, s.final_score, s.risk_tier
            FROM transactions t
            JOIN scored_cases s ON t.id = s.transaction_id
            ORDER BY s.final_score DESC
        """, conn)


def save_review_decision(transaction_id: int, decision: str, notes: str = ""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO review_decisions (transaction_id, decision, notes)
               VALUES (?, ?, ?)""",
            (transaction_id, decision, notes)
        )
        conn.commit()


def get_review_decisions() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
            SELECT transaction_id, decision, notes, decided_at
            FROM review_decisions
            ORDER BY decided_at DESC
        """, conn)


def get_latest_decision_per_transaction() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql("""
            SELECT transaction_id, decision, notes, decided_at
            FROM review_decisions
            WHERE id IN (
                SELECT MAX(id) FROM review_decisions GROUP BY transaction_id
            )
        """, conn)
