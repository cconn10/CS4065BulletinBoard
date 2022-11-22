import socket
import select
import errno
import sys
from datetime import date

messageID = 0
HEADER_LENGTH = 10
IP = "192.168.1.46"
PORT = 6789
my_username = input("Username: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
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
recentMessage = client_socket.recv(1024)
recentMessage = str(recentMessage.decode('utf-8'))
recentMessage = recentMessage.split("\n")
print("Recent Messages:")
if recentMessage[0] == '0':
    print("None")
else:
    for i in range(1, len(recentMessage), 2):
        messageID = int(recentMessage[i])
        username = recentMessage[i + 1].split(" ")[0]
        subject = recentMessage[i + 1].split(" ")[2]
        print(f"MessageID: {str(messageID)}\nSender: {username}\nDate: {date.today()}\nSubject: {subject}\n")
    messageID = messageID + 1
client_socket.setblocking(0)



def recieveAllMessages():
    global messageID
    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # Receive and decode username
            username = client_socket.recv(username_length).decode('utf-8')

            # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            # Print message
            if not message.endswith("joined the server!") and not username == 'Server':
                print(f"MessageID: {str(messageID)}\nSender: {username}\nPost Date: {date.today()}\nSubject: {message}\n")
                messageID = messageID + 1
            else:
                print(f'{username} > {message}\n')

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()


    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: {}'.format(str(e)))
        sys.exit()

while True:

    # Wait for user to input a message
    message = input(f'{my_username}: ')
    print()

    # If message is not empty - send it
    if message:
        
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        recieveAllMessages()
        test = f"MessageID: {str(messageID)}\nSender: {my_username}\nDate: {date.today()}\nSubject: {message}\n"
        print("Message Sent:\n" + test)
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        
        client_socket.send(message_header + message)

        messageID = messageID + 1

        message = message.decode('utf-8')
        if message.startswith("!!getMessage"):
            client_socket.setblocking(1)
            recentMessage = client_socket.recv(1024)
            recentMessage.decode('utf-8')
            recentMessage = str(recentMessage)
            recentMessage = recentMessage.split("'")
            print(recentMessage[1])
            client_socket.setblocking(0)

        message = message.encode('utf-8')
    
    