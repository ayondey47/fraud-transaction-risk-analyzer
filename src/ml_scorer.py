import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ML_FEATURES = [
    "amount", "hour", "is_night", "is_round_amount",
    "is_high_risk_category", "is_foreign",
    "daily_merchant_count", "daily_location_count"
]


def train_and_score(df: pd.DataFrame) -> pd.Series:
    """Train Isolation Forest on df, return anomaly scores 0–100.
    Higher = more anomalous. Falls back to zeros if training fails or data too small."""
    try:
        feature_df = df[ML_FEATURES].copy()

        for col in ["is_night", "is_round_amount", "is_high_risk_category", "is_foreign"]:
            feature_df[col] = feature_df[col].astype(int)

        feature_df = feature_df.fillna(0)

        if len(feature_df) < 5:
            return pd.Series(0.0, index=df.index)

        scaler = StandardScaler()
        X = scaler.fit_transform(feature_df)

        model = IsolationForest(
            n_estimators=100,
            contamination=0.15,
            random_state=42
        )
        model.fit(X)

        # decision_function: higher = more normal, lower = more anomalous
        raw_scores = model.decision_function(X)
        inverted = -raw_scores

        min_s, max_s = inverted.min(), inverted.max()
        if max_s == min_s:
            return pd.Series(0.0, index=df.index)

        normalized = (inverted - min_s) / (max_s - min_s) * 100
        return pd.Series(normalized.values, index=df.index).clip(0, 100)

    except Exception:
        return pd.Series(0.0, index=df.index)
