import socket
import threading
from threading import Thread


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
        # check client is on omok game or not
        self.isOmok = {}
        self.omokPending = False
        self.turn = 0
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
        client.send(str("Please write your NIckname : ").encode())
        thread_nickname = client.recv(2048).decode()
        with self.lock:
            self.nickname[client] = thread_nickname
            self.clientlist.append(client)
            self.isOmok[client] = False
        print(str(thread_nickname) + "is connected" + str(address))
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
                        self.turn += 1
                        self.announce("Turn", self.omokPlayer[self.turn % 2], "now your turn")
                    else:
                        self.announce("Turn", self.omokPlayer[self.turn % 2], "not your turn")
                elif inst == "\\gg":
                    print("gg")
                    self.announce("game end", speaker, "you lose")
                    self.announce("game end", self.omokPlayer[(self.turn + 1) % 2], "you win")
                    for player in self.omokPlayer:
                        self.isOmok[player] = False
                        self.omokPlayer = []
                        self.turn = 0
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
                print("suggest player to play omok")
                listener = split_message[1]
                self.announce("Suggest", self.clientlist[list(self.nickname.values()).index(listener)],
                              self.nickname[speaker] + " wants to play with you. agree? [y/n]")
                self.omokPlayer.append(speaker)
                self.omokPending = True
        else:
            if self.omokPending:
                if input_message == "y":
                    self.omokPlayer.append(speaker)
                    for player in self.omokPlayer:
                        self.isOmok[player] = True
                    self.omokPending = False
                    self.announce("omok", self.omokPlayer[0],
                                  "game started. " + self.nickname[self.omokPlayer[0]] + " plays first.")
                    self.announce("temp", self.omokPlayer[0], "omok map")
                else:
                    self.omokPending = False
                    self.announce("game denied", self.omokPlayer[0], self.nickname[speaker] + " deny to play game")
                    self.omokPlayer = []

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


if __name__ == "__main__":
    try:
        OmokServer(' ', 26561).listen()
    except KeyboardInterrupt:
        print("Bye bye~")
        exit(1)
