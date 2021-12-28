import struct
from socket import *
import threading
import time
# import scapy
from magicCookie import MagicCookie

teamPort = 2140
serverIp = "127.0.0.1"
localPort = 13117
bufferSize = 1024
server_ip_and_port = (serverIp, localPort)
msg_magic_cookie = 0xabcddcba
msg_type = 0x2
msg_server_port = teamPort
structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, msg_server_port)
# global
clients_counter = -1  # will be initialized in the server
# Create a datagram socket
# UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
UDPServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
UDPServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
# UDPServerSocket.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1)
# UDPServerSocket.setsockopt(sc.SOL_SOCKET, sc.SO_BROADCAST, 1)
# Bind to address and ip
UDPServerSocket.bind((serverIp, localPort))
print("Server started, listening on IP address " + serverIp)
# Listen for incoming datagrams
threads = []
lock = threading.Lock()


class TCPconnectionThread(threading.Thread):
    def __init__(self, teamPort, bufferSize):
        threading.Thread.__init__(self)
        self.teamPort = teamPort
        self.bufferSize = bufferSize

    def run(self):
        server_socket = socket(family=AF_INET, type=SOCK_STREAM)
        server_socket.bind(('', self.teamPort))
        server_socket.listen()

        # connection_socket.close()


class ClientHandlerThread(threading.Thread):
    def __init__(self, connection_socket, addr):
        threading.Thread.__init__(self)
        self.connection_socket = connection_socket
        self.addr = addr
        print("new TCPconnectionThread")

    def run(self):
        client_team_name = self.connection_socket.recv(bufferSize).decode()
        print(str(client_team_name))


class OfferSendingThread(threading.Thread):
    def __init__(self, server_socket, address, msg_magic_cookie, msg_type, teamPort, localPort):
        threading.Thread.__init__(self)
        self.structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, teamPort)
        self.server_socket = server_socket
        self.local_port = localPort
        print("initialized offer!")

    def run(self):
        while True:
            lock.acquire()
            count = globals()
            if count['clients_counter'] >= 2:
                lock.release()
                break
            lock.release()
            # UDPServerSocket.sendto(self.structured_msg, ("127.255.255.255", self.msg_server_port))
            UDPServerSocket.sendto(self.structured_msg, ('<broadcast>', self.local_port))
            # UDPServerSocket.sendall(self.structured_msg)
            time.sleep(1)


class GameThread(threading.Thread):
    def __init__(self, connection_socket, addr, client_team_name, other_team_name):
        threading.Thread.__init__(self)
        self.connection_socket = connection_socket
        self.addr = addr
        self.client_team_name = client_team_name
        self.other_team_name = other_team_name

    def run(self):
        welcome_msg = "Welcome to Quick Maths.\n" \
                      "Player 1: " + self.client_team_name + \
                      "Player 2: " + self.other_team_name +  \
                      "==\n" \
                      "Please answer the following question as fast as you can:\n"
        #         todo: try and catch
        self.connection_socket.send(str(welcome_msg).encode())
#         todo: rcv answer from client


# players addresses is of the form: (connection_socket, addr, client_team_name)
def start_game(players_addresses):
    game_threads = []
    gameThread1 = GameThread(players_addresses[0][0], players_addresses[0][1], players_addresses[0][2],
                             players_addresses[1][2])
    gameThread2 = GameThread(players_addresses[1][0], players_addresses[1][1], players_addresses[1][2],
                             players_addresses[0][2])
    gameThread1.start()
    gameThread2.start()
    game_threads.append(gameThread1)
    game_threads.append(gameThread2)


while True:
    lock.acquire()
    count = globals()
    count['clients_counter'] = 0
    lock.release()
    # creating a thread for sending offers once per sec
    newthread = OfferSendingThread(UDPServerSocket, serverIp, msg_magic_cookie, msg_type, teamPort, localPort)
    newthread.start()
    threads.append(newthread)
    # each address in the form (ip, port)
    players_addresses = []

    server_socket = socket(family=AF_INET, type=SOCK_STREAM)
    server_socket.bind(('', teamPort))
    server_socket.listen()
    while True:
        lock.acquire()
        count = globals()
        if count['clients_counter'] >= 2:
            lock.release()
            break
        lock.release()
        # todo: create thread to do this job:
        connection_socket, addr = server_socket.accept()
        client_team_name = connection_socket.recv(bufferSize).decode()
        print(client_team_name)
        lock.acquire()
        count = globals()
        count['clients_counter'] += 1
        players_addresses.append((connection_socket, addr, client_team_name))
        lock.release()
    time.sleep(2)
    start_game(players_addresses)

    # while True:
    #     lock.acquire()
    #     count = globals()
    #     if count['clients_counter'] >= 2: #we have 2 clients connected
    #         lock.release()
    #         break
    #     lock.release()

    # bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    # message = bytesAddressPair[0]
    # address = bytesAddressPair[1]
    # need to verify that the received msg not sent from server itself
    # tcpThread = TCPconnectionThread(teamPort, bufferSize)
    # tcpThread.start()
    # threads.append(tcpThread)
    # connection_socket, addr = server_socket.accept()

    # todo: close udp socket after while
    # todo: increase client_counter after receive group name

    # todo: now we have 2 addresses in the form of (ip, port) in players_addresses with 2 TCP connections

    for t in threads:
        t.join()

    # todo: delete this:
    exit(0)
