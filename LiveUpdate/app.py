from flask import Flask, request, jsonify, render_template
import json
import socket
import os
import subprocess
import threading
import random
import string
import time

app = Flask(__name__)
client_data = {
    "connection_type": "webapp",
}

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

# Function to receive data from server.
def receive_messages(client_socket):
    while True:
        try:
            # Receive data from server.
            message = client_socket.recv(1024).decode('utf-8')

            # If server returns error data, ask client to restart.
            if message == "server_control:quit":
                print("[Quit signal received from server. Shutting client down...]")
                os._exit(1)
            else:
                print("\n" + message)
            
        except Exception as e:
            # Display error message.
            print(f"\nError: {e}")
            break

    client_socket.close()
    quit()

# Connect to the server
def app_to_server():
    global connectedClient  # Declare connectedClient as a global variable
    
    while True:
        try:
            host = get_local_ip()
            port = 8888
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            break
        except Exception as e:
            print(f"Error connecting to server: {e}")
    
    print(client_socket.recv(1024).decode('utf-8'))
    client_socket.sendall(json.dumps(client_data).encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    
    if(response == "[Sensor identification success.]"):
        print("[Sensor identification success.]")
        connectedClient = client_socket
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, ))
        receive_thread.start()
    else: 
        print("[Sensor identification failed.]")
        client_socket.close()
        os._exit(1)
        
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

# Route to save threshold data to JSON file
@app.route('/save_threshold_data', methods=['POST'])
def save_threshold_data():
    try:
        threshold_data = request.json
        with open('threshold_data.json', 'w') as file:
            json.dump(threshold_data, file)
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error saving threshold data: {str(e)}")
        return jsonify({'success': False}), 500

# Route to load the threshold rules from the file
@app.route('/load_rules')
def load_rules():
    try:
        with open('threshold_data.json', 'r') as file:
            threshold_data = json.load(file)
        return jsonify(threshold_data)
    except FileNotFoundError:
        # Create a new file with an empty list if it doesn't exist
        with open('threshold_data.json', 'w') as file:
            json.dump([], file)
        return jsonify([])  # Return an empty list if the file didn't exist
    except Exception as e:
        print(f"Error loading threshold data: {str(e)}")
        return jsonify([])

# Route to receive messages from the client
@app.route('/send_server_message', methods=['POST'])
def receive_message():
    # Extract the message from the request
    message = request.json.get('message')

    connectedClient.sendall(message.encode('utf-8'))
    
    # Optionally, send a response back to the client
    response = {'status': 'Message received successfully'}
    return jsonify(response)


if __name__ == '__main__':
    # Run server main in a separate thread
    server_thread = threading.Thread(target=app_to_server, kwargs={})
    server_thread.start()
    
    # Start the Flask app in the main thread
    app.run(host='0.0.0.0', debug=True)



