import os
import socket
import struct


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
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
        packet = active_socket.recv(buffer_size)
        if packet[-10:] == eof_token:
            message_content += packet[:-10]
            break
        else:
            message_content += packet
    return message_content


def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """

    # raise NotImplementedError('Your implementation here.')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        s.connect((host, port))
        print('Connected to server at IP:', host, 'and Port:', port)
        eof_token = s.recv(10)
        print('Handshake Done. EOF is:', eof_token)
        cwd = receive_message_ending_with_token(s, 1024, eof_token)
        print(cwd.decode())
        return s, eof_token


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    # raise NotImplementedError('Your implementation here.')
    client_socket.sendall(command_and_arg.encode() + eof_token)
    print(receive_message_ending_with_token(client_socket, 1024, eof_token).decode())


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    # raise NotImplementedError('Your implementation here.')
    client_socket.sendall(command_and_arg.encode() + eof_token)
    print(receive_message_ending_with_token(client_socket, 1024, eof_token).decode())


def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    # raise NotImplementedError('Your implementation here.')
    client_socket.sendall(command_and_arg.encode() + eof_token)
    print(receive_message_ending_with_token(client_socket, 1024, eof_token).decode())


def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    # raise NotImplementedError('Your implementation here.')
    client_socket.sendall(command_and_arg.encode() + eof_token)
    file_name = command_and_arg[3:]
    with open(file_name.encode(), "rb") as r:
        file_content = r.read()
    file_content_with_token = file_content + eof_token
    client_socket.sendall(file_content_with_token)
    print(receive_message_ending_with_token(client_socket, 1024, eof_token).decode())


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """
    # raise NotImplementedError('Your implementation here.')
    # print("in issue dl on client")
    file_name = command_and_arg[2:]
    client_socket.sendall(command_and_arg.encode() + eof_token)
    buffer_size = struct.unpack("i", client_socket.recv(struct.calcsize("i")))[0]
    file_content = receive_message_ending_with_token(client_socket, buffer_size, eof_token)

    with open(file_name, "wb") as f:
        f.write(file_content)

    print(receive_message_ending_with_token(client_socket, 1024, eof_token).decode())


def main():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    # raise NotImplementedError('Your implementation here.')

    # initialize
    client_socket, eof_token = initialize(HOST, PORT)
    # while True:
    # get user input
    while True:
        user_input = input("Enter the command you want to execute")
        # call the corresponding command function or exit
        # sample user input is "cd ..". All inputs are strings with whitespace as separator.
        if user_input[0:2].lower() == 'cd':
            issue_cd(user_input, client_socket, eof_token)
        elif user_input[0:5].lower() == 'mkdir':
            issue_mkdir(user_input, client_socket, eof_token)
        elif user_input[0:2].lower() == 'rm':
            issue_rm(user_input, client_socket, eof_token)
        elif user_input[0:2].lower() == 'ul':
            issue_ul(user_input, client_socket, eof_token)
        elif user_input[0:2].lower() == 'dl':
            issue_dl(user_input, client_socket, eof_token)
        elif user_input.lower() == 'exit':
            client_socket.close()
            break

    # print('Exiting the application.')


if __name__ == '__main__':
    main()
