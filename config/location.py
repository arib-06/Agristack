## Shared location resolver — used by weather.py and ndvi.py

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_coordinates(city: str) -> tuple[float, float]:

    params = {"name": city}

    response = requests.get(GEOCODING_URL, params=params)
    response.raise_for_status()

    data = response.json()

    latitude  = data["results"][0]["latitude"]
    longitude = data["results"][0]["longitude"]

    return latitude, longitude
