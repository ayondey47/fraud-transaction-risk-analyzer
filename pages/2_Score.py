import streamlit as st
import pandas as pd
from src.database import init_db, get_transactions, save_scores, get_scored_cases
from src.scorer import score_transactions

st.set_page_config(page_title="Score | Fraud Analyzer", page_icon="⚡", layout="wide")
init_db()

TIER_COLORS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}

st.title("⚡ Score Transactions")

transactions = get_transactions()

if transactions.empty:
    st.warning("No transactions loaded. Go to **1 Upload** first.")
    st.stop()

st.metric("Transactions Ready to Score", len(transactions))

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("Click **Run** to execute the full fraud detection pipeline (rule engine + ML anomaly detection).")
with col2:
    run_btn = st.button("🚀 Run Fraud Detection Pipeline", type="primary")

if run_btn:
    with st.spinner("Running rule engine + Isolation Forest ML scoring..."):
        try:
            raw = transactions.drop(columns=["id", "upload_batch", "created_at"], errors="ignore")
            scored = score_transactions(raw)
            scored["transaction_id"] = transactions["id"].values
            save_scores(scored[["transaction_id", "rule_score", "ml_score", "final_score", "risk_tier"]])
            st.success("✅ Scoring complete!")
        except Exception as e:
            st.error(f"❌ Scoring failed: {e}")
            st.stop()

scored_cases = get_scored_cases()

if not scored_cases.empty:
    st.markdown("---")
    st.subheader("Risk Summary")

    tier_counts = scored_cases["risk_tier"].value_counts()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Critical", tier_counts.get("Critical", 0))
    col2.metric("🟠 High", tier_counts.get("High", 0))
    col3.metric("🟡 Medium", tier_counts.get("Medium", 0))
    col4.metric("🟢 Low", tier_counts.get("Low", 0))

    flagged_pct = (
        (tier_counts.get("Critical", 0) + tier_counts.get("High", 0)) / len(scored_cases) * 100
        if len(scored_cases) > 0 else 0
    )
    st.metric("High+ Flagged Rate", f"{flagged_pct:.1f}%")

    st.markdown("---")
    st.subheader("All Scored Transactions")

    tier_filter = st.multiselect(
        "Filter by Risk Tier",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"]
    )

    display = scored_cases[scored_cases["risk_tier"].isin(tier_filter)].copy()
    display["Tier"] = display["risk_tier"].map(TIER_COLORS) + " " + display["risk_tier"]
    display = display.sort_values("final_score", ascending=False)

    st.dataframe(
        display[["date", "merchant", "category", "amount", "location",
                 "rule_score", "ml_score", "final_score", "Tier"]].rename(columns={
            "rule_score": "Rule Score",
            "ml_score": "ML Score",
            "final_score": "Final Score"
        }),
        use_container_width=True
    )
else:
    st.info("Click **Run Fraud Detection Pipeline** to score the loaded transactions.")
