import pandas as pd

HIGH_RISK_CATEGORIES = {"casino", "wire transfer", "cryptocurrency", "crypto", "gambling"}
US_STATE_ABBREVS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC"
}


def _is_foreign(location: str) -> bool:
    if pd.isna(location):
        return False
    loc = str(location).strip().lower()
    if loc in {"online", ""}:
        return False
    parts = str(location).split()
    return not any(p.upper() in US_STATE_ABBREVS for p in parts)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["hour"] = out["date"].dt.hour.fillna(-1).astype(int)
    out["date_only"] = out["date"].dt.date

    out["is_night"] = out["hour"].apply(lambda h: h >= 23 or h < 5)
    out["is_round_amount"] = out["amount"].apply(
        lambda a: float(a) == int(float(a)) if pd.notna(a) else False
    )
    out["is_high_risk_category"] = out["category"].str.lower().isin(HIGH_RISK_CATEGORIES)
    out["is_foreign"] = out["location"].apply(_is_foreign)

    merchant_day_counts = out.groupby(["merchant", "date_only"])["amount"].transform("count")
    out["daily_merchant_count"] = merchant_day_counts.fillna(1).astype(int)

    location_day_counts = out.groupby(["card_last4", "date_only"])["location"].transform("nunique")
    out["daily_location_count"] = location_day_counts.fillna(1).astype(int)

    return out
