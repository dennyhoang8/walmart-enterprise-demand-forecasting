# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, and database connections.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine


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
# Store the IDs of all 10 M5 stores
# that need to be processed and loaded.
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
# Empty fact_sales before loading fresh data
# so previous rows are not duplicated.
# ================================

def clear_fact_sales() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Open a database transaction.
    with engine.begin() as connection:

        # Remove all rows from fact_sales.
        connection.execute(
            text("TRUNCATE TABLE fact_sales;")
        )

    # Confirm the table was cleared.
    print("Cleared fact_sales.")


# ================================
# 5. LOAD SALES FOR ONE STORE
# Take the full sales dataset, keep one store,
# reshape it, attach dates, validate it,
# and load it into fact_sales.
# ================================

def load_sales_for_store(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> None:

    # Show which store is currently being processed.
    print(f"\nProcessing store: {store_id}")


    # ================================
    # 5A. FILTER TO ONE STORE
    # Keep only rows belonging to the current store.
    # ================================

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()


    # ================================
    # 5B. DEFINE IDENTIFIER COLUMNS
    # These columns identify the product and store
    # and should stay as columns during melt.
    # ================================

    id_columns = [
        "item_id",
        "store_id",
    ]


    # ================================
    # 5C. FIND ALL DAILY SALES COLUMNS
    # Keep every column whose name starts with "d_"
    # such as d_1, d_2, d_3, etc.
    # ================================

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]


    # ================================
    # 5D. RESHAPE SALES FROM WIDE TO LONG
    # Turn thousands of d_ columns into rows
    # with one "d" column and one "units_sold" column.
    # ================================

    long_sales = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )


    # ================================
    # 5E. ATTACH REAL CALENDAR DATES
    # Match each d_ value such as d_1 or d_500
    # to the real calendar date.
    # ================================

    long_sales = long_sales.merge(
        calendar,
        on="d",
        how="left",
        validate="many_to_one",
    )


    # ================================
    # 5F. CONVERT DATE FORMAT
    # Make sure the date column is stored
    # as proper date values.
    # ================================

    long_sales["date"] = pd.to_datetime(
        long_sales["date"]
    ).dt.date


    # ================================
    # 5G. BUILD FINAL FACT TABLE FORMAT
    # Keep only the columns that belong
    # in fact_sales.
    # ================================

    fact_sales = long_sales[
        [
            "date",
            "item_id",
            "store_id",
            "units_sold",
        ]
    ].copy()


    # ================================
    # 5H. VALIDATE DATES
    # Stop if any sales row failed
    # to match to a real calendar date.
    # ================================

    if fact_sales["date"].isna().any():
        raise ValueError(
            f"{store_id}: Some sales rows "
            f"could not be matched to a date."
        )


    # ================================
    # 5I. VALIDATE SALES VALUES
    # Stop if any units_sold value is negative.
    # ================================

    if (fact_sales["units_sold"] < 0).any():
        raise ValueError(
            f"{store_id}: Negative unit sales were found."
        )


    # ================================
    # 5J. CHECK FOR DUPLICATE SALES KEYS
    # A row should be unique for:
    # date + item + store.
    # ================================

    duplicate_count = fact_sales.duplicated(
        subset=[
            "date",
            "item_id",
            "store_id",
        ]
    ).sum()


    # Stop if duplicate fact rows exist.
    if duplicate_count > 0:
        raise ValueError(
            f"{store_id}: Found "
            f"{duplicate_count:,} duplicate sales keys."
        )


    # ================================
    # 5K. LOAD TO POSTGRESQL
    # Connect to the database and insert
    # this store's fact_sales rows.
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


    # Confirm how many rows were loaded.
    print(
        f"Loaded {len(fact_sales):,} sales rows "
        f"for store {store_id}."
    )


# ================================
# 6. LOAD SALES FOR ALL STORES
# Read the raw datasets once,
# then process each store one at a time.
# ================================

def load_all_sales() -> None:

    # Show that the large Walmart sales file
    # is being read.
    print("Reading Walmart sales dataset...")


    # Read the full raw sales CSV.
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


    # Clear old fact_sales data first.
    clear_fact_sales()


    # Count how many stores will be processed.
    total_stores = len(STORES)


    # ================================
    # 6A. LOOP THROUGH EVERY STORE
    # Process CA_1, CA_2, ..., WI_3
    # one store at a time.
    # ================================

    for index, store_id in enumerate(
        STORES,
        start=1,
    ):

        # Show progress before starting the store.
        print(
            f"\n[{index}/{total_stores}] "
            f"Starting {store_id}"
        )


        # Process and load this store's sales.
        load_sales_for_store(
            sales=sales,
            calendar=calendar,
            store_id=store_id,
        )


        # Show progress after the store is finished.
        print(
            f"[{index}/{total_stores}] "
            f"Finished {store_id}"
        )


    # Confirm all stores finished successfully.
    print(
        "\nAll Walmart stores loaded successfully."
    )


# ================================
# 7. RUN THE SALES LOAD PIPELINE
# When this file is run directly,
# load sales for every Walmart store.
# ================================

if __name__ == "__main__":
    load_all_sales()