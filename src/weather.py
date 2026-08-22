import json
import requests
import pandas as pd
from pathlib import Path
import sys

# Repository root
BASE_DIR = Path(__file__).resolve().parent.parent

# Weather output directory
WEATHER_DIR = BASE_DIR / "data" / "raw" / "weather"
WEATHER_DIR.mkdir(parents=True, exist_ok=True)

# Add repository root to Python path
sys.path.insert(0, str(BASE_DIR))

from config.location import get_coordinates
from config.analysis import (
    START_DATE,
    END_DATE,
    WEATHER_HISTORY_DAYS
)

# Open-Meteo historical weather API
URL = "https://archive-api.open-meteo.com/v1/archive"

if __name__ == "__main__":

    # Temporary test location
    city = "Ludhiana"

    # Convert city name into latitude and longitude
    latitude, longitude = get_coordinates(city)

    print(f"Location: {city}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")

    # Calculate the start date including the historical buffer
    start_date = pd.to_datetime(START_DATE)

    weather_start_date = (
        start_date
        - pd.Timedelta(days=WEATHER_HISTORY_DAYS)
    ).strftime("%Y-%m-%d")

    print(f"Analysis start date: {START_DATE}")
    print(
        f"Weather fetch start date: {weather_start_date}"
    )
    print(f"Weather fetch end date: {END_DATE}")

    # Define Open-Meteo request parameters
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "Asia/Kolkata",
        "start_date": weather_start_date,
        "end_date": END_DATE,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m"
        ])
    }

    # Fetch weather data from Open-Meteo
    weather_response = requests.get(
        URL,
        params=weather_params
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    # Save the original API response
    with open(
        WEATHER_DIR / "weather_raw.json",
        "w"
    ) as f:

        json.dump(
            weather_data,
            f,
            indent=4
        )

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
    weather_df["time"] = pd.to_datetime(
        weather_df["time"]
    )

    # Extract the date from each hourly timestamp
    weather_df["date"] = weather_df["time"].dt.date

    # Aggregate hourly weather into daily weather
    daily_weather = (
        weather_df
        .groupby("date")
        .agg({
            "temperature": "mean",
            "humidity": "mean",
            "precipitation": "sum",
            "wind_speed": "mean"
        })
        .reset_index()
    )

    # Convert date column back to datetime
    daily_weather["date"] = pd.to_datetime(
        daily_weather["date"]
    )

    # Validate the daily dataset
    print("\nFirst 10 daily records:")
    print(daily_weather.head(10))

    print(
        f"\nDaily dataset shape: "
        f"{daily_weather.shape}"
    )

    print("\nData types:")
    print(daily_weather.dtypes)

    print("\nMissing values:")
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

    print(
        f"\nSaved hourly weather to: "
        f"{WEATHER_DIR / 'weather.csv'}"
    )

    print(
        f"Saved daily weather to: "
        f"{WEATHER_DIR / 'weather_daily.csv'}"
    )