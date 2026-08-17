from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.database import get_engine
from etl.transform.transform_weather import transform_weather


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEATHER_FILE = PROJECT_ROOT / "data" / "external" / "weather_history.csv"


def clear_weather_table() -> None:
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE fact_weather;")
        )

    print("Cleared fact_weather.")


def validate_weather(weather: pd.DataFrame) -> None:
    if weather["date"].isnull().any():
        raise ValueError(
            "Weather data contains invalid dates."
        )

    if weather["state_id"].isnull().any():
        raise ValueError(
            "Weather data contains missing state IDs."
        )

    duplicate_count = weather.duplicated(
        subset=["date", "state_id"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Weather data contains "
            f"{duplicate_count} duplicate keys."
        )

    if (weather["precipitation"].dropna() < 0).any():
        raise ValueError(
            "Weather data contains negative precipitation."
        )

    if (weather["snowfall"].dropna() < 0).any():
        raise ValueError(
            "Weather data contains negative snowfall."
        )


def load_weather() -> None:
    weather = pd.read_csv(
        WEATHER_FILE
    )

    weather = transform_weather(
        weather
    )

    validate_weather(
        weather
    )

    engine = get_engine()

    weather.to_sql(
        "fact_weather",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    print(
        f"Loaded {len(weather):,} weather rows."
    )


if __name__ == "__main__":
    clear_weather_table()
    load_weather()