# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, database connections,
# and our sales transformation.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_sales import transform_sales


# ================================
# 2. FIND RAW DATA FILES
# Point Python to the raw M5
# sales and calendar CSV files.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SALES_FILE = RAW_DATA_DIR / "sales_train_evaluation.csv"
CALENDAR_FILE = RAW_DATA_DIR / "calendar.csv"


# ================================
# 3. LIST ALL WALMART STORES
# These are the 10 stores that
# need to be processed.
# ================================

STORES = [
    "CA_1",
    "CA_2",
    "CA_3",
    "CA_4",
    "TX_1",
    "TX_2",
    "TX_3",
    "WI_1",
    "WI_2",
    "WI_3",
]


# ================================
# 4. CLEAR OLD SALES DATA
# Remove old rows before loading
# the fresh transformed data.
# ================================

def clear_fact_sales() -> None:

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE fact_sales;")
        )

    print("Cleared fact_sales.")


# ================================
# 5. LOAD SALES FOR ONE STORE
# Send the M5 data to transform_sales(),
# receive the transformed fact_sales data,
# validate it, and load it to PostgreSQL.
# ================================

def load_sales_for_store(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> None:

    print(f"\nProcessing store: {store_id}")


    # ================================
    # 5A. TRANSFORM
    # Pass the actual M5 sales data,
    # calendar data, and store ID into
    # transform_sales.py.
    # ================================

    fact_sales = transform_sales(
        sales=sales,
        calendar=calendar,
        store_id=store_id,
    )


    # ================================
    # 5B. CHECK SALES VALUES
    # Sales should never be negative.
    # ================================

    if (fact_sales["units_sold"] < 0).any():
        raise ValueError(
            f"{store_id}: Negative unit sales were found."
        )


    # ================================
    # 5C. CHECK FOR DUPLICATES
    # Each date + item + store
    # combination should be unique.
    # ================================

    duplicate_count = fact_sales.duplicated(
        subset=[
            "date",
            "item_id",
            "store_id",
        ]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"{store_id}: Found "
            f"{duplicate_count:,} duplicate sales keys."
        )


    # ================================
    # 5D. LOAD TO POSTGRESQL
    # Insert the transformed sales data
    # into the fact_sales table.
    # ================================

    engine = get_engine()

    fact_sales.to_sql(
        "fact_sales",
        engine,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )

    print(
        f"Loaded {len(fact_sales):,} sales rows "
        f"for store {store_id}."
    )


# ================================
# 6. LOAD SALES FOR ALL STORES
# Read the raw M5 files once,
# then process each store.
# ================================

def load_all_sales() -> None:

    print("Reading Walmart sales dataset...")


    # Read M5 sales CSV.
    sales = pd.read_csv(
        SALES_FILE
    )


    # Read M5 calendar CSV.
    calendar = pd.read_csv(
        CALENDAR_FILE,
        usecols=[
            "d",
            "date",
        ],
    )


    # Clear existing database data.
    clear_fact_sales()


    # Count stores.
    total_stores = len(STORES)


    # ================================
    # 6A. LOOP THROUGH STORES
    # Each loop sends one store ID
    # into load_sales_for_store().
    # ================================

    for index, store_id in enumerate(
        STORES,
        start=1,
    ):

        print(
            f"\n[{index}/{total_stores}] "
            f"Starting {store_id}"
        )


        # ================================
        # THIS IS WHERE THE DATA IS PASSED
        # sales = actual M5 sales DataFrame
        # calendar = actual M5 calendar DataFrame
        # store_id = CA_1, CA_2, etc.
        # ================================

        load_sales_for_store(
            sales=sales,
            calendar=calendar,
            store_id=store_id,
        )


        print(
            f"[{index}/{total_stores}] "
            f"Finished {store_id}"
        )


    print(
        "\nAll Walmart stores loaded successfully."
    )


# ================================
# 7. RUN THE SALES LOAD PIPELINE
# Start the process when this
# file is run directly.
# ================================

if __name__ == "__main__":
    load_all_sales()