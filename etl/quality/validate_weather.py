print(__file__)

from etl.database import get_engine
from sqlalchemy import text


def validate_weather() -> None:
    engine = get_engine()

    checks = {
        "missing_weather_keys": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE date IS NULL
               OR state_id IS NULL;
        """,

        "negative_precipitation": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE precipitation < 0;
        """,

        "negative_snowfall": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE snowfall < 0;
        """
    }

    with engine.connect() as connection:
        for name, sql in checks.items():
            result = connection.execute(text(sql)).scalar()

            if result != 0:
                raise ValueError(f"{name} failed: {result}")

            print(f"PASS: {name}")


if __name__ == "__main__":
    validate_weather()