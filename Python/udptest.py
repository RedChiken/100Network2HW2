#20146561 유재범

import socket
import threading
from datetime import datetime

serverPort = 36561
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
# serverSocket.settimeout(5)


def send():
    while True:
        message = input("input: ")
        serverSocket.sendto(message.encode(), ('localhost', 26561))


def receive():
    while True:
        try:
            message, clientAddress = serverSocket.recvfrom(2048)
        except socket.timeout:
            pass
        print('Connection requested from', clientAddress)
        print(message.decode())


print("The server is ready to receive on port", serverPort)
sthread = threading.Thread(target=send)
rthread = threading.Thread(target=receive)
sthread.start()
rthread.start()
sthread.join()
rthread.join()

