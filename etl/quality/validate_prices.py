# ================================
# 1. IMPORT TOOLS
# Load our database connection function
# and SQLAlchemy's tool for running SQL commands.
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE PRICE DATA
# Check the fact_prices table in PostgreSQL
# for bad prices, duplicates, and missing keys.
# ================================

def validate_prices() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()


    # ================================
    # 3. CREATE VALIDATION CHECKS
    # Store each validation test as:
    # check name → SQL query.
    # Each query counts how many problems exist.
    # ================================

    checks = {

        # Count prices that are zero or negative.
        "negative_or_zero_prices": """
            SELECT COUNT(*)
            FROM fact_prices
            WHERE sell_price <= 0;
        """,

        # Count duplicate price records.
        # One price row should be unique for:
        # store + item + Walmart year/week.
        "duplicate_price_keys": """
            SELECT COUNT(*)
            FROM (
                SELECT store_id, item_id, wm_yr_wk
                FROM fact_prices
                GROUP BY store_id, item_id, wm_yr_wk
                HAVING COUNT(*) > 1
            ) x;
        """,

        # Count rows where one of the important
        # price keys is missing.
        "missing_price_keys": """
            SELECT COUNT(*)
            FROM fact_prices
            WHERE store_id IS NULL
               OR item_id IS NULL
               OR wm_yr_wk IS NULL;
        """
    }


    # ================================
    # 4. CONNECT TO THE DATABASE
    # Open a connection so Python can run
    # the SQL validation checks.
    # ================================

    with engine.connect() as connection:


        # ================================
        # 5. RUN EVERY VALIDATION CHECK
        # Loop through the checks dictionary
        # and run each SQL query one at a time.
        # ================================

        for name, sql in checks.items():

            # Run the SQL query and get
            # the single number returned by COUNT(*).
            result = connection.execute(
                text(sql)
            ).scalar()


            # ================================
            # 6. CHECK THE RESULT
            # Every validation query should return 0.
            # Anything else means bad data exists.
            # ================================

            if result != 0:

                # Stop the program and show
                # which validation test failed.
                raise ValueError(
                    f"{name} failed: {result}"
                )


            # If result equals 0,
            # this check passed.
            print(f"PASS: {name}")


# ================================
# 7. RUN THE VALIDATION SCRIPT
# When this file is run directly,
# run all price validation checks.
# ================================

if __name__ == "__main__":
    validate_prices()