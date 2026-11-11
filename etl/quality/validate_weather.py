
# ================================
# 1. IMPORT TOOLS
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE WEATHER DATA
# Check fact_weather after loading.
# ================================

def validate_weather() -> None:

    engine = get_engine()

    # ================================
    # 3. DEFINE VALIDATION CHECKS
    # Each SQL query counts invalid records.
    # ================================

    checks = {

        # Check missing required values.
        "missing_weather_values": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE date IS NULL
               OR state_id IS NULL
               OR temperature_max IS NULL
               OR temperature_min IS NULL
               OR precipitation IS NULL
               OR snowfall IS NULL
               OR wind_speed_max IS NULL;
        """,

        # Check negative precipitation.
        "negative_precipitation": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE precipitation < 0;
        """,

        # Check negative snowfall.
        "negative_snowfall": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE snowfall < 0;
        """,

        # Check negative wind speeds.
        "negative_wind_speed": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE wind_speed_max < 0;
        """,

        # Check inconsistent temperatures.
        "invalid_temperature_range": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE temperature_max < temperature_min;
        """,

        # Check duplicate state-date combinations.
        "duplicate_weather_keys": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM fact_weather
                GROUP BY date, state_id
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """
    }

    # ================================
    # 4. CONNECT TO POSTGRESQL
    # ================================

    with engine.connect() as connection:

        # Confirm the table contains data.
        total_rows = connection.execute(
            text("SELECT COUNT(*) FROM fact_weather;")
        ).scalar_one()

        if total_rows == 0:
            raise ValueError(
                "fact_weather is empty. No weather data was loaded."
            )

        print(f"Total weather rows: {total_rows:,}")

        # ================================
        # 5. RUN VALIDATION CHECKS
        # ================================

        for name, sql in checks.items():

            result = connection.execute(
                text(sql)
            ).scalar_one()

            # ================================
            # 6. CHECK EACH RESULT
            # ================================

            if result != 0:
                raise ValueError(
                    f"FAIL: {name} - {result:,} invalid records."
                )

            print(f"PASS: {name}")

    # ================================
    # 7. CONFIRM COMPLETION
    # ================================

    print("All weather validation checks passed.")


# ================================
# 8. RUN VALIDATION SCRIPT
# ================================

if __name__ == "__main__":
    validate_weather()
