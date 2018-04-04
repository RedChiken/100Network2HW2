# 20146561 유재범
# SimpleEchoTCPServer.py
#

import socket
from datetime import datetime
import threading


class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.clientNum = 0
        self.clientSize = 0
        print("The server is opened with ", port)

    lock = threading.Lock()

    def listen(self):
        self.sock.listen(5)
        try:
            while True:
                client, address = self.sock.accept()
                client.settimeout(1000)
                threading.Thread(target=self.listen_to_client, args=(client, address)).start()
            client.close()
        except KeyboardInterrupt:
            print("Bye bye~")
            exit(1)

    def listen_to_client(self, client, address):
        with self.lock:
            self.clientNum += 1
            num = self.clientNum
            self.clientSize += 1
            print("Client " + str(num) + " connected. Number of connected clients = " + str(self.clientSize))
        try:
            print("The server is ready to receive on port", address)
            input = client.recv(2048).decode()
            option = input[0]
            if option == "1":
                client.send(input[1:].upper().encode())
            elif option == "2":
                client.send(input[1:].lower().encode())
            elif option == "3":
                client.send((str(socket.gethostbyname(socket.gethostname())) + " " + str(self.port)).encode())
            elif option == "4":
                client.send(str(datetime.now()).encode())
            else:
                print("Wrong input. Bye bye~")
        except KeyboardInterrupt:
            print("Bye bye~")
            exit(1)
        except ConnectionError:
            print("Client disconnect impolitely")
        with self.lock:
            self.clientSize -= 1
            print("Client " + str(num) + " disConnected. Number of connected clients = " + str(self.clientSize))


if __name__ == "__main__":
    try:
        Server(' ', 26561).listen()
    except KeyboardInterrupt:
        print("Bye bye~")
        exit(1)
