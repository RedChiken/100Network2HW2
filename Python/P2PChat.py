# 20146561 Yu Jaebeom
import threading
import socket
import queue
import time
import json

peer_name = 'localhost'
# peer_name = 'nsl2.cau.ac.kr'
peer_port = 26561
my_port = 36561

peer_list = {
    "1": 26561,
    "2": 36561,
    "3": 46561,
    "4": 56561
}


class P2PChat(object):
    def __init__(self, node_id, nickname):
        self.nodeID = node_id
        self.nickname = nickname
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', peer_list[str(node_id)]))
        self.sock.setblocking(False)
        self.sock.settimeout(5)
        self.receive_thread = None
        self.send_thread = None
        # find peer's nickname by user number
        self.peer_nickname_list = {}
        # get directly connected peer number
        self.connected_peer = []
        # cache of input message
        self.message_cache = queue.Queue(15)
        # cache of getaddr
        self.getaddr_cache = queue.Queue(3)
        # start time of ping
        self.rtt_start = 0
        self.size_of_incoming = 0
        self.incoming_pending_state = [False, False, False, False]
        self.size_of_outgoing = 0
        self.ack = 0

    # TODO: message form
    # type : state of message
    # src : number of sender
    # dst : number of receiver
    # ACK : ACK number of sender
    # message : raw message(or addr dictionary)

    def run(self):
        self.receive_thread = threading.Thread(target=self.receive)
        self.send_thread = threading.Thread(target=self.send)
        self.receive_thread.daemon = True
        self.send_thread.daemon = True
        self.send_thread.start()
        self.receive_thread.start()
        self.send_thread.join()
        self.receive_thread.join()
        print(str(self.nodeID) + " " + str(peer_list[str(self.nickname)]) + " connected")

    def send(self):
        # TODO: send connection REQUEST to all exist nodes
        for key in peer_list.keys():
            self.sock.sendto(json.dumps(
                self.serialize("connection REQUEST", self.nodeID, key, self.nickname)).encode(),
                             (peer_name, peer_list[key]))
        while True:
            print("input")
            try:
                message = input()
                if message[0] == "\\":
                    inst = message.split('\\')[1]
                    if inst == 'connection':
                        # TODO: print all directly connected nodes itself.
                        for key in self.peer_nickname_list.keys():
                            if key != self.nodeID:
                                print("peer " + str(key)
                                      + "(" + self.peer_nickname_list[key] + ") has "
                                      + str(peer_list[key]) + " port")
                    elif inst == "quit":
                        # TODO: send disconnect message
                        # TODO: kill thread
                        print()
                    elif inst == "w":
                        # TODO: whisper to nickname
                        print()
                    elif inst == "getaddr":
                        # TODO: broadcast addr response to all directly connected node
                        print()
                    elif inst == "ping":
                        # TODO: set RTT start time and whisper to nickname
                        # TODO: if it doesn't come during 5 sec, print special text.
                        print()
                    elif inst == "addr":
                        # TODO: whisper addr to nickname
                        print()
                else:
                    # TODO: broadcast message to all directly connected nodes
                    self.broadcast("message", self.nodeID, message)
            except socket.timeout:
                print("send timeout")
                time.sleep(1)

    def receive(self):
        while True:
            print("get")
            try:
                raw_data, client_address = self.sock.recvfrom(1048576)
                data_obj = json.loads(raw_data.decode())
                print(data_obj)
                # TODO: if message already exist in queue, expire
                # TODO: check message by src and ACK number
                if (data_obj['dst'] in self.message_cache.queue) or (data_obj['dst'] == str(self.nodeID)):
                    self.transport(data_obj, data_obj['dst'])
                else:
                    state = data_obj['type']
                    if state == "connection REQUEST":
                        # TODO: if condition, response ACK and delete incoming pending state on.
                        # TODO: else, response FAIL
                        if (self.size_of_incoming < 2) and (self.size_of_incoming + self.size_of_outgoing < 3):
                            print("set pending and wait")
                            self.unicast("connection ACK", self.nodeID, data_obj['src'], self.nickname)
                            self.incoming_pending_state[data_obj['src']] = True
                        else:
                            print("not allowed")
                            self.unicast("connection FAIL", data_obj['dst'], data_obj['src'], "")
                        self.peer_nickname_list[data_obj['src']] = data_obj['message']
                    elif state == "connection ACK":
                        # self.sock.settimeout(0)
                        # TODO: if condition A and B, add outgoing nodes and response ACK.
                        # TODO: if condition A and not B, add incoming nodes and pending state off.
                        # TODO: if not A, response FAIL
                        # condition A : outgoing nodes < 3 and all nodes < 4
                        # condition B : pending state off
                        if (self.size_of_outgoing < 2) and (self.size_of_outgoing + self.size_of_incoming < 3):
                            if self.incoming_pending_state:
                                print("incomming node connected")
                                self.peer_nickname_list[data_obj['src']] = data_obj['message']
                                self.connected_peer.append(data_obj['src'])
                                self.incoming_pending_state[data_obj['src']] = False
                                self.size_of_incoming += 1
                            else:
                                print("outgoing node connected")
                                self.peer_nickname_list[data_obj['src']] = data_obj['message']
                                self.connected_peer.append(data_obj['src'])
                                self.unicast("connection ACK", self.nodeID, data_obj['src'], self.nickname)
                                self.size_of_outgoing += 1
                        else:
                            print("not connected")
                            self.unicast("connection FAIL", self.nodeID, data_obj["src"], self.nickname)
                    elif state == "connection FAIL":
                        # self.sock.settimeout(0)
                        print("denied")
                        # TODO: if incoming nodes pending, state off.
                        self.incoming_pending_state[data_obj['src']] = False
                    elif state == "whisper":
                        # TODO: if dst is me, print it.
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        print()
                    elif state == "getaddr":
                        # TODO: if dst is me, response my directly connected peer list with "getaddr_response"
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        print()
                    elif state == "getaddr_response":
                        # TODO: if dst is me, insert data to addr_queue
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        # TODO: if size of queue is three, print it all and clear.
                        print()
                    elif state == "addr":
                        # TODO: if dst is me, response my directly connected peer list with "addr_response"
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        print()
                    elif state == "addr_response":
                        # TODO: if dst is me, print it
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        print()
                    elif state == "ping":
                        # TODO: if dst is me, send "pong" state to src.
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        print()
                    elif state == "pong":
                        # TODO: if dst is me, print time.time() - rtt_start
                        # TODO: else if dst is directly connected, transport to it.
                        # TODO: else, broadcast except src
                        print()
                    else:
                        # TODO: print data and transport it to all connected nodes
                        print(self.peer_nickname_list[data_obj['src']] + "> " + data_obj['message'])
            except socket.timeout:
                print("receive times up")
                # time.sleep(1)
            # TODO: insert message to queue
            # message, clientAddress = self.sock.recvfrom(2048)
            # print("mesasge : " + str(message))
            # print("clientAddress : " + str(clientAddress))

            # TODO: get type, sender, receiver

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
        print(sender_id)
        if receiver_id in self.connected_peer:
            self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[receiver_id]))
        else:
            for key in self.connected_peer:
                print(key)
                if (str(self.nodeID) != key) and (str(sender_id) != key):
                    print(str(self.nodeID))
                    self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[key]))

    def transport_all(self, obj):
        # transport to all nodes
        for key in peer_list.keys():
            if str(self.nodeID) != key:
                self.transport(obj, key)

    def broadcast(self, message_type, sender_id, message):
        # make each json object and sent it.
        for key in peer_list.keys():
            if str(self.nodeID) != key:
                self.unicast(message_type, sender_id, key, message)


if __name__ == "__main__":
    P2PChat(2, 2).run()
