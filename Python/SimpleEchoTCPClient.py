#
# SimpleEchoTCPClient.py
#

from socket import *

serverName = 'nsl2.cau.ac.kr'
localhost = 'localhost'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((localhost, serverPort))

print("The client is running on port", clientSocket.getsockname()[1])

print("Press number of option to select it\n"
      "option 1) convert text to UPPER-case letters\n"
      "option 2) convert text to LOWER-case letters\n"
      "option 3) ask the server what is the IP address and port number of the client\n"
      "option 4) ask the server what the current time on the server is\n"
      "option 5) exit client program\n")

option = input("option : ")
clientSocket.send(option.encode())
if option == '1':
    #lowercase to uppercase
    message = input('Input lowercase sentence: ')
    clientSocket.send(message.encode())
    modifiedMessage = clientSocket.recv(2048)
    print('Reply from server:', modifiedMessage.decode())

elif option == '2':
    #uppercase to lowercase
    message = input('Input uppercase sentence: ')
    clientSocket.send(message.encode())
    modifiedMessage = clientSocket.recv(2048)
    print('Reply from server:', modifiedMessage.decode())

elif option == '3':
    #get server's ip and port number
    modifiedMessage = clientSocket.recv(2048)
    print('Reply from server:', modifiedMessage.decode())
    modifiedMessage = clientSocket.recv(2048)
    print('Reply from server:', modifiedMessage.decode())

elif option  == '4':
    #get server's time
    modifiedMessage = clientSocket.recv(2048)
    print('Reply from server:', modifiedMessage.decode())

elif option == '5':
    #exit
    exit()

else:
    #error case
    print("")
clientSocket.close()
