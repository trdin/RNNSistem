import requests
import csv
import os
from datetime import datetime
import json

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

# Function to save data to CSV
def save_to_csv(data, filename):
    file_exists = os.path.exists(filename)
    columns = ["name", "position", "bike_stands", "available_bike_stands", "available_bikes", "last_update", "date"]
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        if not file_exists:
            writer.writeheader()
        for station in data:
            station["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({key: station[key] for key in columns})
    print("Data saved to", filename)

# Main function
def main():
    api_url = "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
    data = fetch_data(api_url)
    if data:
        # Save raw data
        raw_filename = 'data/raw/bike_data_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.json'
        save_raw_data(data, raw_filename)
        
        # Save processed data to CSV
        for station in data:
            filename = 'data/processed/' + station['name'] + '.csv'
            save_to_csv([station], filename)

if __name__ == "__main__":
    main()
