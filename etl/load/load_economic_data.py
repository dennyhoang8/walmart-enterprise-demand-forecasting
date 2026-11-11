
# ================================
# 1. IMPORT TOOLS
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_economic import transform_economic


# ================================
# 2. FIND THE FRED CSV FILE
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRED_FILE = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "fred_economic_data.csv"
)


# ================================
# 3. DEFINE ECONOMIC SERIES METADATA
# ================================

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


# ================================
# 4. VALIDATE ECONOMIC DATA
# ================================

def validate_economic_data(
    economic_data: pd.DataFrame,
) -> None:

    # Check for missing values.
    if economic_data.isnull().any().any():
        raise ValueError(
            "Economic data contains missing values."
        )

    # Check for duplicate records.
    duplicate_count = economic_data.duplicated(
        subset=["series_id", "observation_date"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count:,} duplicate economic records."
        )

    # Check for unexpected series IDs.
    valid_series = set(SERIES_METADATA["series_id"])

    invalid_series = set(
        economic_data["series_id"]
    ) - valid_series

    if invalid_series:
        raise ValueError(
            f"Unknown economic series: {sorted(invalid_series)}"
        )


# ================================
# 5. LOAD ECONOMIC DATA
# Read, transform, validate, and load.
# ================================

def load_economic_data() -> None:

    # Confirm the CSV file exists.
    if not FRED_FILE.exists():
        raise FileNotFoundError(
            f"FRED file not found: {FRED_FILE}"
        )

    # Read the FRED CSV.
    print("Reading FRED economic dataset...")

    economic_data = pd.read_csv(FRED_FILE)

    # Transform the economic data.
    print("Transforming economic data...")

    economic_data = transform_economic(
        economic_data
    )

    # Validate before changing PostgreSQL.
    print("Validating economic data...")

    validate_economic_data(
        economic_data
    )

    if economic_data.empty:
        raise ValueError(
            "Economic dataset is empty."
        )

    # Connect to PostgreSQL.
    engine = get_engine()

    # ================================
    # 6. REPLACE ECONOMIC TABLE DATA
    # Clear and reload within one transaction.
    # ================================

    print("Loading economic data into PostgreSQL...")

    with engine.begin() as connection:

        # Clear the fact and dimension tables.
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    fact_economic_indicator,
                    dim_economic_series;
                """
            )
        )

        # Load series metadata first.
        SERIES_METADATA.to_sql(
            "dim_economic_series",
            connection,
            if_exists="append",
            index=False,
            method="multi",
        )

        # Load economic observations second.
        economic_data.to_sql(
            "fact_economic_indicator",
            connection,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )

    # ================================
    # 7. CONFIRM COMPLETION
    # ================================

    print(
        f"Loaded {len(SERIES_METADATA):,} economic series."
    )

    print(
        f"Loaded {len(economic_data):,} economic observations."
    )

    print("Economic ETL completed successfully.")


# ================================
# 8. RUN ECONOMIC LOAD PIPELINE
# ================================

if __name__ == "__main__":
    load_economic_data()
