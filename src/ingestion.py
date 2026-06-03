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
