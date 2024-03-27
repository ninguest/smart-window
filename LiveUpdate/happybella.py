import subprocess
import RPi.GPIO as GPIO
import json
import socket
import threading
import os
import random
import string
import time
from motor import motor

# Path to your compiled C executable
connection_type = "action"
dataJSONPath = "data.json"
action_type = ["motor"]
restartScriptPath = "restartSensor.sh"
LIGHT_PORT = 18

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
            "action_id": random_id_generator(8),
            "action_type": action_type,
            "host_ip": host_ip,
            "host_port": host_port,
            "light_state": False,
            "window_state": False
        }
        # Write default data to file
        write_json_file(data, file_path)
    return data

# Function to write JSON data to file
def write_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Function to receive data from server.
def receive_messages(client_socket, random):
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
            elif message == "action_control:light_on":
                toggleLight(True)
            elif message == "action_control:light_off":
                toggleLight(False)
            elif message == "action_control:window_on":
                toggleMotor(True)
            elif message == "action_control:window_off":
                toggleMotor(False)
            else:
                print("\n" + message)

        except Exception as e:
            # Display error message.
            print(f"\nError: {e}")
            break

    client_socket.close()
    quit()

# Jerry Update
# control window on/off
def window_control(bool):
    if bool == True:
        print("Open Window")
        motor(True)
        # subprocess.run(["python", "motor.py", "TRUE"], check=True)
        # Open the window
    elif bool == False:
        print("Close Window")
        motor(False)
        # subprocess.run(["python", "motor.py", "FALSE"], check=True)
        # Close the window

def toggleLight(bool):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18,GPIO.OUT)
    
    if bool:
        if client_data["light_state"] == False:
            client_data["light_state"] = True
            write_json_file(client_data, dataJSONPath)
            print("LED on")
            GPIO.output(18,GPIO.HIGH)
        else:
            print("LED already on")
    else:
        if client_data["light_state"] == True:
            client_data["light_state"] = False
            write_json_file(client_data, dataJSONPath)
            print("LED off")
            GPIO.output(18,GPIO.LOW)
        else:
            print("LED already off")

def toggleMotor(bool):
    if client_data == bool:
        print("Window is already in this state")
        return
    else:
        client_data["window_state"] = bool
        write_json_file(client_data, dataJSONPath)
        motor(bool)

# Jerry Update
# control light on/off
def light_control(bool):
    if bool == True:
        light(True)
        print("Light is on")
        # turn on the light
    else:
        light(False)
        print("Light is off")
        # turn off the light

# Random ID generator
def random_id_generator(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Main function.
def main():
    global client_data
    # Client Data
    client_data = read_json_file(dataJSONPath)
    
    if client_data is None:
        print("\nError reading data from file. Exiting program....")
        return

    print(f"\n[Client Information]\nID: {client_data['action_id']}\nType: {client_data['action_type']}\nHost IP: {client_data['host_ip']}\nHost Port: {client_data['host_port']}\n")

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
        print("[Identification success.]")
        # Start thread to receive data from server.
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, 1))
        receive_thread.start()

    else:
        GPIO.cleanup()
        print("\nExiting program....")
        os._exit(1)


if __name__ == "__main__":
    main()