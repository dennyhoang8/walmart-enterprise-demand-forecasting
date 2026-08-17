from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_dimensions import (
    transform_products,
    transform_stores,
    transform_calendar,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_products() -> None:
    sales = pd.read_csv(
        RAW_DATA_DIR / "sales_train_evaluation.csv",
        usecols=[
            "item_id",
            "dept_id",
            "cat_id",
        ],
    )

    products = transform_products(sales)

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
        usecols=[
            "store_id",
            "state_id",
        ],
    )

    stores = transform_stores(sales)

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
    calendar = pd.read_csv(
        RAW_DATA_DIR / "calendar.csv"
    )

    calendar = transform_calendar(calendar)

    engine = get_engine()

    calendar.to_sql(
        "dim_calendar",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(
        f"Loaded {len(calendar):,} calendar rows."
    )


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