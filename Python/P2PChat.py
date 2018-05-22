import threading
import socket
import queue
import time
import json

peer_name = 'localhost'
# peer_name = 'nsl2.cau.ac.kr'
peer_port = 26561
my_port = 36561


class P2PChat(object):
    def __init__(self, node_id, nickname):
        self.nodeID = node_id
        self.nickname = nickname
        self.peer_port_list = {}
        self.peer_nickname_list = {}
        #peer_id : client port
        self.cache = queue.Queue(15)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', my_port))
        self.receive_thread = None

    def run(self):

        self.receive_thread = threading.Thread(target=self.receive).start()
        while True:
            self.sock.sendto(input().encode(), (peer_name, peer_port))

    def receive(self):

        while True:
            #1. get Text and conver to Json
            #2. Parse Json and get request message
            #3. split it by request message
            message, clientAddress = self.sock.recvfrom(2048)
            print("mesasge : " + str(message))
            print("clientAddress : " + str(clientAddress))

    def whisper(self, peer_id, message):
        self.sock.sendto(message.encode(), (peer_name, self.peer_list[peer_id]))

    def broadcast(self, message):
        for key in self.peer_port_list.keys():
            if self.nodeID != key:
                self.whisper(key, message)

    def transport(self):
        print()


if __name__ == "__main__":
    P2PChat(1, 1).run()