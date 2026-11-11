
# ================================
# 1. IMPORT TOOLS
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE ECONOMIC DATA
# Check PostgreSQL after loading.
# ================================

def validate_economic() -> None:

    engine = get_engine()

    # ================================
    # 3. DEFINE VALIDATION CHECKS
    # Each query counts invalid records.
    # ================================

    checks = {

        # Check missing required values.
        "missing_economic_values": """
            SELECT COUNT(*)
            FROM fact_economic_indicator
            WHERE series_id IS NULL
               OR observation_date IS NULL
               OR value IS NULL;
        """,

        # Check duplicate series-date combinations.
        "duplicate_economic_keys": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM fact_economic_indicator
                GROUP BY series_id, observation_date
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """,

        # Check for economic series without metadata.
        "unknown_series_ids": """
            SELECT COUNT(*)
            FROM fact_economic_indicator AS f
            LEFT JOIN dim_economic_series AS d
                ON f.series_id = d.series_id
            WHERE d.series_id IS NULL;
        """,

        # Check for non-finite numeric values.
        "invalid_economic_values": """
            SELECT COUNT(*)
            FROM fact_economic_indicator
            WHERE value::text IN (
                'NaN', 'Infinity', '-Infinity'
            );
        """
    }

    # ================================
    # 4. CONNECT TO POSTGRESQL
    # ================================

    with engine.connect() as connection:

        # Confirm economic observations exist.
        total_rows = connection.execute(
            text(
                "SELECT COUNT(*) FROM fact_economic_indicator;"
            )
        ).scalar_one()

        if total_rows == 0:
            raise ValueError(
                "fact_economic_indicator is empty."
            )

        print(f"Total economic observations: {total_rows:,}")

        # Confirm economic series metadata exists.
        series_count = connection.execute(
            text(
                "SELECT COUNT(*) FROM dim_economic_series;"
            )
        ).scalar_one()

        if series_count == 0:
            raise ValueError(
                "dim_economic_series is empty."
            )

        print(f"Total economic series: {series_count:,}")

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

    print("All economic validation checks passed.")


# ================================
# 8. RUN VALIDATION SCRIPT
# ================================

if __name__ == "__main__":
    validate_economic()
