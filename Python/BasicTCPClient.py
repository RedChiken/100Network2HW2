#
# SimpleEchoTCPClient.py
#

from socket import *
import time


def run_program():
    start_time = time.time()
    server_name = 'nsl2.cau.ac.kr'
    localhost = 'localhost'
    server_port = 12000
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((localhost, server_port))

        print("The client is running on port", client_socket.getsockname()[1])

        print("Press number of option to select it\n"
              "option 1) convert text to UPPER-case letters\n"
              "option 2) convert text to LOWER-case letters\n"
              "option 3) ask the server what is the IP address and port number of the client\n"
              "option 4) ask the server what the current time on the server is\n"
              "option 5) exit client program\n")
        try:
            option = input("option : ")
            client_socket.send(option.encode())
            if option == '1':
                # lowercase to uppercase
                message = input('Input lowercase sentence: ')
                client_socket.send(message.encode())
                modified_message = client_socket.recv(2048)
                print('Reply from server:', modified_message.decode())

            elif option == '2':
                # uppercase to lowercase
                message = input('Input uppercase sentence: ')
                client_socket.send(message.encode())
                modified_message = client_socket.recv(2048)
                print('Reply from server:', modified_message.decode())

            elif option == '3':
                # get server's ip and port number
                modified_message = client_socket.recv(2048)
                print('Reply from server:', modified_message.decode())
                modified_message = client_socket.recv(2048)
                print('Reply from server:', modified_message.decode())

            elif option == '4':
                # get server's time
                modified_message = client_socket.recv(2048)
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
    except ConnectionRefusedError:
        print("Server is not ready yet. Wait until server ")
        exit(0)
    client_socket.close()
    print("%s miliseconds" %((time.time() - start_time) * 1000))


if __name__ == '__main__':
    # signal.signal(signal.SIGINT, handler)
    run_program()
