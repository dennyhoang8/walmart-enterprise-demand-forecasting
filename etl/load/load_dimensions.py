
# ================================
# 1. IMPORT TOOLS
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
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SALES_FILE = RAW_DATA_DIR / "sales_train_evaluation.csv"
CALENDAR_FILE = RAW_DATA_DIR / "calendar.csv"


# ================================
# 3. READ AND TRANSFORM DIMENSIONS
# ================================

def prepare_dimensions():

    # Confirm the CSV files exist.
    for file in [SALES_FILE, CALENDAR_FILE]:
        if not file.exists():
            raise FileNotFoundError(
                f"Required file not found: {file}"
            )

    # Read only the required sales columns.
    print("Reading Walmart dimension data...")

    sales = pd.read_csv(
        SALES_FILE,
        usecols=[
            "item_id",
            "dept_id",
            "cat_id",
            "store_id",
            "state_id",
        ],
    )

    calendar = pd.read_csv(CALENDAR_FILE)

    # Transform each dimension.
    print("Transforming dimension data...")

    products = transform_products(sales)
    stores = transform_stores(sales)
    calendar = transform_calendar(calendar)

    # Prevent empty datasets.
    for name, data in [
        ("products", products),
        ("stores", stores),
        ("calendar", calendar),
    ]:
        if data.empty:
            raise ValueError(
                f"{name} dataset is empty."
            )

    return products, stores, calendar


# ================================
# 4. LOAD DIMENSIONS SAFELY
# Insert new records and update existing
# records without deleting fact tables.
# ================================

def load_dimensions() -> None:

    products, stores, calendar = prepare_dimensions()

    engine = get_engine()

    print("Loading dimensions into PostgreSQL...")

    # Use one transaction for all changes.
    with engine.begin() as connection:

        # ================================
        # 5. LOAD PRODUCT DIMENSION
        # ================================

        products.to_sql(
            "_stage_dim_product",
            connection,
            if_exists="replace",
            index=False,
            method="multi",
        )

        connection.execute(text("""
            INSERT INTO dim_product (
                item_id, dept_id, cat_id
            )
            SELECT item_id, dept_id, cat_id
            FROM _stage_dim_product
            ON CONFLICT (item_id)
            DO UPDATE SET
                dept_id = EXCLUDED.dept_id,
                cat_id = EXCLUDED.cat_id;
        """))

        # ================================
        # 6. LOAD STORE DIMENSION
        # ================================

        stores.to_sql(
            "_stage_dim_store",
            connection,
            if_exists="replace",
            index=False,
            method="multi",
        )

        connection.execute(text("""
            INSERT INTO dim_store (
                store_id, state_id
            )
            SELECT store_id, state_id
            FROM _stage_dim_store
            ON CONFLICT (store_id)
            DO UPDATE SET
                state_id = EXCLUDED.state_id;
        """))

        # ================================
        # 7. LOAD CALENDAR DIMENSION
        # ================================

        calendar.to_sql(
            "_stage_dim_calendar",
            connection,
            if_exists="replace",
            index=False,
            method="multi",
        )

        columns = list(calendar.columns)

        # Quote column names for SQL.
        column_sql = ", ".join(
            f'"{column}"' for column in columns
        )

        # Update every column except the date key.
        update_sql = ", ".join(
            f'"{column}" = EXCLUDED."{column}"'
            for column in columns
            if column != "date"
        )

        connection.execute(text(f"""
            INSERT INTO dim_calendar ({column_sql})
            SELECT {column_sql}
            FROM _stage_dim_calendar
            ON CONFLICT (date)
            DO UPDATE SET {update_sql};
        """))

        # ================================
        # 8. REMOVE STAGING TABLES
        # ================================

        connection.execute(text("""
            DROP TABLE _stage_dim_product;
            DROP TABLE _stage_dim_store;
            DROP TABLE _stage_dim_calendar;
        """))

    # ================================
    # 9. CONFIRM COMPLETION
    # ================================

    print(f"Processed {len(products):,} products.")
    print(f"Processed {len(stores):,} stores.")
    print(f"Processed {len(calendar):,} calendar rows.")

    print("Dimension ETL completed successfully.")


# ================================
# 10. RUN DIMENSION LOAD PIPELINE
# ================================

if __name__ == "__main__":
    load_dimensions()
