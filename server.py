import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 6789

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set socket options
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Server informs operating system that it's going to use given IP and port
server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

def disconnect_user(clients, disconnected_user):
    print('Closed connection from: {}'.format(clients[disconnected_user]['data'].decode('utf-8')))
    sockets_list.remove(disconnected_user)
    del clients[disconnected_user]

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # If true, client gracefully closed a connection
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        # Client closed connection violently
        return False

while True:

    # Returns reading, writing, and exception sockets:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # Checks for new connection
        if notified_socket == server_socket:

            # Get new socket and ip/port set for newly connected client
            client_socket, client_address = server_socket.accept()

            # Receive client's name
            user = receive_message(client_socket)

            # If false, client disconnected before they sent their name
            if user is False:
                continue

            sockets_list.append(client_socket)

            # Save username and username header
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

            client_count_header = f"{len(clients):<{HEADER_LENGTH}}".encode('utf-8')

            # Sends number of clients currently connected - 1, so as to not include the client it is sending to
            client_socket.send(client_count_header + str(len(clients)-1).encode())
            for client in clients:
                if clients[client] != user:
                    client_socket.send(clients[client]['header'] + clients[client]['data'])

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If false, client disconnected
            if message is False:
                
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by socket, so we know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            messageText = message['data'].decode("utf-8")
            if messageText.startswith("!!"):
                match(messageText):
                    case "!!leave":
                        disconnect_user(clients, notified_socket)
                        notified_socket.shutdown(socket.SHUT_RDWR)
                        notified_socket.close()
                        continue
            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Handles some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]