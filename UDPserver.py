import struct
import socket
import threading
import time
import scapy as sc
from magicCookie import MagicCookie

serverIp = "127.0.0.1"
localPort = 13117
bufferSize = 1024
server_ip_and_port = (serverIp, localPort)
msg_magic_cookie = 0xabcddcba
msg_type = 0x2
msg_server_port = localPort
structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, msg_server_port)
#global
clients_counter = -1  # will be initialized in the server
# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# UDPServerSocket.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1)
# UDPServerSocket.setsockopt(sc.SOL_SOCKET, sc.SO_BROADCAST, 1)
# Bind to address and ip
UDPServerSocket.bind((serverIp, localPort))
print("Server started, listening on IP address " + serverIp)
# Listen for incoming datagrams
threads = []
lock = threading.Lock()

class TCPconnectionThread(threading.Thread):
    def __init__(self, server_ip_and_port):
        threading.Thread.__init__(self)
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_socket.bind(server_ip_and_port)
        print("new TCPconnectionThread")

    def run(self):
        while 1:
            self.server_socket.listen(1)
            connection_socket, addr = self.server_socket.accept()
            # todo: put team_name in try
            team_name = connection_socket.recv(bufferSize).decode()
            # name = struct.unpack('s', team_name)
            # str_name = name.decode()
            # connection_socket.send(team_name)
            print("name: ", team_name)
            lock.acquire()
            count = globals()  # todo: lock this
            count['clients_counter'] += 1
            lock.release()
            connection_socket.close()


class OfferSendingThread(threading.Thread):
    def __init__(self, server_socket, address, msg_magic_cookie, msg_type, msg_server_port):
        threading.Thread.__init__(self)
        self.structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, msg_server_port)
        self.server_socket = server_socket
        self.address = address
        self.msg_magic_cookie = msg_magic_cookie
        self.msg_type = msg_type
        self.msg_server_port = msg_server_port
        print("initialized offer!")

    def run(self):
        while True:
            lock.acquire()
            count = globals()  # todo: lock this
            if count['clients_counter'] >= 2:
                lock.release()
                break
            lock.release()
            UDPServerSocket.sendto(self.structured_msg, ("127.255.255.255", self.msg_server_port))
            # UDPServerSocket.sendall(self.structured_msg)
            time.sleep(1)


while True:
    lock.acquire()
    count = globals()
    count['clients_counter'] = 0
    lock.release()
    # creating a thread for sending offers once per sec
    newthread = OfferSendingThread(UDPServerSocket, serverIp, msg_magic_cookie, msg_type, msg_server_port)
    newthread.start()
    threads.append(newthread)
    # each address in the form (ip, port)
    players_addresses = []

    while True:
        lock.acquire()
        count = globals()
        if count['clients_counter'] >= 2: #we have 2 clients connected
            lock.release()
            break
        lock.release()
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        # need to verify that the received msg not sent from server itself
        if address[0] == serverIp and address[1] == msg_server_port:
            continue
        else:
            clientMsg = "Message from Client:{}".format(message)
            clientIP = "Client IP Address:{}".format(address)
            print(clientMsg)
            print(clientIP)
            UDPServerSocket.sendto(structured_msg, address)
            players_addresses.append(address)
            tcpThread = TCPconnectionThread((server_ip_and_port[0], server_ip_and_port[1]))
            tcpThread.start()
            threads.append(tcpThread)
        # todo: close udp socket after while
        # todo: increase client_counter after receive group name

    # todo: now we have 2 addresses in the form of (ip, port) in players_addresses with 2 TCP connections

    for t in threads:
        t.join()

    # todo: delete this:
    exit(0)
