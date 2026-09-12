# ================================
# 1. IMPORT TOOLS
# Load Python tools needed for file paths,
# API requests, and working with DataFrames.
# ================================

from pathlib import Path

import requests
import pandas as pd


# ================================
# 2. SET FILE LOCATION
# Find the main project folder and decide
# where the extracted weather data will be saved.
# ================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "weather_history.csv"
)


# ================================
# 3. SET LOCATIONS
# Store the latitude and longitude used to
# collect weather data for each M5 state.
# ================================

LOCATIONS = {
    "CA": {
        "latitude": 34.0522,
        "longitude": -118.2437,
    },
    "TX": {
        "latitude": 32.7767,
        "longitude": -96.7970,
    },
    "WI": {
        "latitude": 43.0389,
        "longitude": -87.9065,
    },
}


# ================================
# 4. SET DATE RANGE
# Choose the historical period of weather
# data that we want to download.
# ================================

START_DATE = "2011-01-29"
END_DATE = "2016-06-19"


# ================================
# 5. SET API ADDRESS
# Store the Open-Meteo historical weather
# API address that we will request data from.
# ================================

URL = "https://archive-api.open-meteo.com/v1/archive"


# ================================
# 6. FETCH WEATHER FOR ONE STATE
# This function requests historical weather
# for ONE location and returns it as a DataFrame.
# ================================

def fetch_weather(
    state_id: str,
    latitude: float,
    longitude: float,
) -> pd.DataFrame:

    # Tell the API which location, dates,
    # and weather measurements we want.
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "snowfall_sum",
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
    }

    # Send the request to Open-Meteo
    # and save the response that comes back.
    response = requests.get(
        URL,
        params=params,
        timeout=60,
    )

    # Stop the program if the API request failed.
    response.raise_for_status()

    # Read the JSON response and keep
    # only the "daily" weather section.
    data = response.json()["daily"]

    # Turn the daily weather data
    # into a Pandas DataFrame.
    df = pd.DataFrame(data)

    # Add the state ID so we know which
    # state every weather row belongs to.
    df["state_id"] = state_id

    # Give the completed weather DataFrame back.
    return df


# ================================
# 7. FETCH WEATHER FOR ALL STATES
# Loop through every state in LOCATIONS,
# fetch its weather, and combine the results.
# ================================

def extract_all_weather() -> pd.DataFrame:

    # Create an empty list that will
    # temporarily hold each state's DataFrame.
    frames = []

    # Loop through every state and
    # its latitude/longitude information.
    for state_id, location in LOCATIONS.items():

        # Show which state is currently
        # being downloaded.
        print(
            f"Fetching weather for {state_id}..."
        )

        # Fetch weather for this state using
        # its latitude and longitude.
        df = fetch_weather(
            state_id=state_id,
            latitude=location["latitude"],
            longitude=location["longitude"],
        )

        # Add this state's DataFrame
        # to our list.
        frames.append(df)

    # Stack all state DataFrames into
    # one large weather DataFrame.
    weather = pd.concat(
        frames,
        ignore_index=True,
    )

    # Give the combined DataFrame back.
    return weather


# ================================
# 8. RUN THE SCRIPT
# Only run this section when
# extract_weather.py is executed directly.
# ================================

if __name__ == "__main__":

    # Fetch and combine weather
    # for all three states.
    weather = extract_all_weather()

    # Make sure the output folder exists
    # before trying to save the CSV.
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save the extracted weather data
    # as a CSV file.
    weather.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # Preview the first 5 rows.
    print(weather.head())

    # Show the number of rows and columns.
    print(weather.shape)

    # Confirm exactly where the file was saved.
    print(
        f"Saved weather data to: "
        f"{OUTPUT_FILE}"
    )