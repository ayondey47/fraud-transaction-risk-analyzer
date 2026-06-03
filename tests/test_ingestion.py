import pytest
import pandas as pd
from src.ingestion import validate_and_load, REQUIRED_COLUMNS


def make_csv(rows: list) -> bytes:
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


GOOD_ROW = {
    "date": "2024-01-15 09:23:00",
    "merchant": "Whole Foods",
    "category": "Grocery",
    "amount": "45.23",
    "card_last4": "1234",
    "location": "New York NY"
}


def test_valid_csv_loads():
    data = make_csv([GOOD_ROW])
    df, warnings = validate_and_load(data, "test.csv")
    assert len(df) == 1
    assert len(warnings) == 0
    assert df["amount"].dtype == float


def test_missing_column_raises():
    bad = {k: v for k, v in GOOD_ROW.items() if k != "merchant"}
    data = make_csv([bad])
    with pytest.raises(ValueError, match="missing columns"):
        validate_and_load(data, "test.csv")


def test_empty_file_raises():
    with pytest.raises(ValueError, match="empty"):
        validate_and_load(b"", "test.csv")


def test_bad_amount_rows_warned_and_dropped():
    bad_row = {**GOOD_ROW, "amount": "not_a_number"}
    data = make_csv([GOOD_ROW, bad_row])
    df, warnings = validate_and_load(data, "test.csv")
    assert len(df) == 1
    assert any("amount" in w.lower() for w in warnings)


def test_column_names_stripped_and_lowercased():
    df_raw = pd.DataFrame([GOOD_ROW])
    df_raw.columns = [" Date ", " Merchant ", " Category ", " Amount ", " Card_Last4 ", " Location "]
    data = df_raw.to_csv(index=False).encode("utf-8")
    df, warnings = validate_and_load(data, "test.csv")
    assert list(df.columns[:6]) == REQUIRED_COLUMNS


def test_multiple_valid_rows():
    data = make_csv([GOOD_ROW, GOOD_ROW, GOOD_ROW])
    df, warnings = validate_and_load(data, "test.csv")
    assert len(df) == 3


def test_whitespace_only_file_raises():
    with pytest.raises(ValueError, match="empty"):
        validate_and_load(b"   \n  ", "test.csv")
