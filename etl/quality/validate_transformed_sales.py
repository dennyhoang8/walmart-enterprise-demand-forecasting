# ================================
# 1. IMPORT TOOLS
# Load our database connection function
# and SQLAlchemy's tool for running SQL commands.
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE SALES DATA
# Check the fact_sales table in PostgreSQL
# for negative sales, missing keys, and duplicates.
# ================================

def validate_sales() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()


    # ================================
    # 3. CREATE VALIDATION CHECKS
    # Store each validation test as:
    # check name → SQL query.
    # Each query counts how many problems exist.
    # ================================

    checks = {

        # Count sales rows where units sold
        # is below zero.
        "negative_sales": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE units_sold < 0;
        """,

        # Count sales rows where any important
        # identifying key is missing.
        "missing_sales_keys": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE date IS NULL
               OR item_id IS NULL
               OR store_id IS NULL;
        """,

        # Count duplicate sales records.
        # One sales row should be unique for:
        # date + item + store.
        "duplicate_sales_keys": """
            SELECT COUNT(*)
            FROM (
                SELECT date, item_id, store_id
                FROM fact_sales
                GROUP BY date, item_id, store_id
                HAVING COUNT(*) > 1
            ) x;
        """
    }


    # ================================
    # 4. CONNECT TO THE DATABASE
    # Open a connection so Python can run
    # each SQL validation query.
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
                # which validation check failed.
                raise ValueError(
                    f"{name} failed: {result}"
                )


            # If result equals 0,
            # this validation check passed.
            print(f"PASS: {name}")


# ================================
# 7. RUN THE VALIDATION SCRIPT
# When this file is run directly,
# run all sales validation checks.
# ================================

if __name__ == "__main__":
    validate_sales()