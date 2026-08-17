from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_sales import transform_sales


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SALES_FILE = RAW_DATA_DIR / "sales_train_evaluation.csv"
CALENDAR_FILE = RAW_DATA_DIR / "calendar.csv"

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


def clear_fact_sales() -> None:
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE fact_sales;")
        )

    print("Cleared fact_sales.")


def validate_sales(fact_sales: pd.DataFrame, store_id: str) -> None:
    if fact_sales["date"].isna().any():
        raise ValueError(
            f"{store_id}: Some sales rows could not be matched to a date."
        )

    if fact_sales["units_sold"].isna().any():
        raise ValueError(
            f"{store_id}: Missing unit sales were found."
        )

    if (fact_sales["units_sold"] < 0).any():
        raise ValueError(
            f"{store_id}: Negative unit sales were found."
        )

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


def load_sales_for_store(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> None:
    print(f"\nProcessing store: {store_id}")

    fact_sales = transform_sales(
        sales=sales,
        calendar=calendar,
        store_id=store_id,
    )

    validate_sales(
        fact_sales=fact_sales,
        store_id=store_id,
    )

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


def load_all_sales() -> None:
    print("Reading Walmart sales dataset...")

    sales = pd.read_csv(SALES_FILE)

    calendar = pd.read_csv(
        CALENDAR_FILE,
        usecols=[
            "d",
            "date",
        ],
    )

    clear_fact_sales()

    total_stores = len(STORES)

    for index, store_id in enumerate(
        STORES,
        start=1,
    ):
        print(
            f"\n[{index}/{total_stores}] "
            f"Starting {store_id}"
        )

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


if __name__ == "__main__":
    load_all_sales()