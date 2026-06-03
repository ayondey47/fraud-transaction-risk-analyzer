import pytest
import pandas as pd
from src.scorer import score_transactions, assign_tier

SAMPLE_ROWS = [
    {"date": "2024-01-15 10:00:00", "merchant": "Whole Foods", "category": "Grocery",
     "amount": 45.23, "card_last4": "1234", "location": "New York NY"},
    {"date": "2024-01-15 23:30:00", "merchant": "MGM Casino", "category": "Casino",
     "amount": 2500.00, "card_last4": "1234", "location": "Lagos Nigeria"},
    {"date": "2024-01-16 10:00:00", "merchant": "Starbucks", "category": "Coffee",
     "amount": 6.75, "card_last4": "1234", "location": "New York NY"},
    {"date": "2024-01-16 14:00:00", "merchant": "Netflix", "category": "Entertainment",
     "amount": 15.99, "card_last4": "1234", "location": "New York NY"},
    {"date": "2024-01-16 19:00:00", "merchant": "Target", "category": "Shopping",
     "amount": 134.56, "card_last4": "1234", "location": "New York NY"},
]


def test_score_returns_expected_columns():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    for col in ["rule_score", "ml_score", "final_score", "risk_tier"]:
        assert col in result.columns


def test_scores_in_valid_range():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    assert result["final_score"].between(0, 100).all()
    assert result["rule_score"].between(0, 100).all()
    assert result["ml_score"].between(0, 100).all()


def test_high_risk_transaction_scores_higher():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    normal_score = result.iloc[0]["final_score"]
    risky_score = result.iloc[1]["final_score"]
    assert risky_score > normal_score


def test_tier_assignment():
    assert assign_tier(85) == "Critical"
    assert assign_tier(80) == "Critical"
    assert assign_tier(65) == "High"
    assert assign_tier(60) == "High"
    assert assign_tier(45) == "Medium"
    assert assign_tier(30) == "Medium"
    assert assign_tier(15) == "Low"
    assert assign_tier(0) == "Low"
    assert assign_tier(100) == "Critical"


def test_ml_fallback_still_returns_scores():
    # Only 3 rows — ml_scorer falls back to zeros, rules still apply
    df = pd.DataFrame(SAMPLE_ROWS[:1] * 3)
    result = score_transactions(df)
    assert len(result) == 3
    assert result["final_score"].between(0, 100).all()


def test_result_length_matches_input():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    assert len(result) == len(SAMPLE_ROWS)


def test_risk_tier_values_are_valid():
    df = pd.DataFrame(SAMPLE_ROWS)
    result = score_transactions(df)
    valid_tiers = {"Critical", "High", "Medium", "Low"}
    assert set(result["risk_tier"].unique()).issubset(valid_tiers)
