import streamlit as st
import pandas as pd
from datetime import datetime
from src.ingestion import validate_and_load
from src.database import init_db, save_transactions, clear_all

st.set_page_config(page_title="Upload | Fraud Analyzer", page_icon="📤", layout="wide")
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

        st.success(f"✅ Loaded **{len(df)}** valid transactions from **{uploaded_file.name}**")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Transactions", len(df))
        col2.metric("Unique Merchants", df["merchant"].nunique())
        try:
            date_range = f"{df['date'].min().date()} → {df['date'].max().date()}"
        except Exception:
            date_range = "N/A"
        col3.metric("Date Range", date_range)
        col4.metric("Total Amount", f"${df['amount'].sum():,.2f}")

        st.subheader("Preview (first 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("---")
        if st.button("💾 Save & Proceed to Scoring", type="primary"):
            with st.spinner("Saving transactions..."):
                clear_all()
                batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_transactions(df, batch_id)
                st.session_state["uploaded"] = True
                st.session_state["batch_id"] = batch_id
            st.success("✅ Transactions saved. Navigate to **2 Score** in the sidebar.")

    except ValueError as e:
        st.error(f"❌ {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error processing file: {e}")

else:
    st.info("👆 Upload a CSV file to get started, or use the sample data below.")
    if st.button("📋 Load Sample Data"):
        with st.spinner("Loading sample transactions..."):
            with open("data/sample_transactions.csv", "rb") as f:
                file_bytes = f.read()
            df, warnings = validate_and_load(file_bytes, "sample_transactions.csv")
            clear_all()
            batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_transactions(df, batch_id)
            st.session_state["uploaded"] = True
        st.success(f"✅ Loaded {len(df)} sample transactions. Navigate to **2 Score**.")
        st.dataframe(df.head(10), use_container_width=True)
