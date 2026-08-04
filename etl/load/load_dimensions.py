from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_products() -> None:
    sales = pd.read_csv(
        RAW_DATA_DIR / "sales_train_evaluation.csv",
        usecols=["item_id", "dept_id", "cat_id"],
    )

    products = (
        sales[["item_id", "dept_id", "cat_id"]]
        .drop_duplicates()
        .sort_values("item_id")
    )

    engine = get_engine()

    products.to_sql(
        "dim_product",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(products):,} products.")


def load_stores() -> None:
    sales = pd.read_csv(
        RAW_DATA_DIR / "sales_train_evaluation.csv",
        usecols=["store_id", "state_id"],
    )

    stores = (
        sales[["store_id", "state_id"]]
        .drop_duplicates()
        .sort_values("store_id")
    )

    engine = get_engine()

    stores.to_sql(
        "dim_store",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(stores):,} stores.")


def load_calendar() -> None:
    calendar = pd.read_csv(RAW_DATA_DIR / "calendar.csv")

    calendar["date"] = pd.to_datetime(calendar["date"]).dt.date

    calendar = calendar.rename(
        columns={
            "snap_CA": "snap_ca",
            "snap_TX": "snap_tx",
            "snap_WI": "snap_wi",
        }
    )

    for column in ["snap_ca", "snap_tx", "snap_wi"]:
        calendar[column] = calendar[column].astype(bool)

    engine = get_engine()

    calendar.to_sql(
        "dim_calendar",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(calendar):,} calendar rows.")


def clear_dimension_tables() -> None:
    engine = get_engine()

    with engine.begin() as connection:
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

    print("Cleared dimension tables.")


if __name__ == "__main__":
    clear_dimension_tables()
    load_products()
    load_stores()
    load_calendar()