import socket
import datetime
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
        self.nickname = {}
        # check client is on omok game or not
        self.isOmok = {}
        print("The server is opened with ", port)

    lock = threading.Lock()

    def listen(self):
        self.sock.listen(8)
        try:
            while True:
                client, address = self.sock.accept()
                client.settimeout(1000)
                t: Thread = threading.Thread(target=self.omok_client_socket, args=(client, address, self.nickname, self.isOmok))
                self.clientlist.append(client)
                self.isOmok[t] = False
                t.start()
        except KeyboardInterrupt:
            print("Bye bye~")
            exit(1)

    def omok_client_socket(self, client, address, nickname, omok):
        client.send(str("Please write your NIckname : ").encode())
        thread_nickname = client.recv(2048).decode()
        print("nickname : " + str(thread_nickname))
        with self.lock:
            nickname[client] = thread_nickname
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

    def protocol(self, speaker, clientinput):
        for client in self.clientlist:
            if speaker != client:
                with self.lock:
                    client.send((self.nickname[speaker] + str(">") + clientinput).encode())
                    

if __name__ == "__main__":
    try:
        OmokServer(' ', 26561).listen()
    except KeyboardInterrupt:
        print("Bye bye~")
        exit(1)