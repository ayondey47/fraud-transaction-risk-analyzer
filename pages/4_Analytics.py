import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import init_db, get_scored_cases

st.set_page_config(page_title="Analytics | Fraud Analyzer", page_icon="📊", layout="wide")
init_db()

TIER_COLORS = {
    "Critical": "#dc2626",
    "High": "#f97316",
    "Medium": "#eab308",
    "Low": "#22c55e"
}

st.title("📊 Analytics")
st.markdown("Visual exploration of transaction risk patterns.")

scored = get_scored_cases()

if scored.empty:
    st.warning("No scored transactions. Go to **2 Score** first.")
    st.stop()

scored["date"] = pd.to_datetime(scored["date"], errors="coerce")
scored["hour"] = scored["date"].dt.hour
scored["day_of_week"] = scored["date"].dt.day_name()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Risk Distribution",
    "🏷️ By Category",
    "💰 Amount vs Risk",
    "🕐 Hourly Heatmap",
    "🏪 Top Merchants"
])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        tier_order = ["Critical", "High", "Medium", "Low"]
        tier_counts = scored["risk_tier"].value_counts().reindex(tier_order).fillna(0).reset_index()
        tier_counts.columns = ["Risk Tier", "Count"]
        fig = px.bar(
            tier_counts, x="Risk Tier", y="Count",
            color="Risk Tier", color_discrete_map=TIER_COLORS,
            title="Transactions by Risk Tier",
            text="Count"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(
            scored, x="final_score", nbins=20,
            title="Risk Score Distribution",
            labels={"final_score": "Final Score"},
            color_discrete_sequence=["#3b82f6"]
        )
        fig2.add_vline(x=30, line_dash="dash", line_color="yellow", annotation_text="Medium")
        fig2.add_vline(x=60, line_dash="dash", line_color="orange", annotation_text="High")
        fig2.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="Critical")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    cat_stats = (
        scored.groupby("category")
        .agg(avg_score=("final_score", "mean"), count=("final_score", "count"))
        .sort_values("avg_score", ascending=False)
        .reset_index()
    )
    fig = px.bar(
        cat_stats, x="category", y="avg_score",
        color="avg_score", color_continuous_scale="RdYlGn_r",
        title="Average Risk Score by Merchant Category",
        labels={"avg_score": "Avg Risk Score", "category": "Category"},
        text=cat_stats["count"].apply(lambda c: f"n={c}")
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.scatter(
        scored,
        x="amount", y="final_score",
        color="risk_tier",
        color_discrete_map=TIER_COLORS,
        hover_data=["merchant", "category", "date", "location"],
        title="Transaction Amount vs Risk Score",
        labels={"amount": "Amount ($)", "final_score": "Risk Score"}
    )
    fig.add_hline(y=30, line_dash="dash", line_color="yellow", opacity=0.5)
    fig.add_hline(y=60, line_dash="dash", line_color="orange", opacity=0.5)
    fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    if scored["hour"].notna().any():
        hour_data = scored.groupby("hour").agg(
            count=("final_score", "count"),
            avg_score=("final_score", "mean")
        ).reset_index()

        fig = px.bar(
            hour_data, x="hour", y="count",
            color="avg_score", color_continuous_scale="RdYlGn_r",
            title="Transactions by Hour of Day (colored by avg risk)",
            labels={"hour": "Hour (24h)", "count": "# Transactions", "avg_score": "Avg Risk"}
        )
        fig.add_vrect(x0=22.5, x1=24, fillcolor="red", opacity=0.07, annotation_text="Night zone")
        fig.add_vrect(x0=0, x1=5, fillcolor="red", opacity=0.07)
        st.plotly_chart(fig, use_container_width=True)

        st.caption("Red shading = night window (11pm–5am), which adds +15 pts to rule score.")
    else:
        st.info("No valid date/hour data available.")

with tab5:
    flagged_merchants = (
        scored[scored["risk_tier"].isin(["Critical", "High"])]
        .groupby("merchant")
        .agg(flagged_count=("final_score", "count"), avg_score=("final_score", "mean"))
        .sort_values("avg_score", ascending=False)
        .head(15)
        .reset_index()
    )
    if not flagged_merchants.empty:
        fig = px.bar(
            flagged_merchants,
            x="avg_score", y="merchant",
            orientation="h",
            color="avg_score", color_continuous_scale="Reds",
            title="Top 15 Risky Merchants (Critical + High only)",
            labels={"avg_score": "Avg Risk Score", "merchant": "Merchant"},
            text=flagged_merchants["flagged_count"].apply(lambda c: f"{c} txn")
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Critical or High risk merchants found.")
