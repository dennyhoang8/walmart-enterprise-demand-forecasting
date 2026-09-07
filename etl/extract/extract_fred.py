# ================================
# 1. IMPORT TOOLS
# Load Python libraries needed for environment variables,
# file paths, DataFrames, and API requests.
# ================================

import os
from dotenv import load_dotenv
from pathlib import Path

import pandas as pd
import requests


# ================================
# 2. LOAD API KEY
# Load secret values from the .env file
# and get the FRED API key.
# ================================

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")


# ================================
# 3. SET FILE LOCATION
# Find the main project folder and decide
# where the extracted FRED data will be saved.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "fred_economic_data.csv"
)


# ================================
# 4. SET DATE RANGE
# Only request economic data covering
# the historical period used in the project.
# ================================

START_DATE = "2011-01-29"
END_DATE = "2016-06-19"


# ================================
# 5. CHOOSE ECONOMIC SERIES
# Store the FRED series IDs that we want to download.
# ================================

SERIES = {
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
    "FEDFUNDS": "Federal Funds Rate",
}


# ================================
# 6. FETCH ONE FRED SERIES
# This function downloads ONE economic series
# from the FRED API and returns it as a DataFrame.
# ================================

def fetch_fred_series(series_id: str) -> pd.DataFrame:

    # FRED API address
    url = "https://api.stlouisfed.org/fred/series/observations"

    # Tell FRED exactly what data we want
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": START_DATE,
        "observation_end": END_DATE,
    }

    # Send the request to FRED and save its response
    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    # Stop the program if the API request failed
    response.raise_for_status()

    # Get only the observations section from the JSON response
    observations = response.json()["observations"]

    # Turn the observations into a Pandas DataFrame
    df = pd.DataFrame(observations)

    # Keep only the columns we need
    df = df[["date", "value"]].copy()

    # Add the economic series ID so we know what each row represents
    df["series_id"] = series_id

    # Convert the value column from text into numbers
    # Invalid numeric values become NaN
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # Give the finished DataFrame back
    return df


# ================================
# 7. FETCH ALL FRED SERIES
# Loop through every series ID,
# download each one, and combine them together.
# ================================

def extract_all_series() -> pd.DataFrame:

    # Empty list that will hold each DataFrame
    frames = []

    # Repeat the extraction for every series
    for series_id in SERIES:

        print(f"Fetching {series_id}...")

        # Fetch one series
        df = fetch_fred_series(series_id)

        # Add its DataFrame to the list
        frames.append(df)

    # Stack all downloaded DataFrames together
    economic_data = pd.concat(
        frames,
        ignore_index=True
    )

    # Give the combined DataFrame back
    return economic_data


# ================================
# 8. RUN THE SCRIPT
# Only run this section when extract_fred.py
# is executed directly.
# ================================

if __name__ == "__main__":

    # Download and combine all economic series
    economic_data = extract_all_series()

    # Save the final DataFrame as a CSV file
    economic_data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # Preview the first 5 rows
    print(economic_data.head())

    # Show rows and columns
    print(economic_data.shape)

    # Confirm that the file was saved
    print("Saved fred_economic_data.csv")