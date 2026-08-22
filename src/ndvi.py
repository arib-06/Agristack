import ee

import pandas as pd

import sys

from pathlib import Path

# Repository root

BASE_DIR = Path(__file__).resolve().parent.parent

# NDVI output directory

NDVI_DIR = BASE_DIR / "data" / "raw" / "ndvi"

NDVI_DIR.mkdir(parents=True, exist_ok=True)

# Add repository root to Python path

sys.path.insert(0, str(BASE_DIR))

from config.location import get_coordinates
from config.analysis import START_DATE, END_DATE


if __name__ == "__main__":

    # Initialize Google Earth Engine

    ee.Initialize(project="fiery-set-472410-j6")

    # Temporary test location

    # Later this will come from the application or user

    city = "Ludhiana"

    # Convert city name into latitude and longitude

    latitude, longitude = get_coordinates(city)

    print(f"Location: {city}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")

    # Earth Engine coordinates use [longitude, latitude]

    location = ee.Geometry.Point([
        longitude,
        latitude
    ])

    # Load Sentinel-2 Surface Reflectance collection

    sentinel2 = ee.ImageCollection(
        "COPERNICUS/S2_SR_HARMONIZED"
    )

    # Filter images by location and date

    sentinel2_location_date = (
        sentinel2
        .filterBounds(location)
        .filterDate(START_DATE, END_DATE)
    )

    # Extract the SCL classification at the target location

    def add_target_scl(image):

        scl_value = image.select("SCL").reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=location,
            scale=20
        ).get("SCL")

        # Store the target-location SCL as an image property

        return image.set(
            "target_SCL",
            scl_value
        )

    # Add target-location SCL to every Sentinel-2 image

    sentinel2_with_scl = sentinel2_location_date.map(
        add_target_scl
    )

    # Keep only vegetation (4) and bare soil (5)

    sentinel2_scl_filtered = sentinel2_with_scl.filter(
        ee.Filter.inList(
            "target_SCL",
            [4, 5]
        )
    )

    # Calculate NDVI for each usable Sentinel-2 image

    def calculate_ndvi(image):

        # B8 is Near Infrared and B4 is Red

        ndvi = image.normalizedDifference(
            ["B8", "B4"]
        ).rename("NDVI")

        # Extract the mean NDVI value at our location

        ndvi_value = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=location,
            scale=10,
            bestEffort=True
        ).get("NDVI")

        # Store the result as an Earth Engine Feature

        return ee.Feature(
            None,
            {
                "date": image.date().format(
                    "YYYY-MM-dd"
                ),
                "ndvi": ndvi_value,
                "cloud_percentage": image.get(
                    "CLOUDY_PIXEL_PERCENTAGE"
                ),
                "SCL": image.get(
                    "target_SCL"
                ),
                "image_id": image.id()
            }
        )

    # Apply the NDVI calculation to every usable image

    ndvi_features = sentinel2_scl_filtered.map(
        calculate_ndvi
    )

    # Remove observations where NDVI could not be calculated

    ndvi_features = ndvi_features.filter(
        ee.Filter.notNull(["ndvi"])
    )

    # Bring the small tabular result from Earth Engine into Python

    ndvi_data = ndvi_features.getInfo()

    # Convert Earth Engine features into Pandas rows

    rows = []

    for feature in ndvi_data["features"]:

        properties = feature["properties"]

        rows.append({
            "date": properties["date"],
            "ndvi": properties["ndvi"],
            "cloud_percentage": properties[
                "cloud_percentage"
            ],
            "SCL": properties["SCL"],
            "image_id": properties["image_id"]
        })

    ndvi_df = pd.DataFrame(rows)

    # Save NDVI data

    output_file = NDVI_DIR / "ndvi.csv"

    ndvi_df.to_csv(
        output_file,
        index=False
    )

    # Validate the resulting dataset

    print("\nNDVI data:")
    print(ndvi_df)

    print("\nData types:")
    print(ndvi_df.dtypes)

    print("\nMissing values:")
    print(ndvi_df.isnull().sum())

    print(f"\nSaved to: {output_file}")