
# ================================
# 1. IMPORT TOOLS
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM WEATHER DATA
# Prepare Open-Meteo data for fact_weather.
# ================================

def transform_weather(
    weather: pd.DataFrame,
) -> pd.DataFrame:

    # ================================
    # 3. DEFINE REQUIRED COLUMNS
    # ================================

    required_columns = [
        "time",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "snowfall_sum",
        "wind_speed_10m_max",
        "state_id",
    ]

    # ================================
    # 4. CHECK REQUIRED COLUMNS
    # ================================

    missing_columns = [
        column
        for column in required_columns
        if column not in weather.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing weather columns: {missing_columns}"
        )

    # ================================
    # 5. COPY THE DATA
    # Avoid modifying the original DataFrame.
    # ================================

    weather = weather[required_columns].copy()

    # ================================
    # 6. RENAME WEATHER COLUMNS
    # Match PostgreSQL column names.
    # ================================

    weather = weather.rename(
        columns={
            "time": "date",
            "temperature_2m_max": "temperature_max",
            "temperature_2m_min": "temperature_min",
            "precipitation_sum": "precipitation",
            "snowfall_sum": "snowfall",
            "wind_speed_10m_max": "wind_speed_max",
        }
    )

    # ================================
    # 7. CONVERT DATE FORMAT
    # ================================

    weather["date"] = pd.to_datetime(
        weather["date"],
        errors="raise",
    ).dt.date

    # ================================
    # 8. CONVERT WEATHER VALUES TO NUMERIC
    # ================================

    numeric_columns = [
        "temperature_max",
        "temperature_min",
        "precipitation",
        "snowfall",
        "wind_speed_max",
    ]

    for column in numeric_columns:
        weather[column] = pd.to_numeric(
            weather[column],
            errors="raise",
        )

    # ================================
    # 9. DEFINE FINAL COLUMNS
    # ================================

    expected_columns = [
        "date",
        "state_id",
        "temperature_max",
        "temperature_min",
        "precipitation",
        "snowfall",
        "wind_speed_max",
    ]

    # ================================
    # 10. KEEP ONLY NEEDED COLUMNS
    # ================================

    weather = weather[expected_columns].copy()

    # ================================
    # 11. CHECK MISSING VALUES
    # ================================

    if weather.isnull().any().any():
        raise ValueError(
            "Weather data contains missing values."
        )

    # ================================
    # 12. CHECK DUPLICATE RECORDS
    # Each state should have one record per date.
    # ================================

    duplicate_count = weather.duplicated(
        subset=["date", "state_id"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count} duplicate weather records."
        )

    # ================================
    # 13. CHECK INVALID WEATHER VALUES
    # ================================

    if (weather["precipitation"] < 0).any():
        raise ValueError(
            "Weather data contains negative precipitation."
        )

    if (weather["snowfall"] < 0).any():
        raise ValueError(
            "Weather data contains negative snowfall."
        )

    if (weather["wind_speed_max"] < 0).any():
        raise ValueError(
            "Weather data contains negative wind speeds."
        )

    if (
        weather["temperature_max"] <
        weather["temperature_min"]
    ).any():
        raise ValueError(
            "Maximum temperature is below minimum temperature."
        )

    # ================================
    # 14. RETURN TRANSFORMED DATA
    # ================================

    return weather
