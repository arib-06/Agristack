import ee
import pandas as pd
import sys
from pathlib import Path

# Project paths

# Repo root = one level up from src/
BASE_DIR = Path(__file__).resolve().parent.parent

NDVI_DIR = BASE_DIR / "data" / "raw" / "ndvi"
NDVI_DIR.mkdir(parents=True, exist_ok=True)



# Import shared location resolver

# config/ lives at the repo root, so add the repo root
# to Python's import path.
sys.path.insert(0, str(BASE_DIR))

from config.location import get_coordinates
from config.analysis import START_DATE, END_DATE



# Main NDVI pipeline


if __name__ == "__main__":

    # Initialize Earth Engine using our registered project
    ee.Initialize(project="fiery-set-472410-j6")

    # Temporary test location.
    # Later this will come from the user/application.
    city = "Ludhiana"

    # Convert city name into latitude and longitude
    latitude, longitude = get_coordinates(city)

    print(f"Location: {city}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")


    # Create Earth Engine geometry
    
    # Earth Engine coordinates use:
    # [longitude, latitude]
    location = ee.Geometry.Point([longitude, latitude])


    
    # Load Sentinel-2 collection
    

    sentinel2 = ee.ImageCollection(
        "COPERNICUS/S2_SR_HARMONIZED"
    )


    
    # Filter Sentinel-2 data
   

    sentinel2_filtered = (
        sentinel2
        .filterBounds(location)
        .filterDate(START_DATE, END_DATE)

        # Keep scenes with less than 20% cloud coverage.
        # This is a scene-level pre-filter.
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                20
            )
        )
    )


    
    # Check how many images remain
   
    image_count = sentinel2_filtered.size().getInfo()

    print(
        f"Sentinel-2 images after filtering: {image_count}"
    )


    
    # Calculate NDVI for each image
   

    def calculate_ndvi(image):

        # NDVI = (NIR - RED) / (NIR + RED)
        #
        # Sentinel-2:
        # B8 = NIR
        # B4 = RED

        ndvi = image.normalizedDifference(
            ["B8", "B4"]
        ).rename("NDVI")


        # Extract the NDVI value at our location
        ndvi_value = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=location,
            scale=10,
            bestEffort=True
        ).get("NDVI")


        # Convert the result into a Feature
        # so we can eventually create a table.
        return ee.Feature(
            None,
            {
                "date": image.date().format("YYYY-MM-dd"),
                "ndvi": ndvi_value,
                "cloud_percentage": image.get(
                    "CLOUDY_PIXEL_PERCENTAGE"
                ),
                "image_id": image.id()
            }
        )


    # Apply our NDVI function to every image
    ndvi_features = sentinel2_filtered.map(
        calculate_ndvi
    )


    
    # Remove observations where NDVI is unavailable
   

    ndvi_features = ndvi_features.filter(
        ee.Filter.notNull(["ndvi"])
    )


    
    # Bring the small tabular result back to Python
    
    ndvi_data = ndvi_features.getInfo()


   
    # Convert Earth Engine result into Pandas
    

    rows = []

    for feature in ndvi_data["features"]:

        properties = feature["properties"]

        rows.append({
            "date": properties["date"],
            "ndvi": properties["ndvi"],
            "cloud_percentage": properties[
                "cloud_percentage"
            ],
            "image_id": properties["image_id"]
        })


    ndvi_df = pd.DataFrame(rows)


    
    # Save raw NDVI result
    

    output_file = NDVI_DIR / "ndvi.csv"

    ndvi_df.to_csv(
        output_file,
        index=False
    )


   
    # Basic validation
    
    print("\nNDVI data:")
    print(ndvi_df)

    print("\nData types:")
    print(ndvi_df.dtypes)

    print("\nMissing values:")
    print(ndvi_df.isnull().sum())

    print(f"\nSaved to: {output_file}")