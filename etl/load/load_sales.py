from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SALES_FILE = RAW_DATA_DIR / "sales_train_evaluation.csv"
CALENDAR_FILE = RAW_DATA_DIR / "calendar.csv"

TEST_STORE = "CA_1"


def clear_fact_sales() -> None:
    """Remove existing sales rows before a test load."""
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE fact_sales;"))

    print("Cleared fact_sales.")


def load_sales_for_store(store_id: str) -> None:
    """Transform one store from wide format to long format and load it."""

    sales = pd.read_csv(SALES_FILE)
    calendar = pd.read_csv(
        CALENDAR_FILE,
        usecols=["d", "date"],
    )

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()

    id_columns = [
        "item_id",
        "store_id",
    ]

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]

    long_sales = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )

    long_sales = long_sales.merge(
        calendar,
        on="d",
        how="left",
        validate="many_to_one",
    )

    long_sales["date"] = pd.to_datetime(
        long_sales["date"]
    ).dt.date

    fact_sales = long_sales[
        [
            "date",
            "item_id",
            "store_id",
            "units_sold",
        ]
    ].copy()

    if fact_sales["date"].isna().any():
        raise ValueError("Some sales rows could not be matched to a date.")

    if (fact_sales["units_sold"] < 0).any():
        raise ValueError("Negative unit sales were found.")

    duplicate_count = fact_sales.duplicated(
        subset=["date", "item_id", "store_id"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count:,} duplicate sales keys."
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


if __name__ == "__main__":
    clear_fact_sales()
    load_sales_for_store(TEST_STORE)