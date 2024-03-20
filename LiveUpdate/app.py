from flask import Flask, jsonify, render_template
import json
import socket

app = Flask(__name__)

# Function to load sensor data from JSON file
def load_sensor_data(file_path):
    try:
        with open('sensor_data.json', 'r') as file:
            data = json.load(file)
            recent_data = data[-20:]  # Get the last 50 entries
            return recent_data
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Unable to decode JSON.")
        return None

# Function to get local IP address
def get_local_ip():
    try:
        # Create a temporary socket
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(('8.8.8.8', 80))  # Google Public DNS
        local_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return local_ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return None

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html', host_ip=get_local_ip())

# Route to provide sensor data in JSON format
@app.route('/get_sensor_data')
def get_sensor_data():
    sensor_data = load_sensor_data('sensor_data.json')  # Load sensor data from JSON file
    if sensor_data:
        return sensor_data
    else:
        return None  # Return empty list if sensor data is not available

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
