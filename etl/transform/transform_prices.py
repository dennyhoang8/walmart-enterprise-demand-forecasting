
import pandas as pd


# ==========================================
# 1. DEFINE PRICE TRANSFORMATION FUNCTION
# Receives raw price data from load_prices.py.
# Returns a cleaned DataFrame for PostgreSQL.
# ==========================================

def transform_prices(prices: pd.DataFrame) -> pd.DataFrame:

    # ==========================================
    # 2. VALIDATE REQUIRED COLUMNS
    # Make sure the CSV contains the columns
    # needed for the fact_prices table.
    # ==========================================

    required_columns = [
        "store_id",
        "item_id",
        "wm_yr_wk",
        "sell_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in prices.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing price columns: {missing_columns}"
        )

    # ==========================================
    # 3. SELECT REQUIRED COLUMNS
    # Keep only the columns needed and create
    # a separate copy of the DataFrame.
    # ==========================================

    prices = prices[required_columns].copy()

    # ==========================================
    # 4. STANDARDIZE DATA TYPES
    # Convert week IDs to integers and
    # selling prices to numeric values.
    # ==========================================

    prices["wm_yr_wk"] = pd.to_numeric(
        prices["wm_yr_wk"],
        errors="raise",
    ).astype("int64")

    prices["sell_price"] = pd.to_numeric(
        prices["sell_price"],
        errors="raise",
    )

    # ==========================================
    # 5. VALIDATE MISSING VALUES
    # Reject records with missing required data.
    # ==========================================

    if prices[required_columns].isna().any().any():
        raise ValueError(
            "Price data contains missing values."
        )

    # ==========================================
    # 6. VALIDATE SELLING PRICES
    # Selling prices must be greater than zero.
    # ==========================================

    if (prices["sell_price"] <= 0).any():
        raise ValueError(
            "Price data contains zero or negative prices."
        )

    # ==========================================
    # 7. VALIDATE DUPLICATE RECORDS
    # Each store, item, and week combination
    # should have only one selling price.
    # ==========================================

    duplicate_count = prices.duplicated(
        subset=["store_id", "item_id", "wm_yr_wk"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count:,} duplicate price records."
        )

    # ==========================================
    # 8. RETURN TRANSFORMED DATA
    # Send the finished DataFrame back to
    # the function that called transform_prices().
    # ==========================================

    return prices
