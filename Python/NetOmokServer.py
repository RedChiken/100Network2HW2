import socket
import threading
from threading import Thread
import time
import json

ROW = 10
COL = 10


class OmokServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((' ', self.port))
        # get client socket and return nickname
        self.clientlist = []
        self.omokPlayer = []
        self.nickname = {}
        self.onOmok = False
        # check client is on omok game or not
        self.isOmok = {}
        self.omokPending = False
        self.turn = 0
        self.board = None
        print("The server is opened with ", port)

    lock = threading.Lock()

    def listen(self):
        self.sock.listen(8)
        try:
            while True:
                client, address = self.sock.accept()
                client.settimeout(1000)
                t: Thread = threading.Thread(target=self.omok_client_socket,
                                             args=(client, address))
                t.start()
        except KeyboardInterrupt:
            print("Bye bye~")
            exit(1)

    def omok_client_socket(self, client, address):
        while True:
            client.send(str("Please write your NIckname : ").encode())
            thread_nickname = client.recv(2048).decode()
            if thread_nickname in self.nickname.values():
                print()
                self.announce("Error", client, thread_nickname + " already exist. Plaese write other nickname\n")
            else:
                with self.lock:
                    self.nickname[client] = thread_nickname
                    self.clientlist.append(client)
                    self.isOmok[client] = False
                print(str(thread_nickname) + " is connected" + str(address))
                break
        while True:
            try:
                clientinput = client.recv(2048).decode()
                print(clientinput)
                self.protocol(client, clientinput)
            except KeyboardInterrupt:
                print("Bye bye~")
                break
            except ConnectionResetError:
                print("client disconnect brutally")
                break

    def protocol(self, speaker, input_message):
        split_message = input_message.split()
        if input_message[0] == '\\':
            inst = split_message[0]
            if self.isOmok[speaker]:
                if inst == "\\ss":
                    if self.omokPlayer[self.turn % 2] == speaker:
                        x = int(split_message[1])
                        y = int(split_message[2])
                        if self.check_position(x, y):
                            self.announce("valid", speaker, "valid value")
                            self.broadcast(speaker, input_message)
                            self.board[x][y] = 2 - self.turn % 2
                            if self.board[x][y] == self.check_win(x, y):
                                self.end_game()
                            else:
                                self.turn += 1
                                for client in self.clientlist:
                                    self.announce("map", client,
                                                  json.dumps({"board": self.board, "row": ROW, "col": COL}))
                                    self.announce("Turn", client,
                                                  str(self.nickname[self.omokPlayer[self.turn % 2]]) + " now your turn")
                        else:
                            self.announce("Invalid", speaker, "Invalid position. Please write proper value")
                    else:
                        self.announce("Turn", self.omokPlayer[self.turn % 2], "not your turn")
                elif inst == "\\gg":
                    self.end_game()
            if inst == "\\list":
                print("print nickname, ip, port list of all users")
                for participants in self.clientlist:
                    self.announce("Info", speaker, self.nickname[participants] + " " + str(participants.getpeername()))
            elif inst == "\\w":
                input_message = input_message.replace(inst, "")
                input_message = input_message.strip()
                split_message = input_message.split()
                listener = split_message[0]
                input_message = input_message.replace(listener, "");
                input_message = input_message.strip()
                try:
                    self.whisper(speaker, self.clientlist[list(self.nickname.values()).index(listener)], input_message)
                except ValueError:
                    self.announce("Error", speaker, "There is no " + listener + " in this chat group.")
            elif inst == "\\quit":
                print("quit program")
            elif inst == "\\play":
                if self.onOmok:
                    self.announce("Error", speaker, "Already other users play Omok.")
                else:
                    listener = split_message[1]
                    if self.nickname[speaker] != listener:
                        self.announce("Suggest", self.clientlist[list(self.nickname.values()).index(listener)],
                                    self.nickname[speaker] + " wants to play with you. agree? [y/n]")
                        self.omokPlayer.append(speaker)
                        self.omokPending = True
                    else:
                        self.announce("Error", speaker, "You cannot play omok alone")
        else:
            if self.omokPending:
                if input_message == "y":
                    self.onOmok = True
                    self.omokPending = False
                    self.omokPlayer.append(speaker)
                    for player in self.omokPlayer:
                        self.isOmok[player] = True
                        self.announce("game start" + str(self.omokPlayer.index(player)), player, "game start")
                    self.board = [[0 for row in range(ROW)] for col in range(COL)]
                    self.print_board(self.board)
                    for client in self.clientlist:
                        self.announce("map", client, json.dumps({"board": self.board, "row": ROW, "col": COL}))
                        self.announce("omok", client,
                                      "game started. " + self.nickname[self.omokPlayer[self.turn % 2]] + " plays first.")
                else:
                    self.omokPending = False
                    self.announce("deny", self.omokPlayer[0], "")
                    self.announce("game denied", self.omokPlayer[0], self.nickname[speaker] + " deny to play game")
                    self.omokPlayer = []
            elif self.onOmok:
                if input_message == "n":
                    for client in self.clientlist:
                        self.announce("times up", client,
                                      str(self.nickname[self.omokPlayer[self.turn % 2]]) + " times up.")
                    self.turn += 1
                    self.announce("Turn", self.omokPlayer[self.turn % 2], "now your turn")
            else:
                self.broadcast(speaker, input_message)

    def broadcast(self, speaker, input_message):
        for client in self.clientlist:
            if speaker != client:
                self.whisper(speaker, client, input_message)

    def whisper(self, speaker, listener, input_message):
        with self.lock:
            listener.send((self.nickname[speaker] + str(" > ") + input_message).encode())

    def announce(self, announce_type, client, announce_message):
        with self.lock:
            client.send((announce_type + str(" > ") + announce_message).encode())

    def print_board(self, board):
        print("   ", end="")
        for j in range(0, COL):
            print("%2d" % j, end="")
        print()
        print("  ", end="")
        for j in range(0, 2 * COL + 3):
            print("-", end="")
        print()
        for i in range(0, ROW):
            print("%d |" % i, end="")
            for j in range(0, COL):
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
        for j in range(0, 2 * COL + 3):
            print("-", end="")
        print()

    def check_position(self, x, y):
        if x < 0 or y < 0 or x >= ROW or y >= COL:
            print("error, out of bound!")
            time.sleep(2)
            return False
        elif self.board[x][y] != 0:
            print("error, already used!")
            time.sleep(2)
            return False
        else:
            return True

    def check_win(self, x, y):
        last_stone = self.board[x][y]
        start_x, start_y, end_x, end_y = x, y, x, y
        # check x
        while (start_x - 1 >= 0 and
               self.board[start_x - 1][y] == last_stone):
            start_x -= 1
        while (end_x + 1 < ROW and
               self.board[(end_x + 1)][y] == last_stone):
            end_x += 1
        if end_x - start_x + 1 >= 5:
            return last_stone
        # check y
        start_x, start_y, end_x, end_y = x, y, x, y
        while (start_y - 1 >= 0 and
               self.board[x][start_y - 1] == last_stone):
            start_y -= 1
        while (end_y + 1 < COL and
               self.board[x][end_y + 1] == last_stone):
            end_y += 1
        if end_y - start_y + 1 >= 5:
            return last_stone
        # check diag 1
        start_x, start_y, end_x, end_y = x, y, x, y
        while (start_x - 1 >= 0 and start_y - 1 >= 0 and
               self.board[start_x - 1][start_y - 1] == last_stone):
            start_x -= 1
            start_y -= 1
        while (end_x + 1 < ROW and end_y + 1 < COL and
               self.board[end_x + 1][end_y + 1] == last_stone):
            end_x += 1
            end_y += 1
        if end_y - start_y + 1 >= 5:
            return last_stone
        # check diag 2
        start_x, start_y, end_x, end_y = x, y, x, y
        while (start_x - 1 >= 0 and end_y + 1 < COL and
               self.board[start_x - 1][end_y + 1] == last_stone):
            start_x -= 1
            end_y += 1
        while (end_x + 1 < ROW and start_y - 1 >= 0 and
               self.board[end_x + 1][start_y - 1] == last_stone):
            end_x += 1
            start_y -= 1
        if end_y - start_y + 1 >= 5:
            return last_stone
        return 0

    def end_game(self):
        self.announce("game end", self.omokPlayer[self.turn % 2], "you lose")
        self.announce("game end", self.omokPlayer[(self.turn + 1) % 2], "you win")
        for player in self.omokPlayer:
            self.isOmok[player] = False
            self.omokPlayer = []
            self.turn = 0


if __name__ == "__main__":
    try:
        OmokServer(' ', 26561).listen()
    except KeyboardInterrupt:
        print("Bye bye~")
        exit(1)
