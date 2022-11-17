import socket
import select
import errno
import sys

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 6789
my_username = input("Username: ")

# Create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state
client_socket.setblocking(False)

# Recieves messages sent by the server
def receive_message():
    message_header = client_socket.recv(HEADER_LENGTH)

    # Server gracefully closed a connection
    if not len(message_header):
        print('Connection closed by the server')
        sys.exit()

    
    message_length = int(message_header.decode('utf-8').strip())

    return client_socket.recv(message_length).decode('utf-8')

# Sends messages to the server
def send_message(message_to_send):
    message = message_to_send.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

send_message(my_username)

# Get list of users on server
try:
    client_socket.setblocking(True)

    client_count = int(receive_message())

    if client_count < 1:
        raise Exception('No Other Users on the Server')

    print("Users on server:")

    for i in range(client_count):
        message = receive_message()
        print(message)
            
    client_socket.setblocking(False)
except Exception as e:
    print(str(e))
    client_socket.setblocking(False)

client_socket.setblocking(1)
length = client_socket.recv(1)
length = str(length)[2:-1]

for i in range(int(length)):
    client_socket.setblocking(1)
    recentMessage = client_socket.recv(1024)
    if not recentMessage:
        break
    recentMessage.decode('utf-8')
    recentMessage = str(recentMessage)
    print(recentMessage[2:-1])
    client_socket.setblocking(0)
client_socket.setblocking(0)

while True:


    # Wait for user to input a message
    message = input(f'{my_username} > ')
    
    # Check for empty message
    if message:
        send_message(message)

    try:
        # Loop over received messages and print them
        while True:

            # Receive username of user that sent message
            username = receive_message()

            # Receive message sent by user whose username was just received
            message = receive_message()

            # Print message
            print(f'{username} > {message}')

    except IOError as e:
        # Checks for both again and wouldblock 
        # Just one or the other is expected behavior for no message received
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # No message received
        continue

    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()