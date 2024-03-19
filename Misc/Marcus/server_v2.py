import socket
import threading
from collections import defaultdict
import json

# setting
DATASET_SIZE = 50
LIGHT_THRESHOLD = 100
TEMP_THRESHOLD = 33.0
HUMIDITY_THRESHOLD = 90.0

# Function to handle client connections
def handle_client(client_socket, server):
    while True:
        try:
            # Receive data from client
            data = client_socket.recv(1024).decode('utf-8')
            xxx = json.loads(data)
            print(xxx)

            # sensor = server.get_sensor()
            # sensor.add_data(float(data))
            

            # print(server.test())

            """ Type code here if else statements to handle data received from client who to reply etc. """

        except Exception as e:
            client_socket.sendall("Error. Restart client and try again.".encode('utf-8')) # Send data to client

    client_socket.close()


class Sensor:

    def __init__(self, sensor_index, sensor_type, client):
        self.dataset = [0 for i in range(DATASET_SIZE)]
        self.sensor_index = sensor_index
        self.sensor_type = sensor_type
        self.client = client
    
    def add_data(self, data):
        self.dataset.pop(0)
        self.dataset.append(data)

    def is_greater_than(self, threshold):
        sum = 0
        for data in self.dataset:
            sum += data
        return True if sum / DATASET_SIZE > threshold else False

    def is_over_threshold(self):
        match self.sensor_type:
            case "light":
                return self.is_greater_than(LIGHT_THRESHOLD)
            case "humidity":
                return self.is_greater_than(HUMIDITY_THRESHOLD)
            case "temp":
                return self.is_greater_than(TEMP_THRESHOLD)
            case _:
                return False


class Server:

    def __init__(self):
        # self.sensor_client_dict = {} # store data
        self.client_sensor_dict = {} # store data
        self.sensors = defaultdict(list)

    def add_sensor(self, sensor_type, client):
        sensor_index = 1 # len(self.sensors.get(sensor_type)) + 
        sensor = Sensor(sensor_index, sensor_type, client)
        self.sensors[sensor_type].append(sensor)
        self.client_sensor_dict[client] = sensor
    
    def get_sensor(self, client):
        return self.client_sensor_dict.get(client)

    def get_clients(self):
        return list(self.client_sensor_dict.keys())

    def is_valid_sensor(self, sensor):
        match(sensor):
            case "light":
                return True
            case "humidity":
                return True
            case _:
                return False

    def get_sensor_index(self, client):
        sensor = self.get_sensor(client)
        return sensor.sensor_index

    def test(self):
        print(self.sensor_client_dict)
        print(self.client_sensor_dict)
        print(self.sensors)


# Main function
def main():
    # Server configuration
    host = '192.168.1.141'
    port = 8888

    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"\n[*] Server listening on {host}:{port}")

    server = Server()

    while True:
        # Accept client connection
        client_socket, addr = server_socket.accept()
        print(f"\n[*] Accepted client connection from {addr[0]}:{addr[1]}")

        # Prompt client to identify what sensor it is representing
        client_socket.sendall("\nGetting sensor information...".encode('utf-8')) # Send data to client
        sensor_type = client_socket.recv(1024).decode('utf-8').strip() # Receive data from client

        # Validate data received from client
        if server.is_valid_sensor(sensor_type): # Check if client sensor is valid
            client_socket.sendall("[Sensor identification success.]".encode('utf-8')) # Send data to client
            server.add_sensor(sensor_type, client_socket)

            # Create thread to handle each client connection respectively
            client_thread = threading.Thread(target=handle_client, args=(client_socket, server))
            client_thread.start()

    server_socket.close()


if __name__ == "__main__":
    main()
