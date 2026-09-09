# ================================
# 1. SHOW CURRENT FILE LOCATION
# Print the path of the Python file that
# is currently being executed.
# ================================

print(__file__)


# ================================
# 2. IMPORT TOOLS
# Load our database connection function
# and SQLAlchemy's tool for running SQL commands.
# ================================

from etl.database import get_engine
from sqlalchemy import text


# ================================
# 3. VALIDATE WEATHER DATA
# Check the fact_weather table in PostgreSQL
# for missing keys and impossible weather values.
# ================================

def validate_weather() -> None:

    # Connect to PostgreSQL.
    engine = get_engine()


    # ================================
    # 4. CREATE VALIDATION CHECKS
    # Store each validation test as:
    # check name → SQL query.
    # Each query counts how many problems exist.
    # ================================

    checks = {

        # Count weather rows that are missing
        # either a date or state ID.
        "missing_weather_keys": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE date IS NULL
               OR state_id IS NULL;
        """,

        # Count weather rows where
        # precipitation is below zero.
        "negative_precipitation": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE precipitation < 0;
        """,

        # Count weather rows where
        # snowfall is below zero.
        "negative_snowfall": """
            SELECT COUNT(*)
            FROM fact_weather
            WHERE snowfall < 0;
        """
    }


    # ================================
    # 5. CONNECT TO THE DATABASE
    # Open a connection so Python can run
    # each SQL validation query.
    # ================================

    with engine.connect() as connection:


        # ================================
        # 6. RUN EVERY VALIDATION CHECK
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
            # 7. CHECK THE RESULT
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
# 8. RUN THE VALIDATION SCRIPT
# When this file is run directly,
# run all weather validation checks.
# ================================

if __name__ == "__main__":
    validate_weather()