# ================================
# 1. IMPORT TOOLS
# Load tools for file paths, Pandas,
# SQL commands, database connections,
# and weather-data transformation.
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_weather import transform_weather


# ================================
# 2. FIND THE WEATHER CSV FILE
# Find the main project folder and point
# Python to the extracted weather CSV.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

WEATHER_FILE = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "weather_history.csv"
)


# ================================
# 3. CLEAR OLD WEATHER DATA
# Empty fact_weather before loading fresh
# weather rows so duplicates are not created.
# ================================

def clear_weather_table() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()

    # Start a database transaction.
    with engine.begin() as connection:

        # Remove all existing rows
        # from fact_weather.
        connection.execute(
            text("TRUNCATE TABLE fact_weather;")
        )

    # Confirm the table was cleared.
    print("Cleared fact_weather.")


# ================================
# 4. VALIDATE WEATHER DATA
# Check for invalid dates, missing state IDs,
# duplicate keys, and impossible negative values.
# ================================

def validate_weather(weather: pd.DataFrame) -> None:

    # Check whether any dates are missing.
    if weather["date"].isnull().any():
        raise ValueError(
            "Weather data contains invalid dates."
        )

    # Check whether any state IDs are missing.
    if weather["state_id"].isnull().any():
        raise ValueError(
            "Weather data contains missing state IDs."
        )

    # Count duplicate rows based on:
    # date + state_id
    duplicate_count = weather.duplicated(
        subset=["date", "state_id"]
    ).sum()

    # Stop if duplicate weather keys exist.
    if duplicate_count > 0:
        raise ValueError(
            f"Weather data contains "
            f"{duplicate_count} duplicate keys."
        )

    # Ignore missing precipitation values,
    # then check whether any remaining values
    # are negative.
    if (weather["precipitation"].dropna() < 0).any():
        raise ValueError(
            "Weather data contains negative precipitation."
        )

    # Ignore missing snowfall values,
    # then check whether any remaining values
    # are negative.
    if (weather["snowfall"].dropna() < 0).any():
        raise ValueError(
            "Weather data contains negative snowfall."
        )


# ================================
# 5. LOAD WEATHER DATA
# Read the weather CSV, transform it,
# validate it, then load it into fact_weather.
# ================================

def load_weather() -> None:

    # Read the extracted weather CSV
    # into a Pandas DataFrame.
    weather = pd.read_csv(
        WEATHER_FILE
    )

    # Clean and prepare the weather data
    # for the database.
    weather = transform_weather(
        weather
    )

    # Check the transformed data
    # before loading it into PostgreSQL.
    validate_weather(
        weather
    )

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load the finished weather DataFrame
    # into the fact_weather table.
    weather.to_sql(
        "fact_weather",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    # Show how many weather rows were loaded.
    print(
        f"Loaded {len(weather):,} weather rows."
    )


# ================================
# 6. RUN THE WEATHER LOAD PIPELINE
# When this file is run directly:
# clear old weather rows first,
# then load fresh weather data.
# ================================

if __name__ == "__main__":
    clear_weather_table()
    load_weather()