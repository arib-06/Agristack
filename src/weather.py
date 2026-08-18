import json
import requests
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.location import get_coordinates
from config.analysis import START_DATE, END_DATE


# Base directory = repository root
BASE_DIR = Path(__file__).resolve().parent.parent

WEATHER_DIR = BASE_DIR / "data" / "raw" / "weather"
WEATHER_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://api.open-meteo.com/v1/forecast"


if __name__ == "__main__":

    city = "Ludhiana"

    latitude, longitude = get_coordinates(city)

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "Asia/Kolkata",
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m"
        ])
    }

    # Fetch weather data from Open-Meteo
    weather_response = requests.get(URL, params=weather_params)
    weather_response.raise_for_status()

    weather_data = weather_response.json()

    # Save raw API response
    with open(WEATHER_DIR / "weather_raw.json", "w") as f:
        json.dump(weather_data, f, indent=4)

    # Extract hourly weather data
    hourly = weather_data["hourly"]

    # Convert API response into a DataFrame
    weather_df = pd.DataFrame({
        "time": hourly["time"],
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "precipitation": hourly["precipitation"],
        "wind_speed": hourly["wind_speed_10m"]
    })

    # Convert time strings into datetime objects
    weather_df["time"] = pd.to_datetime(weather_df["time"])

    # Extract only the date
    weather_df["date"] = weather_df["time"].dt.date

    # Convert hourly weather into daily weather
    daily_weather = weather_df.groupby("date").agg({
        "temperature": "mean",
        "humidity": "mean",
        "precipitation": "sum",
        "wind_speed": "mean"
    }).reset_index()

    # Check the daily dataset
    print(daily_weather.head())
    print(daily_weather.shape)
    print(daily_weather.dtypes)
    print(daily_weather.isnull().sum())

    # Save hourly weather data
    weather_df.to_csv(
        WEATHER_DIR / "weather.csv",
        index=False
    )

    # Save daily weather data
    daily_weather.to_csv(
        WEATHER_DIR / "weather_daily.csv",
        index=False
    )