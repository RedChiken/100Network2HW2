import socket
import time
import threading


class Client(object):
    def __init__(self):
        self.server_name = 'nsl2.cau.ac.kr'
        self.localhost = 'localhost'
        self.server_port = 26561
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ''

    lock = threading.Lock()

    def start(self):
        try:
            self.client_socket.connect((self.localhost, self.server_port))
        except ConnectionRefusedError:
            print("server denied to connect.")
            exit(1)
        nickname = input(self.client_socket.recv(2048).decode())
        self.client_socket.send(nickname.encode())

        receive_thread = threading.Thread(target=self.receive, args=(self.client_socket, self.context))
        receive_thread.start()

        send_thread = threading.Thread(target=self.send, args=(self.client_socket, self.context))
        send_thread.start()

    def send(self, client_socket, context):
        while True:
            context = input()
            client_socket.send(context.encode())

    def receive(self, client_socket, context):
        while True:
            context = client_socket.recv(2048).decode()
            print(str(context))


if __name__ == '__main__':
    Client().start()
