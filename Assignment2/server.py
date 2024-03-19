import socket
import threading

# Global variables
groups = {}

# Function to handle client connections.
def handle_client(client_socket, clients, client_names):
    while True:
        try:
            # Receive message from client.
            if client_socket in clients:
                message = client_socket.recv(1024).decode('utf-8')

            # If no message received, break out of the loop
            if not message:
                break
            
            # If message is "@names", send connected users.
            if message == "@names":
                send_connected_users(client_socket, clients, client_names)
            
            # If message is "@help", send available commands.
            elif message == "@help": 
                help_message = """
                \n[Available commands:]
                \n- @names: List all connected users.
                \n- @groups: List all available groups.
                \n- @group set <group_name> <members>: Create a group.
                \n- @group add <group_name> <members>: Add members to a group.
                \n- @group send <group_name> <message>: Send a message to a group.
                \n- @group delete <group_name>: Delete a group.
                \n- @group leave <group_name>: Leave a group.
                \n- @quit: Disconnect from the server.
                \n- @<username>: Send a private message to a user.
                \n- @help: Display available commands.
                """
                client_socket.sendall(help_message.encode('utf-8'))
            
            # If message is "@quit", close client socket and remove from clients list.
            elif message == "@quit":
                handle_quit(client_socket, clients, client_names)

            # If message is "@groups", send group list.
            elif message == "@groups":
                group_list = ", ".join(groups.keys())
                client_socket.sendall(f"\n[Groups: {group_list}]".encode('utf-8'))
                
            # If message starts with "@group set", create a group
            elif message.startswith("@group set"):
                create_group(message, client_socket, client_names, clients)
            
            elif message.startswith("@group add"):
                add_group_member(message, client_socket, client_names, clients)
                
            # If message starts with "@group send", send message to group members
            elif message.startswith("@group send"):
                send_group_message(message, client_socket, client_names, clients)
            
            # If message starts with "@group delete", delete the group
            elif message.startswith("@group delete"):
                delete_group(message, client_socket, client_names, clients)
            
            # If message starts with "@group leave", remove client from the group
            elif message.startswith("@group leave"):
                leave_group(message, client_socket, client_names, clients)

            # If message starts with "@", handle private message.
            elif message.startswith("@"):
                handle_private_message(message, client_socket, client_names, clients)
            
            # Otherwise, broadcast message to all clients.
            else:
                broadcast_message(message, client_socket, client_names, clients)
        
        except Exception as e:
            print(f"Error: {e}")
            break
    
    if (client_socket in clients):
        del client_names[client_socket]
        clients.remove(client_socket)
        client_socket.close()

def create_group(message, client_socket, client_names, clients):
    try:
        # Extract group name and members from the message
        _, _, group_name, members_str = message.split(" ", 3)
        group_name = group_name.strip()
        members = [member.strip() for member in members_str.split(",")]
        
        # Step 1: Check if the group already exists
        if group_name in groups:
            client_socket.sendall("\n[Group with this name already exists]".encode('utf-8'))
            return
        
        # Step 2: Check if all members are connected
        for member in members:
            member_socket = find_client_socket_by_username(member, clients, client_names)
            if not member_socket:
                client_socket.sendall(f"\n[User {member} is not connected to the server]".encode('utf-8'))
                return

        # Step 3: Create the group and add members
        groups[group_name] = members
        
        # Send confirmation message to group members
        confirmation_message = f"\n[You are enrolled in the {group_name} group]"
        for member in members:
            member_socket = find_client_socket_by_username(member, clients, client_names)
            if member_socket:
                member_socket.sendall(confirmation_message.encode('utf-8'))

    except Exception as e:
        client_socket.sendall(f"\n[{e}]\nPlease use the format '@group set group_name member1 member2 ...'\n".encode('utf-8'))
        return

def add_group_member(message, client_socket, client_names, clients):
    try:
        # Extract group name and members from the message
        _, _, group_name, members_str = message.split(" ", 3)
        group_name = group_name.strip()
        members = [member.strip() for member in members_str.split(",")]
        
        # Step 1: Check if the group exists
        if group_name not in groups:
            client_socket.sendall("\n[Group does not exist]".encode('utf-8'))
            return
        
        # Step 2: Check if the user is in the group
        username = client_names[client_socket]
        if username not in groups[group_name]:
            client_socket.sendall("\n[You are not a member of this group]".encode('utf-8'))
            return
        
        # Step 3: Check if all members are connected
        for member in members:
            member_socket = find_client_socket_by_username(member, clients, client_names)
            if not member_socket:
                client_socket.sendall(f"\n[User {member} is not connected to the server]".encode('utf-8'))
                return

        # Step 4: Add members to the group
        groups[group_name].extend(members)
        
        # Send confirmation message to group members
        confirmation_message = f"\n[You are enrolled in the {group_name} group]"
        for member in members:
            member_socket = find_client_socket_by_username(member, clients, client_names)
            if member_socket:
                member_socket.sendall(confirmation_message.encode('utf-8'))

        # Inform the client that the group has been created
        client_socket.sendall(f"\n[Members added to Group {group_name} successfully]".encode('utf-8'))

    except Exception as e:
        client_socket.sendall(f"\n[{e}]\nPlease use the format '@group add group_name member1 member2 ...'\n".encode('utf-8'))
        return

def send_group_message(message, client_socket, client_names, clients):
    try:
        # Extract group name and message content from the message
        _, _, group_name, message_content = message.split(" ", 3)
        group_name = group_name.strip()
        
        # Check if the user is in the specified group
        username = client_names[client_socket]
        if username not in groups.get(group_name, []):
            client_socket.sendall(f"\n[You are not a member of the group {group_name}]".encode('utf-8'))
            return

        # Broadcast the message to all members of the group
        group_broadcast_message(message_content, username, group_name, client_names, clients)
        
    except Exception as e:
        client_socket.sendall(f"\n[{e}]\nPlease use the format '@group send group_name message'\n".encode('utf-8'))
        return

def delete_group(message, client_socket, client_names, clients):
    try:
        # Extract the group name from the message
        groupName = message.split(" ", 2)[-1].strip()
        username = client_names[client_socket]
        
        # Check if the group exists
        if groupName in groups:
            
            # Stop the user from deleting the group if they are not a member
            if username not in groups[groupName]:
                client_socket.sendall("\n[You are not a member of this group]".encode('utf-8'))
                return
            
            # Inform group members that the group has been deleted
            deleteMessage = f"\n[{username} requested to deleted the group {groupName}]"
            group_broadcast_message(deleteMessage, username, groupName, client_names, clients)
            del groups[groupName]
            print (f"\n[Group {groupName} has been deleted]")
            
        else:
            client_socket.sendall("\n[Group does not exist]".encode('utf-8'))
        
    except Exception as e:
        client_socket.sendall(f"\n[{e}]\nPlease use the format '@group delete group_name'\n".encode('utf-8'))
        return

def leave_group(message, client_socket, client_names, clients):
    try:
        # Extract the group name from the message
        groupName = message.split(" ", 2)[-1].strip()
        username = client_names[client_socket]
        
        # Check if the group exists
        if groupName in groups:
            
            # Stop the user from leaving the group if they are not a member
            if username not in groups[groupName]:
                client_socket.sendall("\n[You are not a member of this group]".encode('utf-8'))
                return
            
            # Inform group members that the user has left the group
            leaveMessage = f"\n[{username} has left the group {groupName}]"
            group_broadcast_message(leaveMessage, username, groupName, client_names, clients)
            groups[groupName].remove(username)
            print (f"\n[{username} has left the group {groupName}]")
            
        else:
            client_socket.sendall("\n[Group does not exist]".encode('utf-8'))
        
    except Exception as e:
        client_socket.sendall(f"\n[{e}]\nPlease use the format '@group leave group_name'\n".encode('utf-8'))
        return

def handle_quit(quit_socket, clients, client_names):
    try:
        quit_message = f"\n[{client_names[quit_socket]} exited]"
        print(quit_message)
        for client_socket in clients:
            if client_socket != quit_socket:
                client_socket.sendall(quit_message.encode('utf-8'))
            
        quit_socket.sendall("[Quit Accepted]".encode('utf-8'))          
    except Exception as e:
        print(f"Error: {e}")      

def send_connected_users(client_socket, clients, client_names):
    connected_users = ", ".join(client_names.values())
    client_socket.sendall(f"\n[Connected users: {connected_users}]".encode('utf-8'))

def handle_private_message(message, client_socket, client_names, clients):
    try:
        message = message[1:]
        recipient_username, message_content = message.split(" ", 1)
        recipient_socket = find_client_socket_by_username(recipient_username, clients, client_names)
        if recipient_socket:
            sender_username = client_names[client_socket]
            recipient_socket.sendall(f"\n[{sender_username}](private): {message_content}".encode('utf-8'))
        else:
            client_socket.sendall("\n[Username you are trying to private message does not exist.]".encode('utf-8'))

    except ValueError as e:
        client_socket.sendall(f"\n[{e}]\nPlease use the format '@username message'\n".encode('utf-8'))
        return

def find_client_socket_by_username(username, clients, client_names):
    for client_socket, name in client_names.items():
        if name == username:
            return client_socket
    return None

def broadcast_message(message, sender_socket, client_names, clients):
    sender_username = client_names[sender_socket]
    for client_socket in clients:
        if client_socket != sender_socket:
            client_socket.sendall(f"[{sender_username}]: {message}".encode('utf-8'))

def group_broadcast_message(message, username, group, client_names, clients):
    for user in groups[group]:
        if user != username:
            client_socket = find_client_socket_by_username(user, clients, client_names)
            client_socket.sendall(f"[{username}]({group}): {message}".encode('utf-8'))

# Handle command-line interface
def command_interface(clients, client_names, server_socket):
    # Function to handle commands entered via the command-line interface
    while True:
        command = input("Enter command: ")
        if command == "@quitserver":
            # Close server socket and break out of the loop
            import os
            os._exit(1)

        elif command == "@names":
            connected_users = ", ".join(client_names.values())
            print(f"\n[Connected users: {connected_users}]")

        elif command == "@groups":
            group_list = ", ".join(groups.keys())
            print(f"\n[Groups: {group_list}]")
            
        elif command == "@help":
            help_message = """
            \n- [Available commands for the server:]
            \n- @names - Display connected users.
            \n- @groups - Display existing groups.
            \n- @group <group_name> - Display members of a specific group.
            \n- @deletegroup <group_name> - Delete a group.
            \n- @quitserver - Close the server.
            \n- @help - Display available commands.
            """
            print(help_message)
        
        elif command.startswith("@group"):
            groupName = command.split(" ", 1)[-1].strip()
            if groupName in groups:
                print(f"\n[Members of group {groupName}: {', '.join(groups[groupName])}]")
            else:
                print("\n[Group does not exist]")
        elif command.startswith("@deletegroup"):
            groupName = command.split(" ", 1)[-1].strip()
            if groupName in groups:
                delete_message = f"\n[Server Admin have deleted {groupName} group]"
                for user in groups[groupName]:
                    client_socket = find_client_socket_by_username(user, clients, client_names)
                    client_socket.sendall(delete_message.encode('utf-8'))
                del groups[groupName]
                print(f"\n[Group {groupName} has been deleted]")
            else:
                print("\n[Group does not exist]")
        else:
            print("Unknown command")

def main():
    host = '127.0.0.1'
    port = 8888

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"\n[*] Server listening on {host}:{port}")

    clients = []
    client_names = {}

    command_thread = threading.Thread(target=command_interface, args=(clients, client_names, server_socket))
    command_thread.start()

    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"\n[*] Accepted client connection from {addr[0]}:{addr[1]}")

        client_socket.sendall("\nEnter your username: ".encode('utf-8'))
        
        username = client_socket.recv(1024).decode('utf-8').strip()

        while username.lower() in map(str.lower, client_names.values()):
            client_socket.sendall("[Unsuccessful username.]".encode('utf-8'))
            client_socket.sendall("\nRe-enter your username: ".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8').strip()
            if username.lower() not in map(str.lower, client_names.values()):
                break
        
        client_socket.sendall("[Successful username.]".encode('utf-8'))

        clients.append(client_socket)
        client_names[client_socket] = username
        print(f"\n[{client_names[client_socket]} joined]")

        for c in clients:
            if c == client_socket:
                phrase = f"\n[Welcome {client_names[client_socket]}!]"
                c.send(phrase.encode('utf-8'))
            else:
                broadcast = f"\n[{client_names[client_socket]} joined]"
                c.send(broadcast.encode('utf-8'))

        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients, client_names))
        client_thread.start()

    server_socket.close()

if __name__ == "__main__":
    main()
