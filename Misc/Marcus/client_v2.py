import socket
import threading

# Function to receive data from server.
def receive_messages(client_socket):
    while True:
        try:
            # Receive data from server.
            message = client_socket.recv(1024).decode('utf-8')

            # If server returns error data, ask client to restart.
            if message == "Error. Restart client and try again.":
                print("\nError. Restart client and try again.")
                break

            print("\n" + message)
            
        except Exception as e:
            # Display error message.
            print(f"\nError: {e}")
            break

    client_socket.close()
    quit()

# Main function.
def main():
    # Client configuration.
    while True:
        server_ip_addr = input("What is the server ip address: ")
        server_port_num = input("\nWhat is the server port number: ")

        try:
            host = server_ip_addr # 192.168.1.141
            port = int(server_port_num) # 8888
            break
        
        except:
            print("\nInvalid host/port.")

    # Create client socket to connect client to server.
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            break

        except:
            print("\nInvalid host/port.")

    """ Functions to do after client sucessfully connects to server. """

    # Prompt client to identify what sensor it is representing.
    sensor = "light"
    print(client_socket.recv(1024).decode('utf-8')) # Receive data from server.
    client_socket.sendall(sensor.encode('utf-8')) # Send data to server.
    print(client_socket.recv(1024).decode('utf-8')) # Receive data from server.

    # Start thread to receive data from server.
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Send data to server.
    while True:
        message = input("\nEnter message to server: ")
        client_socket.sendall(message.encode('utf-8')) # Send data to server.


if __name__ == "__main__":
    main()
