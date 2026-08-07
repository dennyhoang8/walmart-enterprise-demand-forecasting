from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRED_FILE = PROJECT_ROOT / "data" / "external" / "fred_economic_data.csv"


SERIES_METADATA = pd.DataFrame(
    [
        {
            "series_id": "CPIAUCSL",
            "series_name": "Consumer Price Index",
            "frequency": "Monthly",
            "units": "Index",
        },
        {
            "series_id": "UNRATE",
            "series_name": "Unemployment Rate",
            "frequency": "Monthly",
            "units": "Percent",
        },
        {
            "series_id": "FEDFUNDS",
            "series_name": "Federal Funds Rate",
            "frequency": "Monthly",
            "units": "Percent",
        },
    ]
)


def clear_economic_tables() -> None:
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    fact_economic_indicator,
                    dim_economic_series
                CASCADE;
                """
            )
        )

    print("Cleared economic tables.")


def load_economic_series() -> None:
    engine = get_engine()

    SERIES_METADATA.to_sql(
        "dim_economic_series",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(SERIES_METADATA):,} economic series.")


def load_economic_indicators() -> None:
    economic_data = pd.read_csv(FRED_FILE)

    economic_data = economic_data.rename(
        columns={
            "date": "observation_date",
        }
    )

    economic_data["observation_date"] = pd.to_datetime(
        economic_data["observation_date"]
    ).dt.date

    economic_data = economic_data[
        [
            "series_id",
            "observation_date",
            "value",
        ]
    ].copy()

    if economic_data["series_id"].isnull().any():
        raise ValueError("Missing series IDs found.")

    if economic_data["observation_date"].isnull().any():
        raise ValueError("Invalid observation dates found.")

    duplicate_count = economic_data.duplicated(
        subset=["series_id", "observation_date"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count:,} duplicate economic records."
        )

    engine = get_engine()

    economic_data.to_sql(
        "fact_economic_indicator",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    print(f"Loaded {len(economic_data):,} economic observations.")


if __name__ == "__main__":
    clear_economic_tables()
    load_economic_series()
    load_economic_indicators()