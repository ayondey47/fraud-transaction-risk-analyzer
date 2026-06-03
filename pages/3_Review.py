import streamlit as st
import pandas as pd
from src.database import init_db, get_scored_cases, save_review_decision, get_latest_decision_per_transaction

st.set_page_config(page_title="Review | Fraud Analyzer", page_icon="🔎", layout="wide")
init_db()

TIER_COLORS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
DECISION_ICONS = {"escalated": "🚨", "reviewed": "✅", "cleared": "⬜", "pending": "⏳"}
DECISION_LABELS = {"escalated": "Escalated", "reviewed": "Reviewed", "cleared": "Cleared as Legit", "pending": "Pending"}

st.title("🔎 Review Flagged Cases")
st.markdown("Investigate flagged transactions and record analyst decisions. Decisions persist between sessions.")

scored = get_scored_cases()

if scored.empty:
    st.warning("No scored transactions. Go to **2 Score** first.")
    st.stop()

flagged = scored[scored["risk_tier"].isin(["Critical", "High", "Medium"])].copy()

if flagged.empty:
    st.success("🎉 No flagged transactions. All transactions scored Low risk.")
    st.stop()

decisions = get_latest_decision_per_transaction()
decision_map = dict(zip(decisions["transaction_id"], decisions["decision"])) if not decisions.empty else {}

flagged["current_decision"] = flagged["transaction_id"].map(decision_map).fillna("pending")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🔴 Critical", len(flagged[flagged["risk_tier"] == "Critical"]))
col2.metric("🟠 High", len(flagged[flagged["risk_tier"] == "High"]))
col3.metric("🟡 Medium", len(flagged[flagged["risk_tier"] == "Medium"]))
col4.metric("⏳ Pending", len(flagged[flagged["current_decision"] == "pending"]))
col5.metric("✅ Actioned", len(flagged[flagged["current_decision"] != "pending"]))

st.markdown("---")

with st.expander("🔽 Filter Options", expanded=True):
    col_a, col_b = st.columns(2)
    tier_filter = col_a.multiselect(
        "Risk Tier", ["Critical", "High", "Medium"],
        default=["Critical", "High", "Medium"]
    )
    status_filter = col_b.multiselect(
        "Decision Status", ["pending", "escalated", "reviewed", "cleared"],
        default=["pending", "escalated"]
    )

view = flagged[
    flagged["risk_tier"].isin(tier_filter) &
    flagged["current_decision"].isin(status_filter)
].sort_values("final_score", ascending=False)

st.markdown(f"**Showing {len(view)} cases**")

if view.empty:
    st.info("No cases match the current filters.")
    st.stop()

for _, row in view.iterrows():
    tier_icon = TIER_COLORS.get(row["risk_tier"], "")
    status_icon = DECISION_ICONS.get(row["current_decision"], "⏳")
    status_label = DECISION_LABELS.get(row["current_decision"], row["current_decision"])
    txn_id = int(row["transaction_id"])

    header = (
        f"{tier_icon} **{row['merchant']}** — "
        f"${row['amount']:.2f} — "
        f"Score: **{row['final_score']:.0f}** — "
        f"{status_icon} {status_label}"
    )

    with st.expander(header):
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**Date:** {row['date']}")
            st.write(f"**Merchant:** {row['merchant']}")
            st.write(f"**Category:** {row['category']}")
            st.write(f"**Location:** {row['location']}")
        with col_b:
            st.write(f"**Amount:** ${row['amount']:.2f}")
            st.write(f"**Card:** ...{row['card_last4']}")
            st.write(f"**Rule Score:** {row['rule_score']:.1f} / 100")
            st.write(f"**ML Score:** {row['ml_score']:.1f} / 100")
            st.write(f"**Final Score:** {row['final_score']:.1f} / 100")
            st.write(f"**Risk Tier:** {tier_icon} {row['risk_tier']}")

        notes = st.text_input(
            "Analyst notes",
            key=f"notes_{txn_id}",
            placeholder="Optional: add context or reason for decision..."
        )

        c1, c2, c3 = st.columns(3)
        if c1.button("🚨 Escalate", key=f"esc_{txn_id}", use_container_width=True):
            save_review_decision(txn_id, "escalated", notes)
            st.rerun()
        if c2.button("✅ Mark Reviewed", key=f"rev_{txn_id}", use_container_width=True):
            save_review_decision(txn_id, "reviewed", notes)
            st.rerun()
        if c3.button("⬜ Clear as Legit", key=f"clr_{txn_id}", use_container_width=True):
            save_review_decision(txn_id, "cleared", notes)
            st.rerun()
