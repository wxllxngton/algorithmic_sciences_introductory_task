#!/usr/bin/python3
"""
Client script that connects to a server, sends messages, and receives responses.
"""

import socket

def client_program():
    """
    Connects to a server, sends messages, and receives responses.
    The connection continues until the user types 'bye'.
    """
    host = socket.gethostname()  # as both code is running on same PC
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate the client socket

    try:
        client_socket.connect((host, port))  # connect to the server
        print("Connected to server at {}:{}".format(host, port))

        message = input(" -> ")  # take input

        while message.lower().strip() != 'bye':
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response

            print('Received from server: ' + data)  # show in terminal

            message = input(" -> ")  # again take input

    except ConnectionError as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()  # close the connection
        print("Connection closed")

if __name__ == '__main__':
    client_program()
