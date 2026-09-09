# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, database connections,
# and price-data transformation.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_prices import transform_prices


# ================================
# 2. FIND THE RAW DATA FOLDER
# Find the main project folder and point
# Python to the raw M5 CSV files.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)


# ================================
# 3. CLEAR OLD PRICE DATA
# Empty fact_prices before loading fresh
# price data so old rows are not duplicated.
# ================================

def clear_fact_prices() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Start a database transaction.
    with engine.begin() as connection:

        # Run SQL that removes all existing
        # rows from fact_prices.
        connection.execute(
            text("TRUNCATE TABLE fact_prices;")
        )

    # Confirm that the table was cleared.
    print("Cleared fact_prices.")


# ================================
# 4. VALIDATE PRICE DATA
# Check the transformed price data for
# missing values, invalid prices, and duplicates.
# ================================

def validate_prices(prices: pd.DataFrame) -> None:

    # Check the ENTIRE DataFrame for missing values.
    # If even one missing value exists, stop the program.
    if prices.isnull().any().any():
        raise ValueError(
            "fact_prices contains missing values."
        )

    # Check whether any sell_price is
    # zero or negative.
    if (prices["sell_price"] <= 0).any():
        raise ValueError(
            "fact_prices contains non-positive prices."
        )

    # Count duplicate price records.
    # A price record should be unique for:
    # store + item + Walmart year/week.
    duplicate_count = prices.duplicated(
        subset=[
            "store_id",
            "item_id",
            "wm_yr_wk",
        ]
    ).sum()

    # If duplicates were found,
    # stop the program and show how many.
    if duplicate_count > 0:
        raise ValueError(
            f"fact_prices contains "
            f"{duplicate_count} duplicate keys."
        )


# ================================
# 5. LOAD PRICE DATA
# Read sell_prices.csv, transform it,
# validate it, and load it into fact_prices.
# ================================

def load_prices() -> None:

    # Read the raw M5 price CSV
    # into a Pandas DataFrame.
    prices = pd.read_csv(
        RAW_DATA_DIR / "sell_prices.csv"
    )

    # Clean/prepare the price data using
    # our price transformation function.
    prices = transform_prices(
        prices
    )

    # Check the transformed data for problems
    # before allowing it into PostgreSQL.
    validate_prices(
        prices
    )

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the finished price DataFrame
    # into the fact_prices table.
    prices.to_sql(
        "fact_prices",
        engine,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )

    # Show how many price rows were loaded.
    print(
        f"Loaded {len(prices):,} price rows."
    )


# ================================
# 6. RUN THE PRICE LOAD PIPELINE
# When this file is run directly:
# clear the old prices first,
# then load the fresh price data.
# ================================

if __name__ == "__main__":
    clear_fact_prices()
    load_prices()