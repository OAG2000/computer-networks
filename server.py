import random
import socket
import threading
import json

print("\033c")

PORT = 4000
HEADER = 1024
FORMAT = "utf-8"
MAX_CLIENT = 5
DISCONNECT_MESSAGE = "!DISCONNECTED!"
FIRST_CONNECTION = "!FIRST_CONNECTION!"
LIST_REQUEST = "!LIST_REQUEST!"
MESSAGE_PREFIX = "!SEND_MESSAGE!"
VIEW_MESSAGES = "!VIEW_MESSAGES!"
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)

user_list = {}
messages_received = {}  # Dictionary to store messages received by each client


try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print(f"[UNABLE TO CREATE SOCKET] : {err}...\n")
    exit(0)

"""
A server has a bind() method which binds it to a specific IP and port so that it can listen to incoming requests on that IP and port.  
"""
try:
    server.bind(ADDRESS)
except socket.error as err:
    print(f"[UNABLE TO BIND TO THE SPECIFIC IP AND PORT] : {err}...\n")
    exit(0)

def decrypt_message(s, key):
    ans = ""
    mat = [[' ' for _ in range(key)] for _ in range((len(s) - 1) // key + 1)]
    k = 0
    n = int((len(s) - 1) // key + 1)
    for i in range(key):
        for j in range(n):
            if k < len(s):
                mat[j][i] = s[k]
                k += 1

    for i in range(n):
        for j in range(key):
            ans += mat[i][j]

    return ans

def send_message(msg, client_connection):
    try:
        client_connection.send(msg.encode(FORMAT))
    except socket.error as err:
        print(f"[UNABLE TO SEND MESSAGE] : {err}...\n")

def decode_message(data, client_connection, client_address):
    global user_list, messages_received
    client_object = json.loads(data)
    if client_object['msg'] == FIRST_CONNECTION:
        user_list[client_address] = {
            "name":  client_object['name'],
            "key": random.randint(1, 10),  # Generate a random key for the client
        }
        messages_received[client_address] = []  # Initialize an empty list for received messages
        return f"joined the server."
    elif client_object['msg'] == LIST_REQUEST:
        clients_list = [user_list[addr]['name'] for addr in user_list if addr != client_address]
        msg = json.dumps({"msg": clients_list})
        send_message(msg, client_connection)
        return ""
    elif client_object['msg'] == VIEW_MESSAGES:
        # Send the messages received by the client
        client_messages = messages_received.get(client_address, [])
        msg = json.dumps({"msg": ",".join(client_messages)})
        send_message(msg, client_connection)
        return ""
    elif client_object['msg'].startswith(MESSAGE_PREFIX):
        target_client_name, message = client_object['msg'][len(MESSAGE_PREFIX):].split(':')
        target_client_address = [addr for addr, info in user_list.items() if info['name'] == target_client_name]
        if target_client_address:
            send_message(message, target_client_address[0])
            messages_received[target_client_address[0]].append(f"From {user_list[client_address]['name']}: {message}")
            return f"Message sent to {target_client_name}."
        else:
            return f"Target client {target_client_name} not found."
    else:
        key = int(client_object["key"])
        msg = client_object["msg"]
        decrypted_msg = client_object["decrypted"]
        send_message(f"Message Received : {msg}", client_connection)
        messages_received[client_address].append(f"From {user_list[client_address]['name']}: {decrypted_msg}")
        return decrypted_msg

def view_messages(client_address):
    global messages_received
    if client_address in messages_received:
        return messages_received[client_address]
    else:
        return ["No messages received."]

def handle_client(client_connection, client_address):
    global user_list
    print(f"[NEW CONNECTION] connected.\n")
    connected = True
    while connected:
        try:
            data = client_connection.recv(HEADER).decode(FORMAT)
        except socket.error as err:
            print(f"[UNABLE TO RECEIVE MESSAGE FROM {user_list[client_address]['name']}] : {err}...\n")
            del user_list[client_address]
            exit(0)

        if len(data) == 0:
            continue

        msg = decode_message(data, client_connection, client_address)
        if msg == DISCONNECT_MESSAGE:
            connected = False
            print(f"{user_list[client_address]['name']} is offline now.")
            continue
        if client_address in user_list and 'key' in user_list[client_address]:
            msg = decrypt_message(msg, int(user_list[client_address]['key']))
        print(f"{user_list[client_address]['name']} : {msg}")

    del user_list[client_address]
    client_connection.close()

def start():
    server.listen(MAX_CLIENT)
    print(f"[LISTENING] server is listening on {SERVER}\n")
    connected = True
    while connected:
        try:
            client_connection, client_address = server.accept()
        except socket.error as err:
            print(f"[UNABLE TO CONNECT TO THE CLIENTS] : {err}...\n")
            exit(0)

        try:
            thread = threading.Thread(target=handle_client, args=(client_connection, client_address))
            thread.start()
        except socket.error as err:
            print(f"[UNABLE TO CREATE THREAD] : {err}...\n")
            exit(0)

        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}\n")

print("[STARTING] server is starting...\n")
start()