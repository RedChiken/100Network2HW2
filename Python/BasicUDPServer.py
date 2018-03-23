#
# SimpleEchoUDPServer.py
#

import socket
from datetime import datetime

serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive on port", serverPort)

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    option = message.decode()
    print('Connection requested from', clientAddress)
    if option == "1":
        message, clientAddress = serverSocket.recvfrom(2048)
        modifiedMessage = message.decode().upper()
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)
    elif option == "2":
        message, clientAddress = serverSocket.recvfrom(2048)
        modifiedMessage = message.decode().lower()
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)
    elif option == "3":
        serverSocket.sendto(str(socket.gethostbyname(socket.gethostname())).encode(), clientAddress)
        serverSocket.sendto(str(serverPort).encode(), clientAddress)
    elif option == "4":
        serverSocket.sendto(str(datetime.now()).encode(), clientAddress)
    else:
        print("Wrong input. Bye bye~")
