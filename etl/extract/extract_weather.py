import requests
import pandas as pd

LOCATIONS = {
    "CA": {"latitude": 34.0522, "longitude": -118.2437},
    "TX": {"latitude": 32.7767, "longitude": -96.7970},
    "WI": {"latitude": 43.0389, "longitude": -87.9065},
}

START_DATE = "2011-01-29"
END_DATE = "2016-06-19"

URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_weather(state_id, latitude, longitude):
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

    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()["daily"]

    df = pd.DataFrame(data)

    df["state_id"] = state_id

    return df


def extract_all_weather():
    frames = []

    for state_id, location in LOCATIONS.items():
        print(f"Fetching weather for {state_id}...")

        df = fetch_weather(
            state_id,
            location["latitude"],
            location["longitude"],
        )

        frames.append(df)

    weather = pd.concat(frames, ignore_index=True)

    return weather


if __name__ == "__main__":
    weather = extract_all_weather()

    print(weather.head())
    print(weather.shape)

    weather.to_csv(
        "data/external/weather_history.csv",
        index=False,
    )

    print("Saved weather_history.csv")