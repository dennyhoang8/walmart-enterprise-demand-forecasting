
# ================================
# 1. IMPORT TOOLS
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE DIMENSION TABLES
# Check PostgreSQL after loading.
# ================================

def validate_dimensions() -> None:

    engine = get_engine()

    # ================================
    # 3. DEFINE VALIDATION CHECKS
    # Each query counts invalid records.
    # ================================

    checks = {

        # Check missing product values.
        "missing_product_values": """
            SELECT COUNT(*)
            FROM dim_product
            WHERE item_id IS NULL
               OR dept_id IS NULL
               OR cat_id IS NULL;
        """,

        # Check missing store values.
        "missing_store_values": """
            SELECT COUNT(*)
            FROM dim_store
            WHERE store_id IS NULL
               OR state_id IS NULL;
        """,

        # Check missing required calendar values.
        # Event names/types may be NULL.
        "missing_calendar_values": """
            SELECT COUNT(*)
            FROM dim_calendar
            WHERE date IS NULL
               OR wm_yr_wk IS NULL
               OR weekday IS NULL
               OR wday IS NULL
               OR month IS NULL
               OR year IS NULL
               OR d IS NULL
               OR snap_ca IS NULL
               OR snap_tx IS NULL
               OR snap_wi IS NULL;
        """,

        # Check duplicate product IDs.
        "duplicate_product_keys": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM dim_product
                GROUP BY item_id
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """,

        # Check duplicate store IDs.
        "duplicate_store_keys": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM dim_store
                GROUP BY store_id
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """,

        # Check duplicate calendar dates.
        "duplicate_calendar_dates": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM dim_calendar
                GROUP BY date
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """,

        # Check duplicate calendar day IDs.
        "duplicate_calendar_day_ids": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM dim_calendar
                GROUP BY d
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """
    }

    # ================================
    # 4. CONNECT TO POSTGRESQL
    # ================================

    with engine.connect() as connection:

        # Confirm all three tables contain data.
        for table_name in [
            "dim_product",
            "dim_store",
            "dim_calendar",
        ]:

            total_rows = connection.execute(
                text(f"SELECT COUNT(*) FROM {table_name};")
            ).scalar_one()

            if total_rows == 0:
                raise ValueError(
                    f"{table_name} is empty."
                )

            print(f"{table_name}: {total_rows:,} rows")

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

    print("All dimension validation checks passed.")


# ================================
# 8. RUN VALIDATION SCRIPT
# ================================

if __name__ == "__main__":
    validate_dimensions()
