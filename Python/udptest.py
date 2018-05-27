#20146561 유재범

import socket
import threading
import time
import sys
from datetime import datetime

serverPort = 36561
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
# serverSocket.settimeout(5)


def send():
    serverSocket.sendto(str("hi ukio").encode(), ('localhost', 26561))
    while True:
        message = input("input: ")
        serverSocket.sendto(message.encode(), ('localhost', 26561))


def receive():
    message = b''
    clientAddress = None
    while True:
        try:
            message, clientAddress = serverSocket.recvfrom(2048)
        except ConnectionResetError:
            print("ukio is not here")
            pass
        print('Connection requested from', clientAddress)
        print(message.decode())
        # TODO : input 한번 씹힘.



print("The server is ready to receive on port", serverPort)
sthread = threading.Thread(target=send)
rthread = threading.Thread(target=receive)
rthread.start()
sthread.start()
sthread.join()
rthread.join()

