import requests
import csv
import os
from datetime import datetime
import json
import src.data.weather_data as wd

import os
from datetime import datetime

import src.helpers.latest_file as lf


    

def merge_and_save_data(weather_data_file, station_data_file, output_directory):
    with open(weather_data_file, 'r') as f:
        weather_data = json.load(f)
    
    with open(station_data_file, 'r') as f:
        station_data = json.load(f)
    
    merged_data = {}

    for weather_entry in weather_data:
        station_number = weather_entry["station_number"]
        if station_number in merged_data:
            merged_data[station_number].update(weather_entry)
        else:
            merged_data[station_number] = weather_entry
    
    for station_entry in station_data:
        station_number = station_entry["station_number"]
        if station_number in merged_data:
            merged_data[station_number].update(station_entry)
        else:
            merged_data[station_number] = station_entry
    

    
    for station_number, data in merged_data.items():
        filename = os.path.join(f"{output_directory}{station_number}", f'station_{station_number}.csv')
        columns = ["date", "bike_stands", "available_bike_stands", "temperature", 
                   "relative_humidity", "dew_point", "apparent_temperature", 
                   "precipitation_probability", "rain", "surface_pressure"]

        file_exists = os.path.exists(filename)

        write_data = {
            "date": data["date"],
            "temperature": data["temperature"], 
            "relative_humidity": data["relative_humidity"],
            "dew_point": data["dew_point"],
            "apparent_temperature": data["apparent_temperature"],
            "precipitation_probability": data["precipitation_probability"],
            "rain": data["rain"],
            "surface_pressure": data["surface_pressure"],
            "bike_stands": data["bike_stands"],
            "available_bike_stands": data["available_bike_stands"],
        }
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            if not file_exists:
                writer.writeheader()
            writer.writerow(write_data)
        print("Data saved to", filename)

# Main function
def main():
    try:
        mbike_dir = "data/preprocessed/mbajk/"
        weather_dir = "data/raw/weather/"
        output_directory = "data/processed/"

        latest_weather_file, weather_timestamp = lf.get_latest_file(weather_dir)
        latest_mbike_file, mbike_timestamp = lf.get_latest_file(mbike_dir)


        if(weather_timestamp == mbike_timestamp and latest_weather_file and latest_mbike_file):
            merge_and_save_data(latest_weather_file, latest_mbike_file, output_directory)
        else:
            print("unable to merge") 

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
