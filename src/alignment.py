import pandas as pd
from pathlib import Path
import sys

# Repository root
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
WEATHER_DIR = BASE_DIR / "data" / "raw" / "weather"
NDVI_DIR = BASE_DIR / "data" / "raw" / "ndvi"

# Add repository root to Python path
sys.path.insert(0, str(BASE_DIR))

from config.analysis import START_DATE, END_DATE


# Load daily weather
weather = pd.read_csv(
    WEATHER_DIR / "weather_daily.csv"
)

# Load NDVI observations
ndvi = pd.read_csv(
    NDVI_DIR / "ndvi.csv"
)


# Convert dates to datetime
weather["date"] = pd.to_datetime(
    weather["date"]
)

ndvi["date"] = pd.to_datetime(
    ndvi["date"]
)


# Sort weather chronologically
weather = weather.sort_values(
    "date"
).reset_index(drop=True)


# Calculate previous 7 complete days of rainfall
weather["rainfall_7d"] = (
    weather["precipitation"]
    .shift(1)
    .rolling(window=7)
    .sum()
)


# Calculate mean temperature during previous 7 complete days
weather["temperature_7d_mean"] = (
    weather["temperature"]
    .shift(1)
    .rolling(window=7)
    .mean()
)


# Calculate mean humidity during previous 7 complete days
weather["humidity_7d_mean"] = (
    weather["humidity"]
    .shift(1)
    .rolling(window=7)
    .mean()
)


# Calculate mean wind speed during previous 7 complete days
weather["wind_speed_7d_mean"] = (
    weather["wind_speed"]
    .shift(1)
    .rolling(window=7)
    .mean()
)


# Convert analysis dates to datetime
start_date = pd.to_datetime(START_DATE)
end_date = pd.to_datetime(END_DATE)


# Remove historical buffer
weather = weather[
    (weather["date"] >= start_date)
    &
    (weather["date"] < end_date)
].copy()


# Merge weather features with NDVI
aligned_data = pd.merge(
    weather,
    ndvi,
    on="date",
    how="inner"
)


# Sort final dataset chronologically
aligned_data = aligned_data.sort_values(
    "date"
).reset_index(drop=True)


# Display final dataset
print("\nFinal aligned agricultural dataset:")
print(aligned_data)


# Display shape
print(
    f"\nShape: {aligned_data.shape}"
)


# Display data types
print("\nData types:")
print(aligned_data.dtypes)


# Display missing values
print("\nMissing values:")
print(aligned_data.isnull().sum())


# Display final date range
if not aligned_data.empty:
    print("\nFinal date range:")
    print(aligned_data["date"].min())
    print(aligned_data["date"].max())


# Save processed dataset
output_file = (
    BASE_DIR
    / "data"
    / "processed"
    / "aligned_data.csv"
)

output_file.parent.mkdir(
    parents=True,
    exist_ok=True
)

aligned_data.to_csv(
    output_file,
    index=False
)


print(
    f"\nSaved to: {output_file}"
)