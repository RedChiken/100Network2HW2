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

    lock = threading.Lock()

    def start(self):
        try:
            self.client_socket.connect((self.localhost, self.server_port))
        except ConnectionRefusedError:
            print("server denied to connect.")
            exit(1)
        nickname = input(self.client_socket.recv(2048).decode())
        try:
            self.client_socket.send(nickname.encode())

            receive_thread = threading.Thread(target=self.receive, args=(self.client_socket, self.context))
            receive_thread.start()

            send_thread = threading.Thread(target=self.send, args=(self.client_socket, self.context))
            send_thread.start()

            receive_thread.join()
            send_thread.join()
        except ConnectionResetError:
            print("Server disconnected")
            #1. 서버에게 죽은 거 날리기. 서버는 이를 받고 쓰레드 삭제. 게임 중일 경우 gg.
            #2. threads 죽이기.

    def send(self, client_socket, context):
        while True:
            context = input()
            client_socket.send(context.encode())

    def receive(self, client_socket, context):
        while True:
            try:
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
                #외부로 서버 죽은걸 던져야 함.

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
    Client().start()
