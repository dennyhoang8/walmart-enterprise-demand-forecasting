# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, database connections,
# and economic-data transformation.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_economic import transform_economic


# ================================
# 2. FIND THE FRED CSV FILE
# Find the main project folder and point
# to the extracted FRED economic CSV.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRED_FILE = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "fred_economic_data.csv"
)


# ================================
# 3. CREATE ECONOMIC SERIES METADATA
# Build a small DataFrame that describes
# each economic series we are using.
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
# 4. CLEAR OLD ECONOMIC DATA
# Empty the economic dimension and fact tables
# before loading fresh data.
# ================================

def clear_economic_tables() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Start a database transaction.
    with engine.begin() as connection:

        # Run SQL that removes old economic data.
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

    # Confirm that the tables were cleared.
    print("Cleared economic tables.")


# ================================
# 5. LOAD ECONOMIC SERIES DIMENSION
# Load the descriptive information about each
# economic series into dim_economic_series.
# ================================

def load_economic_series() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the metadata DataFrame
    # into the economic series dimension table.
    SERIES_METADATA.to_sql(
        "dim_economic_series",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    # Show how many series were loaded.
    print(
        f"Loaded {len(SERIES_METADATA):,} economic series."
    )


# ================================
# 6. VALIDATE ECONOMIC DATA
# Check the transformed economic data for
# missing IDs, bad dates, and duplicates.
# ================================

def validate_economic_data(
    economic_data: pd.DataFrame,
) -> None:

    # Check whether any series IDs are missing.
    if economic_data["series_id"].isnull().any():
        raise ValueError(
            "Missing series IDs found."
        )

    # Check whether any observation dates are missing/invalid.
    if economic_data["observation_date"].isnull().any():
        raise ValueError(
            "Invalid observation dates found."
        )

    # Count duplicate rows based on
    # series ID + observation date.
    duplicate_count = economic_data.duplicated(
        subset=[
            "series_id",
            "observation_date",
        ]
    ).sum()

    # Stop the program if duplicate records exist.
    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count:,} "
            f"duplicate economic records."
        )


# ================================
# 7. LOAD ECONOMIC INDICATORS
# Read the extracted FRED CSV, transform it,
# validate it, and load it into the fact table.
# ================================

def load_economic_indicators() -> None:

    # Read the extracted FRED CSV into Pandas.
    economic_data = pd.read_csv(
        FRED_FILE
    )

    # Transform the raw FRED data into
    # the format expected by PostgreSQL.
    economic_data = transform_economic(
        economic_data
    )

    # Check the transformed data for problems
    # before loading it into the database.
    validate_economic_data(
        economic_data
    )

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the economic observations into
    # the fact_economic_indicator table.
    economic_data.to_sql(
        "fact_economic_indicator",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    # Show how many observations were loaded.
    print(
        f"Loaded {len(economic_data):,} "
        f"economic observations."
    )


# ================================
# 8. RUN THE ECONOMIC LOAD PIPELINE
# When this file is run directly:
# clear old data, load series metadata,
# then load the actual economic observations.
# ================================

if __name__ == "__main__":
    clear_economic_tables()
    load_economic_series()
    load_economic_indicators()