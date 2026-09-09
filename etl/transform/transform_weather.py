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

def transform_weather(weather: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw weather API data into the
    warehouse-ready fact_weather format.
    """


    # ================================
    # 3. RENAME WEATHER COLUMNS
    # Change the original API column names
    # into simpler names used by our database.
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
    # 4. CONVERT DATE FORMAT
    # Convert the date column into
    # proper Python date values.
    # ================================

    weather["date"] = pd.to_datetime(
        weather["date"]
    ).dt.date


    # ================================
    # 5. DEFINE NEEDED COLUMNS
    # Create a list of the exact columns
    # that fact_weather needs.
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
    # 6. KEEP ONLY NEEDED COLUMNS
    # Select the expected columns and make
    # a separate copy of the DataFrame.
    # ================================

    weather = weather[
        expected_columns
    ].copy()


    # ================================
    # 7. RETURN TRANSFORMED DATA
    # Give the finished weather DataFrame
    # back to the code that called this function.
    # ================================

    return weather