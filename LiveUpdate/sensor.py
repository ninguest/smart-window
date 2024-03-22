import subprocess
import json
import socket
import threading
import os
import random
import string
import time


# Path to your compiled C executable
connection_type = "sensor"
sensor_type = "multi"
dataJSONPath = "data.json"
sensor_data = ["pressure", "temperature", "humidity", "light", "uv", "gas"]
restartScriptPath = "restartSensor.sh"

# Read Data 
def read_json_file(file_path):
    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        # If the file does not exist, create default data
        print("\nData File does not exist. Creating default data...")
        username = input("\nWhat is your system username? \n")
        host_ip = input("\nWhat is the host IP?\n")
        host_port = input("\nWhat is the host port?\n")
        data = {
            "connection_type": connection_type,
            "sensor_id": random_id_generator(8),
            "sensor_type": sensor_type,
            "sensor_data": sensor_data,
            "c_executable_path": f"/home/{username}/Desktop/sensorReader/main",
            "host_ip": host_ip,
            "host_port": host_port
        }
        # Write default data to file
        write_json_file(data, file_path)
    return data

# Function to write JSON data to file
def write_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

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
            elif message == "server_control:restart":
                try:
                    print("\nRestarting client...")
                    subprocess.run([restartScriptPath], capture_output=True, text=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error restarting sensor: {e}")
            else:
                print("\n" + message)
            
        except Exception as e:
            # Display error message.
            print(f"\nError: {e}")
            break

    client_socket.close()
    quit()

# Random ID generator 
def random_id_generator(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Function to execute the C code and capture output
def execute_c_code(c_executable_path):
    try:
        time.sleep(1)
        # Execute the C code and capture output
        result = subprocess.run([c_executable_path], capture_output=True, text=True, check=True)
        this_output = result.stdout.strip()
        return this_output
    except subprocess.CalledProcessError as e:
        print(f"Error executing C code: {e}")
        return None

# Main function.
def main():
    
    # Client Data 
    client_data = read_json_file(dataJSONPath)
    
    if client_data is None:
        print("\nError reading data from file. Exiting program....")
        return
    
    print(f"\n[Client Information]\nID: {client_data['sensor_id']}\nType: {client_data['sensor_type']}\nData: {client_data['sensor_data']}\nC Executable Path: {client_data['c_executable_path']}\nHost IP: {client_data['host_ip']}\nHost Port: {client_data['host_port']}\n")

    # Create client socket to connect client to server.
    while True:
        try:
            host = client_data["host_ip"]
            port = int(client_data["host_port"])
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            break
        except ValueError:
            print("\nPort number must be an integer. Please try again.")
        except socket.error as e:
            print(f"\nUnable to connect to server. {e}\nRetrying...")


    # Prompt client to identify what sensor it is representing.
    print(client_socket.recv(1024).decode('utf-8')) # Receive data from server.
    client_socket.sendall(json.dumps(client_data).encode('utf-8')) # Send data to server.
    response = client_socket.recv(1024).decode('utf-8') # Receive data from server.
    
    if(response == "[Sensor identification success.]"):
        print("[Sensor identification success.]")
        # Start thread to receive data from server.
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, 1))
        receive_thread.start()

        # Send data to server.
        print("\n[Sending sensor data to server]")
        while True:
            # Execute C code and send output to server
            data = execute_c_code(client_data["c_executable_path"])
            if data is not None:
                client_socket.sendall(data.encode('utf-8')) # Send data to server.
            else:
                client_socket.sendall("no data".encode('utf-8'))
    else:
        print("\nExiting program....")
        os._exit(1)
    
        
if __name__ == "__main__":
    main()