# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, database connection,
# and our transformation functions.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_dimensions import (
    transform_products,
    transform_stores,
    transform_calendar,
)


# ================================
# 2. FIND THE RAW DATA FOLDER
# Find the main project folder, then point
# to the folder that contains the raw CSV files.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ================================
# 3. LOAD PRODUCT DATA
# Read product columns from the sales CSV,
# transform them, then load them into dim_product.
# ================================

def load_products() -> None:

    # Read only the columns needed for products.
    sales = pd.read_csv(
        RAW_DATA_DIR / "sales_train_evaluation.csv",
        usecols=[
            "item_id",
            "dept_id",
            "cat_id",
        ],
    )

    # Clean/organize the product data.
    products = transform_products(sales)

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the product DataFrame into dim_product.
    products.to_sql(
        "dim_product",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    # Show how many product rows were loaded.
    print(f"Loaded {len(products):,} products.")


# ================================
# 4. LOAD STORE DATA
# Read store columns from the sales CSV,
# transform them, then load them into dim_store.
# ================================

def load_stores() -> None:

    # Read only the columns needed for stores.
    sales = pd.read_csv(
        RAW_DATA_DIR / "sales_train_evaluation.csv",
        usecols=[
            "store_id",
            "state_id",
        ],
    )

    # Clean/organize the store data.
    stores = transform_stores(sales)

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the store DataFrame into dim_store.
    stores.to_sql(
        "dim_store",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    # Show how many store rows were loaded.
    print(f"Loaded {len(stores):,} stores.")


# ================================
# 5. LOAD CALENDAR DATA
# Read the calendar CSV, transform it,
# then load it into dim_calendar.
# ================================

def load_calendar() -> None:

    # Read the raw calendar CSV.
    calendar = pd.read_csv(
        RAW_DATA_DIR / "calendar.csv"
    )

    # Clean/organize the calendar data.
    calendar = transform_calendar(calendar)

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the calendar DataFrame into dim_calendar.
    calendar.to_sql(
        "dim_calendar",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    # Show how many calendar rows were loaded.
    print(
        f"Loaded {len(calendar):,} calendar rows."
    )


# ================================
# 6. CLEAR OLD DIMENSION DATA
# Empty the dimension tables before reloading them
# so duplicate rows are not created.
# ================================

def clear_dimension_tables() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Start a database transaction.
    with engine.begin() as connection:

        # Run SQL that clears all 3 dimension tables.
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    dim_calendar,
                    dim_store,
                    dim_product
                RESTART IDENTITY CASCADE;
                """
            )
        )

    # Confirm that the old data was removed.
    print("Cleared dimension tables.")


# ================================
# 7. RUN THE LOAD PIPELINE
# When this file is run directly:
# clear old dimension data first,
# then load products, stores, and calendar.
# ================================

if __name__ == "__main__":
    clear_dimension_tables()
    load_products()
    load_stores()
    load_calendar()