import pandas as pd
from src.features import engineer_features
from src.rules import apply_rules
from src.ml_scorer import train_and_score

RULE_WEIGHT = 0.6
ML_WEIGHT = 0.4

TIER_THRESHOLDS = [
    (80, "Critical"),
    (60, "High"),
    (30, "Medium"),
    (0, "Low"),
]


def assign_tier(score: float) -> str:
    for threshold, tier in TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return "Low"


def score_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Full pipeline: raw df → feature engineering → rule score → ML score → combined."""
    featured = engineer_features(df)

    rule_scores = apply_rules(featured)
    ml_scores = train_and_score(featured)

    final_scores = (RULE_WEIGHT * rule_scores + ML_WEIGHT * ml_scores).clip(0, 100)
    tiers = final_scores.apply(assign_tier)

    result = df.copy()
    result["rule_score"] = rule_scores.round(2)
    result["ml_score"] = ml_scores.round(2)
    result["final_score"] = final_scores.round(2)
    result["risk_tier"] = tiers
    return result
