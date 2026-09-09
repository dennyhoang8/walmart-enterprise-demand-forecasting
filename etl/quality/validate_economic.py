# ================================
# 1. IMPORT TOOLS
# Load our database connection function
# and SQLAlchemy's tool for running SQL commands.
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 2. VALIDATE ECONOMIC DATA
# Check the economic fact table in PostgreSQL
# for missing IDs, missing dates, and duplicates.
# ================================

def validate_economic() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()


    # ================================
    # 3. CREATE VALIDATION CHECKS
    # Store each validation test as:
    # check name → SQL query.
    # Each query counts how many problems exist.
    # ================================

    checks = {

        # Count economic rows that are
        # missing a series ID.
        "missing_series_ids": """
            SELECT COUNT(*)
            FROM fact_economic_indicator
            WHERE series_id IS NULL;
        """,

        # Count economic rows that are
        # missing an observation date.
        "missing_observation_dates": """
            SELECT COUNT(*)
            FROM fact_economic_indicator
            WHERE observation_date IS NULL;
        """,

        # Count duplicate economic records.
        # Each series should only have ONE
        # observation for each observation date.
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


    # ================================
    # 4. CONNECT TO THE DATABASE
    # Open a connection so Python can run
    # the SQL validation queries.
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
            # Anything other than 0 means bad data exists.
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
# run all economic-data validation checks.
# ================================

if __name__ == "__main__":
    validate_economic()