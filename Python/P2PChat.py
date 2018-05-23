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
        self.receive_thread = None
        self.sock.bind(('', my_port))
        # find peer's nickname by user number
        self.peer_nickname_list = {}
        # get directly connected peer number
        self.peer_real_port = []
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
        self.receive_thread = threading.Thread(target=self.receive).start()
        # TODO: send connection REQUEST to all exist nodes
        while True:
            message = input()
            inst = message.split('\\')[1]
            if inst == 'connection':
                # TODO: print all directly connected nodes itself.
                for key in self.peer_nickname_list.keys():
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
                print()

    def receive(self):

        while True:
            raw_data, clientAddress = self.sock.recvfrom(16384)
            data_obj = json.loads(raw_data.decode())
            # TODO: if message already exist in queue, expire
            # TODO: check message by src and ACK number
            state = data_obj['type']
            if state == "connection REQUEST":
                # TODO: if condition, response ACK and delete incoming pending state on.
                # TODO: else, response FAIL
                print()
            elif state == "connection ACK":
                # TODO: if condition A and B, add outgoing nodes and response ACK.
                # TODO: if condition A and not B, add incoming nodes and pending state off.
                # TODO: if not A, response FAIL
                # condition A : outgoing nodes < 3 and all nodes < 4
                # condition B : pending state off
                print()
            elif state == "connection FAIL":
                # TODO: if incoming nodes pending, state off.
                print()
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
                print()
            # TODO: insert message to queue
            # message, clientAddress = self.sock.recvfrom(2048)
            # print("mesasge : " + str(message))
            # print("clientAddress : " + str(clientAddress))

            # TODO: get type, sender, receiver

    def serialize(self, message_type, sender_id, receiver_id, message):
        # make json object
        return {
            'type': message_type,
            'src': sender_id,
            'dst': receiver_id,
            'ack': self.ack,
            'message': message
        }

    def whisper(self, message_type, sender_id, receiver_id, message):
        # make json object and send it to object's destination
        obj = self.serialize(message_type, sender_id, receiver_id, message)
        self.transport(obj, receiver_id)
        self.ack += 1

    def transport(self, obj, receiver_id):
        # transport existing json object to new destination
        sender_id = obj['src']
        if receiver_id in self.peer_real_port.keys():
            self.sock.sendto(json.dumps(obj).encode(), (peer_name, self.peer_real_port[receiver_id]))
        else:
            for key in self.peer_real_port.keys():
                if sender_id != key:
                    self.sock.sendto(json.dumps(obj).encode(), (peer_name, self.peer_real_port[key]))

    def transport_all(self, obj):
        # transport to all nodes
        for key in peer_list.keys():
            if self.nodeID != key:
                self.transport(obj, key)

    def broadcast(self, message_type, sender_id, message):
        # make each json object and sent it.
        for key in peer_list.keys():
            if self.nodeID != key:
                self.whisper(message_type, sender_id, key, message)


if __name__ == "__main__":
    P2PChat(1, 1).run()