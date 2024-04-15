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
        output_directory = "data/preprocessed/mbajk/"

        # Check if output directory exists, create if not
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        latest_edited_file, timestamp = lf.get_latest_file(input_directory)

        # Read the JSON contents of the file
        with open(latest_edited_file, "r") as file:
            data = json.load(file)


        # Extract required fields and write to a new file
        output_data = []
        for entry in data:
            output_entry = {
                "station_number": entry["number"],
                "bike_stands": entry["bike_stands"],
                "date": entry["date"],
                "available_bike_stands": entry["available_bike_stands"]
            }
            output_data.append(output_entry)




        # Write to the output file
        output_filename = os.path.join(output_directory, latest_edited_file.split("/")[-1])	
        with open(output_filename, "w") as output_file:
            json.dump(output_data, output_file, indent=4)


    except Exception as  e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
