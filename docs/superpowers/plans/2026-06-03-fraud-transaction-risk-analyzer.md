# Fraud Transaction Risk Analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multi-page Streamlit dashboard that lets users upload credit card transactions, score them with a rule engine + Isolation Forest ML model, manage flagged cases in an analyst queue, and export reviewed results to Excel.

**Architecture:** Multi-page Streamlit app with SQLite persistence. Core logic split into focused modules: ingestion → feature engineering → rules → ML → combined scoring → database. Pages are thin wrappers that call src/ modules.

**Tech Stack:** Python 3.10, Streamlit, pandas, scikit-learn (IsolationForest), SQLite (stdlib), openpyxl, plotly

---

## File Map

| File | Responsibility |
|------|---------------|
| `requirements.txt` | Dependencies |
| `data/sample_transactions.csv` | Demo data |
| `src/database.py` | SQLite init, read/write helpers |
| `src/ingestion.py` | CSV validation and loading |
| `src/features.py` | Feature engineering from raw transactions |
| `src/rules.py` | Deterministic rule engine → score 0–100 |
| `src/ml_scorer.py` | Isolation Forest → anomaly score 0–100 |
| `src/scorer.py` | Combines rule + ML → final score + tier |
| `app.py` | Streamlit entry point, page config |
| `pages/1_Upload.py` | Upload & validate CSV |
| `pages/2_Score.py` | Run pipeline, show scored table |
| `pages/3_Review.py` | Analyst case queue |
| `pages/4_Analytics.py` | Charts |
| `pages/5_Export.py` | Excel download |
| `tests/test_ingestion.py` | Ingestion edge cases |
| `tests/test_rules.py` | Rule boundary conditions |
| `tests/test_scorer.py` | Score range, tier assignment, fallback |

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `data/sample_transactions.csv`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create directory structure**

```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\ayond\fraud-transaction-risk-analyzer\src"
New-Item -ItemType Directory -Force -Path "C:\Users\ayond\fraud-transaction-risk-analyzer\pages"
New-Item -ItemType Directory -Force -Path "C:\Users\ayond\fraud-transaction-risk-analyzer\tests"
New-Item -ItemType Directory -Force -Path "C:\Users\ayond\fraud-transaction-risk-analyzer\data"
```

- [ ] **Step 2: Write requirements.txt**

```
streamlit>=1.32.0
pandas>=2.0.0
scikit-learn>=1.4.0
numpy>=1.26.0
openpyxl>=3.1.0
plotly>=5.19.0
```

- [ ] **Step 3: Create sample_transactions.csv**

60 rows: realistic credit card data with ~15 flagged transactions (high amount, late night, casino, duplicate merchant same day, foreign location).

```csv
date,merchant,category,amount,card_last4,location
2024-01-15 09:23:00,Whole Foods,Grocery,45.23,1234,New York NY
2024-01-15 12:45:00,Shell Gas Station,Gas,67.50,1234,New York NY
2024-01-15 19:30:00,Netflix,Entertainment,15.99,1234,New York NY
2024-01-16 08:15:00,Starbucks,Coffee,6.75,1234,New York NY
2024-01-16 11:00:00,CVS Pharmacy,Pharmacy,23.40,1234,New York NY
2024-01-16 14:30:00,Subway,Restaurant,12.50,1234,New York NY
2024-01-17 10:00:00,Amazon,Shopping,89.99,1234,New York NY
2024-01-17 15:45:00,Target,Shopping,134.56,1234,New York NY
2024-01-18 09:00:00,Trader Joes,Grocery,56.78,1234,New York NY
2024-01-18 13:15:00,BP Gas,Gas,45.00,1234,New York NY
2024-01-19 20:00:00,Applebees,Restaurant,38.90,1234,New York NY
2024-01-19 22:30:00,Lyft,Transportation,24.50,1234,New York NY
2024-01-20 07:30:00,Dunkin Donuts,Coffee,5.25,1234,New York NY
2024-01-20 12:00:00,Chipotle,Restaurant,14.75,1234,New York NY
2024-01-20 16:30:00,Home Depot,Hardware,234.56,1234,New York NY
2024-01-21 09:30:00,Whole Foods,Grocery,67.89,1234,New York NY
2024-01-21 14:00:00,Costco,Shopping,256.78,1234,New York NY
2024-01-22 11:00:00,Spotify,Entertainment,9.99,1234,New York NY
2024-01-22 15:30:00,McDonalds,Restaurant,8.45,1234,New York NY
2024-01-22 18:45:00,Uber,Transportation,18.90,1234,New York NY
2024-01-23 10:00:00,Best Buy,Electronics,299.99,1234,New York NY
2024-01-23 14:30:00,Walgreens,Pharmacy,34.56,1234,New York NY
2024-01-24 09:00:00,Panera Bread,Restaurant,13.45,1234,New York NY
2024-01-24 13:00:00,Gap,Shopping,89.99,1234,New York NY
2024-01-24 17:00:00,Whole Foods,Grocery,78.34,1234,New York NY
2024-01-25 08:30:00,Starbucks,Coffee,7.25,1234,New York NY
2024-01-25 12:15:00,Shake Shack,Restaurant,22.50,1234,New York NY
2024-01-25 16:00:00,Apple Store,Electronics,1299.00,1234,New York NY
2024-01-26 09:45:00,Whole Foods,Grocery,45.67,1234,New York NY
2024-01-26 14:30:00,Shell Gas Station,Gas,58.90,1234,New York NY
2024-01-26 23:45:00,MGM Grand Casino,Casino,500.00,1234,Las Vegas NV
2024-01-27 00:30:00,MGM Grand Casino,Casino,1000.00,1234,Las Vegas NV
2024-01-27 02:15:00,MGM Grand Casino,Casino,2500.00,1234,Las Vegas NV
2024-01-27 08:00:00,Starbucks,Coffee,6.50,1234,New York NY
2024-01-27 12:30:00,Subway,Restaurant,11.25,1234,New York NY
2024-01-28 10:00:00,Amazon,Shopping,45.99,1234,New York NY
2024-01-28 14:00:00,Target,Shopping,67.34,1234,New York NY
2024-01-29 09:30:00,Whole Foods,Grocery,89.12,1234,New York NY
2024-01-29 13:00:00,CVS Pharmacy,Pharmacy,18.75,1234,New York NY
2024-01-29 23:00:00,Binance,Cryptocurrency,3000.00,1234,Online
2024-01-30 00:15:00,Coinbase,Cryptocurrency,5000.00,1234,Online
2024-01-30 01:30:00,Kraken Exchange,Cryptocurrency,2000.00,1234,Online
2024-01-30 09:00:00,Starbucks,Coffee,5.75,1234,New York NY
2024-01-30 12:45:00,Chipotle,Restaurant,13.90,1234,New York NY
2024-01-31 10:30:00,Best Buy,Electronics,599.99,1234,New York NY
2024-01-31 14:00:00,Home Depot,Hardware,145.67,1234,New York NY
2024-02-01 09:00:00,Whole Foods,Grocery,56.23,1234,New York NY
2024-02-01 13:30:00,Panera Bread,Restaurant,14.50,1234,New York NY
2024-02-02 10:00:00,Western Union,Wire Transfer,1000.00,1234,New York NY
2024-02-02 11:00:00,Western Union,Wire Transfer,1000.00,1234,New York NY
2024-02-02 12:00:00,Western Union,Wire Transfer,1000.00,1234,Online
2024-02-03 09:30:00,Starbucks,Coffee,6.25,1234,New York NY
2024-02-03 14:00:00,McDonalds,Restaurant,9.50,1234,New York NY
2024-02-04 10:00:00,Amazon,Shopping,234.56,1234,New York NY
2024-02-04 15:00:00,Netflix,Entertainment,15.99,1234,New York NY
2024-02-05 11:00:00,Shell Gas Station,Gas,72.00,1234,New York NY
2024-02-05 23:30:00,Unknown Merchant,Shopping,750.00,1234,Nigeria
2024-02-06 01:00:00,Unknown Merchant,Shopping,850.00,5678,Russia
2024-02-06 02:30:00,Unknown Merchant,Shopping,920.00,5678,China
2024-02-06 09:00:00,Whole Foods,Grocery,43.21,1234,New York NY
2024-02-06 13:30:00,Subway,Restaurant,10.75,1234,New York NY
```

- [ ] **Step 4: Create __init__.py files**

Create empty `src/__init__.py` and `tests/__init__.py`.

- [ ] **Step 5: Install dependencies**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pip install streamlit pandas scikit-learn numpy openpyxl plotly
```

- [ ] **Step 6: Git init and initial commit**

```bash
cd C:/Users/ayond/fraud-transaction-risk-analyzer
git init
git add requirements.txt data/ src/__init__.py tests/__init__.py
git commit -m "chore: project scaffold and sample data"
```

---

### Task 2: Database Module

**Files:**
- Create: `src/database.py`

- [ ] **Step 1: Write src/database.py**

```python
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

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
    rows = df.copy()
    rows["upload_batch"] = batch_id
    ids = []
    with get_connection() as conn:
        for _, row in rows.iterrows():
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
```

- [ ] **Step 2: Commit**

```bash
git add src/database.py
git commit -m "feat: SQLite database module with transactions, scores, review decisions"
```

---

### Task 3: Ingestion Module + Tests

**Files:**
- Create: `src/ingestion.py`
- Create: `tests/test_ingestion.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_ingestion.py
import pytest
import pandas as pd
import io
from src.ingestion import validate_and_load, REQUIRED_COLUMNS

def make_csv(rows: list[dict]) -> bytes:
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")

GOOD_ROW = {
    "date": "2024-01-15 09:23:00",
    "merchant": "Whole Foods",
    "category": "Grocery",
    "amount": "45.23",
    "card_last4": "1234",
    "location": "New York NY"
}

def test_valid_csv_loads():
    data = make_csv([GOOD_ROW])
    df, warnings = validate_and_load(data, "test.csv")
    assert len(df) == 1
    assert len(warnings) == 0
    assert df["amount"].dtype == float

def test_missing_column_raises():
    bad = {k: v for k, v in GOOD_ROW.items() if k != "merchant"}
    data = make_csv([bad])
    with pytest.raises(ValueError, match="missing columns"):
        validate_and_load(data, "test.csv")

def test_empty_file_raises():
    with pytest.raises(ValueError, match="empty"):
        validate_and_load(b"", "test.csv")

def test_bad_amount_rows_warned_and_dropped():
    bad_row = {**GOOD_ROW, "amount": "not_a_number"}
    data = make_csv([GOOD_ROW, bad_row])
    df, warnings = validate_and_load(data, "test.csv")
    assert len(df) == 1
    assert any("amount" in w.lower() for w in warnings)

def test_column_names_stripped_and_lowercased():
    df_raw = pd.DataFrame([GOOD_ROW])
    df_raw.columns = [" Date ", " Merchant ", " Category ", " Amount ", " Card_Last4 ", " Location "]
    data = df_raw.to_csv(index=False).encode("utf-8")
    df, warnings = validate_and_load(data, "test.csv")
    assert list(df.columns[:6]) == REQUIRED_COLUMNS
```

- [ ] **Step 2: Run tests — expect FAIL**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_ingestion.py -v
```
Expected: `ModuleNotFoundError` or `ImportError` — `src.ingestion` not found.

- [ ] **Step 3: Write src/ingestion.py**

```python
import pandas as pd
import io

REQUIRED_COLUMNS = ["date", "merchant", "category", "amount", "card_last4", "location"]


def validate_and_load(file_bytes: bytes, filename: str) -> tuple:
    """Returns (cleaned_df, warnings). Raises ValueError on fatal errors."""
    if not file_bytes or not file_bytes.strip():
        raise ValueError("File is empty.")

    try:
        df = pd.read_csv(io.StringIO(file_bytes.decode("utf-8", errors="replace")))
    except Exception as e:
        raise ValueError(f"Could not parse CSV: {e}")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}. Required: {REQUIRED_COLUMNS}")

    if df.empty:
        raise ValueError("CSV has no data rows.")

    warnings = []

    original_len = len(df)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    bad_amount = df["amount"].isna().sum()
    if bad_amount > 0:
        warnings.append(f"{bad_amount} row(s) dropped: amount could not be converted to number.")
        df = df.dropna(subset=["amount"])

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_date = df["date"].isna().sum()
    if bad_date > 0:
        warnings.append(f"{bad_date} row(s) have unparseable dates and will use NaT.")

    df = df[REQUIRED_COLUMNS].reset_index(drop=True)
    return df, warnings
```

- [ ] **Step 4: Run tests — expect PASS**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_ingestion.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/ingestion.py tests/test_ingestion.py
git commit -m "feat: CSV ingestion with validation and tests"
```

---

### Task 4: Feature Engineering

**Files:**
- Create: `src/features.py`

- [ ] **Step 1: Write src/features.py**

```python
import pandas as pd
import numpy as np

HIGH_RISK_CATEGORIES = {"casino", "wire transfer", "cryptocurrency", "crypto", "gambling"}
US_STATE_ABBREVS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}


def _is_foreign(location: str) -> bool:
    if pd.isna(location):
        return False
    location = str(location).strip()
    if location.lower() in {"online", ""}:
        return False
    parts = location.split()
    return not any(p.upper() in US_STATE_ABBREVS for p in parts)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["hour"] = out["date"].dt.hour.fillna(-1).astype(int)
    out["date_only"] = out["date"].dt.date

    out["is_night"] = out["hour"].apply(lambda h: h >= 23 or h < 5)
    out["is_round_amount"] = out["amount"].apply(lambda a: float(a) == int(float(a)) if pd.notna(a) else False)
    out["is_high_risk_category"] = out["category"].str.lower().isin(HIGH_RISK_CATEGORIES)
    out["is_foreign"] = out["location"].apply(_is_foreign)

    merchant_day_counts = out.groupby(["merchant", "date_only"])["amount"].transform("count")
    out["daily_merchant_count"] = merchant_day_counts.fillna(1).astype(int)

    location_day_counts = out.groupby(["card_last4", "date_only"])["location"].transform("nunique")
    out["daily_location_count"] = location_day_counts.fillna(1).astype(int)

    return out
```

- [ ] **Step 2: Commit**

```bash
git add src/features.py
git commit -m "feat: transaction feature engineering"
```

---

### Task 5: Rule Engine + Tests

**Files:**
- Create: `src/rules.py`
- Create: `tests/test_rules.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_rules.py
import pytest
import pandas as pd
from src.features import engineer_features
from src.rules import apply_rules


def make_txn(**overrides):
    base = {
        "date": "2024-01-15 10:00:00",
        "merchant": "Whole Foods",
        "category": "Grocery",
        "amount": 45.23,
        "card_last4": "1234",
        "location": "New York NY"
    }
    base.update(overrides)
    df = pd.DataFrame([base])
    return engineer_features(df)


def test_normal_transaction_scores_zero():
    df = make_txn()
    scores = apply_rules(df)
    assert scores.iloc[0] == 0


def test_high_amount_over_500():
    df = make_txn(amount=600.00)
    scores = apply_rules(df)
    assert scores.iloc[0] >= 20


def test_high_amount_over_2000():
    df = make_txn(amount=2500.00)
    scores = apply_rules(df)
    assert scores.iloc[0] >= 35


def test_night_transaction():
    df = make_txn(date="2024-01-15 23:30:00")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 15


def test_casino_category():
    df = make_txn(category="Casino")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 30


def test_foreign_location():
    df = make_txn(location="Lagos Nigeria")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 20


def test_round_amount():
    df = make_txn(amount=500.00)
    scores = apply_rules(df)
    assert scores.iloc[0] >= 10


def test_score_capped_at_100():
    df = make_txn(
        amount=3000.00,
        date="2024-01-15 23:30:00",
        category="Casino",
        location="Lagos Nigeria"
    )
    scores = apply_rules(df)
    assert scores.iloc[0] <= 100


def test_score_never_negative():
    df = make_txn()
    scores = apply_rules(df)
    assert scores.iloc[0] >= 0
```

- [ ] **Step 2: Run tests — expect FAIL**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_rules.py -v
```
Expected: ImportError on `src.rules`.

- [ ] **Step 3: Write src/rules.py**

```python
import pandas as pd
import numpy as np


def apply_rules(df: pd.DataFrame) -> pd.Series:
    """Apply rule engine to feature-engineered DataFrame. Returns Series of scores 0–100."""
    scores = pd.Series(0.0, index=df.index)

    # Amount rules (mutually exclusive tiers)
    scores += df["amount"].apply(lambda a: 35 if a > 2000 else (20 if a > 500 else 0))

    # Time-based
    scores += df["is_night"].apply(lambda x: 15 if x else 0)

    # Category risk
    scores += df["is_high_risk_category"].apply(lambda x: 30 if x else 0)

    # Foreign location
    scores += df["is_foreign"].apply(lambda x: 20 if x else 0)

    # Round dollar amount
    scores += df["is_round_amount"].apply(lambda x: 10 if x else 0)

    # Same merchant multiple times same day
    scores += df["daily_merchant_count"].apply(lambda c: 25 if c >= 3 else 0)

    # Card used in multiple locations same day
    scores += df["daily_location_count"].apply(lambda c: 20 if c >= 3 else 0)

    return scores.clip(0, 100)
```

- [ ] **Step 4: Run tests — expect PASS**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_rules.py -v
```
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add src/rules.py tests/test_rules.py
git commit -m "feat: rule engine with boundary tests"
```

---

### Task 6: ML Scorer

**Files:**
- Create: `src/ml_scorer.py`

- [ ] **Step 1: Write src/ml_scorer.py**

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ML_FEATURES = ["amount", "hour", "is_night", "is_round_amount",
               "is_high_risk_category", "is_foreign",
               "daily_merchant_count", "daily_location_count"]


def train_and_score(df: pd.DataFrame) -> pd.Series:
    """Train Isolation Forest on df, return anomaly scores 0–100.
    Higher = more anomalous. Falls back to zeros if training fails."""
    try:
        feature_df = df[ML_FEATURES].copy()

        for col in ["is_night", "is_round_amount", "is_high_risk_category", "is_foreign"]:
            feature_df[col] = feature_df[col].astype(int)

        feature_df = feature_df.fillna(0)

        if len(feature_df) < 5:
            return pd.Series(0.0, index=df.index)

        scaler = StandardScaler()
        X = scaler.fit_transform(feature_df)

        model = IsolationForest(
            n_estimators=100,
            contamination=0.15,
            random_state=42
        )
        model.fit(X)

        raw_scores = model.decision_function(X)
        # decision_function: higher = more normal, lower = more anomalous
        # Invert and scale to 0–100
        inverted = -raw_scores
        min_s, max_s = inverted.min(), inverted.max()
        if max_s == min_s:
            return pd.Series(0.0, index=df.index)

        normalized = (inverted - min_s) / (max_s - min_s) * 100
        return pd.Series(normalized, index=df.index).clip(0, 100)

    except Exception:
        return pd.Series(0.0, index=df.index)
```

- [ ] **Step 2: Commit**

```bash
git add src/ml_scorer.py
git commit -m "feat: Isolation Forest ML scorer"
```

---

### Task 7: Combined Scorer + Tests

**Files:**
- Create: `src/scorer.py`
- Create: `tests/test_scorer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scorer.py
import pytest
import pandas as pd
from src.scorer import score_transactions, assign_tier

SAMPLE_ROWS = [
    {"date": "2024-01-15 10:00:00", "merchant": "Whole Foods", "category": "Grocery",
     "amount": 45.23, "card_last4": "1234", "location": "New York NY"},
    {"date": "2024-01-15 23:30:00", "merchant": "MGM Casino", "category": "Casino",
     "amount": 2500.00, "card_last4": "1234", "location": "Lagos Nigeria"},
]


def test_score_returns_expected_columns():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    assert "rule_score" in result.columns
    assert "ml_score" in result.columns
    assert "final_score" in result.columns
    assert "risk_tier" in result.columns


def test_scores_in_valid_range():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    assert result["final_score"].between(0, 100).all()
    assert result["rule_score"].between(0, 100).all()
    assert result["ml_score"].between(0, 100).all()


def test_high_risk_transaction_scores_higher():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    normal_score = result.iloc[0]["final_score"]
    risky_score = result.iloc[1]["final_score"]
    assert risky_score > normal_score


def test_tier_assignment():
    assert assign_tier(85) == "Critical"
    assert assign_tier(65) == "High"
    assert assign_tier(45) == "Medium"
    assert assign_tier(15) == "Low"
    assert assign_tier(0) == "Low"
    assert assign_tier(100) == "Critical"


def test_ml_fallback_still_returns_scores():
    # Only 3 rows — ml_scorer falls back to zeros, rules still apply
    df = pd.DataFrame(SAMPLE_ROWS[:1] * 3)
    result = score_transactions(df)
    assert len(result) == 3
    assert result["final_score"].between(0, 100).all()
```

- [ ] **Step 2: Run tests — expect FAIL**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_scorer.py -v
```
Expected: ImportError on `src.scorer`.

- [ ] **Step 3: Write src/scorer.py**

```python
import pandas as pd
from src.features import engineer_features
from src.rules import apply_rules
from src.ml_scorer import train_and_score

RULE_WEIGHT = 0.6
ML_WEIGHT = 0.4

TIER_THRESHOLDS = [
    (80, "Critical"),
    (60, "High"),
    (30, "Medium"),
    (0, "Low"),
]


def assign_tier(score: float) -> str:
    for threshold, tier in TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return "Low"


def score_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Full pipeline: raw df → feature engineering → rule score → ML score → combined."""
    featured = engineer_features(df)

    rule_scores = apply_rules(featured)
    ml_scores = train_and_score(featured)

    final_scores = (RULE_WEIGHT * rule_scores + ML_WEIGHT * ml_scores).clip(0, 100)
    tiers = final_scores.apply(assign_tier)

    result = df.copy()
    result["rule_score"] = rule_scores.round(2)
    result["ml_score"] = ml_scores.round(2)
    result["final_score"] = final_scores.round(2)
    result["risk_tier"] = tiers
    return result
```

- [ ] **Step 4: Run tests — expect PASS**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/test_scorer.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Run all tests**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/ -v
```
Expected: All pass.

- [ ] **Step 6: Commit**

```bash
git add src/scorer.py tests/test_scorer.py
git commit -m "feat: combined scorer with tier assignment and tests"
```

---

### Task 8: Main App Entry Point

**Files:**
- Create: `app.py`

- [ ] **Step 1: Write app.py**

```python
import streamlit as st
from src.database import init_db

st.set_page_config(
    page_title="Fraud Transaction Risk Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

st.title("🔍 Fraud Transaction Risk Analyzer")
st.markdown("""
Welcome to the Fraud Transaction Risk Analyzer — a compliance-grade tool for detecting
suspicious credit card transactions using rule-based scoring and machine learning.

**Workflow:**
1. **Upload** — Import your credit card transaction CSV
2. **Score** — Run the fraud detection pipeline
3. **Review** — Investigate and action flagged cases
4. **Analytics** — Explore patterns and risk distribution
5. **Export** — Download reviewed cases as Excel

Navigate using the sidebar →
""")

st.info("📁 Expected CSV format: `date, merchant, category, amount, card_last4, location`")

with st.expander("📋 See sample data format"):
    import pandas as pd
    sample = pd.DataFrame([
        {"date": "2024-01-15 09:23:00", "merchant": "Whole Foods", "category": "Grocery",
         "amount": 45.23, "card_last4": "1234", "location": "New York NY"},
        {"date": "2024-01-15 23:45:00", "merchant": "MGM Casino", "category": "Casino",
         "amount": 2500.00, "card_last4": "1234", "location": "Las Vegas NV"},
    ])
    st.dataframe(sample)
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "feat: Streamlit app entry point"
```

---

### Task 9: Page 1 — Upload & Validate

**Files:**
- Create: `pages/1_Upload.py`

- [ ] **Step 1: Write pages/1_Upload.py**

```python
import streamlit as st
import pandas as pd
from datetime import datetime
from src.ingestion import validate_and_load
from src.database import init_db, save_transactions, clear_all

init_db()

st.title("📤 Upload Transactions")
st.markdown("Upload a credit card transaction CSV to begin analysis.")

uploaded_file = st.file_uploader(
    "Choose CSV file",
    type=["csv"],
    help="Required columns: date, merchant, category, amount, card_last4, location"
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    try:
        df, warnings = validate_and_load(file_bytes, uploaded_file.name)

        if warnings:
            for w in warnings:
                st.warning(f"⚠️ {w}")

        st.success(f"✅ Loaded {len(df)} valid transactions from **{uploaded_file.name}**")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Transactions", len(df))
        col2.metric("Date Range", f"{df['date'].min().date()} → {df['date'].max().date()}")
        col3.metric("Total Amount", f"${df['amount'].sum():,.2f}")

        st.subheader("Preview (first 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        if st.button("💾 Save & Proceed to Scoring", type="primary"):
            clear_all()
            batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_transactions(df, batch_id)
            st.session_state["uploaded"] = True
            st.session_state["batch_id"] = batch_id
            st.success("✅ Transactions saved. Navigate to **Score** in the sidebar.")

    except ValueError as e:
        st.error(f"❌ {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
```

- [ ] **Step 2: Commit**

```bash
git add pages/1_Upload.py
git commit -m "feat: upload and validate page"
```

---

### Task 10: Page 2 — Score Transactions

**Files:**
- Create: `pages/2_Score.py`

- [ ] **Step 1: Write pages/2_Score.py**

```python
import streamlit as st
import pandas as pd
from src.database import init_db, get_transactions, save_scores, get_scored_cases
from src.scorer import score_transactions

init_db()

TIER_COLORS = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢"
}

st.title("⚡ Score Transactions")

transactions = get_transactions()

if transactions.empty:
    st.warning("No transactions loaded. Go to **Upload** first.")
    st.stop()

st.metric("Transactions Ready to Score", len(transactions))

if st.button("🚀 Run Fraud Detection Pipeline", type="primary"):
    with st.spinner("Running rule engine + ML scoring..."):
        try:
            scored = score_transactions(transactions.drop(columns=["id", "upload_batch", "created_at"], errors="ignore"))
            scored["transaction_id"] = transactions["id"].values

            save_scores(scored[["transaction_id", "rule_score", "ml_score", "final_score", "risk_tier"]])
            st.success("✅ Scoring complete.")
        except Exception as e:
            st.error(f"❌ Scoring failed: {e}")
            st.stop()

scored_cases = get_scored_cases()

if not scored_cases.empty:
    st.subheader("Risk Summary")
    col1, col2, col3, col4 = st.columns(4)
    tier_counts = scored_cases["risk_tier"].value_counts()
    col1.metric("🔴 Critical", tier_counts.get("Critical", 0))
    col2.metric("🟠 High", tier_counts.get("High", 0))
    col3.metric("🟡 Medium", tier_counts.get("Medium", 0))
    col4.metric("🟢 Low", tier_counts.get("Low", 0))

    st.subheader("All Scored Transactions")

    tier_filter = st.multiselect(
        "Filter by Risk Tier",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"]
    )

    display = scored_cases[scored_cases["risk_tier"].isin(tier_filter)].copy()
    display["tier"] = display["risk_tier"].map(TIER_COLORS) + " " + display["risk_tier"]
    display = display.sort_values("final_score", ascending=False)

    st.dataframe(
        display[["date", "merchant", "category", "amount", "location", "rule_score", "ml_score", "final_score", "tier"]],
        use_container_width=True
    )
```

- [ ] **Step 2: Commit**

```bash
git add pages/2_Score.py
git commit -m "feat: scoring page with pipeline execution and results display"
```

---

### Task 11: Page 3 — Review Cases

**Files:**
- Create: `pages/3_Review.py`

- [ ] **Step 1: Write pages/3_Review.py**

```python
import streamlit as st
import pandas as pd
from src.database import init_db, get_scored_cases, save_review_decision, get_latest_decision_per_transaction

init_db()

TIER_COLORS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
DECISION_COLORS = {"escalated": "🚨", "reviewed": "✅", "cleared": "⬜"}

st.title("🔎 Review Flagged Cases")

scored = get_scored_cases()

if scored.empty:
    st.warning("No scored transactions. Go to **Score** first.")
    st.stop()

flagged = scored[scored["risk_tier"].isin(["Critical", "High", "Medium"])].copy()

if flagged.empty:
    st.success("No flagged transactions found.")
    st.stop()

decisions = get_latest_decision_per_transaction()
decision_map = dict(zip(decisions["transaction_id"], decisions["decision"])) if not decisions.empty else {}

flagged["current_decision"] = flagged["transaction_id"].map(decision_map).fillna("pending")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔴 Critical", len(flagged[flagged["risk_tier"] == "Critical"]))
col2.metric("🟠 High", len(flagged[flagged["risk_tier"] == "High"]))
col3.metric("🟡 Medium", len(flagged[flagged["risk_tier"] == "Medium"]))
col4.metric("Reviewed", len([v for v in decision_map.values() if v != "pending"]))

st.subheader("Case Queue")

tier_filter = st.multiselect("Filter by Tier", ["Critical", "High", "Medium"], default=["Critical", "High", "Medium"])
status_filter = st.multiselect("Filter by Status", ["pending", "escalated", "reviewed", "cleared"], default=["pending", "escalated"])

view = flagged[
    flagged["risk_tier"].isin(tier_filter) &
    flagged["current_decision"].isin(status_filter)
].sort_values("final_score", ascending=False)

st.markdown(f"Showing **{len(view)}** cases")

for _, row in view.iterrows():
    tier_icon = TIER_COLORS.get(row["risk_tier"], "")
    status_icon = DECISION_COLORS.get(row["current_decision"], "⏳")

    with st.expander(
        f"{tier_icon} {row['merchant']} — ${row['amount']:.2f} — Score: {row['final_score']:.0f} — {status_icon} {row['current_decision'].upper()}"
    ):
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**Date:** {row['date']}")
            st.write(f"**Merchant:** {row['merchant']}")
            st.write(f"**Category:** {row['category']}")
            st.write(f"**Location:** {row['location']}")
        with col_b:
            st.write(f"**Amount:** ${row['amount']:.2f}")
            st.write(f"**Card:** ...{row['card_last4']}")
            st.write(f"**Rule Score:** {row['rule_score']:.1f}")
            st.write(f"**ML Score:** {row['ml_score']:.1f}")
            st.write(f"**Final Score:** {row['final_score']:.1f}")

        notes = st.text_input("Analyst notes", key=f"notes_{row['transaction_id']}", placeholder="Optional notes...")

        c1, c2, c3 = st.columns(3)
        txn_id = int(row["transaction_id"])

        if c1.button("🚨 Escalate", key=f"esc_{txn_id}"):
            save_review_decision(txn_id, "escalated", notes)
            st.rerun()
        if c2.button("✅ Mark Reviewed", key=f"rev_{txn_id}"):
            save_review_decision(txn_id, "reviewed", notes)
            st.rerun()
        if c3.button("⬜ Clear as Legitimate", key=f"clr_{txn_id}"):
            save_review_decision(txn_id, "cleared", notes)
            st.rerun()
```

- [ ] **Step 2: Commit**

```bash
git add pages/3_Review.py
git commit -m "feat: analyst review queue with persist decisions"
```

---

### Task 12: Page 4 — Analytics

**Files:**
- Create: `pages/4_Analytics.py`

- [ ] **Step 1: Write pages/4_Analytics.py**

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database import init_db, get_scored_cases

init_db()

st.title("📊 Analytics")

scored = get_scored_cases()

if scored.empty:
    st.warning("No scored transactions. Go to **Score** first.")
    st.stop()

scored["date"] = pd.to_datetime(scored["date"], errors="coerce")
scored["hour"] = scored["date"].dt.hour

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Risk Distribution", "By Category", "Amount vs Risk",
    "Hourly Heatmap", "Top Merchants"
])

with tab1:
    tier_order = ["Critical", "High", "Medium", "Low"]
    tier_counts = scored["risk_tier"].value_counts().reindex(tier_order).fillna(0).reset_index()
    tier_counts.columns = ["Risk Tier", "Count"]
    colors = {"Critical": "#dc2626", "High": "#f97316", "Medium": "#eab308", "Low": "#22c55e"}
    fig = px.bar(tier_counts, x="Risk Tier", y="Count",
                 color="Risk Tier", color_discrete_map=colors,
                 title="Transactions by Risk Tier")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(scored, x="final_score", nbins=20,
                        title="Risk Score Distribution",
                        labels={"final_score": "Final Score"})
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    cat_scores = scored.groupby("category")["final_score"].mean().sort_values(ascending=False).reset_index()
    cat_scores.columns = ["Category", "Avg Risk Score"]
    fig = px.bar(cat_scores, x="Category", y="Avg Risk Score",
                 title="Average Risk Score by Category",
                 color="Avg Risk Score", color_continuous_scale="RdYlGn_r")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.scatter(scored, x="amount", y="final_score",
                     color="risk_tier",
                     color_discrete_map={"Critical": "#dc2626", "High": "#f97316",
                                         "Medium": "#eab308", "Low": "#22c55e"},
                     hover_data=["merchant", "category", "date"],
                     title="Transaction Amount vs Risk Score",
                     labels={"amount": "Amount ($)", "final_score": "Risk Score"})
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    if scored["hour"].notna().any():
        hour_counts = scored.groupby("hour").size().reset_index(name="count")
        fig = px.bar(hour_counts, x="hour", y="count",
                     title="Transactions by Hour of Day",
                     labels={"hour": "Hour (24h)", "count": "# Transactions"})
        fig.add_vrect(x0=22.5, x1=24, fillcolor="red", opacity=0.1, annotation_text="Night zone")
        fig.add_vrect(x0=0, x1=5, fillcolor="red", opacity=0.1)
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    merchant_risk = (
        scored[scored["risk_tier"].isin(["Critical", "High"])]
        .groupby("merchant")
        .agg(count=("final_score", "count"), avg_score=("final_score", "mean"))
        .sort_values("avg_score", ascending=False)
        .head(15)
        .reset_index()
    )
    if not merchant_risk.empty:
        fig = px.bar(merchant_risk, x="avg_score", y="merchant",
                     orientation="h",
                     title="Top 15 Risky Merchants (Critical + High only)",
                     labels={"avg_score": "Avg Risk Score", "merchant": "Merchant"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No high-risk merchants found.")
```

- [ ] **Step 2: Commit**

```bash
git add pages/4_Analytics.py
git commit -m "feat: analytics page with 5 chart tabs"
```

---

### Task 13: Page 5 — Export

**Files:**
- Create: `pages/5_Export.py`

- [ ] **Step 1: Write pages/5_Export.py**

```python
import streamlit as st
import pandas as pd
import io
from openpyxl.styles import PatternFill, Font
from src.database import init_db, get_scored_cases, get_latest_decision_per_transaction

init_db()

TIER_FILL_COLORS = {
    "Critical": "FFDC2626",
    "High": "FFF97316",
    "Medium": "FFEAB308",
    "Low": "FF22C55E"
}

st.title("📥 Export Results")

scored = get_scored_cases()

if scored.empty:
    st.warning("No scored transactions. Go to **Score** first.")
    st.stop()

decisions = get_latest_decision_per_transaction()
if not decisions.empty:
    scored = scored.merge(
        decisions[["transaction_id", "decision", "notes"]],
        on="transaction_id",
        how="left"
    )
    scored["decision"] = scored["decision"].fillna("pending")
    scored["notes"] = scored["notes"].fillna("")
else:
    scored["decision"] = "pending"
    scored["notes"] = ""

st.subheader("Export Preview")

col1, col2 = st.columns(2)
include_tiers = col1.multiselect(
    "Include Risk Tiers",
    ["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium"]
)
include_statuses = col2.multiselect(
    "Include Decision Status",
    ["pending", "escalated", "reviewed", "cleared"],
    default=["pending", "escalated", "reviewed", "cleared"]
)

export_df = scored[
    scored["risk_tier"].isin(include_tiers) &
    scored["decision"].isin(include_statuses)
].copy()

st.metric("Rows to Export", len(export_df))
st.dataframe(export_df[["date", "merchant", "category", "amount", "location",
                          "final_score", "risk_tier", "decision", "notes"]].head(20),
             use_container_width=True)


def build_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Fraud Cases")
        ws = writer.sheets["Fraud Cases"]

        header_fill = PatternFill(start_color="FF1E3A5F", end_color="FF1E3A5F", fill_type="solid")
        header_font = Font(color="FFFFFFFF", bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font

        tier_col = None
        for idx, cell in enumerate(ws[1], 1):
            if cell.value == "risk_tier":
                tier_col = idx

        if tier_col:
            for row in ws.iter_rows(min_row=2):
                tier_val = row[tier_col - 1].value
                fill_color = TIER_FILL_COLORS.get(tier_val, "FFFFFFFF")
                fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                for cell in row:
                    cell.fill = fill

        for col in ws.columns:
            max_len = max((len(str(cell.value)) for cell in col if cell.value), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)

    return output.getvalue()


if st.button("📥 Generate Excel Report", type="primary") and not export_df.empty:
    excel_bytes = build_excel(export_df)
    st.download_button(
        label="⬇️ Download Excel",
        data=excel_bytes,
        file_name="fraud_analysis_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

- [ ] **Step 2: Commit**

```bash
git add pages/5_Export.py
git commit -m "feat: Excel export with color-coded risk tiers"
```

---

### Task 14: Final Test Run + GitHub Push

- [ ] **Step 1: Run all tests**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m pytest tests/ -v
```
Expected: All pass.

- [ ] **Step 2: Smoke test — launch app**

```powershell
C:/Users/ayond/AppData/Local/Programs/Python/Python310/python.exe -m streamlit run app.py
```
Navigate to Upload → upload `data/sample_transactions.csv` → Score → Review → Analytics → Export. Confirm no errors.

- [ ] **Step 3: Create GitHub repo and push**

```powershell
gh repo create fraud-transaction-risk-analyzer --public --description "Credit card fraud analysis dashboard with rule engine + ML scoring" --source . --remote origin --push
```

- [ ] **Step 4: Final commit with README**

Write README.md with usage instructions, then commit and push.
