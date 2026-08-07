from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def clear_fact_prices() -> None:
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE fact_prices;"))

    print("Cleared fact_prices.")


def load_prices() -> None:
    prices = pd.read_csv(RAW_DATA_DIR / "sell_prices.csv")

    prices = prices[
        ["store_id", "item_id", "wm_yr_wk", "sell_price"]
    ].copy()

    if prices.isnull().any().any():
        raise ValueError("fact_prices contains missing values.")

    if (prices["sell_price"] <= 0).any():
        raise ValueError("fact_prices contains non-positive prices.")

    duplicate_count = prices.duplicated(
        subset=["store_id", "item_id", "wm_yr_wk"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"fact_prices contains {duplicate_count} duplicate keys."
        )

    engine = get_engine()

    prices.to_sql(
        "fact_prices",
        engine,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )

    print(f"Loaded {len(prices):,} price rows.")


if __name__ == "__main__":
    clear_fact_prices()
    load_prices()