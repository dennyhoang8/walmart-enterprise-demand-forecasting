# ================================
# 1. IMPORT TOOLS
# Load Python tools needed for file paths,
# DataFrames, and U.S. holiday data.
# ================================

from pathlib import Path

import pandas as pd
import holidays


# ================================
# 2. SET FILE LOCATION
# Find the main project folder and decide
# where the extracted holiday data will be saved.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "us_holidays.csv"
)


# ================================
# 3. SET YEAR RANGE
# Choose which years of U.S. holiday data
# we want to extract.
# ================================

START_YEAR = 2011
END_YEAR = 2016


# ================================
# 4. EXTRACT U.S. HOLIDAYS
# This function gets U.S. holidays for our
# selected years and returns them as a DataFrame.
# ================================

def extract_holidays() -> pd.DataFrame:

    # Get U.S. holidays from 2011 through 2016
    us_holidays = holidays.US(
        years=range(START_YEAR, END_YEAR + 1)
    )

    # Convert the holiday data into a Pandas DataFrame
    # with one row for each holiday.
    holiday_data = pd.DataFrame(
        [
            {
                "date": date,
                "holiday_name": name,
            }
            for date, name in us_holidays.items()
        ]
    )

    # Convert the date column into proper dates
    # instead of leaving them as other Python objects/types.
    holiday_data["date"] = pd.to_datetime(
        holiday_data["date"]
    ).dt.date

    # Sort the holidays from earliest date to latest date.
    holiday_data = holiday_data.sort_values("date")

    # Give the completed holiday DataFrame back.
    return holiday_data


# ================================
# 5. RUN THE SCRIPT
# Only run this section when extract_holidays.py
# is executed directly.
# ================================

if __name__ == "__main__":

    # Run the extraction function and save
    # the returned DataFrame as holiday_data.
    holiday_data = extract_holidays()

    # Save the holiday DataFrame as a CSV file.
    holiday_data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # Preview the first 5 holiday rows.
    print(holiday_data.head())

    # Show how many holiday rows were saved.
    print(f"Saved {len(holiday_data):,} holiday rows.")