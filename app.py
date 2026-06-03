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
Welcome to the **Fraud Transaction Risk Analyzer** — a compliance-grade tool for detecting
suspicious credit card transactions using rule-based scoring and machine learning.

---

### Analyst Workflow

| Step | Page | What Happens |
|------|------|-------------|
| 1 | **Upload** | Import your credit card transaction CSV |
| 2 | **Score** | Run the fraud detection pipeline |
| 3 | **Review** | Investigate and action flagged cases |
| 4 | **Analytics** | Explore patterns and risk distribution |
| 5 | **Export** | Download reviewed cases as Excel |

Navigate using the **sidebar →**
""")

st.info("📁 Expected CSV format: `date, merchant, category, amount, card_last4, location`")

with st.expander("📋 See sample data format"):
    import pandas as pd
    sample = pd.DataFrame([
        {"date": "2024-01-15 09:23:00", "merchant": "Whole Foods", "category": "Grocery",
         "amount": 45.23, "card_last4": "1234", "location": "New York NY"},
        {"date": "2024-01-15 23:45:00", "merchant": "MGM Casino", "category": "Casino",
         "amount": 2500.00, "card_last4": "1234", "location": "Las Vegas NV"},
        {"date": "2024-01-29 23:00:00", "merchant": "Binance", "category": "Cryptocurrency",
         "amount": 3000.00, "card_last4": "1234", "location": "Online"},
    ])
    st.dataframe(sample, width="stretch")

with st.expander("🔎 How Scoring Works"):
    st.markdown("""
    **Rule Engine (60% weight)** — Deterministic flags:
    - Amount > $500 (+20 pts) or > $2,000 (+35 pts)
    - Late-night transaction 11pm–5am (+15 pts)
    - High-risk category: Casino, Wire Transfer, Cryptocurrency (+30 pts)
    - Foreign location (+20 pts)
    - Round dollar amount (+10 pts)
    - Same merchant 3+ charges same day (+25 pts)
    - Card used in 3+ locations same day (+20 pts)

    **ML Anomaly Detection (40% weight)** — Isolation Forest trained on your uploaded data.
    Flags transactions that are statistically unusual relative to the overall spending pattern.

    **Risk Tiers:**
    🔴 Critical (80–100) | 🟠 High (60–79) | 🟡 Medium (30–59) | 🟢 Low (0–29)
    """)
