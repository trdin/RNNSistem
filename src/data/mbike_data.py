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

# Function to save data to CSV
def save_to_csv(station, filename, station_number ,timestamp):
    weather_data = wd.fetch_and_write_weather_data(station['position']['lat'], station['position']['lng'], station_number , timestamp=timestamp)
    columns = ["date", "bike_stands", "available_bike_stands", "temperature", 
               "relative_humidity", "dew_point", "apparent_temperature", 
               "precipitation_probability", "rain", "surface_pressure"]
    
    weather_data = json.loads(weather_data)
    
    file_exists = os.path.exists(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        
        if not file_exists:
            writer.writeheader()
        
        station_data = {
            "date": timestamp,
            "temperature": weather_data["temperature"], 
            "relative_humidity": weather_data["relative_humidity"],
            "dew_point": weather_data["dew_point"],
            "apparent_temperature": weather_data["apparent_temperature"],
            "precipitation_probability": weather_data["precipitation_probability"],
            "rain": weather_data["rain"],
            "surface_pressure": weather_data["surface_pressure"],
            "bike_stands": station["bike_stands"],
            "available_bike_stands": station["available_bike_stands"],
        }
        
        writer.writerow(station_data)
    
    print("Data saved to", filename)
    return weather_data

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
            save_raw_data(data, raw_filename)

        
            
            weather_data = []

            # Save processed data to CSV
            for station in data:
                filename = 'data/processed/station_' + str(station['number']) + '.csv'
                weather_data.append(save_to_csv(station, filename, station['number'], timestamp))
            
            save_raw_data(weather_data, 'data/raw/weather/weather_data_' + timestamp_filename + '.json')
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
