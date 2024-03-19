import json
import os

# Define the file path
file_path = "data.json"

# Function to read JSON data from file
def read_json_file(file_path):
    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        # If the file does not exist, create default data
        data = {
            "type": "sensor",
            "sensor_id": "default_id",
            "sensor_type": "default_type",
            "sensor_data": ["default_data1", "default_data2"],
            "c_executable_path": "/home/nin/Downloads/TestC/main"
        }
        # Write default data to file
        write_json_file(data, file_path)
    return data

# Function to write JSON data to file
def write_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Example usage: Read JSON data from file
json_data = read_json_file(file_path)
print("Read JSON data:", json_data)

# Modify the JSON data
# json_data["sensor_id"] = "newid"
# json_data["sensor_type"] = "newtype"
# json_data["sensor_data"] = ["new_data1", "new_data2", "new_data3"]
# json_data["c_executable_path"] = "/home/nin/Downloads/TestC/main"

# Example usage: Write JSON data to file
# write_json_file(json_data, file_path)
# print("Updated JSON data written to file.")