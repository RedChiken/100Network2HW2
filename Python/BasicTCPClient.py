# 20146561 유재범
# SimpleEchoTCPClient.py
#

from socket import *
import time


def run_program():
    server_name = 'nsl2.cau.ac.kr'
    localhost = 'localhost'
    server_port = 26561
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((localhost, server_port))

    print("The client is running on port", client_socket.getsockname()[1])

    print("Press number of option to select it\n"
          "option 1) convert text to UPPER-case letters\n"
          "option 2) convert text to LOWER-case letters\n"
          "option 3) ask the server what is the IP address and port number of the client\n"
          "option 4) ask the server what the current time on the server is\n"
          "option 5) exit client program\n")
    start_time = time.time()
    try:
        option = input("option : ")
        if option == '1':
            option += input('Input lowercase sentence: ')
        elif option == '2':
            option += input('Input uppercase sentence: ')
        elif option == '5':
            print("exit program")
        if option < '5':
            client_socket.send(option.encode())
            modified_message = client_socket.recv(2048)
            print('Reply from server: ', modified_message.decode())
    except KeyboardInterrupt:
        print("bye bye~")
    except ConnectionRefusedError:
        print("Server is not ready yet. Wait until server ")
    except ConnectionError:
        print("Server disconnect suddenly")
    client_socket.close()
    print("%s miliseconds" %((time.time() - start_time) * 1000))


if __name__ == '__main__':
    # signal.signal(signal.SIGINT, handler)
    run_program()
