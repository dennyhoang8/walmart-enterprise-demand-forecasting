from etl.database import get_engine
from sqlalchemy import text


def validate_economic() -> None:
    engine = get_engine()

    checks = {
        "missing_series_ids": """
            SELECT COUNT(*)
            FROM fact_economic_indicator
            WHERE series_id IS NULL;
        """,

        "missing_observation_dates": """
            SELECT COUNT(*)
            FROM fact_economic_indicator
            WHERE observation_date IS NULL;
        """,

        "duplicate_economic_keys": """
            SELECT COUNT(*)
            FROM (
                SELECT series_id, observation_date
                FROM fact_economic_indicator
                GROUP BY series_id, observation_date
                HAVING COUNT(*) > 1
            ) x;
        """
    }

    with engine.connect() as connection:
        for name, sql in checks.items():
            result = connection.execute(text(sql)).scalar()

            if result != 0:
                raise ValueError(f"{name} failed: {result}")

            print(f"PASS: {name}")


if __name__ == "__main__":
    validate_economic()