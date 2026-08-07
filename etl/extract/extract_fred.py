import os
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "data" / "external" / "fred_economic_data.csv"

START_DATE = "2011-01-29"
END_DATE = "2016-06-19"

SERIES = {
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
    "FEDFUNDS": "Federal Funds Rate",
}


def fetch_fred_series(series_id: str) -> pd.DataFrame:
    url = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": series_id,
        "api_key": "2d69e628154494dd86c22a6add246ff2",
        "file_type": "json",
        "observation_start": START_DATE,
        "observation_end": END_DATE,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    observations = response.json()["observations"]

    df = pd.DataFrame(observations)

    df = df[["date", "value"]].copy()

    df["series_id"] = series_id

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    return df


def extract_all_series() -> pd.DataFrame:
    frames = []

    for series_id in SERIES:
        print(f"Fetching {series_id}...")

        df = fetch_fred_series(series_id)

        frames.append(df)

    economic_data = pd.concat(
        frames,
        ignore_index=True
    )

    return economic_data


if __name__ == "__main__":
    economic_data = extract_all_series()

    economic_data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(economic_data.head())
    print(economic_data.shape)
    print("Saved fred_economic_data.csv")