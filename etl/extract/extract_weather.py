# ================================
# 1. IMPORT TOOLS
# Load Python tools needed for API requests
# and working with DataFrames.
# ================================

import requests
import pandas as pd


# ================================
# 2. SET LOCATIONS
# Store the latitude and longitude used to
# collect weather data for each M5 state.
# ================================

LOCATIONS = {
    "CA": {"latitude": 34.0522, "longitude": -118.2437},
    "TX": {"latitude": 32.7767, "longitude": -96.7970},
    "WI": {"latitude": 43.0389, "longitude": -87.9065},
}


# ================================
# 3. SET DATE RANGE
# Choose the historical period of weather
# data that we want to download.
# ================================

START_DATE = "2011-01-29"
END_DATE = "2016-06-19"


# ================================
# 4. SET API ADDRESS
# Store the Open-Meteo historical weather
# API address that we will request data from.
# ================================

URL = "https://archive-api.open-meteo.com/v1/archive"


# ================================
# 5. FETCH WEATHER FOR ONE STATE
# This function requests historical weather
# for ONE location and returns it as a DataFrame.
# ================================

def fetch_weather(state_id, latitude, longitude):

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
        timeout=60
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
# 6. FETCH WEATHER FOR ALL STATES
# Loop through every state in LOCATIONS,
# fetch its weather, and combine the results.
# ================================

def extract_all_weather():

    # Create an empty list that will
    # temporarily hold each state's DataFrame.
    frames = []

    # Loop through every state and its location information.
    for state_id, location in LOCATIONS.items():

        # Show which state is currently being downloaded.
        print(f"Fetching weather for {state_id}...")

        # Fetch weather for this state using
        # its latitude and longitude.
        df = fetch_weather(
            state_id,
            location["latitude"],
            location["longitude"],
        )

        # Add this state's DataFrame to our list.
        frames.append(df)

    # Stack all state DataFrames into
    # one large weather DataFrame.
    weather = pd.concat(
        frames,
        ignore_index=True
    )

    # Give the combined DataFrame back.
    return weather


# ================================
# 7. RUN THE SCRIPT
# Only run this section when this Python
# file is executed directly.
# ================================

if __name__ == "__main__":

    # Fetch and combine weather for all states.
    weather = extract_all_weather()

    # Preview the first 5 rows.
    print(weather.head())

    # Show the number of rows and columns.
    print(weather.shape)

    # Save the extracted weather data as a CSV file.
    weather.to_csv(
        "/opt/airflow/data/external/weather_history.csv",
        index=False,
    )

    # Confirm that the CSV was saved.
    print("Saved weather_history.csv")