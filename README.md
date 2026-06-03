# Fraud Transaction Risk Analyzer

A compliance-grade interactive dashboard for detecting suspicious credit card transactions using a rule-based scoring engine combined with Isolation Forest machine learning.

## Features

- **Upload** CSV transactions and validate column structure
- **Score** each transaction with a hybrid rule engine + ML anomaly detector
- **Review** flagged cases in an analyst-style queue with Escalate / Mark Reviewed / Clear actions
- **Analytics** — risk distribution, category breakdown, amount vs risk scatter, hourly heatmap, top risky merchants
- **Export** reviewed cases to color-coded Excel reports
- **Persistent** — review decisions survive app restarts (SQLite)

## Risk Scoring

### Rule Engine (60% weight)
| Rule | Points |
|------|--------|
| Amount > $500 | +20 |
| Amount > $2,000 | +35 |
| Late-night transaction (11pm–5am) | +15 |
| High-risk category (Casino, Wire Transfer, Crypto) | +30 |
| Foreign location | +20 |
| Round dollar amount | +10 |
| Same merchant 3+ charges same day | +25 |
| Card in 3+ locations same day | +20 |

### ML Anomaly Detection (40% weight)
Isolation Forest trained on uploaded data. Flags transactions statistically unusual relative to overall spending patterns.

### Risk Tiers
| Tier | Score Range |
|------|------------|
| 🔴 Critical | 80–100 |
| 🟠 High | 60–79 |
| 🟡 Medium | 30–59 |
| 🟢 Low | 0–29 |

## Quick Start

```bash
# Clone
git clone https://github.com/ayondey47/fraud-transaction-risk-analyzer.git
cd fraud-transaction-risk-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Input CSV Format

```
date,merchant,category,amount,card_last4,location
2024-01-15 09:23:00,Whole Foods,Grocery,45.23,1234,New York NY
2024-01-15 23:45:00,MGM Casino,Casino,2500.00,1234,Las Vegas NV
```

A sample dataset with 61 transactions (including deliberate fraud patterns) is included at `data/sample_transactions.csv`.

## Running Tests

```bash
pytest tests/ -v
```

27 tests covering ingestion validation, rule engine boundary conditions, score ranges, tier assignment, and ML fallback behavior.

## Tech Stack

- **Streamlit** — multi-page dashboard
- **pandas** — data processing
- **scikit-learn** — Isolation Forest anomaly detection
- **SQLite** — persistent case storage
- **plotly** — interactive charts
- **openpyxl** — Excel export with color-coded risk tiers

## Project Structure

```
fraud-transaction-risk-analyzer/
├── app.py                  # Entry point
├── pages/
│   ├── 1_Upload.py         # CSV upload & validation
│   ├── 2_Score.py          # Fraud detection pipeline
│   ├── 3_Review.py         # Analyst case queue
│   ├── 4_Analytics.py      # Charts & patterns
│   └── 5_Export.py         # Excel download
├── src/
│   ├── database.py         # SQLite helpers
│   ├── ingestion.py        # CSV validation
│   ├── features.py         # Feature engineering
│   ├── rules.py            # Rule engine
│   ├── ml_scorer.py        # Isolation Forest
│   └── scorer.py           # Combined pipeline
├── tests/                  # 27 pytest tests
└── data/
    └── sample_transactions.csv
```
