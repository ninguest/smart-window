import socket
import threading

# Function to receive messages from server.
def receive_messages(client_socket):
    while True:
        try:
            # Receive message from server.
            message = client_socket.recv(1024).decode('utf-8')
            
            # Check if server accepted quit for the client.
            if message == "[Quit Accepted]":
                print("\n\n[Quit Server. Goodbye.]")
                import os
                os._exit(1)
            else: 
                print("\n" + message)

        except Exception as e:
            # Display error message.
            print(f"\nError: {e}")
            break

# Main function.
def main():
    # Prompt user to enter server IP address and port number with error handling.
    while True:
        server_ip_addr = input("\nWhat is the server ip address: ")
        server_port_num = input("\nWhat is the server port number: ")
        print(f"\n[*] Connecting to server {server_ip_addr}:{server_port_num}. Please wait...")

        try:
            host = server_ip_addr 
            port = int(server_port_num)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            break
        except ValueError:
            print("\nPort number must be an integer. Please try again.")
        except socket.error as e:
            print(f"\nCould not connect to the server: {e}. Please try again with a different IP address or port number.")
    
    print(f"\n[*] Connected to server {server_ip_addr}:{server_port_num}.")

    while True:
        username = input(client_socket.recv(1024).decode('utf-8')) 
        client_socket.sendall(username.encode('utf-8')) 

        response = client_socket.recv(1024).decode('utf-8')
        if response == "[Successful username.]":
            break
        elif response == "[Unsuccessful username.]":
            print("\nUsername has already been used. Please enter another name.")

    print(f"\n[*] Username {username} has been accepted by the server.")
    
    # Start thread to receive messages from server.
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Send messages to server.
    while True:
        message = input("\nEnter message to server: ")
        client_socket.sendall(message.encode('utf-8'))

if __name__ == "__main__":
    main()
