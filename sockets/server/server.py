import socket
import random
import struct
from threading import Thread
import os
import shutil
from pathlib import Path


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():
    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    # raise NotImplementedError('Your implementation here.')
    separator_token = '<'.encode() + random.randbytes(8) + '>'.encode()
    return separator_token


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    # raise NotImplementedError('Your implementation here.')
    message_content = bytearray()
    while True:
        packet = active_socket.recv(1024)

        if packet[-10:] == eof_token:
            message_content += packet[:-10]
            break
        else:
            message_content += packet
    return message_content


def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """
    # raise NotImplementedError('Your implementation here.')
    os.chdir(current_working_directory)
    os.chdir(new_working_directory)
    return os.getcwd()


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    # raise NotImplementedError('Your implementation here.')
    os.chdir(current_working_directory)
    os.mkdir(directory_name)
    return os.getcwd()  # added this on my own


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    # raise NotImplementedError('Your implementation here.')
    os.chdir(current_working_directory)
    if os.path.isfile(object_name):
        os.remove(object_name)
    else:
        os.rmdir(object_name)
    return os.getcwd()


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """
    # raise NotImplementedError('Your implementation here.')
    os.chdir(current_working_directory)
    file = receive_message_ending_with_token(service_socket, 1024, eof_token)
    with open(file_name, "wb") as f:
        f.write(file)
    return os.getcwd()


def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """
    # raise NotImplementedError('Your implementation here.')
    os.chdir(current_working_directory)
    with open(file_name, "rb") as r:
        file_content = r.read()
    file_content_with_token = file_content + eof_token
    service_socket.sendall(struct.pack("i", len(file_content_with_token)) + file_content_with_token)

    # print("file read and sent")
    return os.getcwd()


class ClientThread(Thread):
    def __init__(self, service_socket: socket.socket, address: str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address

    def run(self):
        # print ("Connection from : ", self.address)
        # raise NotImplementedError('Your implementation here.')

        # initialize the connection
        eof_token = generate_random_eof_token()
        # send random eof token
        self.service_socket.sendall(eof_token)  # self implemented

        # establish working directory
        cwd = os.getcwd()

        # send the current dir info
        self.service_socket.sendall(str.encode(cwd) + eof_token)

        # while True:
        # get the command and arguments and call the corresponding method
        while True:
            user_command = self.service_socket.recv(2).decode()
            if user_command == 'cd':
                user_input = receive_message_ending_with_token(self.service_socket, 1024, eof_token)
                cwd = handle_cd(cwd, user_input.decode()[1:])

            elif user_command == 'mk':
                local_read = self.service_socket.recv(3).decode()
                if user_command + local_read == 'mkdir':
                    user_input = receive_message_ending_with_token(self.service_socket, 1024, eof_token)
                    cwd = handle_mkdir(cwd, user_input.decode()[1:])
                else:
                    break

            elif user_command == 'rm':
                user_input = receive_message_ending_with_token(self.service_socket, 1024, eof_token)
                cwd = handle_rm(cwd, user_input.decode()[1:])

            elif user_command == 'ul':
                file_name = receive_message_ending_with_token(self.service_socket, 1024, eof_token)[1:]
                cwd = handle_ul(cwd, file_name.decode(), self.service_socket, eof_token)
                # print("success")

            elif user_command == 'dl':
                filename = receive_message_ending_with_token(self.service_socket, 1024, eof_token)[1:].decode()
                cwd = handle_dl(cwd, filename, self.service_socket, eof_token)

            else:
                break
            # send current dir info
            self.service_socket.sendall(cwd.encode() + eof_token)
        self.service_socket.close()
        # print('Connection closed from:', self.address)


def main():
    HOST = "127.0.0.1"
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        # raise NotImplementedError('Your implementation here.')
        while True:
            conn, addr = s.accept()
            client_thread = ClientThread(conn, addr)
            client_thread.start()


if __name__ == '__main__':
    main()
