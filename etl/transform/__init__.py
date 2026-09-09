# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, database connections,
# and the sales transformation function.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_sales import transform_sales


# ================================
# 2. FIND RAW DATA FILES
# Find the project root and point Python
# to the raw Walmart sales and calendar CSVs.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SALES_FILE = RAW_DATA_DIR / "sales_train_evaluation.csv"
CALENDAR_FILE = RAW_DATA_DIR / "calendar.csv"


# ================================
# 3. LIST ALL WALMART STORES
# Store the IDs of all M5 stores
# that need to be processed.
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
# Empty fact_sales before loading new data
# so old rows are not duplicated.
# ================================

def clear_fact_sales() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Open a database transaction.
    with engine.begin() as connection:

        # Remove all existing rows from fact_sales.
        connection.execute(
            text("TRUNCATE TABLE fact_sales;")
        )

    # Confirm the table was cleared.
    print("Cleared fact_sales.")


# ================================
# 5. VALIDATE ONE STORE'S SALES
# Check the transformed sales data for
# missing dates, missing sales, negatives,
# and duplicate keys.
# ================================

def validate_sales(
    fact_sales: pd.DataFrame,
    store_id: str,
) -> None:

    # Check whether any sales rows
    # are missing a date.
    if fact_sales["date"].isna().any():
        raise ValueError(
            f"{store_id}: Some sales rows could not be matched to a date."
        )

    # Check whether any units_sold
    # values are missing.
    if fact_sales["units_sold"].isna().any():
        raise ValueError(
            f"{store_id}: Missing unit sales were found."
        )

    # Check whether any units_sold
    # values are negative.
    if (fact_sales["units_sold"] < 0).any():
        raise ValueError(
            f"{store_id}: Negative unit sales were found."
        )

    # Count duplicate sales rows.
    # One sales row should be unique for:
    # date + item + store.
    duplicate_count = fact_sales.duplicated(
        subset=[
            "date",
            "item_id",
            "store_id",
        ]
    ).sum()

    # Stop if any duplicate keys exist.
    if duplicate_count > 0:
        raise ValueError(
            f"{store_id}: Found "
            f"{duplicate_count:,} duplicate sales keys."
        )


# ================================
# 6. LOAD SALES FOR ONE STORE
# Transform, validate, and load the sales
# for a single Walmart store.
# ================================

def load_sales_for_store(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> None:

    # Show which store is being processed.
    print(f"\nProcessing store: {store_id}")

    # Send the raw sales and calendar data
    # into the transform_sales function.
    # It returns the finished fact_sales DataFrame
    # for this specific store.
    fact_sales = transform_sales(
        sales=sales,
        calendar=calendar,
        store_id=store_id,
    )

    # Validate the transformed sales data
    # before putting it into PostgreSQL.
    validate_sales(
        fact_sales=fact_sales,
        store_id=store_id,
    )

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load this store's sales rows
    # into the fact_sales table.
    fact_sales.to_sql(
        "fact_sales",
        engine,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )

    # Show how many rows were loaded.
    print(
        f"Loaded {len(fact_sales):,} sales rows "
        f"for store {store_id}."
    )


# ================================
# 7. LOAD SALES FOR ALL STORES
# Read the raw datasets once,
# then process each store one at a time.
# ================================

def load_all_sales() -> None:

    # Show that the large Walmart dataset
    # is being read.
    print("Reading Walmart sales dataset...")

    # Read the entire raw sales CSV.
    sales = pd.read_csv(
        SALES_FILE
    )

    # Read only the calendar columns needed
    # to match d_ values to real dates.
    calendar = pd.read_csv(
        CALENDAR_FILE,
        usecols=[
            "d",
            "date",
        ],
    )

    # Clear old sales rows first.
    clear_fact_sales()

    # Count how many stores will be processed.
    total_stores = len(STORES)

    # Loop through every store.
    # enumerate gives us:
    # 1, CA_1
    # 2, CA_2
    # ...
    # 10, WI_3
    for index, store_id in enumerate(
        STORES,
        start=1,
    ):

        # Show progress before starting.
        print(
            f"\n[{index}/{total_stores}] "
            f"Starting {store_id}"
        )

        # Transform, validate, and load
        # this store's sales.
        load_sales_for_store(
            sales=sales,
            calendar=calendar,
            store_id=store_id,
        )

        # Show progress after finishing.
        print(
            f"[{index}/{total_stores}] "
            f"Finished {store_id}"
        )

    # Confirm all stores finished.
    print(
        "\nAll Walmart stores loaded successfully."
    )


# ================================
# 8. RUN THE SALES LOAD PIPELINE
# When this file is run directly,
# load sales for all Walmart stores.
# ================================

if __name__ == "__main__":
    load_all_sales()