import socket
import threading

peer_list = {
    1: 26561,
    2: 36561,
    3: 46561,
    4: 56561
}


class P2P(object):
    def __init__(self, node_id):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((' ', peer_list[node_id]))
        # self.sock.setblocking(0)
        # self.sock.settimeout(0.5)
        # self.receive_thread = None
        self.node_id = id

    def send(self):
        # self.receive_thread = threading.Thread(args=self.receive)
        # self.receive_thread.start()
        # self.receive_thread.join()
        self.sock.sendto("hello world".encode(), ('localhost', peer_list[1]))
        message = None
        while True:
            try:
                message, clientAddress = self.sock.recvfrom(16000)
            except ConnectionResetError:
                print("ConnectionResetError")
            except BlockingIOError:
                print("BlockingIOError")
            try:
                print(message.decode())
            except AttributeError:
                print("attribute error")
            message = input("input: ")
            self.sock.sendto(message.encode(), ('localhost', peer_list[1]))


if __name__ == "__main__":
    P2P(2).send()

