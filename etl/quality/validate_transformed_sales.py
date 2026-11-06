# ================================
# 1. IMPORT TOOLS
# Load database and SQL tools.
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE SALES DATA
# Check fact_sales after it has
# been loaded into PostgreSQL.
# ================================

def validate_sales() -> None:

    engine = get_engine()


    # ================================
    # 3. CHECK TABLE IS NOT EMPTY
    # Make sure sales data was actually loaded.
    # ================================

    with engine.connect() as connection:

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM fact_sales;")
        ).scalar()

        if row_count == 0:
            raise ValueError(
                "fact_sales is empty."
            )

        print(
            f"PASS: fact_sales contains "
            f"{row_count:,} rows"
        )


        # ================================
        # 4. CREATE VALIDATION CHECKS
        # Each SQL query counts bad rows.
        # A result of 0 means the check passed.
        # ================================

        checks = {

            # Sales cannot be negative.
            "negative_sales": """
                SELECT COUNT(*)
                FROM fact_sales
                WHERE units_sold < 0;
            """,

            # Required values cannot be missing.
            "missing_sales_values": """
                SELECT COUNT(*)
                FROM fact_sales
                WHERE date IS NULL
                   OR item_id IS NULL
                   OR store_id IS NULL
                   OR units_sold IS NULL;
            """,

            # date + item + store must be unique.
            "duplicate_sales_keys": """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        date,
                        item_id,
                        store_id
                    FROM fact_sales
                    GROUP BY
                        date,
                        item_id,
                        store_id
                    HAVING COUNT(*) > 1
                ) AS duplicates;
            """
        }


        # ================================
        # 5. RUN VALIDATION CHECKS
        # Run each SQL query one at a time.
        # ================================

        for name, sql in checks.items():

            result = connection.execute(
                text(sql)
            ).scalar()


            # ================================
            # 6. CHECK RESULT
            # 0 = PASS
            # Anything above 0 = FAIL
            # ================================

            if result != 0:
                raise ValueError(
                    f"{name} failed: "
                    f"{result:,} problems found."
                )

            print(f"PASS: {name}")


    # ================================
    # 7. CONFIRM SUCCESS
    # All validation checks passed.
    # ================================

    print(
        "\nAll fact_sales validation checks passed."
    )


# ================================
# 8. RUN VALIDATION
# Run validate_sales() when this
# file is executed directly.
# ================================

if __name__ == "__main__":
    validate_sales()