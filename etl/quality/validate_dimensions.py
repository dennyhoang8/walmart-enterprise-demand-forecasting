# ================================
# 1. IMPORT TOOLS
# Load our database connection function
# and SQLAlchemy's tool for running SQL text.
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE DIMENSION TABLES
# Check the dimension tables in PostgreSQL
# for missing keys and duplicate keys.
# ================================

def validate_dimensions() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()


    # ================================
    # 3. CREATE VALIDATION CHECKS
    # Store each validation test as:
    # check name → SQL query
    # ================================

    checks = {

        # Count products that are missing item_id.
        "dim_product_null_keys": """
            SELECT COUNT(*)
            FROM dim_product
            WHERE item_id IS NULL;
        """,

        # Count stores that are missing store_id.
        "dim_store_null_keys": """
            SELECT COUNT(*)
            FROM dim_store
            WHERE store_id IS NULL;
        """,

        # Count calendar rows that are missing dates.
        "dim_calendar_null_dates": """
            SELECT COUNT(*)
            FROM dim_calendar
            WHERE date IS NULL;
        """,

        # Count item IDs that appear more than once.
        "dim_product_duplicates": """
            SELECT COUNT(*)
            FROM (
                SELECT item_id
                FROM dim_product
                GROUP BY item_id
                HAVING COUNT(*) > 1
            ) x;
        """,

        # Count store IDs that appear more than once.
        "dim_store_duplicates": """
            SELECT COUNT(*)
            FROM (
                SELECT store_id
                FROM dim_store
                GROUP BY store_id
                HAVING COUNT(*) > 1
            ) x;
        """,
    }


    # ================================
    # 4. CONNECT TO DATABASE
    # Open a connection so Python can run
    # each SQL validation query.
    # ================================

    with engine.connect() as connection:


        # ================================
        # 5. LOOP THROUGH EVERY CHECK
        # Take each check name and SQL query
        # from the checks dictionary.
        # ================================

        for name, sql in checks.items():

            # Run the SQL query and get
            # the single number it returns.
            result = connection.execute(
                text(sql)
            ).scalar()


            # ================================
            # 6. CHECK THE RESULT
            # Every validation query should return 0.
            # Anything above 0 means bad data exists.
            # ================================

            if result != 0:

                # Stop the program and report
                # which validation test failed.
                raise ValueError(
                    f"{name} failed: {result}"
                )


            # If result was 0, the test passed.
            print(f"PASS: {name}")


# ================================
# 7. RUN THE VALIDATION SCRIPT
# When this file is run directly,
# run all dimension validation checks.
# ================================

if __name__ == "__main__":
    validate_dimensions()