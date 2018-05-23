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
        self.peer_nickname_list = {}
        self.peer_real_port = {}
        self.cache = queue.Queue(15)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', my_port))
        self.receive_thread = None
        self.rtt_start = 0
        self.size_of_incoming = 0
        self.size_of_outgoing = 0

    def run(self):

        self.receive_thread = threading.Thread(target=self.receive).start()
        # TODO: send connection REQUEST
        for key in peer_list.keys():
            if key != self.nodeID:
                obj = {
                    'type': "connection REQUEST",
                    'src': self.nodeID,
                    'dst': peer_list[key],
                    'message': ""
                }
                self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[key]))
        while True:
            # self.sock.sendto(input().encode(), (peer_name, peer_port))
            message = input()
            inst = message.split('\\')[1]
            if inst == 'connection':
                for key in self.peer_nickname_list.keys():
                    print("peer " + str(key)
                          + "(" + self.peer_nickname_list[key] + ") has "
                          + str(peer_list[key]) + " port")
            elif inst == "quit":
                for key in peer_list.keys():
                    self.whisper(inst, key, self.nickname + "will disconnect")
                # TODO: kill thread
                print()
            elif inst == "w":
                nickname = message.split()[1]
                real_message = message.split()[2]
                des_node = list(self.peer_nickname_list.keys())[list(self.peer_nickname_list.values()).index(nickname)]
                self.whisper(inst, des_node, real_message)
            elif inst == "getaddr":
                self.broadcast("getaddr", "")
                print()
            elif inst == "ping":
                nickname = message.split()[1]
                des_node = list(self.peer_nickname_list.keys())[list(self.peer_nickname_list.values()).index(nickname)]
                self.whisper(inst, des_node, "")
                self.rtt_start = time.time()
            elif inst == "addr":
                nickname = message.split()[1]
                des_node = list(self.peer_nickname_list.keys())[list(self.peer_nickname_list.values()).index(nickname)]
                self.whisper(inst, des_node, "")
            else:
                self.broadcast(3, message)
        #1. input 받음
        #2. 명령어 확인
        #   1) \connection
        #       전송 없음
        #       자신의 peer 정보 출력
        #   2) \quit
        #       전송 없음
        #       receive 쓰레드 종료 후 프로그램 종료.
        #       종료 전 피어들에게 종료 메세지 출력
        #   3) \w <nickname> <message>
        #       특정 유저에게만 메세지 전송
        #       state 설정 필요
        #   4) \getaddr
        #       각 피어들의 연결된 피어 상태 받음
        #       큐에 정보(객체)를 넣고 존재 여부 확인
        #       state 설정 필요
        #   5) \ping <nickname>
        #       time()을 이용해 RTT 출력
        #       state 설정 필요
        #       연결되어 있지 않을 경우 별도 처리 필요
        #   6) \addr <nickname>
        #       특정 닉네임의 피어 연결 정보 확인
        #       state 설정 필요
        #메세지 전송은 Json 객체로 묶어서 전송

    def receive(self):

        while True:
            raw_data, clientAddress = self.sock.recvfrom(16384)
            data_obj = json.loads(raw_data.decode())
            state = data_obj['type']
            if state == "connection REQUEST":
                if (self.size_of_incoming + self.size_of_outgoing < 3) and (self.size_of_incoming < 2):
                    obj = {
                        'type': "connection ACK",
                        'src': self.nodeID,
                        'dst': data_obj['src'],
                        'nickname': self.nickname,
                        'message': "answer"
                    }
                    self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[data_obj['src']]))
                    self.size_of_incoming += 1
                else:
                    obj = {
                        'type': "connection FAIL",
                        'src': self.nodeID,
                        'dst': data_obj['src'],
                        'message': ""
                    }
                    self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[data_obj['src']]))
            elif state == "connection ACK":
                if (self.size_of_outgoing < 2) and (self.size_of_outgoing + self.size_of_incoming < 3):
                    if data_obj['message'] == "answer":
                        self.peer_real_port[data_obj['src']] = peer_list[data_obj['src']]
                        self.peer_nickname_list[data_obj['src']] = data_obj['nickname']
                        self.size_of_outgoing += 1
                        obj = {
                            'type': "connection FAIL",
                            'src': self.nodeID,
                            'dst': data_obj['src'],
                            'message': "re_answer"
                        }
                        self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[data_obj['src']]))
                    elif data_obj['message'] == "re_answer":
                        self.peer_real_port[data_obj['src']] = peer_list[data_obj['src']]
                        self.peer_nickname_list[data_obj['src']] = data_obj['nickname']
                else:
                    obj = {
                        'type': "connection FAIL",
                        'src': self.nodeID,
                        'dst': data_obj['src'],
                        'message': ""
                    }
                    self.sock.sendto(json.dumps(obj).encode(), (peer_name, peer_list[data_obj['src']]))
            elif state == "connection FAIL":
                # TODO: 상대 노드를 내 연결 노드 안에서 검색해야 한다. 간접 연결로 돌려야 한다.
                print()
            elif state == "whisper":
                if data_obj['dst'] == self.nodeID:
                    print(self.nickname[data_obj['src']] + "> " + data_obj['message'])
                else:
                    self.sock.sendto(json.dumps(data_obj).encode, (peer_name, self.peer_real_port[data_obj['dst']]))
            elif state == "getaddr":
                print()
            elif state == "addr":
                if data_obj['dst'] == self.nodeID:
                    obj = {
                        'type': "addr_response",
                        'src': self.nodeID,
                        'dst': data_obj['src'],
                        'addr': self.peer_real_port
                    }
                    self.sock.sendto(json.dumps(obj).encode(), (peer_name, self.peer_real_port[data_obj['dst']]))
                else:
                    self.sock.sendto(json.dumps(data_obj).encode, (peer_name, self.peer_real_port[data_obj['dst']]))
            elif state == "addr_response":
                # TODO: response of addr
                print()
            elif state == "getaddr_response":
                # TODO: response of getaddr. use queue
                print()
            elif state == "ping":
                if data_obj['dst'] == self.nodeID:
                    self.whisper("pong", data_obj['src'], "")
                else:
                    self.sock.sendto(json.dumps(data_obj).encode, (peer_name, self.peer_real_port[data_obj['dst']]))
                print()
            elif state == "pong":
                rtt = time.time() - self.rtt_start
                self.rtt_start = 0
                print("RTT with " + self.peer_nickname_list[data_obj['src']] + ": " + str(rtt))
            else:
                if data_obj['dst'] == self.nodeID:
                    print()
                else:
                    print()
                print()
            # 1. Json 객체의 정보 풀기
            # 2. state 확인
            #  1) connection REQUEST
            #      incoming node가 남았는지 확인
            #        true : pending state, connection ACK를 전송
            #        false : connection FAIL 전송
            #  2) connection ACK
            #      pending state인지 확인
            #        true : 노드 연결
            #      내 outcoming node가 남았는지 확인
            #        true : 노드 연결, connection ACK 전송
            #        false : 무시, connection FAIL 전송
            #  3) connection FAIL
            #    pending state인지 확인
            #       true : pending 해제
            #  4) whisper state
            #      state 설정 필요
            #      자신과 대상이 맞는지 확인
            #        true : 메세지 출력
            #        false : 내 peer 중 해당 대상의 peer 있는지 확인
            #          true : 자신의 peer 연결 정보를 전송
            #          false : 자신의 모든 peer들에게 peer 연결 정보를 전송
            #  5) getaddr
            #      state 설정 필요
            #      이 메세지 전송자가 peer에 있는지 확인
            #        true : 자신의 peer 연결 정보를 전송
            #        false : 자신의 모든 peer들에게 peer 연결 정보를 전송
            #  6) addr
            #      getaddr과 같은 기능, 같은 state
            #  7) ping
            #      state 설정 필요
            #      자신의 peer 중 전송자가 있는지 확인
            #        true : 자신의 peer에게 ping message 전송
            #        true : 자신의 모든 peer에게 ping message 전송
            #  8) 일반 메세지
            #      message가 큐에 있는지 확인
            #        false : 메세지 출력, queue에 추가
            #      message life cycle 확인
            #        cycle == 0 : 정지
            #        cycle > 0 : cycle--, 자신의 peer들에게 메세지 전송
            message, clientAddress = self.sock.recvfrom(2048)
            print("mesasge : " + str(message))
            print("clientAddress : " + str(clientAddress))

    def whisper(self, message_type, peer_id, message):
        obj = {
            'type': message_type,
            'src': self.nodeID,
            'dst': peer_id,
            'message': message
        }
        self.sock.sendto(json.dumps(obj).encode(), (peer_name, self.peer_real_port[peer_id]))

    def broadcast(self, message_type, message):
        for key in peer_list.keys():
            if self.nodeID != key:
                self.whisper(message_type, key, message)


if __name__ == "__main__":
    P2PChat(1, 1).run()