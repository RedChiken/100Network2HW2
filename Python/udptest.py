import socket
import threading
import json

peer_list = {
    1: 26561,
    2: 36561,
    3: 46561,
    4: 56561
}

peer_name = 'localhost'


class P2P(object):
    def __init__(self, node_id, nickname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((' ', peer_list[node_id]))
        # self.sock.setblocking(0)
        # self.sock.settimeout(0.5)
        # self.receive_thread = None
        self.node_id = node_id
        self.nickname = nickname
        self.ack = 0
        self.size_of_incoming = 0
        self.size_of_outgoing = 0
        self.incoming_pending_state = [False, False, False, False]
        self.peer_nickname = {}
        self.connected_peer = []

    def send(self):
        # self.sock.sendto(str(peer_list[2]).encode(), ('localhost', peer_list[2]))
        # self.sock.sendto(str(peer_list[3]).encode(), ('localhost', peer_list[3]))
        # self.sock.sendto(str(peer_list[4]).encode(), ('localhost', peer_list[4]))
        self.broadcast("connection REQUEST", self.node_id, "")
        message = None
        while True:
            try:
                message, clientAddress = self.sock.recvfrom(16000)
                raw_message = json.loads(message.decode())
                state = raw_message['type']
                if (raw_message['dst'] == self.node_id) and (raw_message['src'] != self.node_id):
                    if state == "connection REQUEST":
                        print(state)
                        if (self.size_of_incoming < 2) and (self.size_of_outgoing + self.size_of_incoming < 3):
                            self.unicast("connection ACK", self.node_id, raw_message['src'], self.nickname)
                            self.incoming_pending_state[raw_message['src']] = True
                        else:
                            self.unicast("connection FAIL", self.node_id, raw_message['src'], self.nickname)
                        self.peer_nickname[raw_message['src']] = raw_message['message']
                        continue
                    elif state == "connection ACK":
                        print(state)
                        if (self.size_of_incoming < 2) and (self.size_of_incoming + self.size_of_outgoing < 3):
                            if self.incoming_pending_state[raw_message['src']]:
                                # receive request, send ack and receive re-ack
                                # incoming node on
                                self.peer_nickname[raw_message['src']] = raw_message['message']
                                self.connected_peer.append(raw_message['src'])
                                self.incoming_pending_state[raw_message['src']] = False
                                self.size_of_incoming += 1
                            else:
                                # send request, receive ack
                                # outgoing node on
                                self.peer_nickname[raw_message['src']] = raw_message['message']
                                self.connected_peer.append(raw_message['src'])
                                self.peer_nickname[raw_message['src']] = raw_message['message']
                                self.size_of_incoming += 1
                                self.unicast("connection ACK", self.node_id, raw_message['src'], self.nickname)
                                self.size_of_outgoing += 1
                                continue
                        else:
                            # receive ack but it full before get it
                            self.unicast("connection FAIL", self.node_id, raw_message['src'], self.nickname)
                            self.incoming_pending_state[raw_message['src']] = False
                            continue
                    elif state == "connection FAIL":
                        print(state)
                        self.incoming_pending_state[raw_message['src']] = False
                    else:
                        print(raw_message['message'])
                else:
                    self.transport_all(message)
                if message != peer_list[self.node_id]:
                    pass
            except ConnectionResetError:
                print("ConnectionResetError")
            except BlockingIOError:
                print("BlockingIOError")
            try:
                print(message.decode())
            except AttributeError:
                print("attribute error")
            message = input("input: ")
            self.broadcast("message", self.node_id, message)
            # self.sock.sendto(message.encode(), ('localhost', peer_list[1]))

    def serialize(self, message_type, sender_id, receiver_id, message):
        # make json object
        return {
            "type": message_type,
            "src": sender_id,
            "dst": receiver_id,
            "ack": self.ack,
            "message": message
        }

    def unicast(self, message_type, sender_id, receiver_id, message):
        # make json object and send it to object's destination
        obj = self.serialize(message_type, sender_id, receiver_id, message)
        self.transport(obj, receiver_id)
        self.ack += 1

    def transport(self, obj, receiver_id):
        # transport existing json object to new destination
        sender_id = obj['src']
        if receiver_id in self.connected_peer:
            self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[receiver_id]))
        else:
            if len(self.connected_peer) > 0:
                for key in self.connected_peer:
                    # problem
                    if (self.node_id != key) and (sender_id != key):
                        self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[key]))
            else:
                for key in peer_list:
                    if (self.node_id != key) and (sender_id != key):
                        self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[key]))

    def transport_all(self, obj):
        # transport to all nodes
        for key in peer_list.keys():
            if self.node_id != key:
                self.transport(obj, key)

    def broadcast(self, message_type, sender_id, message):
        # make each json object and sent it.
        for key in peer_list.keys():
            if self.node_id != key:
                self.unicast(message_type, sender_id, key, message)


if __name__ == "__main__":
    P2P(2, 2).send()

