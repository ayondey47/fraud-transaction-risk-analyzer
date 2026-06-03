import pytest
import pandas as pd
from src.features import engineer_features
from src.rules import apply_rules


def make_txn(**overrides):
    base = {
        "date": "2024-01-15 10:00:00",
        "merchant": "Whole Foods",
        "category": "Grocery",
        "amount": 45.23,
        "card_last4": "1234",
        "location": "New York NY"
    }
    base.update(overrides)
    df = pd.DataFrame([base])
    return engineer_features(df)


def test_normal_transaction_scores_zero():
    df = make_txn()
    scores = apply_rules(df)
    assert scores.iloc[0] == 0


def test_high_amount_over_500():
    df = make_txn(amount=600.00)
    scores = apply_rules(df)
    assert scores.iloc[0] >= 20


def test_high_amount_over_2000():
    df = make_txn(amount=2500.00)
    scores = apply_rules(df)
    assert scores.iloc[0] >= 35


def test_night_transaction():
    df = make_txn(date="2024-01-15 23:30:00")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 15


def test_early_morning_is_night():
    df = make_txn(date="2024-01-15 03:00:00")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 15


def test_casino_category():
    df = make_txn(category="Casino")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 30


def test_wire_transfer_category():
    df = make_txn(category="Wire Transfer")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 30


def test_foreign_location():
    df = make_txn(location="Lagos Nigeria")
    scores = apply_rules(df)
    assert scores.iloc[0] >= 20


def test_round_amount():
    df = make_txn(amount=500.00)
    scores = apply_rules(df)
    assert scores.iloc[0] >= 10


def test_non_round_amount_no_bonus():
    df = make_txn(amount=45.23)
    scores = apply_rules(df)
    # No round-amount flag
    assert scores.iloc[0] == 0


def test_score_capped_at_100():
    df = make_txn(
        amount=3000.00,
        date="2024-01-15 23:30:00",
        category="Casino",
        location="Lagos Nigeria"
    )
    scores = apply_rules(df)
    assert scores.iloc[0] <= 100


def test_score_never_negative():
    df = make_txn()
    scores = apply_rules(df)
    assert scores.iloc[0] >= 0


def test_duplicate_merchant_same_day_penalty():
    rows = [
        {"date": "2024-01-15 10:00:00", "merchant": "Casino", "category": "Grocery",
         "amount": 10.0, "card_last4": "1234", "location": "New York NY"},
        {"date": "2024-01-15 11:00:00", "merchant": "Casino", "category": "Grocery",
         "amount": 10.0, "card_last4": "1234", "location": "New York NY"},
        {"date": "2024-01-15 12:00:00", "merchant": "Casino", "category": "Grocery",
         "amount": 10.0, "card_last4": "1234", "location": "New York NY"},
    ]
    df = engineer_features(pd.DataFrame(rows))
    scores = apply_rules(df)
    assert all(scores >= 25)
