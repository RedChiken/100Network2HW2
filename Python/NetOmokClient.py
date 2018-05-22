# 20146561 Yu Jae Beom
import socket
import time
import threading
import json


class Client(object):
    def __init__(self):
        self.server_name = 'nsl2.cau.ac.kr'
        self.localhost = 'localhost'
        self.server_port = 26561
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ''
        self.onTimer = False
        self.answer = True
        self.alive = True
        self.send_thread = None
        self.receive_thread = None
    lock = threading.Lock()

    def start(self):
        try:
            self.client_socket.connect((self.server_name, self.server_port))
        except ConnectionRefusedError:
            print("server denied to connect.")
            exit(1)
        try:
            nickname = input(self.client_socket.recv(2048).decode())
            self.client_socket.send(nickname.encode())
            self.receive_thread = threading.Thread(target=self.receive, args=(self.client_socket, self.context))
            self.receive_thread.start()

            self.send_thread = threading.Thread(target=self.send, args=(self.client_socket, self.context))
            self.send_thread.start()
        except ConnectionResetError:
            print("Server disconnected")
            self.client_socket.close()
            self.alive = False
        except KeyboardInterrupt:
            print("Bye bye~")
            self.alive = False
            self.client_socket.close()
        except EOFError:
            return "main thread eof occur"
            self.client_socket.close()

    def send(self, client_socket, context):
        while self.alive:
            try:
                context = input()
                if context == "\\quit":
                    self.alive = False
                client_socket.send(context.encode())
            except EOFError:
                print("Eof Error occur")
                self.alive = False
                break
            except ConnectionResetError:
                print("Connection Reset Error in send thread")
                self.alive = False
                break
        print("send die")

    def receive(self, client_socket, context):
        try:
            while self.alive:
                context = client_socket.recv(2048).decode()
                inst = str(context).split(" > ")[0]
                if inst == "Suggest":
                    self.answer = False
                    threading.Thread(target=self.stopwatch, args=(client_socket, 10)).start()
                elif inst == "gamestart":
                    self.answer = True
                if inst == "map":
                    self.print_board(json.loads(str(context).split(" > ")[1]).get("board"),
                                     json.loads(str(context).split(" > ")[1]).get("row"),
                                     json.loads(str(context).split(" > ")[1]).get("col"))
                else:
                    print(str(context))
        except ConnectionResetError:
            print("server disconnected")
            self.alive = False

        except KeyboardInterrupt:
            print("Bye bye~")
            self.alive = False
        print("receive die")

    def stopwatch(self, client_socket, limit):
        time.sleep(limit)
        if not self.answer:
            client_socket.send(str("n").encode())
            self.answer = True

    def print_board(self, board, row, col):
        print("   ", end="")
        for j in range(0, col):
            print("%2d" % j, end="")
        print()
        print("  ", end="")
        for j in range(0, 2 * col + 3):
            print("-", end="")
        print()
        for i in range(0, row):
            print("%d |" % i, end="")
            for j in range(0, col):
                c = board[i][j]
                if c == 0:
                    print(" +", end="")
                elif c == 1:
                    print(" 0", end="")
                elif c == 2:
                    print(" @", end="")
                else:
                    print("ERROR", end="")
            print(" |")
        print("  ", end="")
        for j in range(0, 2 * col + 3):
            print("-", end="")
        print()


if __name__ == '__main__':
    socket = Client()
    socket.start()
