
# ================================
# 1. IMPORT TOOLS
# ================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_weather import transform_weather


# ================================
# 2. FIND THE WEATHER CSV FILE
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
# Remove existing rows before reloading.
# ================================

def clear_weather_table() -> None:

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE fact_weather;")
        )

    print("Cleared fact_weather.")


# ================================
# 4. VALIDATE WEATHER DATA
# Check transformed data before loading.
# ================================

def validate_weather(weather: pd.DataFrame) -> None:

    # Check for missing values.
    if weather.isnull().any().any():
        raise ValueError(
            "Weather data contains missing values."
        )

    # Check for duplicate date-state combinations.
    duplicate_count = weather.duplicated(
        subset=["date", "state_id"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Weather data contains "
            f"{duplicate_count} duplicate keys."
        )

    # Check for negative precipitation.
    if (weather["precipitation"] < 0).any():
        raise ValueError(
            "Weather data contains negative precipitation."
        )

    # Check for negative snowfall.
    if (weather["snowfall"] < 0).any():
        raise ValueError(
            "Weather data contains negative snowfall."
        )

    # Check for negative wind speeds.
    if (weather["wind_speed_max"] < 0).any():
        raise ValueError(
            "Weather data contains negative wind speeds."
        )

    # Check for inconsistent temperatures.
    if (
        weather["temperature_max"]
        < weather["temperature_min"]
    ).any():
        raise ValueError(
            "Maximum temperature is below minimum temperature."
        )


# ================================
# 5. LOAD WEATHER DATA
# Read, transform, validate, and load.
# ================================

def load_weather() -> None:

    # Confirm the CSV file exists.
    if not WEATHER_FILE.exists():
        raise FileNotFoundError(
            f"Weather file not found: {WEATHER_FILE}"
        )

    # Read the weather CSV.
    print("Reading Walmart weather dataset...")

    weather = pd.read_csv(
        WEATHER_FILE
    )

    # Transform the weather data.
    print("Transforming weather data...")

    weather = transform_weather(
        weather
    )

    # Validate the transformed data.
    print("Validating weather data...")

    validate_weather(
        weather
    )

    # Prevent an empty file from clearing the table.
    if weather.empty:
        raise ValueError(
            "Weather dataset is empty."
        )

    # Clear old data only after validation passes.
    clear_weather_table()

    # Connect to PostgreSQL.
    engine = get_engine()

    # Load weather data into PostgreSQL.
    print("Loading weather into PostgreSQL...")

    weather.to_sql(
        "fact_weather",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    # Confirm the number of loaded rows.
    print(
        f"Loaded {len(weather):,} weather rows."
    )

    print("Weather ETL completed successfully.")


# ================================
# 6. RUN THE WEATHER LOAD PIPELINE
# ================================

if __name__ == "__main__":
    load_weather()
