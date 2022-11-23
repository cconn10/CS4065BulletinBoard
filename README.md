# Simple Bulletin Board Using Socket Programming

## Created by John Thompson and Colin Conn

This application is a simple bulletin

## How to Install and Run:
1. Download `Client.py` and `Server.py`
2. Change the ip in both files to your IPv4
  1. Try `127.0.0.1` if you're having trouble
3. Open up two different terminals.
4. On one terminal, navigate to the folder containing `Server.py` and run it with `py Server.py`.
5. On the other terminal, navigate to the folder containing `Client.py` and run it with `py Client.py`.
6. Enter your username on the client.
7. Repeat for as many clients as you wish to have.
Now you can enter in the content of your message and it will send to your server. Use the Command `!!help` to get access to all commands that you can use in the server.

## Quirks with the Program
The program has a couple quirks that are caused by not having threading implemented (See second paragraph of **Major Issues Encountered**).
- You must send a message to receive messages from other users
- If you use !!leave, you must send another message (this message is not sent to other users)


## Major Issues Encountered

Our main source of issues came from generating message ID's for each message sent in our chats. The first problem we ran into was getting the client to recieve the message's ID from the server. We fixed this by having a variable on the client track the message ID as messages were received. However, this caused issues when users were able to receive messages from multiple groups and be excluded. Because the ID was tracked by the client, a message sent in a private channel could be tracked by one user but not by another.

We had issues implementing threading into our project. We originally wanted to use threading to avoid having to send a message to get the messages that have been sent previously. The program uses input() to get a user's message, which blocks the user from receiving any messages, and our intentionw as to get around this using threading. If we were to continue working on the project in the future we would definitely implement threading or use a library like pygame to capture inputs.
