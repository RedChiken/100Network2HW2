#20146561 유재범
# SimpleEchoTCPServer.py
#

import socket
from datetime import datetime
import select, sys, queue

serverPort = 26561
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setblocking(0)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
inputs = [serverSocket]
outputs = []
message_queues = {}

print("The server is ready to receive on port", serverPort)

while True:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s is serverSocket:
            try:
                (connectionSocket, clientAddress) = s.accept()
                connectionSocket.setblocking(0)
                inputs.append(connectionSocket)
                message_queues[connectionSocket] = queue.Queue()
            except InterruptedError:
                #다른 에러 확인 필요
                print("socket is not created")
                exit(1)
        else:
            try:
                option = s.recv(2048).decode()
                if option:
                    message_queues[s].put(option)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    input.remove(s)
                    s.close()
                    del message_queues[s]
            except KeyboardInterrupt:
                print("Bye bye~")
                exit(1)

    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            outputs.remove(s)
        else:
            s.send(next_msg)

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]

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

