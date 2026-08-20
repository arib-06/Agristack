import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

WEATHER_DIR = BASE_DIR / "data" / "raw" / "weather"
NDVI_DIR = BASE_DIR / "data" / "raw" / "ndvi"

weather = pd.read_csv(WEATHER_DIR / "weather_daily.csv")
ndvi = pd.read_csv(NDVI_DIR / "ndvi.csv")
weather["date"] = pd.to_datetime(weather["date"])
ndvi["date"] = pd.to_datetime(ndvi["date"])

print(weather.dtypes)
print(ndvi.dtypes)
aligned_data = pd.merge(
    weather,
    ndvi,
    on="date",
    how="inner"
)
print(aligned_data)
print(aligned_data.shape)

weather["rainfall_7d"] = (
    weather["precipitation"]
    .rolling(window=7)
    .sum()
)
print(weather[["date", "precipitation", "rainfall_7d"]].head(10))