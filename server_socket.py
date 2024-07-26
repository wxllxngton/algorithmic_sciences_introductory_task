#!/usr/bin/python3
"""
Server script that binds to a port and responds to connections, allowing an unlimited number of concurrent connections.
"""

import sys
import asyncio
import socket
import subprocess
from config import linuxpath

global_reread_on_query = False
client_queues = {}

async def handle_client(reader, writer):
    """
    Handles the communication with a connected client.

    Parameters:
    reader (asyncio.StreamReader): The stream reader for reading data from the client.
    writer (asyncio.StreamWriter): The stream writer for sending data to the client.
    """
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")

    # Initialize the re_read_queue for this client
    client_queues[addr] = []

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received {message} from {addr}")

            response = await search_term_in_linuxpath(addr, message)
            print(client_queues[addr])
            writer.write(response.encode())
            await writer.drain()

    finally:
        print(f"Closing connection from {addr}")
        writer.close()
        await writer.wait_closed()
        # Remove the client's queue when the connection closes
        del client_queues[addr]

async def search_term_in_linuxpath(client_addr, message):
    """
    Searches for a term in the specified file path using grep.

    Parameters:
    client_addr (tuple): The address of the client.
    message (str): The message containing the search term from the client.

    Returns:
    str: The response indicating whether the term was found or not.
    """
    def search_string_with_grep(file_path, search_string):
        """
        Searches for a string in a file using grep.

        Parameters:
        file_path (str): The path to the file.
        search_string (str): The string to search for.

        Returns:
        bool: True if the string is found, False otherwise.
        """
        try:
            subprocess.check_output(['grep', search_string, file_path])
            return True
        except subprocess.CalledProcessError:
            return False

    # Access the re_read_queue for the specific client
    global client_queues

    # print(f"Start Re_read_queue for {client_addr}: ", client_queues[client_addr])
    re_read_queue = client_queues.get(client_addr, [])

    if global_reread_on_query:
        if message in re_read_queue:
            re_read_queue.remove(message)
        result = search_string_with_grep(linuxpath, message)
        if result:
            response = "STRING EXISTS\n"
        else:
            response = "STRING NOT FOUND\n"
            if message not in re_read_queue:
                re_read_queue.append(message)
                # print(f"Updated Re_read_queue for {client_addr}: ", client_queues[client_addr])
        # Process all terms in re_read_queue
        for term in re_read_queue.copy():  # Use a copy to avoid modification issues
            if search_string_with_grep(linuxpath, term):
                re_read_queue.remove(term)
    else:
        # Use a single read of the file for efficiency
        file_contents = read_file_contents()
        if message in file_contents:
            response = "STRING EXISTS\n"
        else:
            response = "STRING NOT FOUND\n"

    # print(f"Final Re_read_queue for {client_addr}: ", client_queues[client_addr])

    return response

def read_file_contents():
    """
    Reads the contents of the file specified by linuxpath.

    Returns:
    str: The contents of the file.
    """
    try:
        with open(linuxpath, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        return ""

async def server_program():
    """
    Starts a server that listens on a specified port and handles client connections.
    The server receives messages from clients and sends responses back.
    """
    # Get the hostname
    host = socket.gethostname()
    port = 5000  # Initiate port number above 1024

    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server started on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'True':
        global_reread_on_query = True
    asyncio.run(server_program())
