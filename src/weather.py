## `open meteo

import json
import requests
import pandas as pd
from pathlib import Path

# Base directory = repo root (one level up from src/)
BASE_DIR = Path(__file__).resolve().parent.parent
WEATHER_DIR = BASE_DIR / "data" / "raw" / "weather"
WEATHER_DIR.mkdir(parents=True, exist_ok=True)

url = "https://api.open-meteo.com/v1/forecast"

city = "Ludhiana"

geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

params = {"name": city}

## params is parameter required for API and the other params is our parameter which we are passing

response = requests.get(geocoding_url, params=params)

data = response.json()   # stores data as a response

print(response.status_code) # server code
print(response.text)       # body


# Extract latitude and longitude from the first search result
latitude = data["results"][0]["latitude"]
longitude = data["results"][0]["longitude"]


weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "timezone": "Asia/Kolkata", #as time zone is in gmt in terminal

    # join combines all the strings in the list using "," between them
    "hourly": ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ])
}


weather_response = requests.get(url, params=weather_params)

print(weather_response.status_code)
print(weather_response.text)


weather_data = weather_response.json()  # got converted into a python dic

with open(WEATHER_DIR / "weather_raw.json", "w") as f:
    json.dump(weather_data, f, indent=4)

# weather_data["hourly"] gives us the nested dictionary containing
# all the hourly weather information
hourly = weather_data["hourly"]


# Pandas can directly create the DataFrame from the parallel lists
# Earlier used a for loop to manually connect the values using their indexes
# The loop is no longer necessary here because Pandas handles the row 
weather_df = pd.DataFrame({

    # key = column name
    # value = list containing the actual data for that column
    "time": hourly["time"],

    "temperature": hourly["temperature_2m"],

    "humidity": hourly["relative_humidity_2m"],

    "precipitation": hourly["precipitation"],

    "wind_speed": hourly["wind_speed_10m"]
})


# Converts the time from a string into Pandas datetime format
weather_df["time"] = pd.to_datetime(weather_df["time"])


print(weather_df.head())
print(weather_df.dtypes)
print(weather_df.isnull().sum())
print(weather_df.describe())


# OLD METHOD — kept here for learning/reference


# temperatures = weather_data["hourly"]["temperature_2m"]  # nested dic access
# times = weather_data["hourly"]["time"]

# for time, temperature in zip(times, temperatures):
#     # zip attaches them together
#     print(time, temperature)
#     # sync temp and times data together


# weather_rows = []  # empty list

# for i in range(len(times)):
#     row = {
#         "time": times[i],
#         "temperature": temperatures[i]   # marking key & value
#     }

#     weather_rows.append(row)

weather_df.to_csv(
    WEATHER_DIR / "weather.csv",
    index=False
)