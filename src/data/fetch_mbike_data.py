import requests
import csv
import os
from datetime import datetime
import json
import src.data.weather_data as wd

# Function to fetch data from the API
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return None

# Function to save raw JSON data
def save_raw_data(data, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(data, indent=4))
    print("Raw data saved to", filename)


# Main function
def main():
    try:
        api_url = "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
        data = fetch_data(api_url)
        if data:

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp_filename = timestamp.replace(" ", "_").replace(":", "-")
            # Save raw data
            raw_filename = 'data/raw/mbajk/bike_data_' + timestamp_filename + '.json'

            # Save processed data to CSV
            for station in data:
                station["date"] = timestamp

            save_raw_data(data, raw_filename)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
