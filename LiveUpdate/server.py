import socket
import threading
from collections import defaultdict
import json
import random
import string
from datetime import datetime

sensors = {}
actions = {}
webapps = {}
sensorDataPath = "sensor_data.json"
thresholdDataPath = "threshold_data.json"

## Note change the threshold class for this TMR

live_sensor_data = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "lux": None,
    "gas": None,
    "uvs": None,
    "timestamp": None
}

server_data = {
    "show_sensor_logs" : False,
    "function_mode" : "auto"
}

def run_threshold():

    if server_data["function_mode"] != "auto":
        threading.Timer(2, run_threshold).start()
        return 
    
    print("\nRunning threshold function...")
    
    # Get the last 20 data
    dataCollection = load_last_n_sensor_data(sensorDataPath, 20)
    
    # Check if data is available or less than 20    
    if dataCollection is None or len(dataCollection) < 20:
        threading.Timer(2, run_threshold).start()
        return
        
    # Check if actions are available
    if len(actions) < 1:
        print(f"\nNo actions available. {len(actions)} actions clients connected.")
        threading.Timer(2, run_threshold).start()
        return
        
    # calculate the mean of the last 20 data
    temperatures = [entry['temperature'] for entry in dataCollection if entry['temperature'] is not None]
    humidities = [entry['humidity'] for entry in dataCollection if entry['humidity'] is not None]
    pressures = [entry['pressure'] for entry in dataCollection if entry['pressure'] is not None]
    luxes = [entry['lux'] for entry in dataCollection if entry['lux'] is not None]
    gases = [entry['gas'] for entry in dataCollection if entry['gas'] is not None]
    uvses = [entry['uvs'] for entry in dataCollection if entry['uvs'] is not None]
    
    temperature_mean = sum(temperatures) / len(temperatures) if temperatures else None
    humidity_mean = sum(humidities) / len(humidities) if humidities else None
    pressure_mean = sum(pressures) / len(pressures) if pressures else None
    lux_mean = sum(luxes) / len(luxes) if luxes else None
    gas_mean = sum(gases) / len(gases) if gases else None
    uvs_mean = sum(uvses) / len(uvses) if uvses else None
    
    # get the threshold rules
    thresholdRules = load_threshold_data()
        
    # check if the mean values satisfy the threshold rules
    for rule in thresholdRules:
        value = float(rule["value"])
        operator = rule["operator"]
        datatype = rule["datatype"]
        action = rule["action"]
        
        print(action)

        # Check if datatype matches and calculate mean accordingly
        if datatype == "lux":
            mean_value = lux_mean
        elif datatype == "temperature":
            mean_value = temperature_mean
        elif datatype == "humidity":
            mean_value = humidity_mean
        elif datatype == "uvs":
            mean_value = uvs_mean
        
        # Check if mean value satisfies the threshold condition
        if mean_value is not None:
            if operator == "more_than" and mean_value > value:
                actionString = actionStringConverter(action)
                actionSender(actionString)
            elif operator == "less_than" and mean_value < value:
                actionString = actionStringConverter(action)
                actionSender(actionString)
            elif operator == "equal" and mean_value == value:
                actionString = actionStringConverter(action)
                actionSender(actionString)
                
    # Schedule the next execution after 2 seconds
    threading.Timer(2, run_threshold).start()
            
def actionStringConverter(action):
    match action:
        case "open_window": return "action_control:window_on"
        case "close_window": return "action_control:window_off"
        case "light_on": return "action_control:light_on"
        case "light_off": return "action_control:light_off"
        case _: return "action_control:window_off"

def actionSender(actionString):
    for action in actions.keys():
        action.sendall(actionString.encode('utf-8'))
    print(f"\nActionSender\n{actionString}")

# Function to handle client connections
def handle_client(client_socket, client_data):
    while True:
        try:
            if client_data["connection_type"] == "sensor":
                # Sensor data will keep coming from the client
                dataString = client_socket.recv(1024).decode('utf-8')
                data = json.loads(dataString)
                # Update live sensor data
                pre_timestamp = live_sensor_data["timestamp"]
                update_live_sensor_data(data)
                post_timestamp = live_sensor_data["timestamp"]
                if post_timestamp != pre_timestamp:
                    # Append sensor data to file
                    append_sensor_data(live_sensor_data, sensorDataPath)
                
            elif client_data["connection_type"] == "action":
                pass
            
            elif client_data["connection_type"] == "webapp":
                message = client_socket.recv(1024).decode('utf-8')
                
                if(message == "function_mode:manual"):
                    server_data["function_mode"] = "manual"
                    print(f"\nFunction mode set to '{server_data['function_mode']}'.")
                elif(message == "function_mode:auto"):
                    server_data["function_mode"] = "auto"
                    print(f"\nFunction mode set to '{server_data['function_mode']}'.")
                elif(message == "action_control:window_on"):
                    print("\nWebApp to Actions: Window On")
                    actionSender("action_control:window_on")
                elif(message == "action_control:window_off"):
                    print("\nWebApp to Actions: Window Off")
                    actionSender("action_control:window_off")
                elif(message == "action_control:light_on"):
                    print("\nWebApp to Actions: Light On")
                    actionSender("action_control:light_on")
                elif(message == "action_control:light_off"):
                    print("\nWebApp to Actions: Light Off")
                    actionSender("action_control:light_off")
                else:
                    print("\n" + message)

        except Exception as e:
            client_socket.sendall("Error. Restart client and try again.".encode('utf-8')) # Send data to client

    client_socket.close()
    
# Update Live Sensor Data 
def update_live_sensor_data(data):
    try:
        if server_data["show_sensor_logs"] == True:
            print(f"\nUpdating live sensor data: \n{data}")
            
        if "temperature" in data and data["temperature"] is not None:
            live_sensor_data["temperature"] = data["temperature"] - 10
        if "humidity" in data and data["humidity"] is not None:
            live_sensor_data["humidity"] = data["humidity"]
        if "pressure" in data and data["pressure"] is not None:
            live_sensor_data["pressure"] = data["pressure"]
        if "lux" in data and data["lux"] is not None:
            live_sensor_data["lux"] = data["lux"]
        
        if "uvs" in data and data["uvs"] is not None:
            live_sensor_data["gas"] = data["uvs"] # due to some unknown problem, gas sensor is showing uvs sensor data
        
        if "gas" in data and data["gas"] is not None: # this is the fix, abandon gas value
            live_sensor_data["uvs"] = data["gas"]
        live_sensor_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error updating live sensor data: {e}")

# Append Sensor Data
def append_sensor_data(data, file_path):
    try:
        with open(file_path, 'r+') as file:
            try:
                sensor_data = json.load(file)
            except json.JSONDecodeError:
                sensor_data = []

            sensor_data.append(data)

            file.seek(0)  # Move the cursor to the beginning of the file
            json.dump(sensor_data, file, indent=4)  # Write the updated data to the file
            file.truncate()  # Truncate the file to remove any remaining data
    except FileNotFoundError:
        print(f"File '{file_path}' not found. Creating a new file...")
        with open(file_path, 'w') as file:
            json.dump([data], file, indent=4)
    except Exception as e:
        print(f"Error appending sensor data to file: {e}")

# Get the latest Data
def load_last_n_sensor_data(file_path, n):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if data:  # Check if the data is not empty
                return data[-n:]  # Return the last n entries in the list
            else:
                return None  # Return None if the file is empty
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{file_path}'.")
        return None

# Get all sensor data
def load_threshold_data():
    try:
        with open("threshold_data.json", "r") as file:
            sensor_data = json.load(file)
        return sensor_data
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty list
        return []

#check connection type validity
def is_valid_connection(connection_type):
        match(connection_type):
            case "sensor":
                return True
            case "action":
                return True
            case "webapp":
                return True
            case _:
                return False

# Function to get the local IP address of the Raspberry Pi
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

# ID generator
def generate_random_id(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

# Function to handle the command interface
def command_interface():
    while True:
        command = input("\nCommand: ")
        
        if command == "shutdown":
            print("\nShutting down server...")
            import os
            os._exit(1)
        
        elif command == "mode":
            print(f"\nCurrent Function mode: '{server_data['function_mode']}'.")
        
        elif command == "mode auto":
            server_data["function_mode"] = "auto"
            print(f"\nFunction mode set to '{server_data['function_mode']}'.")
        
        elif command == "mode manual":
            server_data["function_mode"] = "manual"
            print(f"\nFunction mode set to '{server_data['function_mode']}'.")
        
        elif command == "sensors":
            print("\nSensors:")
            for sensor in sensors.values():
                print(f"\n- {sensor['sensor_id']} : {sensor['sensor_data']}")
        
        elif command == "logon":
            server_data["show_sensor_logs"] = True
            print(f"\nSensor logs {server_data['show_sensor_logs']}")
        
        elif command == "logoff":
            server_data["show_sensor_logs"] = False
            print(f"\nSensor logs {server_data['show_sensor_logs']}")
        
        elif command == "actionWO":
            print("\nActions: Window On")
            actionSender("action_control:window_on")
        elif command == "actionWC":
            print("\nActions: Window Close")
            actionSender("action_control:window_close")
        elif command == "actionLO":
            print("\nActions: Light On")
            actionSender("action_control:light_on")
        elif command == "actionLC":
            print("\nActions: Light Close")
            actionSender("action_control:light_close")
        elif command == "test":
            run_threshold()
        else:
            print("\nInvalid command.")
    
# Main function
def main():
    
    # Server configuration
    host = get_local_ip()  # Get Server IP address
    if host is None:
        print("\nError getting local IP address. Exiting program....")
        return
    port = 8888

    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"\n[*] Server listening on {host}:{port}")
        
    # Server will listen for commands in a separate thread
    command_thread = threading.Thread(target=command_interface, args=())
    command_thread.start()
    
    run_threshold()

    while True:
        
        # Accept client connection
        client_socket, addr = server_socket.accept()
        print(f"\n[*] Accepted client connection from {addr[0]}:{addr[1]}")

        # Prompt client to identify what sensor it is representing
        client_socket.sendall("\nGetting connection data...".encode('utf-8')) # Ask client for sensor information (data will be received)
        client_data_string = client_socket.recv(1024).decode('utf-8')
        client_data = json.loads(client_data_string)
        
        # Validate data received from client
        if is_valid_connection(client_data["connection_type"]): # Check if client sensor is valid
            client_socket.sendall("[Sensor identification success.]".encode('utf-8')) # Send data to client
            
            if client_data["connection_type"] == "sensor":
                sensors[client_socket] = client_data
            elif client_data["connection_type"] == "action":
                actions[client_socket] = client_data
            elif client_data["connection_type"] == "webapp":
                webapps[client_socket] = client_data
                
            # Create thread to handle each client connection respectively
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_data))
            client_thread.start()

        else:
            client_socket.sendall("[Sensor identification failed.]".encode('utf-8'))
            client_socket.sendall("server_control:quit")

    server_socket.close()

if __name__ == "__main__":
    main()