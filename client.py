import socket
import select
import errno
import sys
from datetime import date

messageID = 0
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 6789

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

commands = ["!!help", "!!getMessage", "!!leave", "!!users", "!!rooms", "!!join"]

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
    
# Get list of users on server
def get_users():
    try:
        client_socket.setblocking(True)

        client_count = int(receive_message())

        if client_count < 1:
            raise Exception('No Other Users on the Server')

        print("Other Users on server:")

        for i in range(client_count):
            message = receive_message()
            print(message)
                
        client_socket.setblocking(False)
    except Exception as e:
        print(str(e))
    client_socket.setblocking(False)

def get_rooms():
    try:
        client_socket.setblocking(True)

        rooms_count = int(receive_message())

        print("Rooms on Server:")
        print(rooms_count)
        for i in range(rooms_count):

            message = receive_message()
            print(message)
                
        client_socket.setblocking(False)
    except Exception as e:
        print(str(e))
    client_socket.setblocking(False)

isUsed = True
while isUsed:
    my_username = input("Username: ")

    send_message(my_username)
    client_socket.setblocking(1)
    isUsed = client_socket.recv(1)
    client_socket.setblocking(0)
    isUsed = isUsed.decode('utf-8')
    
    if isUsed == "1":
        print("Please input a unique username")
    else:
        break

get_users()

client_socket.setblocking(1)
recentMessage = client_socket.recv(1024)
recentMessage = str(recentMessage.decode('utf-8'))
recentMessage = recentMessage.split("\n")
print("\nRecent Messages:")
length = recentMessage[0]
if length == '0':
    print("None")
else:
    for i in range(1, len(recentMessage), 4):
        messageID = int(recentMessage[i])
        subject = recentMessage[i + 1]
        postDate = recentMessage[i + 2]
        username = recentMessage[i + 3]
        print(f"MessageID: {str(messageID)}\nSender: {username}\nDate: {postDate}\nSubject: {subject}\n")
    messageID = messageID + 1
client_socket.setblocking(0)

print("Welcome " + my_username + "! Type in !!help for all commands in the chat room!")


def recieveAllMessages():
    global messageID
    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # Receive and decode username
            username = client_socket.recv(username_length).decode('utf-8')

            # Now do the same for message
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
        # This is normal on non blocking connections
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()


    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: {}'.format(str(e)))
        sys.exit()

while True:

    # Wait for user to input a message
    print("Enter Message, press 'Enter' to post.")
    message = input(f'{my_username}: ')
    print()

    # If message is not empty - send it
    if message:
        
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        recieveAllMessages()
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        
        client_socket.send(message_header + message)

        message = message.decode('utf-8')
        test = f"MessageID: {str(messageID)}\nSender: {my_username}\nDate: {date.today()}\nSubject: {message}\n"
        # Each Command
        if message.startswith("!!"):
            message = message.lower()
            if message.startswith("!!getmessage"):
                client_socket.setblocking(1)
                recentMessage = client_socket.recv(1024)
                recentMessage.decode('utf-8')
                recentMessage = str(recentMessage)
                recentMessage = recentMessage.split("'")
                print(recentMessage[1])
                client_socket.setblocking(0)
            elif message.startswith("!!help"):
                print("List of Commands:")
                print(f"!!getMessage {{id}}: Get Message with Specific Message ID as Parameter.")
                print("!!help: Get List of Commands.")
                print("!!leave: Disconnect from the Server.")
                print(f"!!leave {{chat name}}: Leave a Specific Chat Room.")
                print("!!users: Get List of Other Users in Chat Room.")
                print("!!rooms: Get List of Existing Chat Rooms.")
                print(f"!!join {{chat name}}: Join Room with the Specified Name or Create Room if it Doesn't Exist.")
                print()
            elif message.startswith("!!users"):
                get_users()
            elif message.startswith("!!rooms"):
                get_rooms()
            elif message.startswith("!!") and message.split()[0] not in commands: 
                print("Command not recognized, use !!help to see list of available commands")
        else:
            print("Message Sent:\n" + test)
            messageID = messageID + 1

    
    