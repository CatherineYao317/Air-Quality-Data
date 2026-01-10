# This is a script to download historical air quality data from Air Quality Ontario.
# This includes all the pairs of station IDs and pollutant IDs specified below.

station_ids = [
    47045, 54012, 46090, 21005, 44008, 13001, 56051, 49010, 15020,
    28028, 29000, 29214, 29118, 52023, 26060, 15026, 13021, 44029,
    46108, 56010, 48006, 75010, 44017, 45027, 51002, 51001, 49005,
    51010, 59006, 16015, 14111, 71078, 27067, 48002, 77233, 63200,
    63203, 18007, 31129, 33003, 34021, 35125, 12008, 12016
]
pollutants = {
    9: "SO2",
    35: "NO",
    36: "NO2",
    37: "NOx",
    46: "CO",
    122: "O3",
    124: "PM2.5"
}


BASE_URL = "https://www.airqualityontario.com/history/searchResults.php"

import os
import requests
from time import sleep

# Define constants
START_DATE = "2020-01-01" # CHOOSE YOUR START DATE
END_DATE   = "2024-12-31" # CHOOSE YOUR END DATE
CATEGORY   = "Academic"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "air_quality_csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Files will be saved to:") # Will tell you where the files are saved. It will create a folder called air_quality_csv in the same directory as this script.
print(os.path.abspath(OUTPUT_DIR))

# Download data for each station and pollutant
for station_id in station_ids:
    for pollutant_id, pollutant_name in pollutants.items():

        params = {
            "page": "CSV",
            "categoryId": CATEGORY,
            "stationId": station_id,
            "pollutantId": pollutant_id,
            "startDate": START_DATE,
            "endDate": END_DATE,
            "reportType": "CSV"
        }

        response = requests.get(BASE_URL, params=params, timeout=60)

        if response.status_code == 200 and len(response.content) > 200:
            filename = os.path.join(
                OUTPUT_DIR,
                f"station_{station_id}_{pollutant_name}.csv"
            )
            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"Downloaded: {filename}")
        else:
            print(f"No data: station {station_id}, {pollutant_name}")

        sleep(1)
