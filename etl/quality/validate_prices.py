
# ==========================================
# 1. IMPORT TOOLS
# Import the database connection function
# and SQLAlchemy's SQL text utility.
# ==========================================

from etl.database import get_engine
from sqlalchemy import text


# ==========================================
# 2. DEFINE PRICE VALIDATION FUNCTION
# Check the fact_prices table in PostgreSQL
# after the pricing ETL has finished loading.
# ==========================================

def validate_prices() -> None:

    # Get the PostgreSQL database engine.
    engine = get_engine()

    # ==========================================
    # 3. DEFINE SQL VALIDATION CHECKS
    # Each query counts problematic records.
    # A successful check must return zero.
    # ==========================================

    checks = {

        # Check for zero or negative selling prices.
        "negative_or_zero_prices": """
            SELECT COUNT(*)
            FROM fact_prices
            WHERE sell_price <= 0;
        """,

        # Check for missing required values.
        "missing_price_values": """
            SELECT COUNT(*)
            FROM fact_prices
            WHERE store_id IS NULL
               OR item_id IS NULL
               OR wm_yr_wk IS NULL
               OR sell_price IS NULL;
        """,

        # Count extra duplicate records.
        # Each store-item-week combination
        # should appear only once.
        "duplicate_price_keys": """
            SELECT COALESCE(
                SUM(duplicate_count - 1), 0
            )
            FROM (
                SELECT COUNT(*) AS duplicate_count
                FROM fact_prices
                GROUP BY store_id, item_id, wm_yr_wk
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """
    }

    # ==========================================
    # 4. CONNECT TO POSTGRESQL
    # Open a connection to execute SQL queries.
    # ==========================================

    with engine.connect() as connection:

        # First, confirm the table contains data.
        total_rows = connection.execute(
            text("SELECT COUNT(*) FROM fact_prices;")
        ).scalar_one()

        if total_rows == 0:
            raise ValueError(
                "fact_prices is empty. No price data was loaded."
            )

        print(f"Total price rows: {total_rows:,}")

        # ==========================================
        # 5. RUN ALL VALIDATION CHECKS
        # Loop through the dictionary of SQL tests.
        # ==========================================

        for name, sql in checks.items():

            # Execute SQL and retrieve its count.
            result = connection.execute(
                text(sql)
            ).scalar_one()

            # ==========================================
            # 6. VALIDATE EACH RESULT
            # Zero means no problems were found.
            # ==========================================

            if result != 0:
                raise ValueError(
                    f"FAIL: {name} - {result:,} invalid records."
                )

            print(f"PASS: {name}")

    # ==========================================
    # 7. CONFIRM COMPLETION
    # All validation checks passed.
    # ==========================================

    print("All price validation checks passed.")


# ==========================================
# 8. START THE VALIDATION SCRIPT
# Execute when run as the main Python module.
# ==========================================

if __name__ == "__main__":
    validate_prices()
