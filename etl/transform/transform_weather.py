import pandas as pd


def transform_weather(weather: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw weather API data into the
    warehouse-ready fact_weather format.
    """

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

    weather["date"] = pd.to_datetime(
        weather["date"]
    ).dt.date

    expected_columns = [
        "date",
        "state_id",
        "temperature_max",
        "temperature_min",
        "precipitation",
        "snowfall",
        "wind_speed_max",
    ]

    weather = weather[
        expected_columns
    ].copy()

    return weather