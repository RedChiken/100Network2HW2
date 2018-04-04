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
clientNum = 0
clientNumDic = {}
connectingClient = 0
print("The server is ready to receive on port", serverPort)

while True:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s is serverSocket:
            try:
                (connectionSocket, clientAddress) = s.accept()
                clientNum += 1
                connectingClient += 1
                clientNumDic[connectionSocket] = clientNum
                #이 값을 어떻게 해야 할까? 마지막 값으로 계속 들어가는데
                print("Client " + str(clientNumDic[connectionSocket]) + " connected. Number of connected clients = " + str(connectingClient))
                connectionSocket.setblocking(0)
                inputs.append(connectionSocket)
                message_queues[connectionSocket] = queue.Queue()
            except InterruptedError:
                #다른 에러 확인 필요
                print("socket is not created")
                exit(1)
        else:
            try:
                clientinput= s.recv(2048).decode()
                if clientinput:
                    option = clientinput[0]
                    if option == "1":
                        message_queues[s].put(clientinput[1:].upper().encode())
                    elif option == "2":
                        message_queues[s].put(clientinput[1:].lower().encode())
                    elif option == "3":
                        message_queues[s].put(str((socket.gethostbyname(socket.gethostname())) + " " + str(serverPort)).encode())
                    elif option == "4":
                        message_queues[s].put(str(datetime.now()).encode())
                    # message_queues[s].put(input)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    connectingClient -= 1
                    print("Client " + str(clientNumDic[connectionSocket]) + " disconnected. number of connected clients = " + str(connectingClient))
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

