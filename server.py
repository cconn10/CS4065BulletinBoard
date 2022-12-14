import socket
import select
from datetime import date

messageID = 0
HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 6789

messageID = 0
totalMessageList = {}
messageList = {}
messageList['public'] = []

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set socket options
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Server informs operating system that it's going to use given IP and port
server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

room_users = {"public": []}

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

def disconnect_user(clients, disconnected_user):

    print('Closed connection from: {}'.format(clients[disconnected_user]['data'].decode('utf-8')))
    sockets_list.remove(disconnected_user)

    send_message_all('{} left the server!'.format(clients[disconnected_user]['data'].decode('utf-8')))

    del clients[disconnected_user]


# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        # Client closed connection violently
        return False

def send_message_all(message): 
    for socket in sockets_list:
        if socket is not server_socket:
            socket.send(
                f"{len('server'):<{HEADER_LENGTH}}".encode('utf-8') +
                'Server'.encode('utf-8') +
                f"{len(message):<{HEADER_LENGTH}}".encode('utf-8') + 
                (message.encode('utf-8')))

def get_users(clients):
    client_count_header = f"{len(clients):<{HEADER_LENGTH}}".encode('utf-8')

    # Sends number of clients currently connected - 1, so as to not include the client it is sending to
    client_socket.send(client_count_header + str(len(clients)-1).encode())
    for client in clients:
        if clients[client] != user:
            print()
            client_socket.send(clients[client]['header'] + clients[client]['data'])

def get_rooms():
    room_count_header = f"{len(room_users):<{HEADER_LENGTH}}".encode('utf-8')

    # Sends number of clients currently connected - 1, so as to not include the client it is sending to
    client_socket.send(room_count_header + str(len(room_users)).encode())
    for room in room_users:
        print()
        client_socket.send(f"{len(room):<{HEADER_LENGTH}}".encode('utf-8') + room.encode('utf-8'))

while True:

    # Returns reading, writing, and exception sockets:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # Checks for new connection
        if notified_socket == server_socket:

            # Get new socket and ip/port set for newly connected client
            client_socket, client_address = server_socket.accept()

            # Receive client's name
            isUsernameUsed = True
            # Loop to check if Username is already used
            while isUsernameUsed:
                user = receive_message(client_socket)

                # If false, client disconnected before they sent their name
                if user is False:
                    continue         
                
                isUsernameUsed = False
                for client in clients:
                    if user['data'] == clients[client]['data']:
                        isUsernameUsed = True
                if isUsernameUsed:
                    client_socket.send('1'.encode('utf-8'))
                else:
                    client_socket.send('0'.encode('utf-8'))

            sockets_list.append(client_socket)

            # Save username and username header
            clients[client_socket] = user
            room_users["public"].append(client_socket) 

            client_count_header = f"{len(clients):<{HEADER_LENGTH}}".encode('utf-8')

            # Sends number of clients currently connected - 1, so as to not include the client it is sending to
            client_socket.send(client_count_header + str(len(clients)-1).encode())
            for client in clients:
                if clients[client] != user:
                    print()
                    client_socket.send(clients[client]['header'] + clients[client]['data'])


            # Send last 2 messages to new client, it puts last 2 messages all in one string for more consistent results
            string = '0'
            client_socket.setblocking(1)
            if len(messageList['public']) >= 2:
                string = '2' + "\n" + str(messageList['public'][-2]['MessageID']) + "\n" + str(messageList['public'][-2]['Subject']) + "\n" + str(messageList['public'][-2]['Date']) + "\n" + str(messageList['public'][-2]['Sender'])\
                         + "\n" + str(messageList['public'][-1]['MessageID']) + "\n" + str(messageList['public'][-1]['Subject']  + "\n" + str(messageList['public'][-1]['Date']) + "\n" + str(messageList['public'][-1]['Sender']))
            elif len(messageList['public']) == 1:
                string = '1' + "\n" + str(str(messageList['public'][-1]['MessageID']) + "\n" + str(messageList['public'][-1]['Subject'])  + "\n" + str(messageList['public'][-1]['Date']) + "\n" + str(messageList['public'][-1]['Sender']))
            client_socket.send(string.encode('utf-8'))
            client_socket.setblocking(0)
                

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

            send_message_all('{} joined the server!'.format(user['data'].decode('utf-8')))
            

        # Else existing socket is sending a message
        else:
            
            # Receive message
            message = receive_message(notified_socket)

            # If false, client disconnected
            if message is False:
                disconnect_user(clients, notified_socket)
                continue

            # Get user by socket, so we know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            archiveMessage = str(f'{user["data"].decode("utf-8")} > {message["data"].decode("utf-8")} > {str(date.today())}')
            messageText = message['data'].decode("utf-8").lower()
            # Commands
            if(messageText.startswith("!!")):
                if messageText.startswith("!!leave"):
                    if(len(messageText) > 7):
                        room_users[messageText[8:]].remove(notified_socket)
                    else:
                        disconnect_user(clients, notified_socket)
                        notified_socket.shutdown(socket.SHUT_RDWR)
                        notified_socket.close()
                elif messageText.startswith("!!users"):
                    get_users(clients)
                elif messageText.startswith("!!rooms"):
                    get_rooms()
                elif messageText.startswith("!!getmessage"):
                    try:                           
                        # Get ID and check to see if it is valid
                        idCmd = int(messageText[12:])
                        Subject = totalMessageList[idCmd]
                        print(f'{user["data"].decode("utf-8")} requested the message: {Subject}')
                        # If ID is valid print message
                        if idCmd >= 0 and idCmd < len(totalMessageList):
                            notified_socket.send(f'Message Content of ID {idCmd}: {Subject}'.encode('utf-8'))

                    except:
                        notified_socket.send("Wrong parameters or messageID out of range, ex: !!getMessage 1".encode('utf-8'))
                elif messageText.startswith("!!join"):
                    roomName = messageText[7:]
                    # Create room if room does not exist
                    if roomName not in room_users:
                        messageList[roomName] = []
                        room_users[roomName] = []
                    room_users[roomName].append(notified_socket) 
                continue
            else:
                # Create dictionary for each group and all groups together
                for room in room_users:
                    if notified_socket in room_users[room]:
                        dict = {}
                        dict['MessageID'] = len(messageList[room])
                        dict['Sender'] = user["data"].decode("utf-8")
                        dict['Date'] = str(date.today())
                        dict['Subject'] = message["data"].decode("utf-8")
                        messageList[room].append(dict)
                totalMessageList[messageID] = message["data"].decode("utf-8")
                messageID = messageID + 1

            for room in room_users:
                currentRoom = room_users[room]
                if notified_socket in currentRoom:
                    # Iterate over connected clients and broadcast message
                    for client_socket in currentRoom:
                        
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