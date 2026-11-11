
# ==========================================
# 1. IMPORT TOOLS
# Import libraries and functions needed
# to read, transform, and load price data.
# ==========================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_prices import transform_prices


# ==========================================
# 2. DEFINE FILE PATHS
# Locate the raw Walmart price CSV file.
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

PRICES_FILE = RAW_DATA_DIR / "sell_prices.csv"


# ==========================================
# 3. DEFINE DATABASE CLEARING FUNCTION
# Remove old price records before reloading.
# ==========================================

def clear_fact_prices() -> None:

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE fact_prices;")
        )

    print("Cleared fact_prices.")


# ==========================================
# 4. DEFINE PRICE VALIDATION FUNCTION
# Check transformed data before loading.
# ==========================================

def validate_prices(prices: pd.DataFrame) -> None:

    # Check for missing values.
    if prices.isnull().any().any():
        raise ValueError(
            "fact_prices contains missing values."
        )

    # Check for zero or negative prices.
    if (prices["sell_price"] <= 0).any():
        raise ValueError(
            "fact_prices contains non-positive prices."
        )

    # Check for duplicate store-item-week keys.
    duplicate_count = prices.duplicated(
        subset=["store_id", "item_id", "wm_yr_wk"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"fact_prices contains "
            f"{duplicate_count:,} duplicate keys."
        )


# ==========================================
# 5. DEFINE MAIN PRICE LOADING FUNCTION
# Read, transform, validate, and load data.
# ==========================================

def load_prices() -> None:

    # Step 1: Confirm the source file exists.
    if not PRICES_FILE.exists():
        raise FileNotFoundError(
            f"Price file not found: {PRICES_FILE}"
        )

    # Step 2: Read the raw CSV into a DataFrame.
    print("Reading Walmart price dataset...")

    prices = pd.read_csv(PRICES_FILE)

    # Step 3: Transform the raw price data.
    print("Transforming price data...")

    prices = transform_prices(prices)

    # Step 4: Validate the transformed data.
    print("Validating price data...")

    validate_prices(prices)

    # Step 5: Clear old database records.
    clear_fact_prices()

    # Step 6: Connect to PostgreSQL.
    engine = get_engine()

    # Step 7: Load the transformed price data.
    print("Loading prices into PostgreSQL...")

    prices.to_sql(
        "fact_prices",
        engine,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )

    # Step 8: Confirm completion.
    print(
        f"Loaded {len(prices):,} price rows."
    )

    print("Price ETL completed successfully.")


# ==========================================
# 6. START THE PROGRAM
# Execute load_prices() when this module
# is run as the main Python program.
# ==========================================

if __name__ == "__main__":
    load_prices()
