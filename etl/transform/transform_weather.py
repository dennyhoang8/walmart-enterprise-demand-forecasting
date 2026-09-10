# ================================
# 1. IMPORT TOOLS
# Load Pandas so we can work with
# and transform the weather DataFrame.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM WEATHER DATA
# Take the raw Open-Meteo weather data
# and prepare it for fact_weather.
# ================================

def transform_weather(
    weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw weather API data into the
    warehouse-ready fact_weather format.
    """


    # ================================
    # 3. DEFINE REQUIRED COLUMNS
    # These columns must exist in the
    # extracted weather dataset.
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
    # Stop early if the extracted weather
    # schema changes or a column is missing.
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
    # Work on a separate copy so the
    # original DataFrame is not modified.
    # ================================

    weather = weather.copy()


    # ================================
    # 6. RENAME WEATHER COLUMNS
    # Change the original API column names
    # into simpler database column names.
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
    # Convert the weather date from text
    # into a proper Python date value.
    # ================================

    weather["date"] = pd.to_datetime(
        weather["date"],
        errors="raise",
    ).dt.date


    # ================================
    # 8. CONVERT WEATHER VALUES TO NUMERIC
    # Make sure all weather measurements are
    # stored using numeric data types.
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
    # These are the exact columns required
    # by fact_weather.
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
    # Select the warehouse-ready columns.
    # ================================

    weather = weather[
        expected_columns
    ].copy()


    # ================================
    # 11. RETURN TRANSFORMED DATA
    # Give the finished weather DataFrame
    # back to the code that called this function.
    # ================================

    return weather