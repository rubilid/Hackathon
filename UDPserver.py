import struct
import socket
import threading
import time
from magicCookie import MagicCookie

serverIp = "127.0.0.1"
localPort = 13117
bufferSize = 1024
msg_magic_cookie = 0xabcddcba
msg_type = 0x2
msg_server_port = localPort
structured_msg = struct.pack('IBH', msg_magic_cookie, msg_type, msg_server_port)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPServerSocket.bind((serverIp, localPort))
print("Server started, listening on IP address " + serverIp)
# Listen for incoming datagrams
threads = []


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
        while clients_counter < 2:
            UDPServerSocket.sendto(self.structured_msg, (self.address, self.msg_server_port))
            time.sleep(1)


while True:
    clients_counter = 0

    newthread = OfferSendingThread(UDPServerSocket, serverIp, msg_magic_cookie, msg_type, msg_server_port)
    newthread.start()
    threads.append(newthread)
    players_addresses = []

    while clients_counter < 2:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        if address[0] == serverIp and address[1] == msg_server_port:
            continue
        else:
            clients_counter += 1
            clientMsg = "Message from Client:{}".format(message)
            clientIP = "Client IP Address:{}".format(address)
            print(clientMsg)
            print(clientIP)
            UDPServerSocket.sendto(structured_msg, address)
            players_addresses.append(address)
            # todo: create a TCP connection

    # todo: now we have 2 addresses in the form of (ip, port) in players_addresses with 2 TCP connections


    for t in threads:
        t.join()

    # todo: delete this:
    exit(0)
