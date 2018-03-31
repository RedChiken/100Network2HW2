#20146561 유재범
# SimpleEchoTCPServer.py
#

import socket
from datetime import datetime
import signal

serverPort = 26561
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print("The server is ready to receive on port", serverPort)

while True:
    try:
        (connectionSocket, clientAddress) = serverSocket.accept()
        print('Connection requested from', clientAddress)
        option = connectionSocket.recv(2048).decode()
    except KeyboardInterrupt:
        print("Bye bye~")
        exit(1)
    if option == "1":
        message = connectionSocket.recv(2048)
        modifiedMessage = message.decode().upper()
        connectionSocket.send(modifiedMessage.encode())
    elif option == "2":
        message = connectionSocket.recv(2048)
        modifiedMessage = message.decode().lower()
        connectionSocket.send(modifiedMessage.encode())
    elif option == "3":
        connectionSocket.send(str(socket.gethostbyname(socket.gethostname())).encode())
        connectionSocket.send(str(serverPort).encode())
    elif option == "4":
        connectionSocket.send(str(datetime.now()).encode())
    else:
        print("Wrong input. Bye bye~")
    connectionSocket.close()

