import pandas as pd


def apply_rules(df: pd.DataFrame) -> pd.Series:
    """Apply rule engine to feature-engineered DataFrame. Returns Series of scores 0–100."""
    scores = pd.Series(0.0, index=df.index)

    # Amount rules — mutually exclusive tiers
    scores += df["amount"].apply(lambda a: 35 if a > 2000 else (20 if a > 500 else 0))

    # Late-night transaction
    scores += df["is_night"].apply(lambda x: 15 if x else 0)

    # High-risk merchant category
    scores += df["is_high_risk_category"].apply(lambda x: 30 if x else 0)

    # Foreign location
    scores += df["is_foreign"].apply(lambda x: 20 if x else 0)

    # Round dollar amount (e.g. $500.00 — common in fraud)
    scores += df["is_round_amount"].apply(lambda x: 10 if x else 0)

    # Same merchant charged 3+ times same day
    scores += df["daily_merchant_count"].apply(lambda c: 25 if c >= 3 else 0)

    # Card used in 3+ distinct locations same day
    scores += df["daily_location_count"].apply(lambda c: 20 if c >= 3 else 0)

    return scores.clip(0, 100)
