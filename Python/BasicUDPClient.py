# 20146561 유재범
# SimpleEchoUDPClient.py
#

from socket import *
import time


def run_program():
    start_time = time.time()
    server_name = 'nsl2.cau.ac.kr'
    localhost = 'localhost'
    server_port = 36561
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.bind(('', 5432))

    print("The client is running on port", client_socket.getsockname()[1])

    print("Press number of option to select it\n"
          "option 1) convert text to UPPER-case letters\n"
          "option 2) convert text to LOWER-case letters\n"
          "option 3) ask the server what is the IP address and port number of the client\n"
          "option 4) ask the server what the current time on the server is\n"
          "option 5) exit client program\n")
    try:
        option = input("option : ")
        client_socket.sendto(option.encode(), (server_name, server_port))
        if option == '1':
            # lowercase to uppercase
            message = input('Input lowercase sentence: ')
            client_socket.sendto(message.encode(), (server_name, server_port))
            modified_message, server_address = client_socket.recvfrom(2048)
            print('Reply from server:', modified_message.decode())

        elif option == '2':
            # uppercase to lowercase
            message = input('Input uppercase sentence: ')
            client_socket.sendto(message.encode(), (server_name, server_port))
            modified_message, server_address = client_socket.recvfrom(2048)
            print('Reply from server:', modified_message.decode())

        elif option == '3':
            # get server's ip and port number
            modified_message, server_address = client_socket.recvfrom(2048)
            print('Reply from server:', modified_message.decode())
            modified_message, server_address = client_socket.recvfrom(2048)
            print('Reply from server:', modified_message.decode())

        elif option == '4':
            # get server's time
            modified_message, server_address = client_socket.recvfrom(2048)
            print('Reply from server:', modified_message.decode())

        elif option == '5':
            # exit
            print("exit program")
        else:
            # error case
            print("Wrong input. Bye bye~")
    except KeyboardInterrupt:
        print("bye bye~")
        exit(0)
    except ConnectionResetError:
        print("Server is not connected")
        exit(0)
    client_socket.close()
    print("%s miliseconds" %((time.time() - start_time) * 1000))


if __name__ == '__main__':
    run_program()
