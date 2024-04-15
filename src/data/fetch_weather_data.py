import requests
import csv
import os
from datetime import datetime
import json
import src.data.weather_data as wd


import src.helpers.latest_file as lf


# Main function
def main():
    try:
        input_directory = "data/raw/mbajk/"
        output_directory = "data/raw/weather/"

        # Check if output directory exists, create if not
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        latest_edited_file, timestamp = lf.get_latest_file(input_directory)

        # Read the JSON contents of the file
        with open(latest_edited_file, "r") as file:
            data = json.load(file)


        # Extract required fields and write to a new file
        output_data = []
        for station in data:

            weather_data =  wd.fetch_and_write_weather_data(station['position']['lat'], station['position']['lng'], station["number"] , timestamp=station["date"])
           
            output_data.append(weather_data)


        

        timestamp_filename = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

        # Write to the output file
        output_filename = os.path.join(output_directory, f"weather_data_{timestamp_filename}.json")
        with open(output_filename, "w") as output_file:
            json.dump(output_data, output_file, indent=4)


    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

