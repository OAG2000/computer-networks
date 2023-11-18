import socket
import json

print("\033c")

PORT = 4000
HEADER = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECTED!"
LIST_REQUEST = "!LIST_REQUEST!"
MESSAGE_PREFIX = "!SEND_MESSAGE!"
VIEW_MESSAGES = "!VIEW_MESSAGES!"

SERVER = "localhost"
ADDRESS = (SERVER, PORT)

def encrypt_message(s, key):
    ans = ""
    n = int((len(s) - 1) // key + 1)
    mat = [[' ' for _ in range(key)] for _ in range((len(s) - 1) // key + 1)]
    k = 0

    for i in range(n):
        for j in range(key):
            if k < len(s):
                mat[i][j] = s[k]
                k += 1

    for i in range(key):
        for j in range(n):
            ans += mat[j][i]

    return ans

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print(f"[UNABLE TO CREATE SOCKET] : {err}...\n")
    exit(0)

try:
    client.connect(ADDRESS)
except socket.error as err:
    print(f"[UNABLE TO CONNECT TO THE SERVER] : {err}...\n")
    exit(0)

def sendMessage(msg, key):
    encrypted_msg = encrypt_message(msg, key)
    json_object = {'msg': encrypted_msg, "key": key, "decrypted": msg}
    msg = json.dumps(json_object)
    try:
        client.send(msg.encode(FORMAT))
    except socket.error as err:
        print(f"[UNABLE TO SEND MESSAGE TO THE SERVER] : {err}...\n")
        exit(0)

def receiveMessage():
    try:
        server_msg = client.recv(HEADER).decode(FORMAT)
    except socket.error as err:
        print(f"[UNABLE TO RECEIVE MESSAGE FROM THE SERVER] : {err}...\n")
        exit(0)
    print(f"Server : {server_msg}")
    return server_msg

def listClients():
    json_object = {'msg': LIST_REQUEST}
    msg = json.dumps(json_object)
    try:
        client.send(msg.encode(FORMAT))
    except socket.error as err:
        print(f"[UNABLE TO SEND LIST REQUEST TO THE SERVER] : {err}...\n")
        exit(0)
    receiveMessage()

def viewMessages():
    json_object = {'msg': VIEW_MESSAGES}
    msg = json.dumps(json_object)
    try:
        client.send(msg.encode(FORMAT))
    except socket.error as err:
        print(f"[UNABLE TO SEND VIEW MESSAGES REQUEST TO THE SERVER] : {err}...\n")
        exit(0)
    server_msg = receiveMessage()
    print("\n".join(server_msg.split(',')))

user_name = input("Enter your name: ")
json_object = {'name': user_name, 'msg': '!FIRST_CONNECTION!'}
msg = json.dumps(json_object)
client.send(msg.encode(FORMAT))

connected = True
key = int(input("Enter the Key: "))
while connected:
    action = input("Enter 'm' to send a message, 'l' to list clients, 'v' to view messages, or 'q' to quit: ")
    if action.lower() == 'm':
        target_client = input("Enter the target client's name: ")
        text = input("Enter the Text: ")
        message = f"{MESSAGE_PREFIX}{target_client}:{text}"
        sendMessage(message, key)
        receiveMessage()
    elif action.lower() == 'l':
        listClients()
    elif action.lower() == 'v':
        viewMessages()
    elif action.lower() == 'q':
        connected = False
    else:
        print("Invalid action. Please enter 'm', 'l', 'v', or 'q'.")

json_object = {'msg': DISCONNECT_MESSAGE}
msg = json.dumps(json_object)
client.send(msg.encode(FORMAT))

print("Connection Closed!")
client.close()