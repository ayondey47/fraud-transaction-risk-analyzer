# Fraud Transaction Risk Analyzer — Design Spec
Date: 2026-06-03

## Overview
Interactive Streamlit dashboard for credit card transaction fraud analysis. Mimics a real fraud analyst workflow: upload transactions → score with rule engine + ML → review flagged cases → export report.

## Architecture

Multi-page Streamlit app with SQLite persistence.

```
fraud-transaction-risk-analyzer/
├── app.py
├── pages/
│   ├── 1_Upload.py
│   ├── 2_Score.py
│   ├── 3_Review.py
│   ├── 4_Analytics.py
│   └── 5_Export.py
├── src/
│   ├── ingestion.py
│   ├── features.py
│   ├── rules.py
│   ├── ml_scorer.py
│   ├── scorer.py
│   └── database.py
├── tests/
│   ├── test_ingestion.py
│   ├── test_rules.py
│   └── test_scorer.py
├── data/
│   └── sample_transactions.csv
└── requirements.txt
```

## Input Format
Credit card CSV: `date, merchant, category, amount, card_last4, location`

## Pages

1. **Upload & Validate** — CSV upload, column mapping, preview, reject bad rows
2. **Score Transactions** — pipeline execution, results table with risk tier badges
3. **Review Cases** — analyst queue (Medium+ only), Mark Reviewed / Escalate / Clear actions, SQLite-persisted
4. **Analytics** — risk distribution, category breakdown, amount vs risk scatter, hourly heatmap, top risky merchants
5. **Export** — Excel download with color-coded tiers and review decisions

## Risk Scoring

### Rule Engine (0–100 pts, capped)
| Rule | Points |
|------|--------|
| Amount > $500 | +20 |
| Amount > $2,000 | +35 |
| Transaction 11pm–5am | +15 |
| Same merchant 3+ charges same day | +25 |
| Category: Casino / Wire / Crypto | +30 |
| Foreign location (non-US) | +20 |
| Round dollar amount | +10 |
| Card used in 3+ locations same day | +20 |

### ML Layer
Isolation Forest trained on uploaded dataset. Flags statistically anomalous transactions relative to user's own spending patterns. Returns anomaly score 0–100.

### Combined Score
`final = (0.6 × rule_score) + (0.4 × ml_score)`, capped at 100.

### Risk Tiers
- Low: 0–29
- Medium: 30–59
- High: 60–79
- Critical: 80–100

## Data Persistence (SQLite)
- `transactions` — raw uploaded rows
- `scored_cases` — transactions + scores + tier
- `review_decisions` — analyst actions with timestamps

DB path: `data/fraud_cases.db`

## Error Handling
- CSV: validates required columns, encoding errors, empty files
- Scoring: rule-only fallback if ML fails, warning banner shown
- DB: writes in transactions with rollback on failure

## Testing
- `test_ingestion.py` — column validation, encoding, empty file edge cases
- `test_rules.py` — boundary conditions per rule, rule combinations
- `test_scorer.py` — score range (0–100), tier assignment, fallback mode
