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
        self.onTimer = False
        self.answer = False

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
            if self.onTimer:
                self.answer = True

    def receive(self, client_socket, context):
        while True:
            context = client_socket.recv(2048).decode()
            inst = str(context).split(" > ")[0]
            if inst == "Suggest" or inst == "Turn":
                self.answer = False
                threading.Thread(target=self.stopwatch, args=(client_socket, 10)).start()
            elif inst == "game end":
                self.onTimer = False
            print(str(context))

    def stopwatch(self, client_socket, limit):
        time.sleep(limit)
        if not self.answer:
            print("n")
            client_socket.send(str("n").encode())


if __name__ == '__main__':
    Client().start()
